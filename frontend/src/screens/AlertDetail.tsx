import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { alertsApi, type Alert } from "../api/alerts";

const verdictConfig = {
  worth_checking: {
    label: "Worth checking",
    color: "text-[#10b981]",
    bg: "bg-[#f0fdf8]",
    dot: "bg-[#10b981]",
    border: "border-[#10b981]/20",
  },
  needs_checking: {
    label: "Needs checking",
    color: "text-[#f59e0b]",
    bg: "bg-[#fffbf0]",
    dot: "bg-[#f59e0b]",
    border: "border-[#f59e0b]/20",
  },
};

function formatFieldKey(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatFieldValue(val: unknown): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "boolean") return val ? "Yes" : "No";
  return String(val);
}

export default function AlertDetail() {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!alertId) return;
    alertsApi
      .get(alertId)
      .then((a) => {
        setAlert(a);
        if (!a.is_read) alertsApi.markAsRead(alertId);
      })
      .finally(() => setLoading(false));
  }, [alertId]);

  const handleDelete = async () => {
    if (!alertId) return;
    setDeleting(true);
    try {
      await alertsApi.delete(alertId);
      navigate(-1);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f7f8fc] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="min-h-screen bg-[#f7f8fc] flex items-center justify-center">
        <p className="text-[#6b7280]">Alert not found.</p>
      </div>
    );
  }

  const vc =
    verdictConfig[alert.verdict as keyof typeof verdictConfig] ??
    verdictConfig.needs_checking;
  const fields = Object.entries(alert.extracted_fields ?? {}).filter(
    ([key, v]) =>
      v !== null &&
      v !== undefined &&
      !["post_id", "post_url", "watch_id", "source_url"].includes(key),
  );

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Header */}
      <div className="px-5 pt-14 pb-4 flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="w-9 h-9 rounded-full bg-white border border-[#e8eaf0] flex items-center justify-center shadow-sm shrink-0"
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
        <p className="text-sm font-semibold text-[#0f1230]">Alert</p>
      </div>

      <div className="px-5 flex flex-col gap-4">
        {/* Title + Verdict */}
        <div className="flex flex-col gap-3">
          <h1 className="text-xl font-bold text-[#0f1230] leading-snug break-words">
            {alert.title || "New match found"}
          </h1>
          <div
            className={`self-start inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${vc.bg} ${vc.border}`}
          >
            <span className={`w-2 h-2 rounded-full shrink-0 ${vc.dot}`} />
            <span className={`text-sm font-semibold ${vc.color}`}>
              {vc.label}
            </span>
          </div>
        </div>

        {/* Why it matched */}
        {fields.length > 0 && (
          <div className="bg-white rounded-2xl border border-[#e8eaf0] overflow-hidden shadow-sm">
            <div className="px-4 py-3 border-b border-[#f0f2f8]">
              <p className="font-semibold text-[#0f1230] text-sm">
                Why it matched
              </p>
            </div>
            <div className="divide-y divide-[#f0f2f8]">
              {fields.map(([key, val]) => (
                <div
                  key={key}
                  className="flex items-start justify-between gap-4 px-4 py-3"
                >
                  <span className="text-sm text-[#6b7280] shrink-0">
                    {formatFieldKey(key)}
                  </span>
                  <span className="text-sm font-semibold text-[#0f1230] text-right break-words min-w-0">
                    {formatFieldValue(val)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        {alert.summary && (
          <div className="bg-white rounded-2xl border border-[#e8eaf0] p-4 shadow-sm">
            <p className="font-semibold text-[#0f1230] text-sm mb-2">Summary</p>
            <p className="text-[#6b7280] text-sm leading-relaxed break-words">
              {alert.summary}
            </p>
          </div>
        )}

        {/* Open original post */}
        <a
          href={alert.post_url}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 shadow-md active:opacity-90 transition-opacity"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
          >
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          Open original post
        </a>

        {/* Delete */}
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-full border border-red-200 bg-white text-red-500 font-medium py-3.5 rounded-2xl active:opacity-80 transition-opacity"
          >
            Delete alert
          </button>
        ) : (
          <div className="bg-white rounded-2xl border border-red-200 p-4 flex flex-col gap-3">
            <p className="text-sm font-semibold text-[#0f1230]">
              Delete this alert?
            </p>
            <p className="text-xs text-[#6b7280]">This cannot be undone.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 border border-[#e8eaf0] bg-white text-[#6b7280] font-medium py-3 rounded-xl active:opacity-80"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 bg-red-500 text-white font-semibold py-3 rounded-xl disabled:opacity-40 active:opacity-90"
              >
                {deleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
