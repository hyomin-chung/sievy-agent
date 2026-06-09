import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { alertsApi, type Alert } from "../api/alerts";
import { useSearchParams } from "react-router-dom";

const verdictConfig = {
  worth_checking: {
    label: "Worth checking",
    color: "text-[#10b981]",
    bg: "bg-[#f0fdf8]",
    dot: "bg-[#10b981]",
  },
  needs_checking: {
    label: "Needs checking",
    color: "text-[#f59e0b]",
    bg: "bg-[#fffbf0]",
    dot: "bg-[#f59e0b]",
  },
};

const FILTERS = ["All", "Worth checking", "Needs checking"] as const;
type Filter = (typeof FILTERS)[number];

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function AlertInbox() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const watchId = searchParams.get("watch_id") ?? undefined;
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<Filter>("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    alertsApi
      .list(watchId)
      .then(setAlerts)
      .finally(() => setLoading(false));
  }, [watchId]);

  const filtered = alerts.filter((a) => {
    if (filter === "All") return true;
    if (filter === "Worth checking") return a.verdict === "worth_checking";
    return a.verdict === "needs_checking";
  });

  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-24">
      {/* Header */}
      <div className="px-5 safe-top pb-4">
        <div className="flex items-center justify-between mb-1">
          <h1 className="text-3xl font-bold text-[#0f1230] tracking-tight">
            Sievy
          </h1>
          <div className="w-9 h-9 rounded-full bg-white border border-[#e8eaf0] flex items-center justify-center shadow-sm">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#6b7280"
              strokeWidth="2"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
        </div>
        <h2 className="text-2xl font-bold text-[#0f1230]">Alerts</h2>
        <p className="text-[#6b7280] text-sm mt-0.5">
          Updates from your watches
        </p>
      </div>

      {/* Filter Pills */}
      <div className="px-5 flex gap-2 mb-4 overflow-x-auto pb-1">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              filter === f
                ? "bg-[#1a1f4e] text-white"
                : "bg-white text-[#6b7280] border border-[#e8eaf0]"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Alert List */}
      <div className="px-5">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
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
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-[#0f1230] font-semibold text-sm">
                No alerts yet
              </p>
              <p className="text-[#6b7280] text-xs mt-1">
                Scan your watches to get started.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {filtered.map((alert) => {
              const vc = verdictConfig[alert.verdict];
              return (
                <button
                  key={alert.alert_id}
                  onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                  className={`w-full bg-white rounded-2xl p-4 border text-left shadow-sm active:opacity-80 transition-opacity ${
                    alert.is_read ? "border-[#e8eaf0]" : "border-[#1a1f4e]/20"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-11 h-11 rounded-xl bg-[#f0f2f8] flex items-center justify-center shrink-0">
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
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p
                          className={`font-semibold text-sm text-[#0f1230] leading-tight ${!alert.is_read ? "font-bold" : ""}`}
                        >
                          {alert.title || "New match found"}
                        </p>
                        {!alert.is_read && (
                          <span className="w-2 h-2 rounded-full bg-[#1a1f4e] shrink-0 mt-1.5" />
                        )}
                      </div>
                      <p className="text-[#6b7280] text-xs mt-0.5">
                        {timeAgo(alert.created_at)}
                      </p>
                      <div
                        className={`inline-flex items-center gap-1.5 mt-2 px-2.5 py-1 rounded-full ${vc.bg}`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${vc.dot}`}
                        />
                        <span className={`text-xs font-medium ${vc.color}`}>
                          {vc.label}
                        </span>
                      </div>
                      {alert.summary && (
                        <p className="text-[#6b7280] text-xs mt-2 leading-relaxed line-clamp-2">
                          {alert.summary}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom Tab Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-[#e8eaf0] px-8 py-3 flex justify-around">
        <button
          onClick={() => navigate("/watches")}
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
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <span className="text-[10px] text-[#9ca3af]">Watches</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <div className="relative">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#1a1f4e"
              strokeWidth="2"
            >
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-[#10b981] text-white text-[8px] font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </div>
          <span className="text-[10px] font-semibold text-[#1a1f4e]">
            Alerts
          </span>
        </button>
      </div>
    </div>
  );
}
