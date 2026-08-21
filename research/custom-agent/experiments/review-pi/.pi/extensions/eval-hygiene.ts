// eval-hygiene v0.1 —— 评审隔离的薄 enforcement 层（notes/08 §2.3 补1-5 设计）
// 默认 observe（只记日志）；enforce 模式经 .pi/eval-hygiene.config.json 开启。
// 职责（物理隔离约定之上的残余通道）：①禁读定稿报告目录；②git 命令形态（定位仅 diff --stat）；③框架会话路径。
// 会话产物自许可：本会话 write 工具创建的文件自动放行（补3 备选机制，临时目录不可用时）。
export default function (pi: any) {
  const cfgPath = ".pi/eval-hygiene.config.json";
  let cfg: any = { mode: "observe", deny_globs: ["reviews-final/**"], framework_deny: ["~/.pi/agent/sessions"] };
  try { cfg = { ...cfg, ...JSON.parse(Deno.readTextFileSync(cfgPath)) }; } catch { /* 默认配置 */ }

  const sessionArtifacts = new Set<string>(); // 会话产物（write 目击创建）
  const log = (kind: string, msg: string) => console.error(`[eval-hygiene:${cfg.mode}:${kind}] ${msg}`);

  const hitGlob = (p: string) => cfg.deny_globs.some((g: string) =>
    p.includes(g.replace("/**", "")) && (g.endsWith("/**") ? true : p === g));

  pi.on("tool_call", async (event: any, ctx: any) => {
    const name = event.toolName as string;
    const input = event.input as any;

    // write 目击创建 → 会话产物集
    if (name === "write" && input?.path) sessionArtifacts.add(String(input.path));

    const forbid = (reason: string) => {
      log("BLOCK", `${name}: ${reason}`);
      return cfg.mode === "enforce" ? { block: true, reason } : undefined;
    };

    if (name === "read" && input?.path) {
      const p = String(input.path);
      if (sessionArtifacts.has(p)) return; // 会话产物自许可
      if (hitGlob(p)) return forbid(`禁读定稿目录: ${p}`);
      if (cfg.framework_deny.some((d: string) => p.includes(d.replace("~", ctx?.home ?? "~"))))
        return forbid("框架会话路径禁读");
    }

    if (name === "bash" && input?.command) {
      const c = String(input.command);
      // git 形态：定位仅放行 diff <X>^ <X> --stat；含 $EVAL_FIX_HASH 的其他 git 命令拦截
      const fix = cfg.fix_hash ?? Deno.env.get("EVAL_FIX_HASH");
      if (fix && /git\s+(show|log|diff)/.test(c) && c.includes(fix)) {
        const isLocate = new RegExp(`git\s+diff\s+\S*${fix}\^?\s*${fix}\s+--stat`).test(c);
        if (!isLocate) return forbid(`git 命令含修复提交 ${fix}（定位仅限 diff --stat 形态）`);
      }
      if (hitGlob(c) && !/git\s+(diff|show)/.test(c)) return forbid("bash 访问禁读目录");
    }
  });

  pi.on("tool_result", async (event: any) => {
    // 观察遥测：结果中的可疑标记（enforce 不处理——内容层归负载扫描/写入扫描）
    const s = JSON.stringify(event?.result ?? "");
    if (cfg.markers && cfg.markers.some((m: string) => s.includes(m))) log("MARKER", "工具结果命中观察标记");
  });

  log("INIT", `config=${cfgPath} mode=${cfg.mode} fix_hash=${cfg.fix_hash ?? "(env)"}`);
}
