# 评审任务：commit {{commit}}

使用 code-review skill 的五步 SOP 评审提交 {{commit}} 的父状态（即评审 `git show {{commit}}` 所示修复针对的代码）。

要求：
1. 先 `git show {{commit}} --stat` 建立变更地图，再读完整 diff 与相关文件上下文；
2. 逐维度检查（正确性/状态生命周期/契约一致性/变更登记/登记真实性/幂等/并发/防御性）；
3. 意见卡写入 `reviews/{{date}}-{{commit_short}}.md`，遵守红线（每条意见带溯源）；
4. 结束时输出一行摘要：意见数（P0/P1/P2/P3）+ 已检查维度数。
