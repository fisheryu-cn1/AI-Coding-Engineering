# llm_app_diagrams 大模型应用架构图目录

本目录收集大模型应用架构相关的 SVG 图解与配套说明文档。

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `llm_app_architecture_guide.html` | 《大模型应用架构选型参考方案》完整 HTML 说明文档，内嵌 9 张架构图 |
| `replace_diagrams.py` | 将 HTML 中 ASCII 图表块替换为 SVG `<img>` 引用的脚本 |
| `01_landscape.svg` | 大模型应用全景图 |
| `02_combo1_rag.svg` | 组合方案 1：RAG 架构 |
| `03_combo2_data.svg` | 组合方案 2：数据应用架构 |
| `04_combo3_crew.svg` | 组合方案 3：Crew / 多 Agent 架构 |
| `05_combo4_dotnet.svg` | 组合方案 4：.NET 生态架构 |
| `06_combo5_migrate.svg` | 组合方案 5：迁移场景架构 |
| `07_combo6_mvp.svg` | 组合方案 6：MVP 架构 |
| `08_memory.svg` | 记忆系统架构 |
| `09_matrix.svg` | 选型矩阵 |

---

## 使用建议

- **阅读完整方案**：用浏览器打开 `llm_app_architecture_guide.html`。
- **单独使用图片**：直接引用 `01_landscape.svg` ~ `09_matrix.svg`。
- **重新生成图表**：运行 `generate_all.py`（SVG 已生成，通常无需重复执行）。
- **重新替换 HTML 中的 ASCII 图**：运行 `replace_diagrams.py`。
