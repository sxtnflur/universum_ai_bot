import io
from pathlib import Path
import re
from urllib.parse import urljoin

from .base import BaseStorage, get_file_path, prepare_file_path
import abc
from io import BytesIO
from typing import Callable, Optional

import aioboto3
from types_aiobotocore_s3.client import S3Client
from botocore.exceptions import ClientError
import asyncio

from types_aiobotocore_s3.type_defs import FileobjTypeDef
import logging


logger = logging.getLogger(__name__)


def file_path_to_key(file_path: Path) -> str:
    file_path = file_path.__str__().replace('\\', '/')
    file_path = re.sub(r'^/+', '/', file_path)
    if file_path.startswith('/'):
        file_path = file_path[1:]
    print(f'{file_path=}')
    return file_path


class S3ConnectionPool:
    """Единый менеджер подключений к S3"""

    def __init__(self):
        self._session: Optional[aioboto3.Session] = None
        self._client: Optional[S3Client] = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self,
                         endpoint_url: str,
                         aws_access_key_id: str,
                         aws_secret_access_key: str,
                         region_name: str,
                         bucket: str,
                         service_name: str = 's3',
                         max_pool_connections: int = 50):  # Увеличиваем пул соединений
        """Инициализация при старте приложения"""
        async with self._lock:
            if self._initialized:
                return

            self._session = aioboto3.Session()

            # Создаем клиент с настройками пула
            self._client = self._session.client(
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
                service_name=service_name,
                # config=aioboto3.session.Config(
                #     max_pool_connections=max_pool_connections,  # Размер пула
                #     retries={'max_attempts': 3},  # Встроенные ретраи
                #     connect_timeout=5,
                #     read_timeout=30,
                # )
            )

            # Активируем клиент
            self._client = await self._client.__aenter__()
            self._initialized = True

            # Прогреваем соединения
            await self._warm_up_connections(bucket)

            logger.info(f"✅ S3 клиент инициализирован. Пул соединений: {max_pool_connections}")

    async def _warm_up_connections(self, bucket: str):
        """Прогрев пула соединений"""
        try:
            # Делаем несколько простых запросов для создания соединений
            tasks = []
            for _ in range(5):  # Создаем несколько соединений в пуле
                tasks.append(self._client.head_bucket(Bucket=bucket))
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("🔥 Пул соединений S3 прогрет")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при прогреве пула S3: {e}")

    async def close(self):
        """Закрытие при остановке приложения"""
        async with self._lock:
            if self._client:
                await self._client.__aexit__(None, None, None)
                self._client = None
                self._session = None
                self._initialized = False
                logger.info("✅ S3 клиент закрыт")

    @property
    def client(self) -> S3Client:
        if not self._initialized or not self._client:
            raise RuntimeError("S3 клиент не инициализирован")
        return self._client


class S3Service:
    """Сервис для работы с S3 используя единый пул соединений"""

    def __init__(self, pool: S3ConnectionPool, bucket: str):
        self._pool = pool
        self._bucket = bucket
        self._max_retries = 3
        self._semaphore = asyncio.Semaphore(100)  # Ограничиваем параллельные запросы

    async def _execute_with_retry(self, operation: str, func: Callable, *args, **kwargs):
        """Выполнение операции с повторными попытками"""
        async with self._semaphore:  # Контроль параллелизма
            for attempt in range(self._max_retries):
                try:
                    return await func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')

                    # Логируем ошибку
                    logger.warning(f"S3 {operation} ошибка (попытка {attempt + 1}/{self._max_retries}): {error_code}")

                    # Ретраи только для определенных ошибок
                    retryable_errors = ['RequestTimeout', 'ServiceUnavailable', 'SlowDown',
                                        'InternalError', 'OperationAborted']

                    if error_code in retryable_errors and attempt < self._max_retries - 1:
                        # Экспоненциальная задержка
                        delay = (2 ** attempt) * 0.1
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Неустранимая ошибка
                        logger.error(f"Неустранимая S3 ошибка в {operation}: {error_code}")
                        raise
                except Exception as e:
                    logger.error(f"Неожиданная ошибка S3 в {operation}: {type(e).__name__}")
                    raise

    async def put_object(self, key: str, body: bytes | str, **kwargs):
        """Загрузка объекта"""
        return await self._execute_with_retry(
            'put_object',
            self._pool.client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=body,
            **kwargs
        )

    async def get_object(self, key: str, **kwargs) -> dict:
        """Получение объекта"""
        return await self._execute_with_retry(
            'get_object',
            self._pool.client.get_object,
            Bucket=self._bucket,
            Key=key,
            **kwargs
        )

    async def delete_object(self, key: str, **kwargs):
        """Удаление объекта"""
        return await self._execute_with_retry(
            'delete_object',
            self._pool.client.delete_object,
            Bucket=self._bucket,
            Key=key,
            **kwargs
        )

    async def upload_fileobj(self, key: str, fileobj, **kwargs):
        """Загрузка файлового объекта"""
        return await self._execute_with_retry(
            'upload_fileobj',
            self._pool.client.upload_fileobj,
            Fileobj=fileobj,
            Bucket=self._bucket,
            Key=key,
            **kwargs
        )

    async def head_object(self, key: str, **kwargs):
        """Проверка существования объекта"""
        try:
            return await self._execute_with_retry(
                'head_object',
                self._pool.client.head_object,
                Bucket=self._bucket,
                Key=key,
                **kwargs
            )
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise


class TextManagerS3:
    def __init__(self, s3_service: S3Service):
        self.s3 = s3_service

    async def set(self, key: str, text: str) -> str:
        await self.s3.put_object(key, text.encode('utf-8'))
        return key

    async def get(self, key: str) -> str:
        response = await self.s3.get_object(key)
        data = await response['Body'].read()
        return data.decode('utf-8')

    async def delete(self, key: str) -> None:
        await self.s3.delete_object(key)


class FilesManagerS3:
    def __init__(self, s3_service: S3Service, base_url: str):
        self.s3 = s3_service
        self.base_url = base_url

    async def set(self, fileobj, key: str) -> str:
        await self.s3.upload_fileobj(key, fileobj)
        return key

    async def get(self, key: str) -> bytes:
        response = await self.s3.get_object(key)
        return await response['Body'].read()

    def create_url(self, key: str) -> str:
        return urljoin(self.base_url.rstrip('/') + '/', key.lstrip('/'))
