from __future__ import annotations

import requests
import ua_generator
from agents import function_tool
from loguru import logger
from requests.exceptions import HTTPError

from .firecrawl import firecrawl_scrape


def markitdown_scrape(url: str) -> str:
    """Scrape the content from the given URL. This is faster than the firecrawl_scrape_tool.

    Args:
        url (str): The URL to scrape.
    """
    try:
        from markitdown import MarkItDown
    except ImportError as e:
        raise ImportError(
            "MarkItDown is not installed. Please install it with `pip install agetnize[markitdown]`."
        ) from e
    user_agent = ua_generator.generate(
        device="desktop",
        platform=("windows", "macos"),
        browser=("chrome", "edge", "firefox", "safari"),
    )
    requests_session = requests.Session()
    requests_session.headers.update(user_agent.headers.get())
    md = MarkItDown(enable_plugins=False, requests_session=requests_session)
    try:
        result = md.convert_url(url)
        result_md = result.markdown
    except HTTPError:
        logger.info(f"Fallback: failed to scrape {url} with MarkItDown, using firecrawl_scrape")
        result_md = firecrawl_scrape(url)

    return result_md


markitdown_scrape_tool = function_tool(markitdown_scrape)
