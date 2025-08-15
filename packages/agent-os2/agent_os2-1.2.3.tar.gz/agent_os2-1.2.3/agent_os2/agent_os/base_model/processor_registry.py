from calendar import c
from typing import Type,Any,AsyncGenerator
from .model_processor import BaseProcessor, DataPackage, StreamDataStatus, ProcessorError
import aiohttp
import json
import os
import asyncio
import time
import uuid
import io
import base64
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from PIL import Image
from .utility import get_model_cost,get_fallback_tokens,ModelConfig
# 模型注册表
TYPE_MAPPINGS: dict[str, Type[BaseProcessor]] = {}

def register(*processor_types: str):
    def decorator(cls: Type[BaseProcessor]):
        for processor_type in processor_types:
            if processor_type in TYPE_MAPPINGS:
                raise ValueError(f"模型类型 '{processor_type}' 已注册")
            TYPE_MAPPINGS[processor_type] = cls
        return cls
    return decorator
def process_messages_to_openai_style(messages:list[dict[str,str]]|str|dict[str,str])->list[dict[str, str]]:
    processed_messages = []
    if isinstance(messages, str):
        processed_messages.append({"role":"user","content":messages})
    elif isinstance(messages,dict):
        if "system" in messages:
            processed_messages.append({"role":"system","content":messages["system"]})
        if "user" in messages:
            processed_messages.append({"role":"user","content":messages["user"]})
        if "assistant" in messages:
            processed_messages.append({"role":"assistant","content":messages["assistant"]})
    elif isinstance(messages,list):
        for message in messages:
            if isinstance(message,dict):
                if "system" in message:
                    processed_messages.append({"role":"system","content":message["system"]})
                elif "user" in message:
                    processed_messages.append({"role":"user","content":message["user"]})
                elif "assistant" in message:
                    processed_messages.append({"role":"assistant","content":message["assistant"]})
            else:
                raise ValueError(f"messages中的元素必须是dict，当前message: {message}")
    return processed_messages
def process_messages_to_genai_format(messages:list[dict[str,str]]|str|dict[str,str])->tuple[str,list[genai_types.Content]]:
        processed_messages = process_messages_to_openai_style(messages)
        system_instruction = ""
        contents = []
        for message in processed_messages:
            if message['role'] == 'system':
                system_instruction += message['content']
            elif message['role'] == 'user':
                contents.append(genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=message['content'])]
                ))
            elif message['role'] == 'assistant':
                contents.append(genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text=message['content'])]
                ))
        return system_instruction,contents
@register("google-chat")
class GoogleChatProcessor(BaseProcessor):
    """
    真异步的 Google Gemini 处理器
    使用新版 google-genai SDK 的异步实现
    """
    async def async_generator(self, messages: Any, model_config: "ModelConfig", proxy: str, api_key: str, base_url: str):
        """真异步实现：使用新版 google-genai SDK"""
        
        try:
            # 创建异步客户端，使用aiohttp后端
            http_options = genai_types.HttpOptions(
                async_client_args={'trust_env': True}
            )
            if proxy:
                http_options.async_client_args['proxy'] = proxy
                
            client = genai.Client(
                api_key=api_key, 
                http_options=http_options
            )
            
            system_instruction, contents = process_messages_to_genai_format(messages)
            config = model_config.get_interact_config()
            
            # 处理thinking相关配置
            if thinking_budget := config.pop("thinking_budget", None):
                config["thinking_config"] = genai_types.ThinkingConfig(
                    include_thoughts=config.pop("include_thoughts", None),
                    thinking_budget=-1 if thinking_budget else 0  # -1开启思考，0关闭思考
                )
                        # 如果有system_instruction，添加到请求参数中
            if system_instruction:
                config["system_instruction"] = system_instruction
            # 构建请求参数
            request_params = {
                "model": model_config.get_model_name(),
                "contents": contents,
                "config": genai_types.GenerateContentConfig(**config)
            }
            
            # 使用异步流式API，BaseProcessor会根据is_stream()决定输出模式
            async for chunk in await client.aio.models.generate_content_stream(**request_params):
                yield chunk
                    
        except Exception as e:
            raise ProcessorError(f"Google GenAI 异步调用失败: {str(e)}", 500)

    def get_usage(self, last_chunk_data: genai_types.GenerateContentResponse, messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        
        # 处理新版SDK的usage
        if hasattr(last_chunk_data, 'usage_metadata') and last_chunk_data.usage_metadata:
            prompt_tokens = last_chunk_data.usage_metadata.prompt_token_count or 0
            candidates_tokens = last_chunk_data.usage_metadata.candidates_token_count or 0
            thoughts_tokens = last_chunk_data.usage_metadata.thoughts_token_count or 0
            completion_tokens = candidates_tokens + thoughts_tokens
            total_tokens = last_chunk_data.usage_metadata.total_token_count or 0
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": get_model_cost(model_name, prompt_tokens, completion_tokens)
            }
        else:
            # 回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name, initial_tokens=3)
            completion_tokens = get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3)
            total_tokens = prompt_tokens + completion_tokens
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": get_model_cost(model_name, prompt_tokens, completion_tokens)
            }

    def process_chunk(self, raw_chunk: genai_types.GenerateContentResponse) -> str | tuple[str,str]:
        """处理新版SDK的响应块"""
        thoughts = ""
        answer = ""
        
        if hasattr(raw_chunk, 'candidates') and raw_chunk.candidates:
            if hasattr(raw_chunk.candidates[0], 'content') and hasattr(raw_chunk.candidates[0].content, 'parts'):
                for part in raw_chunk.candidates[0].content.parts:
                    if not hasattr(part, 'text') or not part.text:
                        continue
                    elif hasattr(part, 'thought') and part.thought:
                        thoughts += part.text
                    else:
                        answer += part.text
        return (thoughts, answer) if thoughts else answer

    def process_complete(self, accumulated_contents: list[str | tuple[str,str]]) -> str:
        accumulated_thoughts = ""
        accumulated_answer = ""
        for result in accumulated_contents:
            if isinstance(result, tuple):
                thoughts, answer = result
                if thoughts:
                    accumulated_thoughts += thoughts
                if answer:
                    accumulated_answer += answer
            elif isinstance(result, str):
                accumulated_answer += result
        return "[思考总结]\n" + accumulated_thoughts + "\n[回答]\n" + accumulated_answer if accumulated_thoughts else accumulated_answer
@register("openai-chat")
class OpenAIChatProcessor(BaseProcessor):
    def transform_model_name(self, model_config: "ModelConfig") -> str:
        """
        转换模型名称，子类可以重写此方法来实现模型名称映射
        默认实现直接返回原始模型名称
        """
        return model_config.get_model_name()
    
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        
        # 优先使用API返回的usage，如果没有则使用fallback计算
        if last_chunk_data.get("usage"):
            usage = last_chunk_data["usage"]
            prompt_tokens = usage.get("prompt_tokens", get_fallback_tokens(str(messages), model=model_name, initial_tokens=3))
            completion_tokens = usage.get("completion_tokens", get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3))
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        else:
            # 完全回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name, initial_tokens=3)
            completion_tokens = get_fallback_tokens(str(final_output), model=model_name, initial_tokens=3)
            total_tokens = prompt_tokens + completion_tokens
            
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": get_model_cost(model_name,prompt_tokens,completion_tokens)
        }
    async def async_generator(self, messages: str|list[dict[str,str]]|dict[str,str], model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        messages = process_messages_to_openai_style(messages)
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url = (base_url[:-1] if base_url.endswith("/") else base_url) + ("" if base_url.endswith("/chat/completions") else "/chat/completions")
        payload = {"model": self.transform_model_name(model_config), "messages": messages, **model_config.get_interact_config(), "stream": True}
        last_chunk_data: dict[str, Any] = {}

        try:
            session_kwargs = {}
            if proxy:
                session_kwargs["proxy"] = proxy

            if not base_url:
                raise ProcessorError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。", 400)

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, headers=headers, json=payload, **session_kwargs) as response:
                        if response.status != 200:
                            error = await response.text()
                            raise ProcessorError(f"请求失败: {error}", response.status)

                        # 简化的 SSE 解析：逐行处理，遇到 data: 就尝试解析 JSON
                        buffer = ""
                        async for chunk in response.content.iter_chunked(4096):
                            try:
                                buffer += chunk.decode("utf-8")
                            except:
                                continue
                            
                            # 按行处理
                            while "\n" in buffer:
                                line, buffer = buffer.split("\n", 1)
                                line = line.strip()
                                
                                if line.startswith("data: "):
                                    data = line[6:].strip()  # 移除 "data: "
                                    if data == "[DONE]":
                                        return
                                    if data:
                                        try:
                                            chunk_data = json.loads(data)
                                            last_chunk_data = chunk_data
                                            yield chunk_data
                                        except:
                                            # JSON 解析失败就跳过，不要过度处理
                                            pass

                except aiohttp.ClientError as net_exc:
                    raise ProcessorError(f"网络异常: {net_exc}", 503)

        except Exception as e:
            if isinstance(e, ProcessorError):
                raise e
            raise ProcessorError(f"OpenAI 请求失败: {str(e)}", 500)



    def process_chunk(self, raw_chunk: dict[str, Any]) -> Any:
        delta = raw_chunk.get('choices', [{}])[0].get('delta', {}) if isinstance(raw_chunk, dict) else {}
        return delta.get('content') or None

    def process_complete(self, accumulated_contents: list[Any]) -> Any:
        return "".join([c for c in accumulated_contents if isinstance(c, str)])

# 图片模型保留自定义实现
@register("openai-image-generate")
class OpenAIImageProcessor(BaseProcessor):
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        model_name = model_config.get_model_name()
        
        # 优先使用API返回的usage，如果没有则使用fallback计算
        if last_chunk_data.get("usage"):
            usage = last_chunk_data["usage"]
            prompt_tokens = usage.get("prompt_tokens", get_fallback_tokens(str(messages), model=model_name))
            completion_tokens = usage.get("completion_tokens", get_fallback_tokens(str(final_output), model=model_name, initial_tokens=200))
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        else:
            # 完全回退计算
            prompt_tokens = get_fallback_tokens(str(messages), model=model_name)
            completion_tokens = get_fallback_tokens(str(final_output), model=model_name, initial_tokens=200)  # 图片生成预估更高
            total_tokens = prompt_tokens + completion_tokens
            
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": get_model_cost(model_name,prompt_tokens,completion_tokens)
        }
    async def async_generator(self, messages:str, model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        try:
            if not base_url:
                raise ProcessorError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。", 400)
            
            session_kwargs = {"proxy": proxy} if proxy else {}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/images/generations",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    # 保持响应格式固定为 b64_json，n 可由配置覆盖（默认 1）
                    json={
                        "model": model_config.get_model_name(),
                        "prompt": messages,
                        **model_config.get_interact_config(),
                        "response_format": "b64_json",
                    },
                    **session_kwargs
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise ProcessorError(f"图片生成失败: {error}", response.status)
                    yield await response.json()
        except Exception as e:
            if isinstance(e, ProcessorError):
                raise e
            raise ProcessorError(f"图片生成失败: {str(e)}", 500)
    


    def process_chunk(self, raw_chunk: dict[str, Any]) -> Any:
        return None  # 不使用chunk模式

    def process_complete(self, accumulated_contents: list[Any]) -> Any:
        # 图片生成不使用累积内容，直接从最后的原始数据处理
        if not accumulated_contents:
            return []
        response_data = accumulated_contents[-1] if accumulated_contents else {}
        folder = os.path.join(os.getcwd(), "memory","pic_lib"); os.makedirs(folder, exist_ok=True)
        return [self.save_image_from_base64(item["b64_json"], folder) for item in response_data.get("data", []) if item.get("b64_json")]

    @staticmethod
    def save_image_from_base64(b64_data, memory_folder, mime_type="image/png"):
        image_id = f"gpt_image_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        extension = "png"
        if "jpeg" in mime_type or "jpg" in mime_type:
            extension = "jpg"
        filename = f"{image_id}.{extension}"
        save_path = os.path.join(memory_folder, filename)
        image_bytes = base64.b64decode(b64_data)
        image = Image.open(io.BytesIO(image_bytes))
        image.save(save_path)
        return {
            "b64_json": b64_data,
            "image_id": image_id,
            "path": save_path,
            "relative_path": os.path.relpath(save_path,os.getcwd()),
            "mime_type": mime_type,
            "created_at": datetime.now().isoformat()
        }
@register("lite-llm-chat")
class LiteLLMChatProcessor(OpenAIChatProcessor):
    def transform_model_name(self, model_config: "ModelConfig") -> str:
        """
        LiteLLM模型名称转换，将原始模型名称转换为带提供商前缀的格式
        """
        name = model_config.get_model_name()
        
        if "gpt" in name or "o1" in name or "o3" in name or "o4" in name or "omni" in name or "dall-e" in name or "text-moderation" in name or "text_embedding" in name:
            return f"openai/{name}"
        elif "gemini" in name or "google" in name:
            return f"gemini/{name}"
        elif "grok" in name:
            return f"xai/{name}"
        elif "claude" in name:
            return f"anthropic/{name}"
        elif "deepseek" in name:
            return f"deepseek/{name}"
        else:
            return f"groq/{name}"
    
    async def async_generator(self, messages: Any, model_config: "ModelConfig", proxy: str, api_key: str, base_url: str):
        # 对于gemini模型，需要特殊处理max_output_tokens参数
        name = model_config.get_model_name()
        config = model_config.get_interact_config()
        if 'reasoning_effort' in config:
            config['allowed_openai_params'] = ['reasoning_effort']
        if "gemini" in name or "google" in name:
            # 创建一个临时的配置副本来处理gemini特殊参数
            config.pop("include_thoughts",None)
            thinking_budget = config.pop("thinking_budget",None)
            config["reasoning_effort"] = "high" if thinking_budget == True else None
            config["allowed_openai_params"] = ['reasoning_effort']
            if tokens := config.pop("max_output_tokens", None):
                config["max_tokens"] = tokens
        async for chunk in super().async_generator(messages, ModelConfig(name,is_stream=model_config.is_stream(),**config), proxy, api_key, base_url):
            yield chunk
@register("flux-image-generate")
class FluxProcessor(BaseProcessor):
    def get_usage(self, last_chunk_data: dict[str,Any], messages: Any, final_output: Any, model_config: "ModelConfig") -> dict[str,Any]:
        # Flux模型固定成本，不需要token计算
        return {
            "cost": 0.02
        }
    async def async_generator(self, messages:str, model_config: "ModelConfig",proxy:str,api_key:str,base_url:str):
        try:
            headers = {'accept': 'application/json','x-key': api_key,'Content-Type': 'application/json'}
            async with aiohttp.ClientSession() as session:
                # 透传交互配置：steps/guidance/aspect_ratio/seed
                payload = {
                    'prompt': messages,
                    **model_config.get_interact_config()
                }

                # 与既有后端保持兼容的固定路由
                async with session.post(f"{base_url}/{model_config.get_model_name()}", headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ProcessorError(f"Flux 图片生成失败: {error_text}", response.status)
                    
                    response_data = await response.json()
                    if not response_data or not response_data.get("polling_url"):
                        raise ProcessorError("未能获取有效的响应数据", 502)
                    
                    # 轮询获取图片
                    while True:
                        await asyncio.sleep(0.5)
                        async with session.get(response_data["polling_url"], headers=headers, params={'id': response_data["id"]}) as polling_response:
                            if polling_response.status != 200:
                                error_text = await polling_response.text()
                                raise ProcessorError(f"轮询请求失败: {error_text}", polling_response.status)
                            
                            polling_data = await polling_response.json()
                            if polling_data["status"] == "Ready":
                                image_url = polling_data['result']['sample']
                                break
                            elif polling_data["status"] in ["Error", "Failed"]:
                                raise ProcessorError("轮询失败", 502)
                    
                    # 下载图片
                    async with session.get(image_url) as image_response:
                        if image_response.status != 200:
                            error_text = await image_response.text()
                            raise ProcessorError(f"图片下载失败: {error_text}", image_response.status)
                        yield {"image_bytes": await image_response.read(), "url": image_url}
        except Exception as e:
            if isinstance(e, ProcessorError):
                raise e
            raise ProcessorError(f"Flux 图片生成失败: {str(e)}", 500)

    @staticmethod
    def save_image_from_bytes(image_bytes: bytes, memory_folder: str, mime_type="image/png"):
        image_id = f"flux_image_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        extension = "png"
        filename = f"{image_id}.{extension}"
        save_path = os.path.join(memory_folder, filename)
        relative_path = os.path.relpath(save_path,os.getcwd())
        image = Image.open(io.BytesIO(image_bytes))
        image.save(save_path)

        return {
            "image_id": image_id,
            "path": save_path,
            "relative_path": relative_path,
            "mime_type": mime_type,
            "created_at": datetime.now().isoformat(),
        }

    def process_chunk(self, raw_chunk: dict[str, Any]) -> Any:
        return None  # 不使用chunk模式

    def process_complete(self, accumulated_contents: list[Any]) -> Any:
        # Flux不使用累积内容，直接从最后的原始数据处理
        if not accumulated_contents:
            return {}
        final_data = accumulated_contents[-1] if accumulated_contents else {}
        if not final_data.get("image_bytes"):
            return {}
        folder = os.path.join(os.getcwd(), "memory","pic_lib"); os.makedirs(folder, exist_ok=True)
        result = self.save_image_from_bytes(final_data["image_bytes"], folder)
        if final_data.get("url"):
            result["url"] = final_data["url"]
        return result