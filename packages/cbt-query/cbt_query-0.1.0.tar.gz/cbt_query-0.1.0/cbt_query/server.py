import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import httpx
from mcp.server.fastmcp import FastMCP

# setup logging
logger = logging.getLogger(__name__)

# get base URL from environment variable
CBT_SERVER_URL = os.environ.get("CBT_SERVER_URL")
if not CBT_SERVER_URL:
    raise EnvironmentError("CBT_SERVER_URL environment variable not set")

DEFAULT_BASE_URL = CBT_SERVER_URL
DEFAULT_TIMEOUT = 30

# initialize FastMCP server
mcp = FastMCP("cbt_query")


async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    simple function to fetch JSON data from a URL.
    
    Args:
        url: the URL to fetch from
        params: optional request parameters
        
    Returns:
        parsed JSON data
    """
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"fetch failed for {url}: {e}")
        raise


def format_list_param(param: Union[str, List[str]]) -> str:
    """format parameter for API request - join list with semicolon"""
    if isinstance(param, list):
        return ";".join(param)
    return param


def extract_base_url(full_url: str, endpoint: str) -> str:
    """extract base URL by removing endpoint"""
    return full_url.replace(endpoint, "")


@mcp.tool()
async def query_all_cases(url: str = f"{DEFAULT_BASE_URL}/query_all_cases") -> List[Any]:
    """Get all cases from the query server."""
    data = await fetch_json(url)
    return data.get("result", data)


@mcp.tool()
async def query_all_files(url: str = f"{DEFAULT_BASE_URL}/query_all_files") -> List[Any]:
    """Get all files from the query server."""
    data = await fetch_json(url)
    return data.get("result", data)


@mcp.tool()
async def query_by_case(case_name: str, url: str = f"{DEFAULT_BASE_URL}/query_by_case") -> Dict[str, Any]:
    """Get coverage mapping result by case name."""
    if not case_name:
        raise ValueError("case_name cannot be empty")
    
    params = {"case": case_name}
    return await fetch_json(url, params)


@mcp.tool()
async def query(
    file_name: Optional[Union[str, List[str]]] = None, 
    funcs: Optional[Union[str, List[str]]] = None, 
    url: str = f"{DEFAULT_BASE_URL}/query"
) -> Any:
    """Query cases by files and/or functions.
    
    Usage examples:
    - query(file_name="file1.cpp")
    - query(funcs="function1")
    - query(file_name=["file1.cpp", "file2.cpp"], funcs=["func1", "func2"])
    """
    if not file_name and not funcs:
        raise ValueError("At least one of file_name or funcs must be provided")
    
    params = {}
    if file_name:
        params["files"] = format_list_param(file_name)
    if funcs:
        params["funcs"] = format_list_param(funcs)
    
    data = await fetch_json(url, params)
    return data.get("result", data)
