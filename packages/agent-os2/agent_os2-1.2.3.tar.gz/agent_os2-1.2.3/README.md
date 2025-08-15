# AgentOS2 项目脚手架
> LLM驱动的智能工作流系统，支持图结构编排、流程嵌套、双层并发架构

## 📌 项目结构
```
agent_os2/
├── agent_os/              # 核心框架
│   ├── base_agent.py      # Agent抽象
│   ├── flow.py            # DAG调度器  
│   ├── base_model/        # 模型接口
│   ├── utility.py         # 工具函数
│   └── visualize.py       # 可视化
├── agents/examples/       # 示例
├── agent_settings.json    # Agent配置
├── model_settings.json    # 模型配置
└── DEVELOPING_GUIDE.md    # 开发指南
```

## 🚀 核心特性

### 一、BaseAgent

#### 1.1 生命周期
✅ **已完成**: 标准流程(`激活→批处理→执行→下发`) | 三阶段(`setup`/`pipeline`/`post_process`) | 纯函数特性

#### 1.2 上下文系统  
✅ **已完成**: Settings(构建时继承) | Args/SharedContext/ExtraContexts(运行时) | 模板系统(`{src.*}`/`{ctx.*}`) | 深度合并  
⏳ **未完成**: 上下文压缩 | RAG/KAG集成

#### 1.3 批处理
✅ **已完成**: `batch_field` | 批处理索引 | 双层并发架构

#### 1.4 模型交互
✅ **已完成**: 统一接口 | 智能重试 | 超时控制 | 严格模式 | JSON校验 | 模型配置优先级加载
⏳ **未完成**: 模型Tag精选 | 动态切换

#### 1.5 日志系统
✅ **已完成**: user_info | debug_info | 批处理标识 | 即时输出

#### 1.6 agent_command
✅ **已完成**: memory(更新context) | actions(修改图结构) | add_context(注入接口对象) | 可扩展

### 二、Flow

#### 2.1 图结构调度
✅ **已完成**: 有向图依赖 | 拓扑并发 | 动态修改 | 循环/条件分支  
⏳ **未完成**: 分布式调度 | 远程执行

#### 2.2 Flow功能
✅ **已完成**: Agent/Flow一体化 | YAML DSL | 入口管理 | 别名机制 | 热重载 | Mock注入

#### 2.3 上下文隔离  
✅ **已完成**: 父子隔离 | 按需继承(`expected_shared_context_keys`) | 动态更新 | 优化传递

#### 2.4 执行统计
✅ **已完成**: 资源限制(`max_*_limit`) | 性能指标 | 执行可视化 | flow_results

### 三、辅助系统

#### 3.1 模型系统
✅ **已完成**: Processor注册 | LLM/ImageConfig | 多模型配置 | 流式输出 | 多模态  
⏳ **未完成**: 模型路由 | 自适应

#### 3.2 工具函数
✅ **已完成**: DSL解析 | Agent发现 | JSON解析 | 字典合并 | 模板解析  
⏳ **未完成**: Token压缩 | RAG/KAG工具

#### 3.3 执行接口
✅ **已完成**: execute() | 可视化执行 | 单Agent测试 | 双模式 | 并发限制 | observer  
⏳ **未完成**: 分布式执行 | MCP插件

## 📖 最新更新
- **上下文传递优化**: 只传递存在的键，改进get()行为

## 🔗 相关文档
- [DEVELOPING_GUIDE.md](DEVELOPING_GUIDE.md) - 详细开发指南
- [agents/examples/](agents/examples/) - 示例工作流
