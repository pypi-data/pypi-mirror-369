import os
import re
import uuid
import json
import logging
import asyncio
from typing import Any, Optional, Callable
from urllib.parse import urlparse
import aiohttp
from functools import wraps
import mimetypes
from datetime import datetime


def validate_api_key(api_key: str) -> bool:
    """
    Validate the format of the API key.

    Args:
        api_key: The API key to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not api_key:
        return False
    # Add your API key format validation logic here
    return bool(re.match(r"^[a-zA-Z0-9]{32,}$", api_key))


def generate_session_id() -> str:
    """
    Generate a unique session ID.

    Returns:
        str: A unique session ID
    """
    return str(uuid.uuid4())


def format_error_message(error: Exception) -> str:
    """
    Format error messages for consistent output.

    Args:
        error: The exception to format

    Returns:
        str: Formatted error message
    """
    return f"{error.__class__.__name__}: {str(error)}"


def sanitize_input(input_data: Any) -> Any:
    """
    Sanitize input data to prevent injection attacks.

    Args:
        input_data: The data to sanitize

    Returns:
        Any: Sanitized data
    """
    if isinstance(input_data, str):
        # Remove potential dangerous characters
        return re.sub(r"[<>{}]", "", input_data)
    elif isinstance(input_data, dict):
        return {k: sanitize_input(v) for k, v in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_input(item) for item in input_data]
    return input_data


def load_environment_variables() -> dict:
    """
    Load environment variables for the SDK.

    Returns:
        dict: Dictionary of environment variables
    """
    return {
        "api_key": os.getenv("PROMPTSTUDIO_API_KEY"),
        "env": os.getenv("PROMPTSTUDIO_ENV", "prod"),
        "bypass": os.getenv("PROMPTSTUDIO_BYPASS", "false").lower() == "true",
    }


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger("promptstudio")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def convert_file_size(size_bytes: int) -> str:
    """
    Convert file size from bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Human readable file size
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f}TB"


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
) -> Any:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        backoff_factor: Factor to increase delay

    Returns:
        Any: Result of the function
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise

            delay = min(delay * backoff_factor, max_delay)
            await asyncio.sleep(delay)

    raise last_exception


async def validate_url(url: str) -> bool:
    """
    Validate if a URL is accessible.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid and accessible, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                return response.status == 200
    except:
        return False


async def is_valid_image_url(url: str) -> bool:
    """
    Check if URL points to a valid image.

    Args:
        url: URL to check

    Returns:
        bool: True if valid image URL, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                if response.status != 200:
                    return False
                content_type = response.headers.get("content-type", "")
                return content_type.startswith("image/")
    except:
        return False


async def is_valid_audio_url(url: str) -> bool:
    """
    Check if URL points to a valid audio file.

    Args:
        url: URL to check

    Returns:
        bool: True if valid audio URL, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                if response.status != 200:
                    return False
                content_type = response.headers.get("content-type", "")
                return content_type.startswith("audio/")
    except:
        return False


def log_api_call(func):
    """
    Decorator to log API calls.

    Args:
        func: Function to decorate

    Returns:
        Callable: Decorated function
    """
    logger = setup_logging()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            logger.info(
                f"API call to {func.__name__} completed successfully "
                f"in {(datetime.now() - start_time).total_seconds():.2f}s"
            )
            return result
        except Exception as e:
            logger.error(
                f"API call to {func.__name__} failed after "
                f"{(datetime.now() - start_time).total_seconds():.2f}s: {str(e)}"
            )
            raise

    return wrapper
