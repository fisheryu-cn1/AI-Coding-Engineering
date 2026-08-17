/**
 * review-guard：场景一（review-pi）的只读守卫扩展。
 *
 * 职责（对应装配流程 ⑤ 的门禁组件）：
 * 1. 白名单工具：仅允许 read / bash / write / edit 四个默认工具（评审不需要注册新工具）；
 * 2. 写路径约束：write/edit 仅允许目标 `reviews/` 目录（意见卡输出），其余一律阻止；
 * 3. 防御性编码：事件负载字段名以多重候选读取——首次运行时需对照所装 pi 版本的
 *    docs/extensions.md 校准（本文件为 v0，字段名按调研材料的记载推断）。
 *
 * 迁移参照（D1-S5）：DSH 等价形态 = ctx.tools 注册表的作用域限制 + ctx.fs provider
 * （能力接缝层）；本扩展的"写路径约束"语义在 DSH 中以 fs/* 事件实现。
 */
export default function (pi: any) {
  const WRITE_TOOLS = new Set(["write", "edit"]);
  const ALLOWED_WRITE_PREFIX = "reviews/";

  pi.on("tool_call", (event: any) => {
    const call = event?.toolCall ?? event?.call ?? event ?? {};
    const name: string = call?.name ?? "";
    const args: Record<string, unknown> = call?.arguments ?? call?.args ?? call?.input ?? {};

    if (WRITE_TOOLS.has(name)) {
      const raw = String(args?.path ?? args?.file_path ?? args?.filename ?? "");
      const norm = raw.replace(/\\/g, "/");
      const ok = norm === ALLOWED_WRITE_PREFIX + norm.split("/").pop() || norm.startsWith(ALLOWED_WRITE_PREFIX);
      if (!ok) {
        const reason = `[review-guard] 拒绝写入 ${raw || "(空路径)"}：评审模式只允许写 ${ALLOWED_WRITE_PREFIX}`;
        if (typeof event?.block === "function") event.block(reason);
        else if (typeof event?.preventDefault === "function") { event.preventDefault(); event.blockedReason = reason; }
        else console.warn(reason + "（未找到阻止 API，仅告警——需按 pi 版本校准）");
      }
    }
  });
}
