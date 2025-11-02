from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict
import uuid
from logger import setup_logging

logger = setup_logging(__name__)


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    filename: str
    status: JobStatus
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    transcription: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self, include_transcription: bool = False) -> Dict[str, Any]:
        """
        Convert job to dictionary for API responses.
        
        Args:
            include_transcription: If False, excludes transcription field to reduce payload size
        """
        data = asdict(self)
        for key in ['created_at', 'started_at', 'completed_at']:
            if data[key]:
                data[key] = data[key].isoformat()
        data['status'] = self.status.value
        
        # Remove transcription from response unless explicitly requested
        if not include_transcription:
            data.pop('transcription', None)
        
        return data
    
    def mark_started(self):
        self.started_at = datetime.now()
    
    def mark_completed(self):
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        self.status = JobStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
    
    def duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class JobManager:
    def __init__(self, max_jobs: int = 1000):
        self._jobs: Dict[str, Job] = {}
        self._max_jobs = max_jobs
        logger.info(f"JobManager initialized (max_jobs={max_jobs})")
    
    def create_job(self, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            filename=filename,
            status=JobStatus.PENDING,
            metadata=metadata or {}
        )
        
        self._jobs[job_id] = job
        logger.info(f"Job created: {job_id} ({filename})")
        
        if len(self._jobs) > self._max_jobs:
            self._cleanup_old_jobs()
        
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: JobStatus):
        job = self._jobs.get(job_id)
        if job:
            old_status = job.status
            job.status = status
            
            if status == JobStatus.TRANSCRIBING and not job.started_at:
                job.mark_started()
            
            logger.info(f"Job {job_id}: {old_status.value} -> {status.value}")
    
    def update_job_transcription(self, job_id: str, transcription: str):
        job = self._jobs.get(job_id)
        if job:
            job.transcription = transcription
            logger.info(f"Job {job_id}: transcription updated ({len(transcription)} chars)")

    def update_job_summary(self, job_id: str, summary: str):
        job = self._jobs.get(job_id)
        if job:
            job.summary = summary
            logger.info(f"Job {job_id}: summary updated ({len(summary)} chars)")
    
    def complete_job(self, job_id: str):
        job = self._jobs.get(job_id)
        if job:
            job.mark_completed()
            duration = job.duration()
            logger.info(f"Job {job_id} completed ({duration:.2f}s)")
    
    def fail_job(self, job_id: str, error: str):
        job = self._jobs.get(job_id)
        if job:
            job.mark_failed(error)
            logger.error(f"Job {job_id} failed: {error}")
    
    def list_jobs(self, limit: int = 100) -> list[Job]:
        jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        return jobs[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {'total': len(self._jobs), 'by_status': {}}
        for status in JobStatus:
            count = sum(1 for job in self._jobs.values() if job.status == status)
            stats['by_status'][status.value] = count
        return stats
    
    def _cleanup_old_jobs(self):
        active_jobs = [j for j in self._jobs.values() 
                      if j.status in [JobStatus.PENDING, JobStatus.TRANSCRIBING, JobStatus.SUMMARIZING]]
        
        finished_jobs = sorted(
            [j for j in self._jobs.values() 
             if j.status in [JobStatus.COMPLETED, JobStatus.FAILED]],
            key=lambda j: j.completed_at or j.created_at,
            reverse=True
        )
        
        keep_jobs = active_jobs + finished_jobs[:self._max_jobs - len(active_jobs)]
        keep_ids = {j.id for j in keep_jobs}
        
        removed = 0
        for job_id in list(self._jobs.keys()):
            if job_id not in keep_ids:
                del self._jobs[job_id]
                removed += 1
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old jobs")


# Global job manager instance
_job_manager = None


def get_job_manager() -> JobManager:
    """
    Get the global job manager instance.
    
    Returns:
        JobManager instance
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
