"""Unity RPC client for file-based communication with Unity Editor."""

import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
import concurrent.futures

import aiofiles
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class UnityRpcClient:
    """Client for communicating with Unity Editor via file-based RPC."""

    def __init__(self) -> None:
        self._unity_project_root: Optional[str] = None
        self._pending_requests: Dict[str, concurrent.futures.Future[Any]] = {}
        self._observer: Optional[Observer] = None
        self._response_handler: Optional[ResponseFileHandler] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_unity_project_root(self, project_root: str) -> None:
        """Set the Unity project root and start watching for responses."""
        if self._unity_project_root == project_root:
            return

        # Stop existing watcher if any
        self._stop_file_watcher()

        self._unity_project_root = project_root
        self._start_file_watcher()
        logger.info(f"Unity project root set to: {project_root}")

    def _start_file_watcher(self) -> None:
        """Start watching for response files."""
        if not self._unity_project_root:
            return

        requests_dir = Path(self._unity_project_root) / "Temp" / "Coplay" / "MCPRequests"
        if not requests_dir.exists():
            logger.warning(f"Unity requests directory does not exist: {requests_dir}")
            return

        # Store the current event loop for thread-safe communication
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No running event loop found, file watching may not work properly")
            return

        self._response_handler = ResponseFileHandler(self._handle_response_file_sync, self._loop)
        self._observer = Observer()
        self._observer.schedule(
            self._response_handler,
            str(requests_dir),
            recursive=False
        )
        self._observer.start()
        logger.info(f"Started watching for responses in: {requests_dir}")

    def _stop_file_watcher(self) -> None:
        """Stop watching for response files."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            self._response_handler = None

    def _handle_response_file_sync(self, file_path: Path) -> None:
        """Handle a response file from Unity (synchronous version for thread safety)."""
        try:
            logger.info(f"Handling file change: {file_path}")

            if not file_path.name.startswith("response_") or not file_path.name.endswith(".json"):
                return

            # Read response file synchronously
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    response_json = f.read()
            except Exception as e:
                logger.error(f"Failed to read response file {file_path}: {e}")
                return

            response_data = json.loads(response_json)
            request_id = response_data.get('id')
            if request_id not in self._pending_requests:
                logger.warning(f"No pending request found for ID: {request_id}")
                return

            future = self._pending_requests.pop(request_id)

            if "error" in response_data and response_data["error"]:
                error_msg = response_data["error"]
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("message", str(error_msg))
                future.set_exception(Exception(str(error_msg)))
            else:
                future.set_result(response_data.get("result"))

            # Clean up response file
            try:
                file_path.unlink()
                logger.debug(f"Deleted response file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete response file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error handling response file {file_path}: {e}")

    async def execute_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 60.0
    ) -> Any:
        """Execute an RPC request to Unity Editor."""
        if not self._unity_project_root:
            raise RuntimeError("Unity project root is not set. Call set_unity_project_root first.")

        requests_dir = Path(self._unity_project_root) / "Temp" / "Coplay" / "MCPRequests"
        if not requests_dir.exists():
            raise RuntimeError("Unity Editor is not running at the specified project root")

        request_id = str(uuid.uuid4())
        request_file = requests_dir / f"req_{request_id}.json"

        # Create request data
        request_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # Create concurrent.futures.Future for thread-safe completion
        future: concurrent.futures.Future[Any] = concurrent.futures.Future()
        self._pending_requests[request_id] = future

        try:
            # Write request file
            async with aiofiles.open(request_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(request_data, indent=2))

            logger.debug(f"Created request file: {request_file}")

            # Wait for response with timeout using asyncio.wrap_future
            try:
                wrapped_future = asyncio.wrap_future(future)
                result = await asyncio.wait_for(wrapped_future, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"Request {method} timed out after {timeout} seconds")

        except Exception as e:
            # Clean up on error
            self._pending_requests.pop(request_id, None)
            try:
                if request_file.exists():
                    request_file.unlink()
            except Exception:
                pass
            raise e

    def close(self) -> None:
        """Close the Unity RPC client and clean up resources."""
        self._stop_file_watcher()
        
        # Cancel any pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()


class ResponseFileHandler(FileSystemEventHandler):
    """File system event handler for Unity response files."""

    def __init__(self, callback, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super().__init__()
        self._callback = callback
        self._loop = loop
        self._processed_files: set[str] = set()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def on_created(self, event) -> None:
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.name.startswith("response_") and file_path.name.endswith(".json"):
            self._process_file_threadsafe(file_path)

    def on_modified(self, event) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.name.startswith("response_") and file_path.name.endswith(".json"):
            # Avoid processing the same file multiple times
            if str(file_path) not in self._processed_files:
                self._processed_files.add(str(file_path))
                self._process_file_threadsafe(file_path)

    def _process_file_threadsafe(self, file_path: Path) -> None:
        """Process a response file in a thread-safe manner."""
        def process_with_delay():
            # Small delay to ensure file is fully written
            import time
            time.sleep(0.1)
            
            if file_path.exists():
                self._callback(file_path)
        
        # Submit to thread pool to avoid blocking the file watcher
        self._executor.submit(process_with_delay)
