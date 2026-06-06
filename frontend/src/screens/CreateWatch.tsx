import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { watchesApi } from "../api/watches";

interface CriteriaField {
  key: string;
  value: string;
}

const categories = [
  {
    id: "housing",
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
  {
    id: "opportunity",
    label: "Scholarships / Programs",
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
  {
    id: "events",
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
  {
    id: "recruiting",
    label: "Jobs / Recruiting",
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
      </svg>
    ),
  },
  {
    id: "audition",
    label: "Auditions",
    icon: (
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
  },
  {
    id: "other",
    label: "Other",
    icon: (
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
  },
];

export default function CreateWatch() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [sourceUrl, setSourceUrl] = useState("");
  const [category, setCategory] = useState("housing");
  const [note, setNote] = useState("");
  const [description, setDescription] = useState("");
  const [fields, setFields] = useState<CriteriaField[]>([]);
  const [loading, setLoading] = useState(false);

  const addField = () => {
    setFields((prev) => [...prev, { key: "", value: "" }]);
  };

  const removeField = (index: number) => {
    setFields((prev) => prev.filter((_, i) => i !== index));
  };

  const updateField = (index: number, part: "key" | "value", val: string) => {
    setFields((prev) =>
      prev.map((f, i) => (i === index ? { ...f, [part]: val } : f)),
    );
  };

  const buildCriteria = () => {
    const result: Record<string, string> = {};
    if (description.trim()) {
      result["description"] = description.trim();
    }
    for (const f of fields) {
      if (f.key.trim() && f.value.trim()) {
        result[f.key.trim()] = f.value.trim();
      }
    }
    return result;
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await watchesApi.create({
        source_url: sourceUrl,
        category,
        criteria: buildCriteria(),
        note,
      });
      navigate("/watches");
    } finally {
      setLoading(false);
    }
  };

  const canContinue =
    step === 1
      ? !!sourceUrl.trim()
      : !description.trim() && fields.every((f) => !f.key.trim());

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Header */}
      <div className="px-5 pt-14 pb-4 flex items-center gap-4">
        <button
          onClick={() => (step === 1 ? navigate(-1) : setStep(1))}
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
        <div className="flex-1">
          <p className="text-xs text-[#6b7280] font-medium">Create Watch</p>
          <p className="text-xs text-[#9ca3af]">Step {step} of 2</p>
        </div>
        <div className="flex gap-1.5">
          {[1, 2].map((s) => (
            <div
              key={s}
              className={`h-1.5 rounded-full transition-all ${
                s <= step ? "bg-[#1a1f4e] w-6" : "bg-[#e8eaf0] w-4"
              }`}
            />
          ))}
        </div>
      </div>

      <div className="px-5">
        {/* Step 1: URL + Category + Note */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold text-[#0f1230] mt-4 mb-1">
              Where should Sievy watch?
            </h2>
            <p className="text-[#6b7280] text-sm mb-6">
              Paste a listing page you check manually.
            </p>

            <div className="flex flex-col gap-3">
              {/* URL */}
              <div className="bg-white rounded-2xl border border-[#e8eaf0] overflow-hidden">
                <div className="flex items-center gap-3 px-4 py-3">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#9ca3af"
                    strokeWidth="2"
                  >
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                  <input
                    type="url"
                    placeholder="https://"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    className="flex-1 text-sm text-[#0f1230] outline-none placeholder-[#9ca3af]"
                  />
                </div>
              </div>

              {/* Category */}
              <div className="bg-white rounded-2xl border border-[#e8eaf0] overflow-hidden">
                <div className="flex items-center gap-3 px-4 py-3">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#9ca3af"
                    strokeWidth="2"
                  >
                    <path d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="flex-1 text-sm text-[#0f1230] outline-none bg-transparent"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Note */}
              <div className="bg-white rounded-2xl border border-[#e8eaf0] overflow-hidden">
                <div className="flex items-center gap-3 px-4 py-3">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#9ca3af"
                    strokeWidth="2"
                  >
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Note (optional) — e.g. on-campus, beginner-friendly"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    className="flex-1 text-sm text-[#0f1230] outline-none placeholder-[#9ca3af]"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-4">
              <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                <div className="flex items-center gap-2 mb-2">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="9 12 11 14 15 10" />
                  </svg>
                  <span className="text-xs font-semibold text-[#10b981]">
                    Works well
                  </span>
                </div>
                <ul className="text-xs text-[#6b7280] space-y-1">
                  <li>Public listing pages</li>
                  <li>Notice boards</li>
                  <li>Community boards</li>
                </ul>
              </div>
              <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                <div className="flex items-center gap-2 mb-2">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#f59e0b"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <span className="text-xs font-semibold text-[#f59e0b]">
                    Not supported
                  </span>
                </div>
                <ul className="text-xs text-[#6b7280] space-y-1">
                  <li>Login-only pages</li>
                  <li>Infinite scroll apps</li>
                  <li>Captcha-heavy sites</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Criteria */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-[#0f1230] mt-4 mb-1">
              What should match?
            </h2>
            <p className="text-[#6b7280] text-sm mb-6">
              Tell Sievy what you're looking for.
            </p>

            <div className="flex flex-col gap-4">
              {fields.length > 0 && (
                <div className="flex flex-col gap-2">
                  {fields.map((field, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="flex-1 bg-white rounded-xl border border-[#e8eaf0] flex overflow-hidden">
                        <input
                          type="text"
                          placeholder="Field"
                          value={field.key}
                          onChange={(e) =>
                            updateField(index, "key", e.target.value)
                          }
                          className="w-24 px-3 py-3 text-sm text-[#0f1230] outline-none border-r border-[#e8eaf0] placeholder-[#9ca3af] shrink-0"
                        />
                        <input
                          type="text"
                          placeholder="Value"
                          value={field.value}
                          onChange={(e) =>
                            updateField(index, "value", e.target.value)
                          }
                          className="flex-1 px-3 py-3 text-sm text-[#0f1230] outline-none placeholder-[#9ca3af]"
                        />
                      </div>
                      <button
                        onClick={() => removeField(index)}
                        className="w-8 h-8 rounded-full border border-[#e8eaf0] bg-white flex items-center justify-center shrink-0 active:opacity-70"
                      >
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#9ca3af"
                          strokeWidth="2"
                        >
                          <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={addField}
                className="flex items-center gap-2 py-3 text-[#1a1f4e] text-sm font-medium border border-dashed border-[#c7cae0] rounded-xl justify-center active:opacity-70 transition-opacity bg-white"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#1a1f4e"
                  strokeWidth="2.5"
                >
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add criteria
              </button>

              <div className="bg-white rounded-2xl border border-[#e8eaf0] p-4">
                <textarea
                  placeholder="Anything else? Describe what you're looking for in your own words."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="w-full text-sm text-[#0f1230] outline-none placeholder-[#9ca3af] resize-none leading-relaxed"
                />
              </div>
            </div>
          </div>
        )}

        {/* Bottom Button */}
        <div className="mt-8">
          {step === 1 ? (
            <button
              disabled={!sourceUrl.trim()}
              onClick={() => setStep(2)}
              className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl disabled:opacity-40 active:opacity-90 transition-opacity"
            >
              Continue
            </button>
          ) : (
            <button
              disabled={loading || canContinue}
              onClick={handleSubmit}
              className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl disabled:opacity-40 flex items-center justify-center gap-2 active:opacity-90 transition-opacity"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating watch...
                </>
              ) : (
                "Start watching"
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
