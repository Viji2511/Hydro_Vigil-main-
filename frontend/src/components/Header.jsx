import { useMemo } from "react";
import { motion } from "framer-motion";
import { FaWater } from "react-icons/fa";
import StatusBadge from "./StatusBadge";

function formatTimestamp(timestamp) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(timestamp);
}

const TABS = [
  { id: "home", label: "Home" },
  { id: "dashboard", label: "Command Center" },
  { id: "guide", label: "System Guide" },
];

export default function Header({ activeTab, setActiveTab, systemStatus, timestamp, userRole, onAssignRole }) {
  const formattedTime = useMemo(() => formatTimestamp(timestamp), [timestamp]);

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-bg/88 px-4 backdrop-blur-lg sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1600px] flex-col md:flex-row items-center justify-between gap-4 py-4">
        {/* Left Side: Brand Logo */}
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-textPrimary sm:text-2xl cursor-pointer" onClick={() => setActiveTab("home")}>
            <span className="rounded-lg border border-accent/40 bg-accent/12 p-1.5 text-accent">
              <FaWater className="h-4 w-4" />
            </span>
            HydroVigil
            <span className="ml-2 text-sm font-medium uppercase tracking-[0.18em] text-accent/90 sm:text-xs">
              National Cyber Command
            </span>
          </h1>
          <p className="mt-1 text-xs tracking-[0.08em] text-textSecondary sm:text-sm">
            AI-Powered Threat Analysis & Digital Twin Visualization
          </p>
        </div>

        {/* Center: Sliding Tab Navigation Bar */}
        <nav className="flex items-center gap-1 overflow-x-auto scrollbar-none rounded-xl bg-white/[0.03] p-1 border border-white/5 max-w-full">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  if (tab.id === "dashboard" && !userRole) {
                    onAssignRole("operator");
                  }
                  setActiveTab(tab.id);
                }}
                className={`relative px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] rounded-lg transition-colors duration-300 whitespace-nowrap ${
                  isActive ? "text-bg font-bold" : "text-textSecondary hover:text-textPrimary"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavTab"
                    className="absolute inset-0 bg-accent rounded-lg"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Side: Clock & Role Badge */}
        <motion.div
          className="flex flex-col items-end gap-2 sm:flex-row sm:items-center sm:gap-4"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.28 }}
        >
          {activeTab === "dashboard" && userRole ? (
            <div className="flex items-center gap-3">
              <div className="rounded-lg border border-white/10 bg-card/40 px-2 py-1 text-center">
                <span className="text-[9px] uppercase tracking-wider text-textSecondary block">Cleared Role</span>
                <span className="text-[10px] font-mono text-accent font-bold uppercase">{userRole}</span>
              </div>
              <StatusBadge status={systemStatus} />
            </div>
          ) : (
            <div className="rounded-xl border border-white/10 bg-card/72 px-3 py-2 text-right shadow-panel">
              <p className="text-[10px] uppercase tracking-[0.2em] text-textSecondary">Live Clock</p>
              <p className="mt-1 font-mono text-xs text-textPrimary sm:text-sm">{formattedTime}</p>
            </div>
          )}
        </motion.div>
      </div>
    </header>
  );
}
