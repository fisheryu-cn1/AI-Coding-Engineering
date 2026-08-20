/**
 * review-guard：场景一（review-pi）的只读守卫扩展。
 * 已按 pi 0.84.2 实版 docs/extensions.md 校准（2026-08-17 第 2 场）：
 *  - tool_call 事件：event.toolName / event.input（可变）；阻断用返回值 { block: true, reason }。
 *  - 写工具 input：write = { path, content }，edit = { path, old_string, new_string }。
 *
 * 职责：
 * 1. write/edit 仅允许目标 `reviews/`（意见卡输出目录）；
 * 2. bash 阻止破坏性命令（rm -rf / git push / git reset --hard / git checkout -- / git clean）。
 *
 * 迁移参照（D1-S5）：DSH 等价形态 = ctx.tools 作用域限制 + ctx.fs provider / fs 事件；
 * "写路径约束 + 危险命令黑名单"语义可平移，接缝模型不同。
 */
export default function (pi: any) {
  const ALLOWED_PREFIX = "reviews/";
  // 不 import isToolCallEventType（避免扩展加载时的包解析依赖），直接按 toolName 字符串分派——
  // 事件字段名以 docs §tool_call 为准。
  const BAD_BASH = /\b(rm\s+(-\w*\s+)*-rf|git\s+push\b|git\s+reset\s+--hard\b|git\s+checkout\s+--\b|git\s+clean\b|git\s+branch\s+-D\b)/;

  pi.on("tool_call", async (event: any) => {
    const tool: string = event?.toolName ?? "";
    const input: any = event?.input ?? {};

    if (tool === "write" || tool === "edit") {
      const raw = String(input?.path ?? "");
      const norm = raw.replace(/\\/g, "/");
      const rel = norm.startsWith("./") ? norm.slice(2) : norm;
      if (!rel.startsWith(ALLOWED_PREFIX)) {
        return {
          block: true,
          reason: `[review-guard] 评审模式只允许写 ${ALLOWED_PREFIX}（意见卡输出目录），拒绝：${raw || "(空路径)"}`,
        };
      }
    }

    if (tool === "bash") {
      const cmd = String(input?.command ?? "");
      if (BAD_BASH.test(cmd)) {
        return {
          block: true,
          reason: `[review-guard] 评审模式禁止破坏性命令：${cmd.slice(0, 120)}`,
        };
      }
    }
  });
}
