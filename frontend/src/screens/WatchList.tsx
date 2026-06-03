import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { watchesApi, type Watch } from "../api/watches";
import { alertsApi, type Alert } from "../api/alerts";
import type { ReactNode } from "react";

const categoryConfig: Record<string, { label: string; icon: ReactNode }> = {
  housing: {
    label: "Housing",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z" />
        <path d="M9 21V12h6v9" />
      </svg>
    ),
  },
  opportunity: {
    label: "Opportunity",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <path d="M22 10v6M2 10l10-5 10 5-10 5-10-5z" />
        <path d="M6 12v5c3.33 2 8.67 2 12 0v-5" />
      </svg>
    ),
  },
  recruiting: {
    label: "Recruiting",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <rect x="2" y="7" width="20" height="14" rx="2" />
        <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
        <line x1="12" y1="12" x2="12" y2="16" />
        <line x1="10" y1="14" x2="14" y2="14" />
      </svg>
    ),
  },
  events: {
    label: "Events",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <rect x="3" y="4" width="18" height="18" rx="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
};

function WatchCard({
  watch,
  alertCount,
  onScan,
  scanning,
}: {
  watch: Watch;
  alertCount: number;
  onScan: (id: string) => void;
  scanning: boolean;
}) {
  const navigate = useNavigate();
  const config = categoryConfig[watch.category] ?? categoryConfig.housing;

  return (
    <div
      className="bg-white rounded-2xl p-4 shadow-sm border border-[#e8eaf0] active:opacity-80 transition-opacity"
      onClick={() => navigate("/alerts")}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-11 h-11 rounded-xl bg-[#f0f2f8] flex items-center justify-center shrink-0">
            {config.icon}
          </div>
          <div>
            <p className="font-semibold text-[#0f1230] text-sm">
              {config.label}
            </p>
            <p className="text-[#6b7280] text-xs mt-0.5 truncate max-w-45">
              {watch.source_url.replace(/https?:\/\//, "")}
            </p>
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onScan(watch.watch_id);
          }}
          disabled={scanning}
          className="shrink-0 text-xs font-medium text-[#1a1f4e] border border-[#1a1f4e] rounded-lg px-3 py-1.5 disabled:opacity-40 active:bg-[#1a1f4e] active:text-white transition-colors"
        >
          {scanning ? (
            <span className="flex items-center gap-1">
              <svg
                className="animate-spin"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              Scanning
            </span>
          ) : (
            "Scan now"
          )}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5 mt-3">
        {Object.entries(watch.criteria)
          .slice(0, 3)
          .map(([key, val]) => (
            <span
              key={key}
              className="text-xs bg-[#f5f6fa] text-[#6b7280] px-2.5 py-1 rounded-full border border-[#e8eaf0]"
            >
              {String(val)}
            </span>
          ))}
      </div>

      {alertCount > 0 ? (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#f0f2f8]">
          <span className="w-5 h-5 rounded-full bg-[#10b981] text-white text-[10px] font-bold flex items-center justify-center">
            {alertCount}
          </span>
          <span className="text-[#10b981] text-xs font-medium">
            New match{alertCount > 1 ? "es" : ""}
          </span>
          <svg
            className="ml-auto"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
      ) : (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#f0f2f8]">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#9ca3af"
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4l3 3" />
          </svg>
          <span className="text-[#9ca3af] text-xs">No new matches</span>
        </div>
      )}
    </div>
  );
}

export default function WatchList() {
  const navigate = useNavigate();
  const [watches, setWatches] = useState<Watch[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [scanning, setScanning] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([watchesApi.list(), alertsApi.list()])
      .then(([w, a]) => {
        setWatches(w);
        setAlerts(a);
      })
      .finally(() => setLoading(false));
  }, []);

  const unreadCount = alerts.filter((a) => !a.is_read).length;
  const alertCountByWatch = (watchId: string) =>
    alerts.filter((a) => a.watch_id === watchId && !a.is_read).length;

  const handleScan = async (watchId: string) => {
    setScanning(watchId);
    try {
      await watchesApi.scan(watchId);
    } finally {
      setTimeout(() => setScanning(null), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-24">
      {/* Header */}
      <div className="px-5 pt-14 pb-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[#0f1230] tracking-tight">
              Sievy
            </h1>
            <p className="text-[#6b7280] text-sm mt-0.5">
              Your watches. Your updates.
            </p>
          </div>
          <button
            onClick={() => navigate("/alerts")}
            className="relative w-10 h-10 rounded-full bg-white border border-[#e8eaf0] flex items-center justify-center shadow-sm"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#0f1230"
              strokeWidth="2"
            >
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-[#10b981] text-white text-[9px] font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Create Button */}
      <div className="px-5 mb-6">
        <button
          onClick={() => navigate("/watches/new")}
          className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 shadow-md active:opacity-90 transition-opacity"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2.5"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Create Watch
        </button>
      </div>

      {/* Watch List */}
      <div className="px-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-[#0f1230]">Active watches</h2>
          <span className="text-[#6b7280] text-sm">{watches.length} total</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : watches.length === 0 ? (
          <div className="flex flex-col items-center py-16 gap-4">
            <div className="w-16 h-16 rounded-2xl bg-white border border-[#e8eaf0] flex items-center justify-center shadow-sm">
              <svg
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#9ca3af"
                strokeWidth="1.5"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-[#0f1230] font-semibold text-sm">
                No watches yet
              </p>
              <p className="text-[#6b7280] text-xs mt-1">
                Create one to start monitoring sources.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {watches.map((watch) => (
              <WatchCard
                key={watch.watch_id}
                watch={watch}
                alertCount={alertCountByWatch(watch.watch_id)}
                onScan={handleScan}
                scanning={scanning === watch.watch_id}
              />
            ))}
          </div>
        )}
      </div>

      {/* Bottom Tab Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-[#e8eaf0] px-8 py-3 flex justify-around">
        <button className="flex flex-col items-center gap-1">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#1a1f4e"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <span className="text-[10px] font-semibold text-[#1a1f4e]">
            Watches
          </span>
        </button>
        <button
          onClick={() => navigate("/alerts")}
          className="flex flex-col items-center gap-1"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#9ca3af"
            strokeWidth="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <span className="text-[10px] text-[#9ca3af]">Alerts</span>
        </button>
      </div>
    </div>
  );
}
