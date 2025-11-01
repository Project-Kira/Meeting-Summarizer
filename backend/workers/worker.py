import asyncio
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import time

from config import get_settings
from db import (
    init_db_pool,
    close_db_pool,
    MeetingRepository,
    SegmentRepository,
    SummaryRepository,
    JobRepository,
)
from models import JobStatus, JobType, SummaryType
from workers.chunker import TranscriptChunker
from workers.merger import SummaryMerger
import logging

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self):
        self.settings = get_settings()
        self.chunker = TranscriptChunker(
            chunk_size=self.settings.chunk_size,
            overlap_ratio=self.settings.chunk_overlap,
        )
        self.merger = SummaryMerger()
        self.running = False
        self.inference_client = httpx.AsyncClient(timeout=120.0)

    async def start(self):
        logger.info("Starting worker...")
        await init_db_pool()
        self.running = True
        
        tasks = [
            self.process_jobs(),
            self.monitor_batches(),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Worker interrupted, shutting down...")
        finally:
            await self.stop()

    async def stop(self):
        self.running = False
        await self.inference_client.aclose()
        await close_db_pool()
        logger.info("Worker stopped")

    async def process_jobs(self):
        while self.running:
            try:
                jobs = await JobRepository.get_pending(limit=5)
                
                if not jobs:
                    await asyncio.sleep(2)
                    continue
                
                for job in jobs:
                    await self.process_job(job)
                    
            except Exception as e:
                logger.error(f"Error in process_jobs: {e}")
                await asyncio.sleep(5)

    async def process_job(self, job):
        job_id = job.id
        max_retries = self.settings.worker_max_retries
        
        try:
            await JobRepository.update_status(job_id, JobStatus.PROCESSING)
            
            if job.type == JobType.CHUNK_SUMMARY:
                await self.handle_chunk_summary(job)
            elif job.type == JobType.COMPOSE_SUMMARY:
                await self.handle_compose_summary(job)
            elif job.type == JobType.ANNOTATE_ACTION_ITEMS:
                await self.handle_annotate_action_items(job)
            
            await JobRepository.update_status(job_id, JobStatus.COMPLETED)
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            attempts = await JobRepository.increment_attempts(job_id)
            error_msg = str(e)
            
            if attempts >= max_retries:
                await JobRepository.update_status(job_id, JobStatus.FAILED, error_msg)
                logger.error(f"Job {job_id} failed after {attempts} attempts: {error_msg}")
            else:
                await JobRepository.update_status(job_id, JobStatus.PENDING, error_msg)
                backoff = self.settings.worker_backoff_base ** attempts
                logger.warning(f"Job {job_id} failed, retry {attempts}/{max_retries} after {backoff}s: {error_msg}")
                await asyncio.sleep(backoff)

    async def handle_chunk_summary(self, job):
        meeting_id = job.meeting_id
        payload = job.payload
        
        segments = await SegmentRepository.get_by_meeting(meeting_id)
        
        if not segments:
            logger.warning(f"No segments found for meeting {meeting_id}")
            return
        
        segment_dicts = [
            {
                "id": str(s.id),
                "speaker": s.speaker,
                "ts": s.ts.isoformat(),
                "text": s.text,
            }
            for s in segments
        ]
        
        chunks = self.chunker.chunk_segments(segment_dicts)
        
        for chunk in chunks:
            prompt = self.chunker.create_prompt(chunk)
            response = await self.call_inference(prompt)
            
            try:
                summary_data = json.loads(response)
                summary_data["source_segment_ids"] = chunk.segment_ids
                
                await SummaryRepository.create(
                    meeting_id=meeting_id,
                    summary_type=SummaryType.INCREMENTAL,
                    content=summary_data,
                )
                logger.info(f"Created incremental summary for meeting {meeting_id}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse summary JSON: {e}, response: {response}")

    async def handle_compose_summary(self, job):
        meeting_id = job.meeting_id
        
        incremental_summaries = await SummaryRepository.get_all_incremental(meeting_id)
        
        if not incremental_summaries:
            logger.warning(f"No incremental summaries for meeting {meeting_id}")
            return
        
        merged = self.merger.merge_summaries([s.content for s in incremental_summaries])
        
        await SummaryRepository.create(
            meeting_id=meeting_id,
            summary_type=SummaryType.FINAL,
            content=merged,
        )
        logger.info(f"Created final summary for meeting {meeting_id}")

    async def handle_annotate_action_items(self, job):
        meeting_id = job.meeting_id
        
        latest_summary = await SummaryRepository.get_latest(meeting_id, SummaryType.FINAL)
        
        if not latest_summary:
            logger.warning(f"No final summary found for meeting {meeting_id}")
            return
        
        content = latest_summary.content
        action_items = content.get("action_items", [])
        
        for item in action_items:
            if not item.get("owner") or not item.get("due_date_iso"):
                prompt = self.create_annotation_prompt(item["text"])
                response = await self.call_inference(prompt)
                
                try:
                    annotation = json.loads(response)
                    item["owner"] = annotation.get("owner", item.get("owner"))
                    item["due_date_iso"] = annotation.get("due_date_iso", item.get("due_date_iso"))
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse annotation: {response}")
        
        await SummaryRepository.create(
            meeting_id=meeting_id,
            summary_type=SummaryType.FINAL,
            content=content,
        )

    async def monitor_batches(self):
        while self.running:
            try:
                await asyncio.sleep(self.settings.worker_batch_timeout)
                
                meetings = await self.get_active_meetings_needing_summary()
                
                for meeting_id in meetings:
                    total_tokens = await SegmentRepository.get_total_tokens(meeting_id)
                    
                    if total_tokens >= self.settings.worker_batch_tokens:
                        await JobRepository.create(
                            meeting_id=meeting_id,
                            job_type=JobType.CHUNK_SUMMARY,
                            payload={},
                        )
                        logger.info(f"Created batch job for meeting {meeting_id} ({total_tokens} tokens)")
                        
            except Exception as e:
                logger.error(f"Error in monitor_batches: {e}")

    async def get_active_meetings_needing_summary(self) -> List[UUID]:
        return []

    async def call_inference(self, prompt: str) -> str:
        url = f"http://{self.settings.inference_host}:{self.settings.inference_port}/v1/completions"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.3,
            "stop": ["User", "Assistant"],
        }
        
        headers = {"Authorization": f"Bearer {self.settings.inference_api_key}"}
        
        response = await self.inference_client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["text"].strip()

    def create_annotation_prompt(self, action_text: str) -> str:
        return f"""Extract owner and due date from this action item.
Return JSON: {{"owner": "name or null", "due_date_iso": "YYYY-MM-DD or null"}}

Action: {action_text}"""


if __name__ == "__main__":
    import sys
    from app.logging import setup_logging
    
    setup_logging()
    worker = Worker()
    
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
