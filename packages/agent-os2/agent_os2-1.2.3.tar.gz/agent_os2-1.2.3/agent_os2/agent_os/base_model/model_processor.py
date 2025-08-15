from typing import Any,AsyncGenerator
from .utility import ModelConfig
from abc import ABC,abstractmethod
from enum import Enum

class ProcessorError(Exception):
    """处理器专用异常，包含状态码信息"""
    def __init__(self, message: str, code: int = 500, detail: str = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or message
class StreamDataStatus(Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"
class DataPackage:
    def __init__(self,status:StreamDataStatus,data:Any,usage:dict[str,Any]|None=None):
        self._status = status
        if self._status == StreamDataStatus.GENERATING:
            self._data = {"data":data}
        elif self._status == StreamDataStatus.COMPLETED:
            self._data = {"full_data":data,"usage":usage}
        elif self._status == StreamDataStatus.ERROR:
            self._data = data

    def to_dict(self)->dict[str,Any]:
        return {
            "status":self._status.value,
            "data":self._data
        }
    def read_data(self) -> Any:
        if self._status == StreamDataStatus.GENERATING:
            return self._data.get("data")
        elif self._status == StreamDataStatus.COMPLETED:
            return self._data.get("full_data")
        return self._data
    def get_status(self)->StreamDataStatus:
        return self._status
    def get_usage(self)->dict[str,Any]:
        return self._data.get("usage") or {}
class BaseProcessor(ABC):
    async def interact(
        self,
        messages: Any,
        llm_config: ModelConfig,
        proxy: str,
        api_key: str,
        base_url: str
    ) -> AsyncGenerator[DataPackage, None]:
        processed_chunks: list[Any] = []
        last_raw_item: Any = None
        try:
            async for raw_item in self.async_generator(messages, llm_config, proxy, api_key, base_url):
                last_raw_item = raw_item
                chunk = self.process_chunk(raw_item)
                if chunk is None:
                    continue
                processed_chunks.append(chunk)
                if llm_config.is_stream():
                    yield DataPackage(StreamDataStatus.GENERATING, data=chunk)
        except Exception as error:  # 统一错误处理
            error_payload = self.process_error(error, llm_config)
            yield DataPackage(StreamDataStatus.ERROR, data=error_payload)
            return

        final_output = self.process_complete(processed_chunks)
        usage = self.get_usage(last_raw_item or {}, messages, final_output, llm_config)
        yield DataPackage(StreamDataStatus.COMPLETED, data=final_output, usage=usage)

    @abstractmethod
    async def async_generator(
        self,
        messages: Any,
        llm_config: ModelConfig,
        proxy: str,
        api_key: str,
        base_url: str
    ) -> AsyncGenerator[Any, None]:
        ...

    @abstractmethod
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, llm_config: ModelConfig) -> dict[str,Any]:
        ...

    @abstractmethod
    def process_chunk(self, raw_chunk: Any) -> Any:
        ...

    @abstractmethod
    def process_complete(self, processed_chunks: list[Any]) -> Any:
        ...

    def process_error(self, error: Exception, llm_config: ModelConfig) -> dict[str, Any]:
        if isinstance(error, ProcessorError):
            return {"code": error.code, "message": str(error), "detail": error.detail}
        # 所有其他异常都应该被处理器封装为ProcessorError，这里是兜底处理
        return {"code": 500, "message": str(error), "detail": f"{self.__class__.__name__} 未处理的异常"}