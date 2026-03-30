import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def async_retry(
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    backoff: float = 1.0,
):
    """
    Декоратор retry для асинхронных функций.

    :param attempts: Количество попыток
    :param delay: Начальная задержка (сек)
    :param exceptions: Исключения для retry
    :param backoff: Множитель увеличения задержки
    """
    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("async_retry можно использовать только с async функциями")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    if attempt == attempts:
                        raise

                    logger.error(
                        f"[async_retry] Ошибка: {e}. "
                        f"Попытка {attempt}/{attempts}. "
                        f"Повтор через {current_delay} сек..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator