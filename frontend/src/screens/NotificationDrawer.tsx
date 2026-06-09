import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function NotificationDrawer({ open, onClose }: Props) {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    alertsApi
      .list()
      .then((all) => setAlerts(all.filter((a) => !a.is_read)))
      .finally(() => setLoading(false));
  }, [open]);

  const handleClickAlert = async (alert: Alert) => {
    await alertsApi.markAsRead(alert.alert_id);
    onClose();
    navigate(`/alerts/${alert.alert_id}`);
  };

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div className="fixed inset-0 bg-black/30 z-40" onClick={onClose} />
      )}

      {/* Drawer */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl shadow-2xl transition-transform duration-300 ease-out ${
          open ? "translate-y-0" : "translate-y-full"
        }`}
        style={{ maxHeight: "70vh" }}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-[#e8eaf0]" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-[#f0f2f8]">
          <p className="font-bold text-[#0f1230]">New Alerts</p>
          <button
            onClick={() => {
              onClose();
              navigate("/alerts");
            }}
            className="text-xs text-[#1a1f4e] font-medium"
          >
            See all
          </button>
        </div>

        {/* Content */}
        <div
          className="overflow-y-auto"
          style={{ maxHeight: "calc(70vh - 80px)" }}
        >
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-6 h-6 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : alerts.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-12">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#9ca3af"
                strokeWidth="1.5"
              >
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              <p className="text-[#6b7280] text-sm">No new alerts</p>
            </div>
          ) : (
            <div className="flex flex-col divide-y divide-[#f0f2f8]">
              {alerts.map((alert) => {
                const vc =
                  verdictConfig[alert.verdict] ?? verdictConfig.needs_checking;
                return (
                  <button
                    key={alert.alert_id}
                    onClick={() => handleClickAlert(alert)}
                    className="w-full px-5 py-4 text-left active:bg-[#f7f8fc] transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-bold text-[#0f1230] leading-tight flex-1">
                        {alert.title || "New match found"}
                      </p>
                      <span className="w-2 h-2 rounded-full bg-[#1a1f4e] shrink-0 mt-1.5" />
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <div
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${vc.bg}`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${vc.dot}`}
                        />
                        <span className={`text-xs font-medium ${vc.color}`}>
                          {vc.label}
                        </span>
                      </div>
                      <span className="text-[#9ca3af] text-xs">
                        {timeAgo(alert.created_at)}
                      </span>
                    </div>
                    {alert.summary && (
                      <p className="text-[#6b7280] text-xs mt-1.5 leading-relaxed line-clamp-2">
                        {alert.summary}
                      </p>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
