import { AnimatePresence, motion } from "framer-motion";

const THREAT_STYLE = {
  Low: "bg-accent/15 text-accent ring-accent/40",
  Guarded: "bg-warning/15 text-warning ring-warning/40",
  High: "bg-critical/15 text-critical ring-critical/40",
};

export default function AIExplanation({
  confidence,
  headline,
  summary,
  signals,
  recommendations,
  threatLevel,
  expanded,
  zScores,
  affectedSensor,
  detectionReason,
  fallbackActivated,
}) {
  const threatClass = THREAT_STYLE[threatLevel] ?? THREAT_STYLE.Low;

  return (
    <section className="glass-panel rounded-xl p-4 shadow-panel sm:p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-textPrimary">AI Threat Briefing</h2>
        <div className="flex items-center gap-2">
          {fallbackActivated ? (
            <span className="animate-pulse rounded-md bg-warning/20 border border-warning/40 px-2 py-0.5 text-[9px] font-bold uppercase text-warning">
              LSTM Fallback Active
            </span>
          ) : (
            <span className="rounded-md bg-accent/20 border border-accent/40 px-2 py-0.5 text-[9px] font-bold uppercase text-accent">
              Transformer Active
            </span>
          )}
          <p className="text-xs uppercase tracking-[0.14em] text-textSecondary">Inference Core v4.8</p>
        </div>
      </div>

      <motion.div
        className="rounded-xl border border-white/10 bg-card/72 p-4"
        animate={{ boxShadow: expanded || threatLevel === "High" ? "0 0 0 1px rgba(220,38,38,0.22)" : "0 0 0 1px rgba(0,0,0,0)" }}
        transition={{ duration: 0.34, ease: "easeOut" }}
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-sm font-semibold text-textPrimary">{headline}</p>
          <span className={`inline-flex rounded-lg px-2 py-1 text-xs font-semibold uppercase ring-1 ${threatClass}`}>
            Threat Level: {threatLevel}
          </span>
        </div>
        
        {/* Natural Language Reasoning Reason */}
        <p className="mt-2 text-sm leading-6 text-textSecondary">
          {detectionReason ?? summary}
        </p>

        {/* Real-time confidence bar */}
        <div className="mt-4">
          <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.12em]">
            <span className="text-textSecondary">Confidence</span>
            <span className="font-semibold text-textPrimary">{confidence}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-bg/80">
            <motion.div
              className="h-2 rounded-full bg-accent"
              initial={false}
              animate={{ width: `${confidence}%` }}
              transition={{ duration: 0.34, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Explainability Z-Scores Metrics Segment */}
        {zScores ? (
          <div className="mt-4 border-t border-white/10 pt-3">
            <p className="text-[10px] uppercase tracking-[0.12em] text-textSecondary mb-2 font-mono">Real-time Attribution Z-Scores</p>
            <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
              <div className="rounded border border-white/5 bg-white/[0.02] p-1.5">
                <span className="block text-[9px] text-textSecondary uppercase">Reconstruction</span>
                <span className={`font-bold ${Math.abs(zScores.reconstruction) > 2.0 ? "text-critical" : "text-textPrimary"}`}>
                  {zScores.reconstruction > 0 ? "+" : ""}{zScores.reconstruction.toFixed(2)}
                </span>
              </div>
              <div className="rounded border border-white/5 bg-white/[0.02] p-1.5">
                <span className="block text-[9px] text-textSecondary uppercase">Temporal (A)</span>
                <span className={`font-bold ${Math.abs(zScores.attention) > 2.0 ? "text-critical" : "text-textPrimary"}`}>
                  {zScores.attention > 0 ? "+" : ""}{zScores.attention.toFixed(2)}
                </span>
              </div>
              <div className="rounded border border-white/5 bg-white/[0.02] p-1.5">
                <span className="block text-[9px] text-textSecondary uppercase">Entropy (E)</span>
                <span className={`font-bold ${Math.abs(zScores.entropy) > 2.0 ? "text-critical" : "text-textPrimary"}`}>
                  {zScores.entropy > 0 ? "+" : ""}{zScores.entropy.toFixed(2)}
                </span>
              </div>
            </div>
            {affectedSensor && affectedSensor !== "Unknown" ? (
              <p className="mt-2 text-[10px] text-textSecondary">
                Most affected anomaly channel: <span className="font-mono font-bold text-accent">{affectedSensor}</span>
              </p>
            ) : null}
          </div>
        ) : null}

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-[0.12em] text-textSecondary">Indicators</p>
            <ul className="mt-2 space-y-2 text-sm text-textPrimary">
              {signals.map((signal) => (
                <li key={signal} className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-xs">
                  {signal}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.12em] text-textSecondary">Recommended Actions</p>
            <ul className="mt-2 space-y-2 text-sm text-textPrimary">
              {recommendations.map((recommendation) => (
                <li key={recommendation} className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-xs">
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
