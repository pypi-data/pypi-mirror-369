"""Main entry point for Coplay MCP Server using FastMCP."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .process_discovery import discover_unity_project_roots
from mcp.server.fastmcp import Context, FastMCP
from mcp import ServerSession

from .unity_client import UnityRpcClient


def setup_logging() -> None:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # Log errors to stderr (visible to MCP client)
            logging.StreamHandler(sys.stderr),
            # Log all messages to file
            logging.FileHandler(log_dir / "coplay-mcp-server.log"),
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


setup_logging()


# Initialize FastMCP server
mcp = FastMCP(name="coplay-mcp-server")

# Global Unity client instance
unity_client = UnityRpcClient()

logger = logging.getLogger(__name__)


@mcp.tool()
async def set_unity_project_root(
    unity_project_root: str,
    ctx: Context[ServerSession, None]
) -> str:
    """Set the Unity project root path for the MCP server instance. This tool should be called before using any other Unity tools."""
    try:
        logger.info(f"Setting Unity project root to: {unity_project_root}")
        
        if not unity_project_root or not unity_project_root.strip():
            raise ValueError("Unity project root cannot be empty")

        # Set the Unity project root in the RPC client
        unity_client.set_unity_project_root(unity_project_root)
        
        result = f"Unity project root set to: {unity_project_root}"
        logger.info("Unity project root set successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to set Unity project root: {e}")
        raise


@mcp.tool()
async def list_unity_project_roots(ctx: Context[ServerSession, None]) -> Any:
    """List all project roots of currently open Unity instances. This tool discovers all running Unity Editor instances and returns their project root directories."""
    try:
        logger.info("Discovering Unity project roots...")
        
        project_roots = discover_unity_project_roots()
        return {
            "count": len(project_roots),
            "projectRoots": [
                {
                    "projectRoot": root,
                    "projectName": root.split("/")[-1] if "/" in root else root.split("\\")[-1]
                }
                for root in project_roots
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list Unity project roots: {e}")
        raise


@mcp.tool()
async def execute_script(
    file_path: str,
    method_name: str = "Execute",
    arguments: Optional[Dict[str, Any]] = None,
    ctx: Context[ServerSession, None] = None
) -> Any:
    """Execute arbitrary C# code inside of the Unity Editor. The supplied code file must contain a class with a public static method that can be specified via method_name parameter (defaults to 'Execute'). This static method can return an object which will be serialized to JSON."""
    try:
        logger.info(f"Executing script: {file_path}, method: {method_name}")
        
        params = {
            "filePath": file_path,
            "methodName": method_name
        }
        if arguments:
            params["arguments"] = arguments
            
        return await unity_client.execute_request("executeScript", params)
    except Exception as e:
        logger.error(f"Failed to execute script: {e}")
        raise


@mcp.tool()
async def get_unity_logs(
    skip: int,
    limit: int,
    show_logs: bool = True,
    show_warnings: bool = True,
    show_errors: bool = True,
    search_term: Optional[str] = None,
    ctx: Context[ServerSession, None] = None
) -> Any:
    """Gets logs sorted from newest to oldest, applying filtering and pagination."""
    try:
        logger.debug(f"Getting Unity logs: skip={skip}, limit={limit}")
        
        params = {
            "skip": skip,
            "limit": limit,
            "showLogs": show_logs,
            "showWarnings": show_warnings,
            "showErrors": show_errors
        }
        if search_term:
            params["searchTerm"] = search_term
            
        return await unity_client.execute_request("getUnityLogs", params)
    except Exception as e:
        logger.error(f"Failed to get Unity logs: {e}")
        raise


@mcp.tool()
async def get_unity_editor_state(ctx: Context[ServerSession, None]) -> Any:
    """Retrieve the current state of the Unity Editor, excluding scene hierarchy."""
    try:
        logger.info("Getting Unity Editor state...")
        
        result = await unity_client.execute_request("getUnityEditorState", {})
        return result
        
    except Exception as e:
        logger.error(f"Failed to get Unity Editor state: {e}")
        raise


@mcp.tool()
async def list_game_objects_in_hierarchy(
    reference_object_path: Optional[str] = None,
    name_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    component_filter: Optional[str] = None,
    include_inactive: Optional[bool] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    only_paths: Optional[bool] = None,
    ctx: Context[ServerSession, None] = None
) -> Any:
    """List game objects in the hierarchy with optional filtering capabilities. Uses breadth-first traversal to prioritize objects closer to the root. Results are truncated if they exceed the limit, with a message indicating the truncation."""
    try:
        logger.debug("Listing game objects in hierarchy...")
        
        params = {}
        if reference_object_path is not None:
            params["referenceObjectPath"] = reference_object_path
        if name_filter is not None:
            params["nameFilter"] = name_filter
        if tag_filter is not None:
            params["tagFilter"] = tag_filter
        if component_filter is not None:
            params["componentFilter"] = component_filter
        if include_inactive is not None:
            params["includeInactive"] = include_inactive
        if limit is not None:
            params["limit"] = limit
        if skip is not None:
            params["skip"] = skip
        if only_paths is not None:
            params["onlyPaths"] = only_paths
            
        return await unity_client.execute_request("listGameObjectsInHierarchy", params)
    except Exception as e:
        logger.error(f"Failed to list game objects: {e}")
        raise


@mcp.tool()
async def create_coplay_task(
    prompt: str,
    file_paths: Optional[str] = None,
    model: Optional[str] = None,
    ctx: Context[ServerSession, None] = None
) -> Any:
    """Creates a new task in the Unity Editor with the specified prompt and optional file attachments. This will start a new chat thread and submit the prompt for processing."""
    try:
        logger.info(f"Creating task with prompt: {prompt[:100]}...")
        
        params = {"prompt": prompt}
        if file_paths:
            params["file_paths"] = file_paths
        if model:
            params["model"] = model
            
        result = await unity_client.execute_request("createTask", params)
        return result
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise


def main():
    mcp.run()


if __name__ == "__main__":
    main()
