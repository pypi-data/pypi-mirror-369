from typing import Any
# 获取保守tokens统计
def get_fallback_tokens(*messages, model="gpt-4o", initial_tokens=0)->int:
    """
    根据messages获取保守的tokens统计，借助tiktoken进行基本统计
    针对字符串消息进行简化处理
    
    args:
        *messages: 字符串消息列表
        model: 用于编码的模型名称，默认为gpt-4o
        initial_tokens: 初始token开销，用于不同类型处理器的格式开销，默认为0
    returns:
        总token数的保守估计
    """
    import tiktoken
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # 如果模型不支持，回退到gpt-4o的编码器
        encoding = tiktoken.encoding_for_model("gpt-4o")
    
    num_tokens = initial_tokens  # 添加初始开销，替代硬编码的3
    for message in messages:
        if message:  # 只处理非空消息
            num_tokens += len(encoding.encode(str(message)))
    
    return num_tokens
    

# 获取模型成本
def get_model_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    根据配置文件获取模型成本，文件中是每1000token的美元计价。
    匹配策略：先精确匹配；若无则使用“键包含于 model_name”的子串匹配（取最长匹配键）。
    """
    import json
    import os
    with open(os.path.join(os.path.dirname(__file__), "models_price.json"), "r") as f:
        model_cost: dict[str, dict[str, float]] = json.load(f)

    # 精确匹配
    entry = model_cost.get(model_name)

    # 子串匹配（最长匹配优先），大小写不敏感
    if not entry:
        lower_name = (model_name or "").lower()
        best_key = None
        best_len = 0
        for key in model_cost.keys():
            k = key.lower()
            if k in lower_name and len(k) > best_len:
                best_key = key
                best_len = len(k)
        entry = model_cost.get(best_key, {})

    return entry.get("input_price", 0) * prompt_tokens / 1000 + entry.get("output_price", 0) * completion_tokens / 1000

# ModelConfig
# 模型配置
class ModelConfig:
    """
    用于基座模型在调用时，向模型发送的配置信息，包括模型名称、流式模式、交互配置等。
    
    参数说明：
    - model_name: 模型名称
    - is_stream: 是否流式模式
    - **kwargs: 其他配置信息
    支持从字典中获取模型配置，并自动根据模型名称获取模型类型，如果模型名称不存在，则抛出异常，可用类方法get_model_config从字典中获取模型配置
    """
    # 自动注册表
    registry: dict[str, type] = {}
    
    def __init_subclass__(cls, **kwargs):
        """子类定义时自动注册"""
        super().__init_subclass__(**kwargs)   
        # 只注册非基类
        if cls.__name__ != 'ModelConfig':
            ModelConfig.registry[cls.__name__.upper()] = cls
    
    def __init__(self,model_name,*,is_stream:bool,**kwargs):
        # 延迟导入避免循环依赖
        from .base_api import get_available_models
        available_models = get_available_models()
        if model_name not in available_models:
            raise ValueError(f"模型 {model_name} 不存在")
        self._model_type = available_models[model_name]
        self._model_name = model_name
        self._is_stream = is_stream
        self._interact_config = {
            **kwargs
        }
    def get_model_name(self)->str:
        return self._model_name
    def get_interact_config(self)->dict[str,Any]:
        return self._interact_config.copy()
    def is_stream(self)->bool:
        return self._is_stream
    def get_model_type(self)->str:
        return self._model_type
    def __str__(self)->str:
        return f"model_name: {self._model_name}, is_stream: {self._is_stream}, interact_config: {self._interact_config}"
    @classmethod
    def get_model_config(cls, config: dict[str, str | dict]) -> "ModelConfig|None":
        if config.get("model_name"):
            best_matched = ModelConfig
            max_score = 0
            # 备份config避免修改原始数据
            config_copy = config.copy()
            model_name = config_copy.pop("model_name")
            is_stream = config_copy.pop("is_stream", True)
            # 1. 精确匹配
            config_name = model_name.replace("-","").replace(".","").replace(" ","").replace("_","").upper()
            if config_name in cls.registry:
                return cls.registry[config_name](model_name, is_stream=is_stream, **config_copy)
            # 2. 模糊匹配：按 - 或 _ 分词后匹配，带版号（数字）的匹配权重*2
            import re
            words = re.split(r'[-_]', model_name.upper())
            words = [w for w in words if w]  # 过滤空字符串
            for registry_key, config_class in cls.registry.items():
                score = 0
                for word in words:
                    if word in registry_key:
                        # 带版号（包含数字）的匹配权重*2，提高版本匹配准确性
                        if re.search(r'\d', word):
                            score += 2
                        else:
                            score += 1
                if score > max_score:
                    max_score = score
                    best_matched = config_class
        return best_matched(model_name, is_stream=is_stream, **config_copy)
class GPT45(ModelConfig):
    def __init__(self,model_name:str="gpt-4.5-preview",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)
class GPT5(ModelConfig):
    def __init__(self,model_name:str="gpt-5",*,is_stream:bool=True,max_completion_tokens:int=128000,reasoning_effort:str="high",**kwargs):
        # GPT5 只支持 temperature=1，不允许自定义
        kwargs.pop('temperature', None)  # 移除外部传入的temperature参数
        super().__init__(model_name,is_stream=is_stream,temperature=1,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)
class GPT5Mini(ModelConfig):
    def __init__(self,model_name:str="gpt-5-mini",*,is_stream:bool=True,max_completion_tokens:int=128000,reasoning_effort:str="high",**kwargs):
        # GPT5Mini 只支持 temperature=1，不允许自定义
        kwargs.pop('temperature', None)  # 移除外部传入的temperature参数
        super().__init__(model_name,is_stream=is_stream,temperature=1,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)
# ========== OpenAI GPT 4.1 系列 ==========
class GPT41(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1",*,is_stream:bool=True,temperature:float=1,max_tokens:int=32000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class GPT41Mini(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1-mini",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class GPT41Nano(ModelConfig):
    def __init__(self,model_name:str="gpt-4.1-nano",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)
# ========== OpenAI GPT 4o 系列 ==========
class GPT4o(ModelConfig):
    def __init__(self,model_name:str="gpt-4o",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== OpenAI O系列推理模型 ==========
class O4Mini(ModelConfig):
    def __init__(self,model_name:str="o4-mini",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O3Pro(ModelConfig):
    def __init__(self,model_name:str="o3-pro-2025-06-10",*,is_stream:bool=False,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O3(ModelConfig):
    def __init__(self,model_name:str="o3",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

class O1(ModelConfig):
    def __init__(self,model_name:str="o1",*,is_stream:bool=True,max_completion_tokens:int=100000,reasoning_effort:str="high",**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_completion_tokens=max_completion_tokens,reasoning_effort=reasoning_effort,**kwargs)

# ========== Anthropic Claude 系列 ==========
class ClaudeOpus4(ModelConfig):
    def __init__(self,model_name:str="claude-opus-4",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=32000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs) 

class ClaudeSonnet4(ModelConfig):
    def __init__(self,model_name:str="claude-sonnet-4",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class Claude37Sonnet(ModelConfig):
    def __init__(self,model_name:str="claude-3-7-sonnet",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=128000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class ClaudeOpus41(ModelConfig):
    def __init__(self,model_name:str="claude-opus-4-1",*,is_stream:bool=True,temperature:float=0.5,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== Alibaba Qwen 系列 ==========
class QwenTurbo(ModelConfig):
    def __init__(self,model_name:str="qwen-turbo-latest",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwenPlus(ModelConfig):
    def __init__(self,model_name:str="qwen-plus-latest",*,is_stream:bool=True,temperature:float=1,max_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwenMax(ModelConfig):
    def __init__(self,model_name:str="qwen-max",*,is_stream:bool=True,temperature:float=1,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

class QwQ32B(ModelConfig):
    def __init__(self,model_name:str="qwq-32b",*,is_stream:bool=True,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

class QwQPlus(ModelConfig):
    def __init__(self,model_name:str="qwq-plus",*,is_stream:bool=True,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

# ========== DeepSeek 系列 ==========
class DeepSeekReasoner(ModelConfig):
    def __init__(self,model_name:str="deepseek-reasoner",*,is_stream:bool=True,max_tokens:int=64000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,max_tokens=max_tokens,**kwargs)

class DeepSeekChat(ModelConfig):
    def __init__(self,model_name:str="deepseek-chat",*,is_stream:bool=True,temperature:float=1,max_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_tokens=max_tokens,**kwargs)

# ========== Google Gemini 系列 ==========
class Gemini25Pro(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-pro",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,include_thoughts:bool=False,**kwargs): #需要看到思考内容就开启include_thoughts
        kwargs.pop("thinking_budget",None) # 2.5Pro无法关闭思考
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,include_thoughts=include_thoughts,thinking_budget=True,**kwargs)

class Gemini25Flash(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-flash",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,include_thoughts:bool=False,thinking_budget:bool=True,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,include_thoughts=include_thoughts,thinking_budget=thinking_budget,**kwargs)
class Gemini25FlashLite(ModelConfig):
    def __init__(self,model_name:str="gemini-2.5-flash-lite",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=65535,**kwargs):
        kwargs.pop("thinking_budget",None) #flash-lite思考
        kwargs.pop("include_thoughts",None) #flash-lite思考
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,**kwargs)
class Gemini20Flash(ModelConfig):
    def __init__(self,model_name:str="gemini-2.0-flash",*,is_stream:bool=True,temperature:float=1,max_output_tokens:int=8000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_output_tokens=max_output_tokens,**kwargs)

# ========== xAI Grok 系列 ==========
class Grok4(ModelConfig):
    def __init__(self,model_name:str="grok-4-0709",*,is_stream:bool=True,temperature:float=1,max_completion_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_completion_tokens=max_completion_tokens,**kwargs)

class Grok3(ModelConfig):
    def __init__(self,model_name:str="grok-3",*,is_stream:bool=True,temperature:float=1,max_completion_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_completion_tokens=max_completion_tokens,**kwargs)

class Grok3Mini(ModelConfig):
    def __init__(self,model_name:str="grok-3-mini",*,is_stream:bool=True,temperature:float=1,max_completion_tokens:int=16000,**kwargs):
        super().__init__(model_name,is_stream=is_stream,temperature=temperature,max_completion_tokens=max_completion_tokens,**kwargs)

# ========== 图像生成模型配置 ==========
class Flux(ModelConfig):
    def __init__(self,model_name: str = "flux-kontext-pro",*,is_stream: bool = False,steps: int = 28,guidance: float = 3.5,aspect_ratio: str = "1:1",seed: int | None = None,output_format: str = "png", **kwargs):
        super().__init__(model_name,is_stream=is_stream,steps=steps,guidance=guidance,aspect_ratio=aspect_ratio,seed=seed,output_format=output_format,**kwargs)
class DallE2(ModelConfig):
    def __init__(self,model_name="dall-e-2",*,is_stream:bool=False,size:str="1024x1024",quality:str="hd",style:str="natural",**kwargs):
        super().__init__(model_name,is_stream=is_stream,size=size,quality=quality,style=style,**kwargs)
class DallE3(ModelConfig):
    def __init__(self,model_name="dall-e-3",*,is_stream:bool=False,size:str="1024x1024",quality:str="hd",style:str="natural",**kwargs):
        super().__init__(model_name,is_stream=is_stream,size=size,quality=quality,style=style,**kwargs)
class GPTImage1(ModelConfig):
    def __init__(self,model_name:str="gpt-image-1",*,is_stream:bool=False,size:str="1024x1024",quality:str="high",output_format:str="png",moderation:str="auto",background:str="auto",**kwargs):
        super().__init__(model_name,is_stream=is_stream,size=size,quality=quality,output_format=output_format,moderation=moderation,background=background,**kwargs)