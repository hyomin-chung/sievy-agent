import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { watchesApi, type Watch } from "../api/watches";
import { alertsApi } from "../api/alerts";
import type { ReactNode } from "react";

const categoryIcons: Record<string, ReactNode> = {
  housing: (
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
  opportunity: (
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
  events: (
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
  recruiting: (
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
    </svg>
  ),
  audition: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#1a1f4e"
      strokeWidth="1.8"
    >
      <circle cx="12" cy="12" r="10" />
      <polygon points="10 8 16 12 10 16 10 8" />
    </svg>
  ),
  other: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#1a1f4e"
      strokeWidth="1.8"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
    </svg>
  ),
};

const categoryLabels: Record<string, string> = {
  housing: "Housing",
  opportunity: "Scholarships / Programs",
  events: "Events",
  recruiting: "Jobs / Recruiting",
  audition: "Auditions",
  other: "Other",
};

const getCategoryIcon = (category: string): ReactNode =>
  categoryIcons[category] ?? categoryIcons.other;

const getCategoryLabel = (category: string): string =>
  categoryLabels[category] ?? "Other";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatFieldKey(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function WatchDetail() {
  const { watchId } = useParams<{ watchId: string }>();
  const navigate = useNavigate();
  const [watch, setWatch] = useState<Watch | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    if (!watchId) return;
    watchesApi
      .get(watchId)
      .then(setWatch)
      .finally(() => setLoading(false));
  }, [watchId]);

  const handleScan = async () => {
    if (!watchId) return;
    setScanning(true);
    try {
      const prevAlerts = await alertsApi.list(watchId);
      const prevCount = prevAlerts.length;

      await watchesApi.scan(watchId);
      const beforeTime = watch?.last_scanned_at
        ? new Date(watch.last_scanned_at).getTime()
        : 0;

      const poll = setInterval(async () => {
        try {
          const updated = await watchesApi.get(watchId);
          const updatedTime = updated.last_scanned_at
            ? new Date(updated.last_scanned_at).getTime()
            : 0;
          if (updatedTime > beforeTime) {
            setWatch(updated);
            setScanning(false);
            clearInterval(poll);

            const newAlerts = await alertsApi.list(watchId);
            if (newAlerts.length === prevCount) {
              showToast("All clear — nothing new matched your criteria");
            }
          }
        } catch {
          clearInterval(poll);
          setScanning(false);
        }
      }, 5000);
    } catch {
      setScanning(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!watch || !watchId) return;
    setToggling(true);
    const newStatus = watch.status === "active" ? "paused" : "active";
    try {
      await watchesApi.updateStatus(watchId, newStatus);
      setWatch({ ...watch, status: newStatus });
    } finally {
      setToggling(false);
    }
  };

  const handleDelete = async () => {
    if (!watchId) return;
    setDeleting(true);
    try {
      await watchesApi.delete(watchId);
      navigate("/watches");
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

  if (!watch) {
    return (
      <div className="min-h-screen bg-[#f7f8fc] flex items-center justify-center">
        <p className="text-[#6b7280]">Watch not found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Toast */}
      {toast && (
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-50 pointer-events-none">
          <div className="bg-[#0f1230] text-white text-sm font-medium px-4 py-2.5 rounded-full shadow-lg whitespace-nowrap">
            {toast}
          </div>
        </div>
      )}

      {/* Scan loading modal */}
      {scanning && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl px-8 py-7 flex flex-col items-center gap-4 shadow-xl mx-5">
            <div className="w-10 h-10 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
            <div className="text-center">
              <p className="font-semibold text-[#0f1230]">Scanning...</p>
              <p className="text-[#6b7280] text-xs mt-1">
                Reading new posts and checking your criteria.
              </p>
            </div>
            <button
              onClick={() => setScanning(false)}
              className="text-xs text-[#9ca3af] mt-1"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="px-5 safe-top pb-4 flex items-center gap-4">
        <button
          onClick={() => navigate("/watches")}
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
        <p className="text-sm font-semibold text-[#0f1230]">Watch</p>
      </div>

      <div className="px-5 flex flex-col gap-4">
        {/* Watch Info */}
        <div className="bg-white rounded-2xl border border-[#e8eaf0] shadow-sm overflow-hidden">
          <div className="p-4 flex items-start gap-3">
            <div className="w-11 h-11 rounded-xl bg-[#f0f2f8] flex items-center justify-center shrink-0">
              {getCategoryIcon(watch.category)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <p className="font-bold text-[#0f1230]">
                  {getCategoryLabel(watch.category)}
                </p>
                {watch.note && (
                  <span className="text-[#6b7280] text-sm font-normal">
                    · {watch.note}
                  </span>
                )}
              </div>
              <p className="text-[#6b7280] text-xs mt-0.5 truncate">
                {watch.source_url}
              </p>
            </div>
            <div
              className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                watch.status === "active"
                  ? "bg-[#f0fdf8] text-[#10b981]"
                  : "bg-[#f5f6fa] text-[#9ca3af]"
              }`}
            >
              {watch.status === "active" ? "Active" : "Paused"}
            </div>
          </div>

          <div className="border-t border-[#f0f2f8] divide-y divide-[#f0f2f8]">
            {Object.entries(watch.criteria).map(([key, val]) => (
              <div
                key={key}
                className="flex items-center justify-between px-4 py-2.5"
              >
                <span className="text-xs text-[#6b7280]">
                  {formatFieldKey(key)}
                </span>
                <span className="text-xs font-semibold text-[#0f1230] max-w-48 text-right">
                  {Array.isArray(val) ? val.join(", ") : String(val)}
                </span>
              </div>
            ))}
            {watch.last_scanned_at && (
              <div className="flex items-center justify-between px-4 py-2.5">
                <span className="text-xs text-[#6b7280]">Last scanned</span>
                <span className="text-xs font-semibold text-[#0f1230]">
                  {timeAgo(watch.last_scanned_at)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleScan}
            disabled={scanning || watch.status === "paused"}
            className="flex-1 bg-[#1a1f4e] text-white font-semibold py-3.5 rounded-2xl flex items-center justify-center gap-2 disabled:opacity-40 active:opacity-90 transition-opacity"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            Scan now
          </button>

          <button
            onClick={handleToggleStatus}
            disabled={toggling}
            className="flex-1 border border-[#e8eaf0] bg-white text-[#0f1230] font-semibold py-3.5 rounded-2xl flex items-center justify-center gap-2 disabled:opacity-40 active:opacity-80 transition-opacity"
          >
            {watch.status === "active" ? (
              <>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#0f1230"
                  strokeWidth="2"
                >
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
                Pause
              </>
            ) : (
              <>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#0f1230"
                  strokeWidth="2"
                >
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                Resume
              </>
            )}
          </button>
        </div>

        {/* View Alerts */}
        <button
          onClick={() => navigate(`/watches/${watchId}/alerts`)}
          className="w-full border border-[#e8eaf0] bg-white text-[#0f1230] font-medium py-3.5 rounded-2xl flex items-center justify-center gap-2 active:opacity-80 transition-opacity"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#0f1230"
            strokeWidth="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          View Alerts
        </button>

        {/* Delete */}
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-full border border-red-200 bg-white text-red-500 font-medium py-3.5 rounded-2xl active:opacity-80 transition-opacity"
          >
            Delete watch
          </button>
        ) : (
          <div className="bg-white rounded-2xl border border-red-200 p-4 flex flex-col gap-3">
            <p className="text-sm font-semibold text-[#0f1230]">
              Delete this watch?
            </p>
            <p className="text-xs text-[#6b7280]">
              All alerts for this watch will also be deleted. This cannot be
              undone.
            </p>
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
