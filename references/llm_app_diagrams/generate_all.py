#!/usr/bin/env python3
"""Generate all 9 SVG diagrams for llm_app_architecture_guide.html"""
import sys, json, os

# Load generate-from-template.py via importlib (filename has hyphen)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_from_template",
    r"C:\Users\Yu\.claude\skills\fireworks-tech-graph\scripts\generate-from-template.py"
)
gen_mod = importlib.util.module_from_spec(spec)
sys.modules["generate_from_template"] = gen_mod
spec.loader.exec_module(gen_mod)
build_svg = gen_mod.build_svg

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def save(name, data):
    svg = build_svg(data.get("template_type", "architecture"), data)
    path = os.path.join(OUTPUT_DIR, f"{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated: {path}")

# =====================================================================
# 1. 大模型应用框架全景图 (Landscape)
# =====================================================================
save("01_landscape", {
    "template_type": "architecture",
    "style": 1,
    "style_overrides": {
        "type_label_fill": "#374151",
        "type_label_size": 13,
    },
    "width": 960,
    "height": 640,
    "title": "大模型应用框架全景图",
    "subtitle": "按设计范式分为 8 大类",
    "nodes": [
        {"id":"n1","kind":"rect","x":70,"y":110,"width":400,"height":75,"label":"LangChain (LCEL) / LangGraph","type_label":"通用编排","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"n2","kind":"rect","x":70,"y":205,"width":400,"height":75,"label":"LlamaIndex","type_label":"检索增强","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"n3","kind":"rect","x":70,"y":300,"width":400,"height":75,"label":"AutoGen / CrewAI / Agno","type_label":"多 Agent 协作","fill":"#faf5ff","stroke":"#e9d5ff"},
        {"id":"n4","kind":"rect","x":70,"y":395,"width":400,"height":75,"label":"PydanticAI","type_label":"类型安全","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"n5","kind":"rect","x":490,"y":110,"width":400,"height":75,"label":"Vercel AI SDK","type_label":"前端集成","fill":"#fef2f2","stroke":"#fecaca"},
        {"id":"n6","kind":"rect","x":490,"y":205,"width":400,"height":75,"label":"OpenAI Agents SDK / Smolagents","type_label":"极简原生","fill":"#f0fdfa","stroke":"#ccfbf1"},
        {"id":"n7","kind":"rect","x":490,"y":300,"width":400,"height":75,"label":"Dify / Flowise","type_label":"低代码平台","fill":"#f8fafc","stroke":"#e2e8f0"},
        {"id":"n8","kind":"rect","x":490,"y":395,"width":400,"height":75,"label":"Semantic Kernel (Microsoft)","type_label":"企业多语言","fill":"#f5f3ff","stroke":"#ddd6fe"},
        {"id":"n9","kind":"rect","x":70,"y":490,"width":820,"height":75,"label":"Letta (MemGPT) / Mem0 / Zep","type_label":"上下文记忆","fill":"#fdf4ff","stroke":"#f0abfc"},
    ],
    "arrows": [],
})

# =====================================================================
# 2. 组合 1：企业知识库 Agent
# =====================================================================
save("02_combo1_rag", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 720,
    "title": "组合 1：企业知识库 Agent",
    "subtitle": "RAG + 状态机 + 类型安全",
    "containers": [
        {"x":40,"y":80,"width":880,"height":620,"label":"","stroke":"#e5e7eb","fill":"none","rx":12}
    ],
    "nodes": [
        {"id":"front","kind":"rect","x":300,"y":110,"width":360,"height":70,"label":"React + Vercel AI SDK","sublabel":"useChat, streamText, 消息状态管理","type_label":"前端层","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"api","kind":"rect","x":300,"y":230,"width":360,"height":70,"label":"FastAPI + PydanticAI","sublabel":"Agent[UserQuery, AgentResponse] 强类型校验","type_label":"API 网关层","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"orch","kind":"rect","x":300,"y":350,"width":360,"height":90,"label":"LangGraph StateGraph","sublabel":"路由→检索→生成→审核→输出","type_label":"编排层","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"retrieve","kind":"rect","x":120,"y":500,"width":320,"height":90,"label":"LlamaIndex","sublabel":"VectorIndex / QueryEngine / Reranker / Source Nodes","type_label":"检索层","fill":"#faf5ff","stroke":"#e9d5ff"},
        {"id":"tools","kind":"rect","x":520,"y":500,"width":320,"height":90,"label":"PydanticAI 工具层","sublabel":"Calculator / SQLQuery / APIClient 类型化调用","type_label":"工具层","fill":"#f5f3ff","stroke":"#ddd6fe"},
    ],
    "arrows": [
        {"source":"front","target":"api","source_port":"bottom","target_port":"top","label":"HTTP / SSE","flow":"control"},
        {"source":"api","target":"orch","source_port":"bottom","target_port":"top","label":"Pydantic Schema","flow":"data"},
        {"source":"orch","target":"retrieve","source_port":"bottom","target_port":"top","label":"检索请求","flow":"data"},
        {"source":"orch","target":"tools","source_port":"bottom","target_port":"top","label":"工具调用","flow":"control"},
    ],
})

# =====================================================================
# 3. 组合 2：智能数据分析平台
# =====================================================================
save("03_combo2_data", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 680,
    "title": "组合 2：智能数据分析平台",
    "subtitle": "代码 Agent + 可视化前端",
    "containers": [
        {"x":40,"y":80,"width":880,"height":560,"label":"","stroke":"#e5e7eb","fill":"none","rx":12}
    ],
    "nodes": [
        {"id":"front2","kind":"rect","x":300,"y":110,"width":360,"height":70,"label":"React + Vercel AI SDK","sublabel":"useChat + 自定义数据卡片/图表组件","type_label":"前端层","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"smol","kind":"rect","x":300,"y":230,"width":360,"height":90,"label":"Smolagents (CodeAgent)","sublabel":"LLM 生成 Python 代码 / 沙箱执行 / Pandas+Matplotlib","type_label":"编排层","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"pydantic","kind":"rect","x":300,"y":370,"width":360,"height":70,"label":"PydanticAI + SQLModel","sublabel":"自然语言 → Text2SQL → Pydantic 校验 → 只读查询","type_label":"数据层","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"store","kind":"cylinder","x":300,"y":490,"width":360,"height":80,"label":"内部数据仓库 / OLAP / ClickHouse","type_label":"存储层","fill":"#f8fafc","stroke":"#94a3b8"},
    ],
    "arrows": [
        {"source":"front2","target":"smol","source_port":"bottom","target_port":"top","label":"查询","flow":"control"},
        {"source":"smol","target":"pydantic","source_port":"bottom","target_port":"top","label":"Text2SQL","flow":"data"},
        {"source":"pydantic","target":"store","source_port":"bottom","target_port":"top","label":"SQL 执行","flow":"data"},
    ],
})

# =====================================================================
# 4. 组合 3：多角色协作内容工厂
# =====================================================================
save("04_combo3_crew", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 640,
    "title": "组合 3：多角色协作内容工厂",
    "subtitle": "多 Agent 团队 + 任务队列",
    "containers": [
        {"x":40,"y":80,"width":880,"height":520,"label":"","stroke":"#e5e7eb","fill":"none","rx":12}
    ],
    "nodes": [
        {"id":"crew","kind":"rect","x":300,"y":110,"width":360,"height":60,"label":"CrewAI Coordinator","sublabel":"分配任务给各角色 Agent","type_label":"管理层","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"research","kind":"rect","x":120,"y":230,"width":220,"height":80,"label":"研究员 Agent","sublabel":"LlamaIndex RAG 检索","type_label":"角色","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"writer","kind":"rect","x":370,"y":230,"width":220,"height":80,"label":"撰稿 Agent","sublabel":"PydanticAI 结构化输出","type_label":"角色","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"reviewer","kind":"rect","x":620,"y":230,"width":220,"height":80,"label":"审核 Agent","sublabel":"PydanticAI 规则校验","type_label":"角色","fill":"#fef2f2","stroke":"#fecaca"},
        {"id":"output","kind":"rect","x":300,"y":380,"width":360,"height":70,"label":"Dify / 内部 CMS","sublabel":"Workflow 接入人工审核节点 → 发布","type_label":"输出层","fill":"#faf5ff","stroke":"#e9d5ff"},
    ],
    "arrows": [
        {"source":"crew","target":"research","source_port":"bottom","target_port":"top","label":"任务","flow":"control"},
        {"source":"crew","target":"writer","source_port":"bottom","target_port":"top","label":"任务","flow":"control"},
        {"source":"crew","target":"reviewer","source_port":"bottom","target_port":"top","label":"任务","flow":"control"},
        {"source":"research","target":"output","source_port":"bottom","target_port":"top","label":"","flow":"data"},
        {"source":"writer","target":"output","source_port":"bottom","target_port":"top","label":"","flow":"data"},
        {"source":"reviewer","target":"output","source_port":"bottom","target_port":"top","label":"","flow":"data"},
    ],
})

# =====================================================================
# 5. 组合 4：.NET 企业级 Copilot
# =====================================================================
save("05_combo4_dotnet", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 680,
    "title": "组合 4：.NET 企业级 Copilot",
    "subtitle": "微软生态全栈",
    "containers": [
        {"x":40,"y":80,"width":880,"height":560,"label":"","stroke":"#e5e7eb","fill":"none","rx":12}
    ],
    "nodes": [
        {"id":"blazor","kind":"rect","x":300,"y":110,"width":360,"height":70,"label":"Blazor / React + Microsoft Fluent UI","sublabel":"嵌入 Teams / SharePoint / Outlook","type_label":"前端","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"sk","kind":"rect","x":300,"y":230,"width":360,"height":90,"label":"Semantic Kernel","sublabel":"Kernel + Plugins + Planner / Prompts + C# 业务逻辑","type_label":"编排层","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"azure","kind":"rect","x":300,"y":370,"width":360,"height":70,"label":"Azure OpenAI Service","sublabel":"GPT-4o + Assistants API + Content Safety","type_label":"模型层","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"aisearch","kind":"rect","x":300,"y":480,"width":360,"height":70,"label":"Azure AI Search + 数据存储","sublabel":"向量+关键词混合检索 / SQL / Cosmos / Blob","type_label":"数据层","fill":"#f8fafc","stroke":"#94a3b8"},
    ],
    "arrows": [
        {"source":"blazor","target":"sk","source_port":"bottom","target_port":"top","label":"Copilot SDK","flow":"control"},
        {"source":"sk","target":"azure","source_port":"bottom","target_port":"top","label":"模型调用","flow":"control"},
        {"source":"azure","target":"aisearch","source_port":"bottom","target_port":"top","label":"检索/存储","flow":"data"},
    ],
})

# =====================================================================
# 6. 组合 5：低代码原型 → 工程化迁移
# =====================================================================
save("06_combo5_migrate", {
    "template_type": "flowchart",
    "style": 1,
    "width": 960,
    "height": 580,
    "title": "组合 5：低代码原型 → 工程化迁移",
    "subtitle": "双轨策略",
    "containers": [
        {"x":40,"y":90,"width":880,"height":200,"label":"阶段一（0-2周）：Dify 快速验证","stroke":"#dbeafe","fill":"#eff6ff","rx":12},
        {"x":40,"y":340,"width":880,"height":200,"label":"阶段二（2-6周）：LangGraph + PydanticAI 工程化重构","stroke":"#dcfce7","fill":"#f0fdf4","rx":12},
    ],
    "nodes": [
        {"id":"d1","kind":"rect","x":100,"y":150,"width":180,"height":50,"label":"拖拽搭建 Workflow","fill":"#ffffff","stroke":"#bfdbfe","flat":True},
        {"id":"d2","kind":"rect","x":320,"y":150,"width":180,"height":50,"label":"验证 Prompt / RAG","fill":"#ffffff","stroke":"#bfdbfe","flat":True},
        {"id":"d3","kind":"rect","x":540,"y":150,"width":180,"height":50,"label":"收集真实用户 query","fill":"#ffffff","stroke":"#bfdbfe","flat":True},
        {"id":"d4","kind":"rect","x":760,"y":150,"width":140,"height":50,"label":"A/B 测试","fill":"#ffffff","stroke":"#bfdbfe","flat":True},
        {"id":"e1","kind":"rect","x":100,"y":400,"width":200,"height":50,"label":"Workflow → StateGraph","fill":"#ffffff","stroke":"#bbf7d0","flat":True},
        {"id":"e2","kind":"rect","x":340,"y":400,"width":200,"height":50,"label":"动态 Prompt → 强类型化","fill":"#ffffff","stroke":"#bbf7d0","flat":True},
        {"id":"e3","kind":"rect","x":580,"y":400,"width":200,"height":50,"label":"CI/CD + 单元测试 + A/B","fill":"#ffffff","stroke":"#bbf7d0","flat":True},
    ],
    "arrows": [
        {"source":"d1","target":"d2","source_port":"right","target_port":"left","flow":"control"},
        {"source":"d2","target":"d3","source_port":"right","target_port":"left","flow":"control"},
        {"source":"d3","target":"d4","source_port":"right","target_port":"left","flow":"control"},
        {"x1":480,"y1":290,"x2":480,"y2":340,"label":"导出配置与数据","flow":"data"},
        {"source":"e1","target":"e2","source_port":"right","target_port":"left","flow":"control"},
        {"source":"e2","target":"e3","source_port":"right","target_port":"left","flow":"control"},
    ],
})

# =====================================================================
# 7. 组合 6：极简全栈 MVP
# =====================================================================
save("07_combo6_mvp", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 580,
    "title": "组合 6：极简全栈 MVP",
    "subtitle": "OpenAI 生态闭环",
    "containers": [
        {"x":40,"y":80,"width":880,"height":460,"label":"","stroke":"#e5e7eb","fill":"none","rx":12}
    ],
    "nodes": [
        {"id":"next","kind":"rect","x":300,"y":110,"width":360,"height":70,"label":"Next.js + Vercel AI SDK","sublabel":"useChat + streamText + useObject / Server Action","type_label":"前端","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"agent","kind":"rect","x":300,"y":230,"width":360,"height":90,"label":"OpenAI Agents SDK + Zod","sublabel":"Agent + function_tool + handoffs / File Search / Web Search / Code Interpreter","type_label":"后端","fill":"#f0fdf4","stroke":"#bbf7d0"},
        {"id":"kv","kind":"rect","x":300,"y":370,"width":360,"height":60,"label":"Vercel KV / Upstash Redis","sublabel":"简单会话状态，无复杂持久化","type_label":"存储","fill":"#f8fafc","stroke":"#94a3b8"},
    ],
    "arrows": [
        {"source":"next","target":"agent","source_port":"bottom","target_port":"top","label":"Server Action","flow":"control"},
        {"source":"agent","target":"kv","source_port":"bottom","target_port":"top","label":"会话状态","flow":"data"},
    ],
})

# =====================================================================
# 8. 五层记忆架构
# =====================================================================
save("08_memory", {
    "template_type": "architecture",
    "style": 1,
    "width": 960,
    "height": 640,
    "title": "工程模式：分层记忆架构",
    "subtitle": "五层记忆架构",
    "nodes": [
        {"id":"l1","kind":"rect","x":180,"y":110,"width":600,"height":70,"label":"系统提示 + 当前任务指令","sublabel":"System Prompt + Task Context / 始终保留，最高优先级","type_label":"第一层","fill":"#fef2f2","stroke":"#fecaca"},
        {"id":"l2","kind":"rect","x":180,"y":210,"width":600,"height":70,"label":"工作记忆（Working Memory）","sublabel":"最近 3-5 轮对话 + 关键中间结果 / Sliding Window","type_label":"第二层","fill":"#fff7ed","stroke":"#fed7aa"},
        {"id":"l3","kind":"rect","x":180,"y":310,"width":600,"height":70,"label":"摘要记忆（Summary Memory）","sublabel":"早期对话的压缩摘要 / Condensed History","type_label":"第三层","fill":"#fefce8","stroke":"#fde047"},
        {"id":"l4","kind":"rect","x":180,"y":410,"width":600,"height":70,"label":"检索记忆（Retrieval Memory）","sublabel":"从向量库实时召回的相关片段 / RAG / Vector Search","type_label":"第四层","fill":"#eff6ff","stroke":"#bfdbfe"},
        {"id":"l5","kind":"rect","x":180,"y":510,"width":600,"height":70,"label":"事实记忆（Fact Memory）","sublabel":"结构化提取的用户偏好、业务规则 / Key-Value / Graph DB","type_label":"第五层","fill":"#f0fdf4","stroke":"#bbf7d0"},
    ],
    "arrows": [
        {"source":"l1","target":"l2","source_port":"bottom","target_port":"top","flow":"data"},
        {"source":"l2","target":"l3","source_port":"bottom","target_port":"top","flow":"data"},
        {"source":"l3","target":"l4","source_port":"bottom","target_port":"top","flow":"data"},
        {"source":"l4","target":"l5","source_port":"bottom","target_port":"top","flow":"data"},
    ],
})

# =====================================================================
# 9. 按复杂度与阶段选型 (2D matrix)
# =====================================================================
save("09_matrix", {
    "template_type": "comparison",
    "style": 1,
    "width": 960,
    "height": 600,
    "title": "按复杂度与阶段选型",
    "subtitle": "复杂度 × 团队规模/工程成熟度",
    "nodes": [
        {"id":"c1","kind":"rect","x":120,"y":130,"width":220,"height":70,"label":"语义内核编排","sublabel":"Semantic Kernel","fill":"#f0fdf4","stroke":"#bbf7d0","flat":True},
        {"id":"c2","kind":"rect","x":380,"y":130,"width":220,"height":70,"label":"多 Agent 状态机","sublabel":"LangGraph + Letta","fill":"#f0fdf4","stroke":"#bbf7d0","flat":True},
        {"id":"c3","kind":"rect","x":640,"y":130,"width":220,"height":70,"label":"企业级 Copilot","sublabel":"Semantic Kernel + Azure","fill":"#f0fdf4","stroke":"#bbf7d0","flat":True},
        {"id":"b1","kind":"rect","x":120,"y":240,"width":220,"height":70,"label":"检索增强 Agent","sublabel":"LlamaIndex + PydanticAI","fill":"#eff6ff","stroke":"#bfdbfe","flat":True},
        {"id":"b2","kind":"rect","x":380,"y":240,"width":220,"height":70,"label":"内容工厂","sublabel":"CrewAI + Dify","fill":"#eff6ff","stroke":"#bfdbfe","flat":True},
        {"id":"b3","kind":"rect","x":640,"y":240,"width":220,"height":70,"label":"复杂 RAG","sublabel":"LlamaIndex + LangGraph","fill":"#eff6ff","stroke":"#bfdbfe","flat":True},
        {"id":"a1","kind":"rect","x":120,"y":350,"width":220,"height":70,"label":"单轮 RAG","sublabel":"LlamaIndex QueryEngine","fill":"#f8fafc","stroke":"#e2e8f0","flat":True},
        {"id":"a2","kind":"rect","x":380,"y":350,"width":220,"height":70,"label":"简单 Agent","sublabel":"OpenAI Agents SDK","fill":"#f8fafc","stroke":"#e2e8f0","flat":True},
        {"id":"a3","kind":"rect","x":640,"y":350,"width":220,"height":70,"label":"客服机器人","sublabel":"Dify / OpenAI Agents SDK","fill":"#f8fafc","stroke":"#e2e8f0","flat":True},
    ],
    "arrows": [
        {"x1":80,"y1":480,"x2":880,"y2":480,"label":"团队规模 / 工程成熟度 →","flow":"neutral"},
        {"x1":80,"y1":480,"x2":80,"y2":100,"label":"复杂度 ↑","flow":"neutral"},
    ],
})

print("\nAll 9 diagrams generated.")
