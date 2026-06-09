import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const features = [
  {
    title: "Watch any public source",
    description: "Paste any listing board, notice page, or community URL.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
    ),
  },
  {
    title: "AI reads so you don't have to",
    description: "Gemini extracts what matters from every new post.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <path d="M12 2a10 10 0 1 0 10 10" />
        <path d="M12 6v6l4 2" />
      </svg>
    ),
  },
  {
    title: "Only get alerted when it matches",
    description: "Set your criteria once. Get notified only when it counts.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1a1f4e"
        strokeWidth="1.8"
      >
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
    ),
  },
];

export default function Onboarding() {
  const { user, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/watches");
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-[#f7f8fc] flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm flex flex-col items-center gap-10">
        {/* Logo */}
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-[#1a1f4e] flex items-center justify-center shadow-lg">
            <svg
              width="30"
              height="30"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.35-4.35" />
              <path d="M11 8v3l2 2" />
            </svg>
          </div>
          <div className="text-center">
            <h1 className="text-4xl font-bold text-[#0f1230] tracking-tight">
              Sievy
            </h1>
            <p className="text-[#6b7280] text-sm mt-1">
              Your watches. Your updates. Your edge.
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="w-full flex flex-col gap-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex items-start gap-4 bg-white rounded-2xl px-4 py-3.5 shadow-sm border border-[#e8eaf0]"
            >
              <div className="w-9 h-9 rounded-xl bg-[#f0f2f8] flex items-center justify-center shrink-0 mt-0.5">
                {f.icon}
              </div>
              <div>
                <p className="text-[#0f1230] text-sm font-semibold">
                  {f.title}
                </p>
                <p className="text-[#6b7280] text-xs mt-0.5 leading-relaxed">
                  {f.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Google Sign In */}
        <div className="w-full flex flex-col gap-3">
          <button
            onClick={signInWithGoogle}
            className="w-full bg-[#1a1f4e] text-white font-semibold py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg active:opacity-90 transition-opacity"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                fill="white"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="white"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="white"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="white"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </button>
          <p className="text-xs text-[#9ca3af] text-center">
            By continuing you agree to our Terms of Service
          </p>
        </div>
      </div>
    </div>
  );
}
