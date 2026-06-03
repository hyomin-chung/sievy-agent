import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { watchesApi } from "../api/watches";

const categories = [
  {
    id: "housing",
    label: "Housing / room rental",
    description: "Rooms, sublets, roommate posts.",
    icon: (
      <svg
        width="22"
        height="22"
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
    label: "Scholarships / programs",
    description: "Deadlines, eligibility, benefits.",
    icon: (
      <svg
        width="22"
        height="22"
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
    description: "Workshops, library events, local programs.",
    icon: (
      <svg
        width="22"
        height="22"
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
    label: "Recruiting",
    description: "Roles, requirements, deadlines.",
    icon: (
      <svg
        width="22"
        height="22"
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
];

const MOVE_IN_OPTIONS = [
  "Within 7 days",
  "Within 30 days",
  "Within 60 days",
  "Flexible",
];

interface HousingCriteria {
  locations: string[];
  max_rent: string;
  move_in_within: string;
}

interface OpportunityCriteria {
  keywords: string;
  open_to_international: boolean;
}

export default function CreateWatch() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [category, setCategory] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [housingCriteria, setHousingCriteria] = useState<HousingCriteria>({
    locations: [],
    max_rent: "",
    move_in_within: "Within 30 days",
  });
  const [opportunityCriteria, setOpportunityCriteria] =
    useState<OpportunityCriteria>({
      keywords: "",
      open_to_international: false,
    });
  const [loading, setLoading] = useState(false);

  const buildCriteria = () => {
    if (category === "housing") {
      return {
        locations: housingCriteria.locations,
        max_rent: Number(housingCriteria.max_rent) || null,
        move_in_within: housingCriteria.move_in_within,
      };
    }
    return {
      keywords: opportunityCriteria.keywords,
      open_to_international: opportunityCriteria.open_to_international,
    };
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await watchesApi.create({
        source_url: sourceUrl,
        category,
        criteria: buildCriteria(),
      });
      navigate("/watches");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f8fc] pb-10">
      {/* Header */}
      <div className="px-5 pt-14 pb-4 flex items-center gap-4">
        <button
          onClick={() => (step === 1 ? navigate(-1) : setStep((s) => s - 1))}
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
          <p className="text-xs text-[#9ca3af]">Step {step} of 3</p>
        </div>
        <div className="flex gap-1.5">
          {[1, 2, 3].map((s) => (
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
        {/* Step 1: Category */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold text-[#0f1230] mt-4 mb-1">
              What should Sievy watch for?
            </h2>
            <p className="text-[#6b7280] text-sm mb-6">
              Choose the kind of posts you want to track.
            </p>
            <div className="flex flex-col gap-3">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={`flex items-center gap-4 p-4 rounded-2xl border transition-all text-left ${
                    category === cat.id
                      ? "border-[#1a1f4e] bg-white shadow-md"
                      : "border-[#e8eaf0] bg-white"
                  }`}
                >
                  <div
                    className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
                      category === cat.id ? "bg-[#eef0f8]" : "bg-[#f5f6fa]"
                    }`}
                  >
                    {cat.icon}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-[#0f1230] text-sm">
                      {cat.label}
                    </p>
                    <p className="text-[#6b7280] text-xs mt-0.5">
                      {cat.description}
                    </p>
                  </div>
                  <div
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                      category === cat.id
                        ? "border-[#1a1f4e] bg-[#1a1f4e]"
                        : "border-[#d1d5db]"
                    }`}
                  >
                    {category === cat.id && (
                      <svg
                        width="10"
                        height="10"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="white"
                        strokeWidth="3"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Criteria */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-[#0f1230] mt-4 mb-1">
              Tell Sievy what should match
            </h2>
            <p className="text-[#6b7280] text-sm mb-6">
              Add your preferences and let Sievy do the watching.
            </p>

            {category === "housing" && (
              <div className="flex flex-col gap-4">
                <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                  <p className="font-semibold text-[#0f1230] text-sm mb-3">
                    Preferred areas
                  </p>
                  <input
                    type="text"
                    placeholder="e.g. Bellevue, Redmond, Seattle"
                    value={housingCriteria.locations.join(", ")}
                    onChange={(e) =>
                      setHousingCriteria((p) => ({
                        ...p,
                        locations: e.target.value
                          .split(",")
                          .map((s) => s.trim())
                          .filter(Boolean),
                      }))
                    }
                    className="w-full px-4 py-3 rounded-xl border border-[#e8eaf0] text-[#0f1230] text-sm outline-none focus:border-[#1a1f4e] transition-colors"
                  />
                  <p className="text-[#9ca3af] text-xs mt-2">
                    Separate multiple areas with commas.
                  </p>
                </div>

                <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                  <p className="font-semibold text-[#0f1230] text-sm mb-3">
                    Budget
                  </p>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#6b7280] font-medium">
                      $
                    </span>
                    <input
                      type="number"
                      placeholder="1000"
                      value={housingCriteria.max_rent}
                      onChange={(e) =>
                        setHousingCriteria((p) => ({
                          ...p,
                          max_rent: e.target.value,
                        }))
                      }
                      className="w-full pl-8 pr-4 py-3 rounded-xl border border-[#e8eaf0] text-[#0f1230] text-sm outline-none focus:border-[#1a1f4e] transition-colors"
                    />
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                  <p className="font-semibold text-[#0f1230] text-sm mb-3">
                    Move-in
                  </p>
                  <select
                    value={housingCriteria.move_in_within}
                    onChange={(e) =>
                      setHousingCriteria((p) => ({
                        ...p,
                        move_in_within: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-3 rounded-xl border border-[#e8eaf0] text-[#0f1230] text-sm outline-none focus:border-[#1a1f4e] bg-white"
                  >
                    {MOVE_IN_OPTIONS.map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {category !== "housing" && (
              <div className="flex flex-col gap-4">
                <div className="bg-white rounded-2xl p-4 border border-[#e8eaf0]">
                  <p className="font-semibold text-[#0f1230] text-sm mb-3">
                    Keywords
                  </p>
                  <input
                    type="text"
                    placeholder="e.g. STEM, international, undergraduate"
                    value={opportunityCriteria.keywords}
                    onChange={(e) =>
                      setOpportunityCriteria((p) => ({
                        ...p,
                        keywords: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-3 rounded-xl border border-[#e8eaf0] text-[#0f1230] text-sm outline-none focus:border-[#1a1f4e] transition-colors"
                  />
                </div>

                <button
                  onClick={() =>
                    setOpportunityCriteria((p) => ({
                      ...p,
                      open_to_international: !p.open_to_international,
                    }))
                  }
                  className={`flex items-center justify-between p-4 rounded-2xl border transition-all ${
                    opportunityCriteria.open_to_international
                      ? "border-[#1a1f4e] bg-white"
                      : "border-[#e8eaf0] bg-white"
                  }`}
                >
                  <span className="font-medium text-[#0f1230] text-sm">
                    Open to international students
                  </span>
                  <div
                    className={`w-12 h-6 rounded-full transition-colors ${
                      opportunityCriteria.open_to_international
                        ? "bg-[#1a1f4e]"
                        : "bg-[#e8eaf0]"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full bg-white shadow-sm mt-0.5 transition-transform ${
                        opportunityCriteria.open_to_international
                          ? "translate-x-6"
                          : "translate-x-0.5"
                      }`}
                    />
                  </div>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Source URL */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold text-[#0f1230] mt-4 mb-1">
              Where should Sievy watch?
            </h2>
            <p className="text-[#6b7280] text-sm mb-6">
              Paste pages you already check manually.
            </p>

            <div className="bg-white rounded-2xl border border-[#e8eaf0] overflow-hidden">
              <div className="flex items-center gap-3 px-4 py-3 border-b border-[#f0f2f8]">
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

            <div className="grid grid-cols-2 gap-3 mt-5">
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
                    Best supported
                  </span>
                </div>
                <ul className="text-xs text-[#6b7280] space-y-1">
                  <li>Public listing pages</li>
                  <li>Notice boards</li>
                  <li>RSS feeds</li>
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
                  <li>Private feeds</li>
                  <li>Captcha-heavy</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Button */}
        <div className="mt-8">
          {step < 3 ? (
            <button
              disabled={step === 1 && !category}
              onClick={() => setStep((s) => s + 1)}
              className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl disabled:opacity-40 active:opacity-90 transition-opacity"
            >
              Continue
            </button>
          ) : (
            <button
              disabled={!sourceUrl || loading}
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
