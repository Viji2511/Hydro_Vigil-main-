import { motion } from "framer-motion";

const NODES = [
  { id: "P-11", label: "Inlet Pump", x: 42, y: 42, type: "pump" },
  { id: "W-05", label: "Pre-Treatment Tank", x: 76, y: 122, type: "tank" },
  { id: "P-17", label: "Control Valve", x: 130, y: 64, type: "valve" },
  { id: "P-23", label: "Pressure Monitor", x: 192, y: 78, type: "sensor" },
  { id: "GW-A2", label: "Discharge Gateway", x: 180, y: 132, type: "gateway" },
];

export default function NetworkMap({ simulationPhase, targetNodeId = "P-23", telemetry, affectedSensor }) {
  const attackMode = simulationPhase === "phase2" || simulationPhase === "phase3";
  const suspiciousMode = simulationPhase === "phase1";
  
  // Use real telemetry if available, else fall back to sensible defaults
  const levelVal = telemetry ? Number(telemetry.level) : 50;
  const flowVal = telemetry ? Number(telemetry.flow) : 12.5;
  const pressureVal = telemetry ? Number(telemetry.pressure) : 45.2;

  // Flow animation speed based on state
  const animDuration = attackMode ? "0.4s" : suspiciousMode ? "0.8s" : "1.5s";
  const pipeColor = attackMode ? "#EF4444" : suspiciousMode ? "#F59E0B" : "#3B82F6";

  return (
    <section className="glass-panel rounded-xl p-4 shadow-panel sm:p-5">
      <style>{`
        @keyframes flow-dash {
          to {
            stroke-dashoffset: -20;
          }
        }
        .scada-pipe-flow {
          stroke-dasharray: 8 6;
          animation: flow-dash var(--flow-speed, 1.2s) linear infinite;
        }
      `}</style>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-textPrimary">SCADA Digital Twin</h2>
        <span className="text-xs uppercase tracking-[0.12em] text-accent">Active Grid Schema</span>
      </div>

      <div className="rounded-xl border border-white/10 bg-card/72 p-3 relative overflow-hidden" style={{ minHeight: "220px" }}>
        <svg viewBox="0 0 240 180" className="h-full w-full">
          {/* Animated Pipes (Flow Lines) */}
          
          {/* Pipe 1: Inlet Pump (P-11) to Pre-Treatment Tank (W-05) */}
          <path
            d="M 42 42 L 42 122 L 76 122"
            fill="none"
            stroke={pipeColor}
            strokeWidth="3.2"
            opacity="0.32"
          />
          <path
            d="M 42 42 L 42 122 L 76 122"
            fill="none"
            stroke={pipeColor}
            strokeWidth="2"
            className="scada-pipe-flow"
            style={{ "--flow-speed": animDuration }}
          />

          {/* Pipe 2: Tank (W-05) to Valve (P-17) */}
          <path
            d="M 94 122 L 130 122 L 130 64"
            fill="none"
            stroke={pipeColor}
            strokeWidth="3.2"
            opacity="0.32"
          />
          <path
            d="M 94 122 L 130 122 L 130 64"
            fill="none"
            stroke={pipeColor}
            strokeWidth="2"
            className="scada-pipe-flow"
            style={{ "--flow-speed": animDuration }}
          />

          {/* Pipe 3: Valve (P-17) to Pressure Monitor (P-23) */}
          <path
            d="M 130 64 L 192 64 L 192 78"
            fill="none"
            stroke={pipeColor}
            strokeWidth="3.2"
            opacity="0.32"
          />
          <path
            d="M 130 64 L 192 64 L 192 78"
            fill="none"
            stroke={pipeColor}
            strokeWidth="2"
            className="scada-pipe-flow"
            style={{ "--flow-speed": animDuration }}
          />

          {/* Pipe 4: Pressure Monitor (P-23) to Discharge Gateway (GW-A2) */}
          <path
            d="M 192 78 L 192 132 L 180 132"
            fill="none"
            stroke={pipeColor}
            strokeWidth="3.2"
            opacity="0.32"
          />
          <path
            d="M 192 78 L 192 132 L 180 132"
            fill="none"
            stroke={pipeColor}
            strokeWidth="2"
            className="scada-pipe-flow"
            style={{ "--flow-speed": animDuration }}
          />

          {/* Cyber attack packet simulation vector */}
          {attackMode ? (
            <motion.path
              d="M 12 42 L 42 42 L 42 122"
              fill="none"
              stroke="#EF4444"
              strokeWidth="2"
              strokeDasharray="4 4"
              animate={{ strokeDashoffset: [0, -20] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: "linear" }}
            />
          ) : null}

          {/* SCADA Hardware Components Rendering */}
          
          {/* 1. Pre-Treatment Tank W-05 */}
          <g transform="translate(62, 102)">
            {/* Outer tank frame */}
            <rect x="0" y="0" width="28" height="34" fill="#0f172a" stroke="#475569" strokeWidth="1.5" rx="3" />
            {/* Dynamic Water fill */}
            <motion.rect 
              x="1.5" 
              y={32.5 - (31 * levelVal) / 100} 
              width="25" 
              height={(31 * levelVal) / 100} 
              fill={attackMode && (targetNodeId === "W-05" || affectedSensor === "LIT101") ? "rgba(239, 68, 68, 0.72)" : "rgba(59, 130, 246, 0.75)"}
              rx="1" 
            />
            {/* Grid level marker lines */}
            <line x1="0" y1="10" x2="6" y2="10" stroke="#334155" strokeWidth="1" />
            <line x1="0" y1="17" x2="10" y2="17" stroke="#334155" strokeWidth="1" />
            <line x1="0" y1="24" x2="6" y2="24" stroke="#334155" strokeWidth="1" />
            
            <text x="32" y="14" fill="#E2E8F0" fontSize="8" fontWeight="bold">W-05</text>
            <text x="32" y="24" fill="#94A3B8" fontSize="7">{levelVal.toFixed(1)}%</text>
          </g>

          {/* 2. Inlet Pump P-11 */}
          <g transform="translate(42, 42)">
            <motion.circle
              cx="0"
              cy="0"
              r="10"
              fill="#1E293B"
              stroke={targetNodeId === "P-11" && (attackMode || suspiciousMode) ? pipeColor : "#475569"}
              strokeWidth="1.5"
              style={{ filter: targetNodeId === "P-11" && attackMode ? "drop-shadow(0 0 8px #EF4444)" : "none" }}
            />
            {/* Spinning pump rotator blades */}
            <motion.path
              d="M -6 0 L 6 0 M 0 -6 L 0 6"
              stroke="#64748B"
              strokeWidth="1.5"
              animate={{ rotate: 360 }}
              transition={{ duration: attackMode ? 0.35 : 1.2, repeat: Infinity, ease: "linear" }}
            />
            <text x="14" y="3" fill="#E2E8F0" fontSize="8" fontWeight="bold">P-11</text>
          </g>

          {/* 3. Control Valve P-17 */}
          <g transform="translate(130, 64)">
            {/* Valve butterfly shape */}
            <polygon 
              points="-8,-6 -8,6 8,-6 8,6" 
              fill={targetNodeId === "P-17" && attackMode ? "#EF4444" : "#1E293B"}
              stroke="#475569" 
              strokeWidth="1.2" 
            />
            <circle cx="0" cy="0" r="2.5" fill="#64748B" />
            <text x="12" y="4" fill="#E2E8F0" fontSize="8" fontWeight="bold">P-17</text>
          </g>

          {/* 4. Pressure Monitor P-23 */}
          <g transform="translate(192, 78)">
            <rect 
              x="-12" 
              y="-8" 
              width="24" 
              height="16" 
              fill="#1E293B" 
              stroke={targetNodeId === "P-23" && (attackMode || suspiciousMode) ? pipeColor : "#475569"} 
              strokeWidth="1.5" 
              rx="2"
            />
            <text x="0" y="2" fill={targetNodeId === "P-23" && attackMode ? "#F87171" : "#38BDF8"} fontSize="8" fontWeight="bold" textAnchor="middle">
              {pressureVal.toFixed(0)}
            </text>
            <text x="0" y="20" fill="#E2E8F0" fontSize="8" fontWeight="bold" textAnchor="middle">P-23</text>
          </g>

          {/* 5. Discharge Gateway GW-A2 */}
          <g transform="translate(170, 132)">
            <polygon 
              points="-6,-8 6,-8 10,8 -10,8" 
              fill="#0F172A" 
              stroke={targetNodeId === "GW-A2" && (attackMode || suspiciousMode) ? pipeColor : "#475569"} 
              strokeWidth="1.5" 
            />
            <text x="14" y="2" fill="#E2E8F0" fontSize="8" fontWeight="bold">GW-A2</text>
            <text x="14" y="10" fill="#94A3B8" fontSize="7">{flowVal.toFixed(1)} m³/h</text>
          </g>

          {/* Glowing Anomaly Warning Overlays */}
          {attackMode ? (
            <motion.circle
              cx={NODES.find(n => n.id === targetNodeId)?.x ?? 192}
              cy={NODES.find(n => n.id === targetNodeId)?.y ?? 78}
              r="22"
              fill="none"
              stroke="#EF4444"
              strokeWidth="1.5"
              strokeDasharray="4 3"
              animate={{ rotate: 360, scale: [1, 1.15, 1] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
          ) : null}
        </svg>

        {/* Dynamic Twin Status overlay */}
        <div className="absolute bottom-2 left-2 right-2 flex justify-between items-center bg-slate-900/80 px-2 py-1 rounded border border-white/5 text-[10px] font-mono">
          <span className="text-textSecondary">GRID FLOW DATA</span>
          <span className={attackMode ? "text-critical font-bold animate-pulse" : "text-accent"}>
            {attackMode ? "ANOMALY PRESSURE DETECTED" : "NOMINAL REGULATION CASCADE"}
          </span>
        </div>
      </div>
    </section>
  );
}
