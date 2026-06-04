import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { alertsApi, type Alert } from "../api/alerts";
import type { ReactNode } from "react";

const fieldIcons: Record<string, ReactNode> = {
  location: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#6b7280"
      strokeWidth="2"
    >
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  ),
  rent: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#6b7280"
      strokeWidth="2"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </svg>
  ),
  move_in_date: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#6b7280"
      strokeWidth="2"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  ),
  utilities_included: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#6b7280"
      strokeWidth="2"
    >
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),
  deadline: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#6b7280"
      strokeWidth="2"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  eligibility: (
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
  ),
};

const defaultIcon = (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="#6b7280"
    strokeWidth="2"
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

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
  if (typeof val === "number") return String(val);
  return String(val);
}

export default function AlertDetail() {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);

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

  const vc = verdictConfig[alert.verdict] ?? verdictConfig.needs_checking;
  const fields = Object.entries(alert.extracted_fields).filter(
    ([, v]) => v !== null && v !== undefined,
  );

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Header */}
      <div className="px-5 pt-14 pb-4 flex items-center gap-4">
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
        <p className="text-sm font-semibold text-[#0f1230]">Alert</p>
      </div>

      <div className="px-5 flex flex-col gap-4">
        {/* Title + Verdict */}
        <div>
          <h1 className="text-2xl font-bold text-[#0f1230] leading-tight mb-3">
            {alert.title || "New match found"}
          </h1>
          <div
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${vc.bg} ${vc.border}`}
          >
            <span className={`w-2 h-2 rounded-full ${vc.dot}`} />
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
                  className="flex items-center justify-between px-4 py-3"
                >
                  <div className="flex items-center gap-2.5">
                    {fieldIcons[key] ?? defaultIcon}
                    <span className="text-sm text-[#6b7280]">
                      {formatFieldKey(key)}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-[#0f1230]">
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
            <p className="text-[#6b7280] text-sm leading-relaxed">
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

        <button
          onClick={() => navigate(-1)}
          className="w-full border border-[#e8eaf0] text-[#6b7280] font-medium py-3.5 rounded-2xl bg-white active:opacity-80 transition-opacity"
        >
          Back to alerts
        </button>
      </div>
    </div>
  );
}
