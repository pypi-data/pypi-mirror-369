import asyncio
import time
from functools import wraps
from typing import Any, Optional

from httpx import HTTPStatusError
from loguru import logger


def retry_http(max_attempts: int, delay_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts}/{max_attempts} failed: {e}")
                    time.sleep(delay_seconds)
            raise Exception(f"Failed after {max_attempts} attempts")

        return wrapper

    return decorator


def async_retry_http(
    max_attempts: int, delay_seconds: int, default_value: Optional[Any] = None
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            exceptions = []

            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except HTTPStatusError as e:
                    logger.warning(e.response.text)
                except Exception as e:
                    exceptions.append(e)
                    logger.warning(e)

                attempts += 1
                logger.warning(f"Attempt {attempts}/{max_attempts} failed")
                total_delay = delay_seconds * attempts
                logger.warning(f"Retrying in {total_delay} seconds...")
                await asyncio.sleep(total_delay)
            if default_value is None:
                raise ExceptionGroup(
                    f"Failed after {max_attempts} attempts", exceptions
                )
            logger.error(f"Failed after {max_attempts} attempts")
            return default_value

        return wrapper

    return decorator


def record_time(log: bool = False):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def wrap_func(*args, **kwargs):
                t1 = time.time()
                result = await func(*args, **kwargs)
                t2 = time.time()
                if log:
                    logger.info(
                        f"Function {func.__name__!r} executed in {(t2 - t1):.2f}s"
                    )
                return result

            return wrap_func

        else:

            @wraps(func)
            def wrap_func(*args, **kwargs):
                t1 = time.time()
                result = func(*args, **kwargs)
                t2 = time.time()
                if log:
                    logger.info(
                        f"Function {func.__name__!r} executed in {(t2 - t1):.2f}s"
                    )

                return result

            return wrap_func

    return decorator
