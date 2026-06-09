import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { watchesApi, type Watch } from "../api/watches";
import { alertsApi, type Alert } from "../api/alerts";

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

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function WatchAlerts() {
  const { watchId } = useParams<{ watchId: string }>();
  const navigate = useNavigate();
  const [watch, setWatch] = useState<Watch | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!watchId) return;
    Promise.all([watchesApi.get(watchId), alertsApi.list(watchId)])
      .then(([w, a]) => {
        setWatch(w);
        setAlerts(a);
      })
      .finally(() => setLoading(false));
  }, [watchId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f7f8fc] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Header */}
      <div className="px-5 safe-top pb-4 flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="w-9 h-9 rounded-full bg-white border border-[#e8eaf0] flex items-center justify-center shadow-sm"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#0f1230"
            strokeWidth="2"
          >
            <path d="M19 12H5M12 5l-7 7 7 7" />
          </svg>
        </button>
        <div>
          <p className="text-sm font-semibold text-[#0f1230]">Alerts</p>
          {watch && (
            <p className="text-xs text-[#6b7280] truncate max-w-56">
              {watch.source_url.replace(/https?:\/\//, "")}
            </p>
          )}
        </div>
      </div>

      <div className="px-5 flex flex-col gap-3">
        {alerts.length === 0 ? (
          <div className="bg-white rounded-2xl border border-[#e8eaf0] p-12 flex flex-col items-center gap-3 mt-4">
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
            <p className="text-[#6b7280] text-sm">
              No alerts yet for this watch.
            </p>
          </div>
        ) : (
          alerts.map((alert) => {
            const vc =
              verdictConfig[alert.verdict] ?? verdictConfig.needs_checking;
            return (
              <button
                key={alert.alert_id}
                onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                className={`w-full bg-white rounded-2xl p-4 border text-left shadow-sm active:opacity-80 transition-opacity ${
                  alert.is_read ? "border-[#e8eaf0]" : "border-[#1a1f4e]/20"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p
                    className={`text-sm text-[#0f1230] leading-tight ${!alert.is_read ? "font-bold" : "font-medium"}`}
                  >
                    {alert.title || "New match found"}
                  </p>
                  {!alert.is_read && (
                    <span className="w-2 h-2 rounded-full bg-[#1a1f4e] shrink-0 mt-1" />
                  )}
                </div>
                <p className="text-[#6b7280] text-xs mt-1">
                  {timeAgo(alert.created_at)}
                </p>
                <div
                  className={`inline-flex items-center gap-1.5 mt-2 px-2.5 py-1 rounded-full ${vc.bg}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${vc.dot}`} />
                  <span className={`text-xs font-medium ${vc.color}`}>
                    {vc.label}
                  </span>
                </div>
                {alert.summary && (
                  <p className="text-[#6b7280] text-xs mt-2 leading-relaxed line-clamp-2">
                    {alert.summary}
                  </p>
                )}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
