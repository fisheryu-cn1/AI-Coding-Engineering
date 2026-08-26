# tools/：定制化程序、Skill 与 Agent

> R2 起渐进产出。规划：

- `scripts/`（R2）：①Z3 规则矛盾检查脚本（输入约束文件，输出 SAT 反例/UNSAT core）；②数据引用完整性检查（依赖图/closed-world）；③分歧度采样脚本（N 次生成+unidiff 规范化去重，借鉴 trae-agent 组件）；④检查套件编排入口（pre-commit 用）。
- `skills/`（R3/R5）：①需求解析 skill（S1，输出六列标注草案）；②形式化翻译 skill（S3，输出翻译件草案+自标注不确定位）；③justification 回译 skill（S4，证据→NL 解释，仅解释不改判定）。遵循 SKILL.md 约定；LLM 只在翻译/建议/回译位。
- 演进触发器见 `../plan/01-工具选型.md` §3。

当前状态：占位。
