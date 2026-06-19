# ContextEngineering 文献目录

本目录收集上下文工程（Context Engineering）相关核心论文，按阅读报告《上下文工程文献综述》中的编号组织。另有奠基性综述与扩展参考资料单独列出。

## 文件命名规则

```
[序号]-[作者姓氏]-[简短标题].[pdf|html|txt]
```

- **序号**：与阅读报告中的文献编号一一对应，便于快速定位。
- **作者姓氏**：主要作者或第一作者的姓氏。
- **简短标题**：论文核心概念的关键词，使用下划线 `_` 代替空格。

## 目录结构

```
references/ContextEngineering/
├── 01-Paulsen-Context_Is_What_You_Need.pdf
├── 02-Liu-Lost_in_the_Middle.pdf
├── ...
├── 17-Vogel-Codebase_Memory.pdf
├── 18-Mei-Survey_of_Context_Engineering.pdf   # 奠基性综述：首次将 Context Engineering 作为正式学科提出
├── 19-Zhang-Memory_in_Large_Language.pdf      # 扩展综述：LLM 记忆机制、评估与治理
├── 06-Hong-Context_Rot.html           # 仅有一篇 HTML 研究报告
├── 06-Hong-Context_Rot_files/         # HTML 引用的静态资源
├── 阅读报告_上下文工程文献综述.md      # 完整综述与横向比较
├── 上下文工程_核心参考资料清单.md      # 领域关键论文、工业实践、框架定义与工具资源索引
├── README.md                          # 本文件
└── notes/                             # PDF 的文本摘录/笔记
    ├── 01-Paulsen-Context_Is_What_You_Need.txt
    ├── ...
    └── 11-Mishra-Harness_Native_Software_Engineering.txt
```

## 分组速查

| 组 | 主题 | 编号 |
|---|---|---|
| A 组 | 长上下文能力的极限与失效机制 | 01–06 |
| B 组 | 上下文工程的基础设施化 | 07–11 |
| C 组 | 代码特异性上下文技术 | 12–17 |
| D 组 | 奠基性与扩展综述 | 18–19 |

## 使用建议

- 想快速了解某篇论文：先看 `notes/` 下对应编号的 txt 摘要。
- 想系统阅读：按阅读报告中的 A→B→C 顺序阅读 PDF/HTML。
- 找代码图谱/AI Coding 相关：直接查看 C 组（12–17）。
