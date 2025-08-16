"""
Interaction logging utilities for LLM requests and responses.
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import threading
from queue import Queue, Empty
import uuid

from ..models.request import LLMRequest
from ..models.response import LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Single interaction log entry."""
    id: str
    timestamp: str
    entry_type: str  # "request" or "response"
    model: str
    content: str
    metadata: Dict[str, Any] = None
    token_usage: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LogRotator:
    """Handles log file rotation and archiving."""
    
    def __init__(self, 
                 log_file_path: Union[str, Path],
                 max_size_bytes: int = 100 * 1024 * 1024,  # 100MB
                 max_files: int = 5):
        """
        Initialize log rotator.
        
        Args:
            log_file_path: Path to the main log file
            max_size_bytes: Maximum size before rotation
            max_files: Maximum number of rotated files to keep
        """
        self.log_file_path = Path(log_file_path)
        self.max_size_bytes = max_size_bytes
        self.max_files = max_files
        self._lock = threading.Lock()
    
    def should_rotate(self) -> bool:
        """Check if log file should be rotated."""
        if not self.log_file_path.exists():
            return False
        
        try:
            return self.log_file_path.stat().st_size >= self.max_size_bytes
        except OSError:
            return False
    
    def rotate(self) -> bool:
        """
        Rotate the log file.
        
        Returns:
            True if rotation was successful
        """
        with self._lock:
            if not self.log_file_path.exists():
                return True
            
            try:
                # Generate timestamp for archived file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Create archive filename
                archive_path = self.log_file_path.with_suffix(f".{timestamp}{self.log_file_path.suffix}")
                
                # Move current log to archive
                self.log_file_path.rename(archive_path)
                
                # Clean up old archives
                self._cleanup_old_archives()
                
                logger.info(f"Rotated log file to {archive_path}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to rotate log file: {e}")
                return False
    
    def _cleanup_old_archives(self) -> None:
        """Remove old archive files beyond the limit."""
        try:
            # Find all archive files
            pattern = f"{self.log_file_path.stem}.*{self.log_file_path.suffix}"
            archives = list(self.log_file_path.parent.glob(pattern))
            
            # Sort by modification time (newest first)
            archives.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove excess files
            for archive in archives[self.max_files:]:
                try:
                    archive.unlink()
                    logger.info(f"Removed old archive: {archive}")
                except Exception as e:
                    logger.warning(f"Failed to remove archive {archive}: {e}")
                    
        except Exception as e:
            logger.warning(f"Failed to cleanup old archives: {e}")
    
    def get_archive_files(self) -> List[Path]:
        """Get list of archive files."""
        try:
            pattern = f"{self.log_file_path.stem}.*{self.log_file_path.suffix}"
            archives = list(self.log_file_path.parent.glob(pattern))
            return sorted(archives, key=lambda p: p.stat().st_mtime, reverse=True)
        except Exception:
            return []


class InteractionLogger:
    """Logs all LLM interactions for debugging and tracking."""
    
    def __init__(self, 
                 log_file_path: Union[str, Path] = "llm_interactions.jsonl",
                 max_log_size: int = 100 * 1024 * 1024,  # 100MB
                 max_files: int = 5,
                 async_logging: bool = True,
                 log_content: bool = True,
                 log_metadata: bool = True):
        """
        Initialize the interaction logger.
        
        Args:
            log_file_path: Path to the log file
            max_log_size: Maximum log file size before rotation
            max_files: Maximum number of rotated files to keep
            async_logging: Whether to use asynchronous logging
            log_content: Whether to log request/response content
            log_metadata: Whether to log metadata
        """
        self.log_file_path = Path(log_file_path)
        self.log_content = log_content
        self.log_metadata = log_metadata
        
        # Ensure log directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log rotator
        self.rotator = LogRotator(log_file_path, max_log_size, max_files)
        
        # Async logging setup
        self.async_logging = async_logging
        if async_logging:
            self._log_queue: Queue = Queue()
            self._logging_thread = threading.Thread(target=self._async_log_worker, daemon=True)
            self._logging_thread.start()
            self._shutdown = False
        
        # Track active requests
        self._active_requests: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def log_request(self, request: LLMRequest, request_id: Optional[str] = None) -> str:
        """
        Log an LLM request.
        
        Args:
            request: The LLM request to log
            request_id: Optional request ID (generates one if None)
            
        Returns:
            Request ID for correlation with response
        """
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        # Store request start time for duration calculation
        with self._lock:
            self._active_requests[request_id] = {
                "start_time": time.time(),
                "model": request.model
            }
        
        # Create log entry
        entry = LogEntry(
            id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry_type="request",
            model=request.model,
            content=self._extract_request_content(request) if self.log_content else "",
            metadata=self._extract_request_metadata(request) if self.log_metadata else {}
        )
        
        self._write_log_entry(entry)
        return request_id
    
    def log_response(self, 
                    response: LLMResponse, 
                    request_id: str,
                    error: Optional[str] = None) -> None:
        """
        Log an LLM response.
        
        Args:
            response: The LLM response to log
            request_id: Request ID for correlation
            error: Optional error message if request failed
        """
        # Calculate duration
        duration_ms = None
        model = response.model if response else "unknown"
        
        with self._lock:
            if request_id in self._active_requests:
                start_time = self._active_requests[request_id]["start_time"]
                duration_ms = (time.time() - start_time) * 1000
                model = self._active_requests[request_id]["model"]
                del self._active_requests[request_id]
        
        # Create log entry
        entry = LogEntry(
            id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry_type="response",
            model=model,
            content=response.content if response and self.log_content else "",
            metadata=self._extract_response_metadata(response) if response and self.log_metadata else {},
            token_usage=response.usage if response else None,
            duration_ms=duration_ms,
            error=error
        )
        
        self._write_log_entry(entry)
    
    def _extract_request_content(self, request: LLMRequest) -> str:
        """Extract content from request for logging."""
        content_parts = []
        
        # Add prompt key
        content_parts.append(f"Prompt: {request.prompt_key}")
        
        # Add substitutions (truncate if too long)
        if request.substitutions:
            for key, value in request.substitutions.items():
                value_str = str(value)
                if len(value_str) > 1000:  # Truncate long values
                    value_str = value_str[:1000] + "... [truncated]"
                content_parts.append(f"{key}: {value_str}")
        
        # Add file attachments info
        if request.file_attachments:
            file_info = [f"{att.file_path} ({att.content_type})" for att in request.file_attachments]
            content_parts.append(f"Files: {', '.join(file_info)}")
        
        return "\n".join(content_parts)
    
    def _extract_request_metadata(self, request: LLMRequest) -> Dict[str, Any]:
        """Extract metadata from request for logging."""
        metadata = {}
        
        if request.response_format:
            metadata["response_format"] = request.response_format
        
        if request.model_params:
            metadata["model_params"] = request.model_params
        
        if request.metadata:
            metadata["request_metadata"] = request.metadata
        
        if request.file_attachments:
            metadata["file_count"] = len(request.file_attachments)
            metadata["file_types"] = list(set(att.content_type for att in request.file_attachments))
        
        if hasattr(request, 'context_analysis') and request.context_analysis:
            metadata["context_analysis"] = {
                "total_tokens": request.context_analysis.total_tokens,
                "requires_upshift": request.context_analysis.requires_upshift,
                "requires_chunking": request.context_analysis.requires_chunking
            }
        
        return metadata
    
    def _extract_response_metadata(self, response: LLMResponse) -> Dict[str, Any]:
        """Extract metadata from response for logging."""
        metadata = {}
        
        if response.metadata:
            metadata["response_metadata"] = response.metadata
        
        if response.usage:
            metadata["token_usage"] = response.usage
        
        # Add content length
        metadata["content_length"] = len(response.content) if response.content else 0
        
        return metadata
    
    def _write_log_entry(self, entry: LogEntry) -> None:
        """Write a log entry to file."""
        if self.async_logging:
            try:
                self._log_queue.put(entry, timeout=1.0)
            except Exception as e:
                logger.warning(f"Failed to queue log entry: {e}")
                # Fallback to synchronous logging
                self._write_log_entry_sync(entry)
        else:
            self._write_log_entry_sync(entry)
    
    def _write_log_entry_sync(self, entry: LogEntry) -> None:
        """Write log entry synchronously."""
        try:
            # Check if rotation is needed
            if self.rotator.should_rotate():
                self.rotator.rotate()
            
            # Write entry as JSON line
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                json.dump(asdict(entry), f, ensure_ascii=False)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")
    
    def _async_log_worker(self) -> None:
        """Worker thread for asynchronous logging."""
        while not self._shutdown:
            try:
                entry = self._log_queue.get(timeout=1.0)
                self._write_log_entry_sync(entry)
                self._log_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in async log worker: {e}")
    
    def get_recent_interactions(self, 
                              count: int = 10,
                              model_filter: Optional[str] = None,
                              entry_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve recent interactions from the log.
        
        Args:
            count: Number of interactions to retrieve
            model_filter: Filter by model name
            entry_type_filter: Filter by entry type ("request" or "response")
            
        Returns:
            List of log entries
        """
        interactions = []
        
        try:
            if not self.log_file_path.exists():
                return interactions
            
            # Read log file in reverse order (most recent first)
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in reversed(lines):
                if len(interactions) >= count:
                    break
                
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if model_filter and entry.get("model") != model_filter:
                        continue
                    
                    if entry_type_filter and entry.get("entry_type") != entry_type_filter:
                        continue
                    
                    interactions.append(entry)
                    
                except json.JSONDecodeError:
                    continue
            
        except Exception as e:
            logger.error(f"Failed to read recent interactions: {e}")
        
        return interactions
    
    def get_interaction_by_id(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Get all log entries for a specific request ID.
        
        Args:
            request_id: Request ID to search for
            
        Returns:
            List of log entries (request and response)
        """
        entries = []
        
        try:
            if not self.log_file_path.exists():
                return entries
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("id") == request_id:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            logger.error(f"Failed to search for interaction {request_id}: {e}")
        
        return entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        stats = {
            "total_entries": 0,
            "requests": 0,
            "responses": 0,
            "errors": 0,
            "models": {},
            "avg_duration_ms": 0,
            "log_file_size": 0,
            "archive_files": 0
        }
        
        try:
            if self.log_file_path.exists():
                stats["log_file_size"] = self.log_file_path.stat().st_size
            
            # Count archive files
            stats["archive_files"] = len(self.rotator.get_archive_files())
            
            # Analyze recent entries for statistics
            recent_entries = self.get_recent_interactions(1000)  # Last 1000 entries
            
            durations = []
            
            for entry in recent_entries:
                stats["total_entries"] += 1
                
                if entry.get("entry_type") == "request":
                    stats["requests"] += 1
                elif entry.get("entry_type") == "response":
                    stats["responses"] += 1
                
                if entry.get("error"):
                    stats["errors"] += 1
                
                model = entry.get("model", "unknown")
                stats["models"][model] = stats["models"].get(model, 0) + 1
                
                if entry.get("duration_ms"):
                    durations.append(entry["duration_ms"])
            
            if durations:
                stats["avg_duration_ms"] = sum(durations) / len(durations)
            
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
        
        return stats
    
    def clear_logs(self, keep_archives: bool = False) -> bool:
        """
        Clear log files.
        
        Args:
            keep_archives: Whether to keep archive files
            
        Returns:
            True if successful
        """
        try:
            # Remove main log file
            if self.log_file_path.exists():
                self.log_file_path.unlink()
            
            # Remove archives if requested
            if not keep_archives:
                for archive in self.rotator.get_archive_files():
                    try:
                        archive.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to remove archive {archive}: {e}")
            
            logger.info("Cleared log files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the logger and cleanup resources."""
        if self.async_logging:
            self._shutdown = True
            
            # Wait for queue to be processed
            try:
                self._log_queue.join()
            except Exception:
                pass
            
            # Wait for thread to finish
            if self._logging_thread.is_alive():
                self._logging_thread.join(timeout=5.0)
        
        logger.info("Interaction logger shutdown complete")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()