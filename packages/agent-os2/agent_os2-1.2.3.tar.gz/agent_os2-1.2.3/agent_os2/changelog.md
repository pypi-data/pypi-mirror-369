# 1.2.3 2025.8.15
    1. 减少了一句因尝试加载Agent失败而产生的print
    2. 更加明确shared_context与extra_contexts的差异和职责。shared_context是flow内所有agent的共享上下文，并且是一个可序列化字典，而extra_contexts是一个会自动向下传递接口对象字典，子Flow的extra_contexts是父Flow的extra_contexts的浅拷贝
    3. 修改对是否是同一个"类对象"的判断方式，放松判断条件。
    4. 修复visualize对执行完毕的元素顺序判断错乱的问题（依赖条件触发）
    5. 增加命令：add_context，用于向extra_contexts注入新的接口对象
    6. 优化了utility中get_context_value的实现，现在这个工具函数变得更加通用了
    7. 优化了DEVELOPING_GUIDE.md，添加了更多关于shared_context与extra_contexts的说明
    8. 减少actions中的命令，将add_*_branch命令合并为add_branch命令，将insert_*命名合并为insert命令，保留dsl键作为构建flow的特工
    9. 将command_to_flow命令重命名为agent_command，明确语义
    10. 优化自动注册机制，防止重复的模块加载
    11. 优化了model_processor内部的逻辑，提高复用性和规范性
    12. 重置了ModelConfig，穷举了常见的模型配置，并为其适配可选默认参数，删除了宽泛的LLMConfig
    13. 为ModelConfig添加基于__init_subclass__的自动注册机制和基于分词的智能匹配功能，支持通过模型名称(如claude-opus-4-20250514)自动匹配到对应的配置类，同时新增GPT4、ClaudeOpus4等模型配置类
# 1.2.2 2025.8.6
    1. 为stdout添加tag参数，用于区分不同类型的输出
    2. 优化报错信息，提示更加具体指明问题原因
    3. 优化agent_settings.json的注册机制，支持多种命名映射方式
# 1.2.1 2025.8.5
    1. 添加settings属性中对model_config配置的支持，并且明确优先级：Agent内setup设置的ModelConfig>settings中的model_config>LLMConfig的构造默认值
# 1.2.0 
    项目正式发布版本，全部流程基本稳定