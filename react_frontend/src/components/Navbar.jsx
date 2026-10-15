import { Bell, Sprout } from "lucide-react";

export default function Navbar() {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-stone-200 bg-white px-5 py-4 md:px-8">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.16em] text-stone-400">
          Workspace / Overview
        </p>
        <h2 className="mt-1 text-lg font-semibold text-stone-800">
          Farm intelligence dashboard
        </h2>
      </div>

      <div className="flex items-center gap-3">
        <span className="hidden items-center gap-2 rounded-full bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-800 sm:flex">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Mkulima API
        </span>

        <button
          type="button"
          aria-label="Notifications"
          className="rounded-xl border border-stone-200 p-2.5 text-stone-500"
        >
          <Bell size={18} />
        </button>

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#10251d] text-lime-300">
          <Sprout size={21} />
        </div>
      </div>
    </header>
  );
}