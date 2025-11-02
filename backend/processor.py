import threading
from pathlib import Path
from queue import Queue, Empty
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

import config
from logger import setup_logging
from transcription import transcribe_audio_simple, SUPPORTED_FORMATS
from summarize import summarize_conversation
from jobs import get_job_manager, JobStatus

logger = setup_logging(__name__)


class AudioFileHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue
        self._processed = set()
    
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = Path(event.src_path)
            
            if file_path.suffix.lower() in SUPPORTED_FORMATS:
                if str(file_path) not in self._processed:
                    logger.info(f"New audio file detected: {file_path.name}")
                    self.queue.put(str(file_path))
                    self._processed.add(str(file_path))


class AudioProcessor:
    def __init__(self):
        self.queue = Queue()
        self.observer = None
        self.worker_thread = None
        self._running = False
        self.job_manager = get_job_manager()
        self._setup_directories()
        logger.info("AudioProcessor initialized")
    
    def _setup_directories(self):
        config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (config.OUTPUT_DIR / "transcriptions").mkdir(exist_ok=True)
        (config.OUTPUT_DIR / "summaries").mkdir(exist_ok=True)
        (config.INPUT_DIR / "processed").mkdir(exist_ok=True)
        logger.info(f"Directories: input={config.INPUT_DIR}, output={config.OUTPUT_DIR}")
    
    def start(self):
        if self._running:
            logger.warning("Processor already running")
            return
        
        self._running = True
        
        if config.AUTO_PROCESS_ON_STARTUP:
            self._start_watcher()
        
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        self._scan_existing_files()
        logger.info("AudioProcessor started")
    
    def stop(self):
        if not self._running:
            return
        
        self._running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        logger.info("AudioProcessor stopped")
    
    def _start_watcher(self):
        handler = AudioFileHandler(self.queue)
        self.observer = Observer()
        self.observer.schedule(handler, str(config.INPUT_DIR), recursive=False)
        self.observer.start()
        logger.info(f"File watcher started: {config.INPUT_DIR}")
    
    def _scan_existing_files(self):
        logger.info("Scanning for existing audio files")
        count = 0
        for file_path in config.INPUT_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
                logger.info(f"Found existing file: {file_path.name}")
                self.queue.put(str(file_path))
                count += 1
        
        if count > 0:
            logger.info(f"Queued {count} existing files")
        else:
            logger.info("No existing files found")
    
    def _process_queue(self):
        logger.info("Worker thread started")
        
        while self._running:
            try:
                file_path = self.queue.get(timeout=1)
                
                try:
                    self._process_file(file_path)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                finally:
                    self.queue.task_done()
            except Empty:
                continue
        
        logger.info("Worker thread stopped")
    
    def _process_file(self, file_path: str):
        file_path = Path(file_path)
        filename = file_path.name
        logger.info(f"Processing: {filename}")
        
        job = self.job_manager.create_job(
            filename=filename,
            metadata={'file_path': str(file_path)}
        )
        
        try:
            logger.info(f"Transcribing: {filename}")
            self.job_manager.update_job_status(job.id, JobStatus.TRANSCRIBING)
            
            transcription = transcribe_audio_simple(str(file_path))
            self.job_manager.update_job_transcription(job.id, transcription)
            
            transcription_path = self._save_transcription(file_path, transcription)
            logger.info(f"Transcription saved: {transcription_path.name}")
            
            logger.info(f"Summarizing: {filename}")
            self.job_manager.update_job_status(job.id, JobStatus.SUMMARIZING)
            
            summary = summarize_conversation(transcription)
            self.job_manager.update_job_summary(job.id, summary)
            
            summary_path = self._save_summary(file_path, summary)
            logger.info(f"Summary saved: {summary_path.name}")
            
            self.job_manager.complete_job(job.id)
            
            if config.DELETE_AFTER_PROCESSING:
                file_path.unlink()
                logger.info(f"Deleted: {filename}")
            else:
                processed_path = config.INPUT_DIR / "processed" / filename
                file_path.rename(processed_path)
                logger.info(f"Moved to processed: {filename}")
            
            logger.info(f"Completed: {filename}")
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            logger.error(f"{filename}: {error_msg}")
            self.job_manager.fail_job(job.id, error_msg)
    
    def _save_transcription(self, audio_path: Path, transcription: str) -> Path:
        output_path = config.OUTPUT_DIR / "transcriptions" / f"{audio_path.stem}.txt"
        output_path.write_text(transcription, encoding='utf-8')
        return output_path
    
    def _save_summary(self, audio_path: Path, summary: str) -> Path:
        output_path = config.OUTPUT_DIR / "summaries" / f"{audio_path.stem}_summary.txt"
        output_path.write_text(summary, encoding='utf-8')
        return output_path
    
    def add_file(self, file_path: str):
        self.queue.put(file_path)
        logger.info(f"File queued: {file_path}")
    
    def get_queue_size(self) -> int:
        return self.queue.qsize()


_processor: Optional[AudioProcessor] = None


def get_processor() -> AudioProcessor:
    global _processor
    if _processor is None:
        _processor = AudioProcessor()
    return _processor
