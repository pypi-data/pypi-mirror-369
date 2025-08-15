# AgentOS 2 开发指南

> **AgentOS** – LLM驱动的图结构自动化工作流框架
> 
> **核心设计哲学**：Flow是逻辑的“编排者”，Agent是能力的“行动者”。

**包导入使用 `agent_os2`**  
**可导入：** `BaseAgent, Flow, execute, execute_with_visualization, ModelConfig, register, BaseProcessor, DataPackage, StreamDataStatus, ProcessorError` 和 `*` 导出工具函数（包括各种预定义模型配置类如`GEMINI25FLASH`, `GPT4o`, `Claude4Sonnet`等）

---

## 1. 快速开始

### 1.1 环境准备
```bash
# 推荐在conda等虚拟环境中安装
pip install ./agent_os2
```

### 1.2 必备配置
在您的项目工作目录/aos_config下，需要准备以下两个配置文件：

**`agent_settings.json`**
此文件用于注册您的自定义Agent。通过命名空间（namespace）来组织Agent，避免命名冲突。
```json
{
  "default_agents": ["agent_os2/agents/base"],
  "story_agents": ["agents/examples/story_generate_example"]
}
```
- 在创建`Flow`时，可以通过`agents_key`参数指定加载哪个命名空间下的Agent。

**`model_settings.json`**
此文件用于配置语言模型或其他API的访问信息。
```json
{
  "openai_processor": {
    "api_key": "sk-...", 
    "base_url": "https://api.openai.com/v1", 
    "proxy": "",
    "models": ["gpt-4o", "gpt-3.5-turbo"]
  }
}
```

### 1.3 Hello, AgentOS!
下面是一个最基础的 AgentOS 工作流示例。

```python
from agent_os2 import execute, Flow, execute_with_visualization

# 1. 创建一个Flow，并声明它期望从外部接收一个名为 `intro` 的共享上下文
flow = Flow("demo_flow", expected_shared_context_keys={"intro"})

# 2. 向Flow中添加一个Agent。这里使用框架内置的 `base` Agent
#    它会简单地将输入参数 `message` 和共享上下文 `intro` 拼接后返回
flow.add_agent("base")

# 3. 执行Flow
#    - `args`: 初始输入参数，传递给没有上游的入口Agent
#    - `shared_context`: 贯穿整个Flow的共享数据
result = await execute(
    flow, 
    args={"message": "Hi!"}, 
    shared_context={"intro": "hello"}
)

# 4. 可视化执行，便于调试
#    这将在浏览器中打开一个显示工作流执行路径和数据的页面
result_viz = await execute_with_visualization(
    flow,
    args={"message": "Hi!"},
    shared_context={"intro": "hello"}
)

# 5. 高级执行参数
observer_list = []
observer = await execute(
    flow,
    args={"message": "Hi!"},
    shared_context={"intro": "hello"},
    concurrent_limit=5,      # 并发限制，控制同时执行的Agent数量
    observer=observer_list,  # 用于监控执行状态的列表
    db_client=my_db_client   # 注入外部服务对象，作为 Extra Contexts
)
```

---

## 2. 核心架构

### 2.1 Agent执行生命周期
每个Agent的执行都遵循一个固定的生命周期：
`setup()` → `batch_field`解析 → 提示词解析 → 模型调用(可选) → `post_process()` → **`apply_command()` (可选)** → 触发下游

### 2.2 DAG约束的图结构
- **核心特性**：AgentOS的工作流是一个有向无环图(DAG)。每个Agent/Flow实例在一次执行中只能运行一次，防止无限循环。
- **并发调度**：框架会根据Agent之间的依赖关系，自动并行执行所有没有未完成上游的节点。

### 2.3 双层并发机制
- **Agent级**: 通过`batch_field`属性，可以对一批同质数据进行并行处理。
- **Flow级**: DAG的图结构天然支持对异构任务进行并行调度。

### 2.4 Flow即Agent
`Flow`本身继承自`BaseAgent`，这意味着任何一个Flow都可以作为一个子节点被嵌套在另一个更大的Flow中，从而实现复杂的模块化和流程复用。

### 2.5 Agent注册规范
框架通过约定来简化Agent的注册，支持多种命名映射方式：

**标准命名映射（推荐）**：
- **文件名**: `example_task.py` 
- **类名**: `ExampleTaskAgent`
- **引用名**: `example_task` (在`add_agent`时使用)

**备选命名映射**：
- **文件名**: `example_task_agent.py`
- **类名**: `ExampleTaskAgent` 
- **引用名**: `example_task`

**Flow类命名映射**：
- **文件名**: `example_flow.py`
- **类名**: `ExampleFlow`
- **引用名**: `example_flow`

**核心原则**: 一个文件对应一个Agent，通过文件名自动推导注册名。

---

## 3. 数据流与上下文核心 (Core Concepts of Data Flow & Context)

### 黄金法则：`post_process` 是唯一的“副作用”出口
为了保证数据流的可预测性和可追溯性，所有对运行时上下文的修改（向下游传递数据、修改共享内存、调用外部服务等），都应该在 `post_process` 方法的末尾集中处理并返回。`_run_agent_pipeline`中的其他部分应被视为纯函数。

### 3.1 构建时上下文 (`Settings`)
`Settings`是Agent/Flow在**创建**时传入的静态配置，用于定义Agent的行为模式，而非传递动态数据。

- **继承原则**：子节点的设置会 **覆盖** 父级同名设置。这允许你对Flow中的单个Agent进行精细化配置。
- **内置支持**：`is_debug`（默认开启）, `stdout`, `stdin`, `max_*_limit`, `debug_context`（开启后，debug_info会显示该agent完整的运行时上下文）。
- **使用方式**：
  ```python
  # 在添加Agent时，将配置作为关键字参数传入
  flow.add_agent("agent_type", alias="a1", is_debug=False, custom_param="value")
  ```

### 3.2 运行时上下文 (`Runtime Contexts`)
运行时上下文是工作流执行过程中动态流动的数据，分为三层，各司其职：

#### 3.2.1 `Args` (`{src.*}`): 接力棒，单站传递
`Args`是连接Agent链条最基础的方式，遵循严格的“单站传递”规则。它就像接力棒，只从上一个Agent传递给紧邻的下一个Agent，不会“穿透”到下下游节点。

- **修改方式**: `post_process`的第一个返回值 `final_result` 将成为下游Agent的`{src.*}`。
  ```python
  async def post_process(self, ...):
      final_result = {"data": "processed_data"} 
      # `final_result` 会被发送给下游Agent作为输入
      return final_result, {} 
  ```

#### 3.2.2 `Shared Context` (`{ctx.*}`): 工作区白板，受控修改
`Shared Context`是Flow的内部工作内存，用于管理 **流程自身产生的数据**，供工作流内所有Agent访问。

- **修改方式**: 在`post_process`中返回`agent_command`的`memory`键来更新。框架会以“平替模式”递归合并字典。
  ```python
  async def post_process(self, ...):
      command = {"memory": {"task_status": "processing", "step": 2}}
      return some_result, command
  ```
- **嵌套继承机制**: 子Flow可以通过`expected_shared_context_keys`属性从父级Flow继承上下文。这实现了上下文的按需、安全地层级传递。
  ```python
  # 父Flow声明它管理 task_info
  parent_flow = Flow("parent", expected_shared_context_keys={"task_info"})
  
  # 子Flow声明它需要从父级继承 task_info，并且自己还管理 user_data
  child_flow = Flow("child", parent=parent_flow, expected_shared_context_keys={"task_info", "user_data"})
  ```
  **注意**：必须显式声明需要继承的键，未声明的键不会传递。
  
 - **序列化与数据类型建议**: `Shared Context`应当是可序列化的字典，建议仅存放基础数据类型（int、str、float、dict、list），避免直接存放引用类型对象。

#### 3.2.3 `Extra Contexts`: 全局工具箱，外部接口
`Extra Contexts`用于传递 **外部服务或接口对象的引用**，例如数据库连接、RAG客户端等。它在整个执行过程中全局共享，所有Agent（包括子Flow中的Agent）都可以访问。

- 注入方式
  - 方式A：顶层注入（通过 `execute` 关键字参数）
    ```python
    rag_client = SimpleRAGClient()
    result = await execute(
        flow,
        args={"question": "AgentOS是什么？"},
        rag_client=rag_client  # 注入后，Agent内部可通过 runtime_contexts.get("rag_client") 访问
    )
    ```
  - 方式B：流内注入（Bootstrap Agent + `add_context`）
    在Flow开头构建一个“引导”Agent以提取初始参数并通过默认命令`add_context`注入对象。
    ```python
    class MyBootstrapAgent(BaseAgent):
        def setup(self):
            self.prompts = {}  # 不调用模型
        async def post_process(self, input_args, model_result, shared_context, extra_contexts, observer, batch_id=None):
            if not isinstance(input_args, dict):
                return {}, {"actions": [{"cancel_next_steps": True}]}
            system = input_args.pop("system")
            to_memory = {"summary": input_args.pop("summary", "")}
            return {**input_args}, {"memory": to_memory, "add_context": {"system": system}}
    ```
  - 如何选择
    - 顶层注入（方式A）：当该Flow作为顶层流程、且需要注入的接口对象是通用/全局共享（例如统一的DB/RAG客户端），由外部应用负责生命周期管理时，优先选择，简单直接。
    - 流内注入（方式B）：当该Flow需要被作为子Flow复用、或接口对象需基于入参在运行时动态生成/选择、或希望将依赖封装在Flow内部以增强可移植性时，优先选择。

- **传播与拷贝语义**:
  - `Extra Contexts`会自动向下传递到子Flow；子Flow中的`extra_contexts`是父Flow`extra_contexts`的浅拷贝。
  - 子Flow在`extra_contexts`中新添加的对象不会影响父Flow。

- **使用方式**:
  1.  **直接调用 (简单场景)**: 在`post_process`的末尾直接调用对象的方法。
  2.  **自定义Command (复杂场景)**: 定义自己的`agent_command`键，并重写Agent的`apply_command`方法来处理，详见动态控制章节。

---

## 4. 构建智能Agent

### 4.1 `BaseAgent`实现骨架
```python
class MyAgent(BaseAgent):
    def setup(self):
        # 1. 配置初始化（必须在setup中设置）
        self.prompts = "Process this data: {src.data}"
        self.strict_mode = True              # 启用解析框架，默认解析JSON
        self.model_config = GEMINI25FLASH()  # 使用预定义模型配置类
        self.batch_field = "src.items"       # 批处理字段
        self.retry_count = 3
        self.model_timeout = 60
        
    async def post_process(self, input_args, llm_result, shared_context, extra_contexts, observer, batch_id=None):
        # 2. 处理模型结果或执行业务逻辑
        #    llm_result 是模型返回或在 strict_mode 下解析后的结果
        return {"result": llm_result}, {"memory": {"status": "done"}}
```

**继承开发原则**
如果需要为多个Agent提供通用功能（例如统一的日志记录、特定的API调用能力），**最佳实践**是继承`BaseAgent`实现一个**抽象的功能基类**，然后让具体的业务Agent继承这个基类，以复用这些通用功能。这避免了代码重复，并保持了业务Agent的逻辑纯粹性。

### 4.2 提示词系统

#### 4.2.1 强大的动态模板
AgentOS的提示词系统是一个功能强大的模板引擎，它能让你在提示词中灵活地访问所有运行时上下文。

- **基础语法**:
  - **`{src.*}`**: 访问 `Args` (上游数据)。
  - **`{ctx.*}`**: 访问 `Shared Context` (工作区白板)。
  - **`%batch_index%`**: 批处理索引（配合`batch_field`使用）。
  - **`{{}}`**: 转义语法，例如 `{{result}}` 会在最终的提示词中变为 `{result}`。

- **工作原理：递归式惰性解析**
  该模板引擎最强大的特性是支持**深度嵌套和动态索引**的解析。它通过“递归式惰性解析”实现：由内而外地、逐层地解析模板。当一次完整的解析后字符串不再变化时，解析结束。这使得复杂的动态数据访问变得轻而易举。
  ```python
  # 支持嵌套访问和动态索引：
  "{src.users[2].name}"           # 列表索引
  "{src.data.config.timeout}"     # 嵌套字典访问
  "{src.items[{ctx.index}]}"      # 动态列表索引（使用ctx.index的值作为索引）
  "{rag.{src.query}}"             # 动态多字典键访问
  ```

#### 4.2.2 扩展提示词能力 (`get_context_value`)
要让提示词能够智能地利用`Extra Contexts`中的外部工具（如RAG），你需要重写`get_context_value`方法。这相当于为提示词模板**定义自己的扩展函数**。

**工作原理**: 框架在解析提示词时，会调用`get_context_value`。通过重写此方法，你可以拦截自定义前缀（如`{rag.*}`），从`extra_contexts`中获取相应的服务对象，执行操作（如搜索），并将结果返回给模板引擎进行替换。

**完整示例：在提示词中集成RAG查询**
1.  **准备一个RAG客户端**
    ```python
    class SimpleRAGClient:
        def search(self, query: str) -> str:
            return f"知识库中关于'{query}'的信息..."
    ```
2.  **在Agent中重写`get_context_value`**
    ```python
    class RagQueryAgent(BaseAgent):
        def setup(self):
            self.prompts = {
                "system": "你是一个问答专家。",
                "user": "根据以下知识：\n{rag.卢浮宫的介绍}\n\n请回答问题：{src.question}"
            }
        
        async def get_context_value(self, key: str, runtime_contexts: dict, default: Any = "") -> Any:
            # 1. 检查是否是我们自定义的前缀
            if key.startswith("rag."):
                query = key[4:]
                rag_client = runtime_contexts.get("rag_client") # 从extra_contexts获取客户端
                
                if rag_client and query:
                    # 2. 调用外部服务并返回结果
                    return rag_client.search(query)
                return "没有找到相关知识。"
            
            # 3. 对于其他前缀，使用父类的默认实现
            return await super().get_context_value(key, runtime_contexts, default)
    ```

#### 4.2.3 提示词模板最佳实践
- 简单优先：建议少构建复杂的嵌套访问结构和使用过深层的转义符，保持提示词清晰
- 不支持：条件判断、循环、函数调用等编程语法
- 扩展通道：通过 `get_context_value` 实现实际找到对应prefix后key的访问逻辑

### 4.3 模型配置与资源管理
AgentOS 2 提供了丰富的预定义模型配置类，覆盖主流AI模型：

#### 4.3.1 预定义模型配置类
- **OpenAI系列**: `GPT5()`, `GPT4o()`, `O1()`, `O3()`, `O4Mini()` 等
- **Claude系列**: `Claude4Opus()`, `Claude4Sonnet()`, `Claude37Sonnet()`
- **Google系列**: `Gemini25Pro()`, `GEMINI25FLASH()`, `Gemini20Flash()` 等  
- **国产模型**: `QwenMax()`, `DeepSeekChat()`, `QwQ32B()` 等
- **图像生成**: `Flux()`, `DallE()`, `GPTIMAGE1()` 等
- **通用配置**: `ModelConfig(model_name, is_stream=True, **kwargs)` - 基础配置类

#### 4.3.2 配置优先级与使用
- **模型配置优先级**：Agent内setup()方法中设置的model_config > settings中的model_config配置 > 预定义配置类的默认值。
- **资源限制**: 在`Settings`中通过`max_*_limit`参数控制资源使用。框架会自动检查处理器返回的`usage`指标。
  - `usage`返回`{"total_tokens": 100}` → 检查`max_tokens_limit`
  - `usage`返回`{"cost": 0.01}` → 检查`max_cost_limit`

#### 4.3.3 自定义模型配置示例
```python
# 使用预定义配置类（推荐）
self.model_config = GEMINI25FLASH(temperature=0.7, max_tokens=4000)

# 使用通用ModelConfig类
self.model_config = ModelConfig("custom-model", is_stream=True, temperature=0.5)

# 从配置字典创建
config_dict = {"model_name": "gpt-4o", "is_stream": False, "interact_config": {"temperature": 0.8}}
self.model_config = ModelConfig.get_model_config(config_dict)
```

### 4.4 解析框架 (`strict_mode`)
启用`strict_mode=True`后，框架会自动解析模型输出（默认为JSON），并在失败时结合`retry_count`进行重试。你可以重写以下方法来自定义解析和重试逻辑。

```python
def parse_model_result(self, runtime_contexts, model_result, batch_id=None):
    # 重写默认的JSON解析，实现任意逻辑
    numbers = re.findall(r'\d+', model_result)
    if not numbers:
        raise ValueError("未找到数字")  # 抛出异常会触发重试
    return float(numbers[0])

def adjust_prompt_after_failure(self, prompts, error_text, hint):
    # 在重试前调整提示词，引导模型输出正确格式
    return super().adjust_prompt_after_failure(prompts, error_text, "\n请注意：你必须只返回一个数字！")
```

---

## 5. 编排复杂工作流

### 5.1 工作流编排方式

#### 5.1.1 DSL方式 (YAML)
```yaml
my_flow:
    agents_key: my_namespace  # 可选：指定Agent注册表命名空间
    expected_shared_context_keys: [key1, key2]
    agents:
        agent1:
            name: agent_type_1
            settings: {is_debug: false}
        agent2:
            name: agent_type_2
    edges:
        - agent1 -> agent2
    entry_agent: agent1
```
```python
flow = Flow.construct_from_dsl(yaml_content)
```

#### 5.1.2 代码方式
```python
# 1. 直接构建
flow = Flow("my_flow", agents_key="my_namespace", expected_shared_context_keys={"key1"})
a1 = flow.add_agent("type1", alias="a1")
a2 = flow.add_agent("type2")
flow.add_edge("a1", "type2")

# 2. 继承方式 (用于创建可复用的Flow模块。Flow是数据桥梁而非逻辑处理单元)
class MyComplexFlow(Flow):
    def __init__(self, name, parent, **settings):
        # 推荐在子类中固定agents_key，避免参数混淆
        super().__init__(name, parent, agents_key="my_namespace", expected_shared_context_keys={...}, **settings)
        # 只在构造函数中组织Agent
        self.add_agent("step1")
        self.add_agent("step2")
        self.add_edge("step1", "step2")
```

  ### 5.2 `agent_command`: 运行时动态控制
Agent可通过`post_process`的第二个返回值发送命令，在Agent流程结束后由其**自行执行命令**，实现运行时动态控制。

#### 5.2.1 默认命令
- **`memory`**: 更新`Shared Context`。
- **`actions`**: 修改Flow图结构。支持的actions包括：
  ```python
  # 添加分支：Agent、Flow(name)、Flow(dsl)
  {"add_branch": {"name": "validator","settings": {...}}}
  {"add_branch": {"name": "sub_flow", "settings": {...}}}
  {"add_branch": {"dsl": "flow:\n  agents:\n    step1:\n      name: processor"}}
  
  # 链式插入：支持Agent/Flow混合，支持并行（嵌套列表）
  {"insert": [
      {"name": "process"}, 
      {"dsl": "validation_flow:\n  agents:\n    validator:\n      name: data_validator"},
      [{"name": "analyze"}, {"name": "validate"}],  # 并行
      {"name": "merge"}
  ]}
  
  # 中断后续步骤
  {"cancel_next_steps": True}
  ```
- **`add_context`**: 向`Extra Contexts`注入新对象

#### 5.2.2 自定义命令与最佳实践
**核心原则**：为了最大化**封装性**和**模块化**，自定义命令的处理逻辑应该在 **Agent 子类**中通过重写 `apply_command` 来实现。这使得 Agent 成为一个可移植、自包含的功能单元。

**最佳实践：通过抽象Agent共享命令处理能力**
当多个Agent都需要同一种自定义命令（如`db_save`）时，**不要**为它们分别实现`apply_command`。最佳实践是创建一个**抽象的“能力”基类**，让其他Agent继承它。

```python
# 步骤1: 创建一个可复用的“能力”基类
class DatabaseAwareAgent(BaseAgent):
    async def apply_command(self, agent_command, input_args, shared_context, extra_contexts):
        # 处理我们自己的特殊指令
        await super().apply_command(agent_command, input_args, shared_context, extra_contexts)
        if "db_save" in agent_command:
            data = agent_command.pop("db_save")
            db_client = extra_contexts.get("db_client")
            if db_client:
                await db_client.save(data)

# 步骤2: 任何需要此能力的Agent只需继承即可
class DataParserAgent(DatabaseAwareAgent):
    async def post_process(self, ...):
        # 我只负责发出指令，父类会处理它
        return result, {"db_save": parsed_data}
```
这个模式避免了代码重复，并且无需修改任何 Flow 的定义。

---

## 6. 高级主题

### 6.1 并发与批处理 (`batch_field`)
当你设置`self.batch_field = "src.items"`时，框架会自动为`src.items`列表中的每个元素启动一个并行的`_run_agent_pipeline`任务，并在所有任务完成后，将结果智能地合并。

- **自动合并策略**:
  - **列表(List)** -> **拼接(extend)**
  - **字典(Dict)** -> **递归合并**
  - **其他类型** -> **汇集成列表**

**注意**: 你无需，也切勿在 `post_process` 中手动聚合批处理的结果。框架会自动处理。

### 6.2 调试
1. **可视化执行**: `execute_with_visualization(flow)` 是最直观的调试工具。
2. **调试上下文**: `debug_context=True` 会在日志中记录Agent执行时的完整上下文。
3. **日志文件**: `is_debug=True`（默认）时，每次执行的详细日志会保存在 `memory/statistics_时间戳/` 目录下，包括`debug_info.md` 和 `visualization.json`。
4. **自定义调试信息**: 在代码中使用`self.debug("my message")`记录信息，会出现在`debug_info`中。

### 6.3 Mock测试
在测试时，可以使用`add_custom_agent_class`注入一个临时的Mock Agent，以绕过模型调用或外部依赖。

```python
# 1. 创建一个Mock Agent类
class MockAgent(BaseAgent):
    def setup(self): self.prompts = {}
    async def post_process(self, *args, **kwargs): return {"mock_result": "test_data"}, {}

# 2. 在测试代码中将其注入Flow
flow = Flow("test_flow")
flow.add_custom_agent_class("mock_agent", MockAgent)
flow.add_agent("mock_agent")

# ⚠️ 此功能仅用于测试环境。
```

### 6.4 使用者交互
- **`stdout`**: 设置`stdout=sys.stdout`，Agent中的`print()`或`record_user_info()`会直接输出到控制台。
- **`stdin`**: 设置`stdin=sys.stdin`，在Agent中调用`self.get_input()`可以接收用户输入。
- **`record_user_info()`**: 推荐使用此函数记录需要给用户看的信息，它会自动处理输出并记录到日志中，使用tag参数区分输出信息。

---

## 7. 参考手册

### 7.1 常见错误
| 错误信息 | 可能原因 | 解决方法 |
|---|---|---|
| `Agent/Flow has been executed` | 工作流(DAG)中存在环路。 | 检查`add_edge`的调用，确保没有形成循环依赖。 |
| `FileNotFoundError` | 配置文件不存在或路径错误。 | 检查配置文件是否在`cwd/aos_config`下，并确保运行环境在`aos_config`同级目录下。 |
| `Agent {agent_type_name} 未找到` | Agent未被成功注册或指定的`agents_key`不正确。 | 检查`agent_settings.json`是否正确将`{agent_type_name}`注册到对应的`{agents_key}`命名空间中。 |

### 7.2 常用工具函数
`agent_os2.utility` 模块提供了一些方便的工具函数：
| 函数 | 用途 |
|---|---|
| `merge_elements()` | 智能地递归合并字典、列表等数据结构，支持替换优先或追加优先两种模式。 |
| `record_user_info()` | 记录面向用户的交互信息，支持标准输出和日志记录。 |
| `get_context_value()` | 解析字典/列表路径以获取值，支持自定义前缀访问。 |

**详细实现和参数说明**请参考 `agent_os2/agent_os/utility.py`。

---
*Happy Hacking with AgentOS 2 🚀*
