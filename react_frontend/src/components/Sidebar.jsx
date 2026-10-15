import {
  LayoutDashboard,
  Sprout,
  Map,
  ChartNoAxesCombined,
  Settings,
  Leaf,
} from "lucide-react";

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Farm analysis", icon: Map, active: false },
  { label: "Yield predictions", icon: ChartNoAxesCombined, active: false },
  { label: "Crop cycles", icon: Sprout, active: false },
];

export default function Sidebar() {
  return (
    <aside className="flex w-full shrink-0 flex-col border-b border-white/10 bg-[#10251d] text-white md:min-h-screen md:w-64 md:border-b-0 md:border-r">
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-lime-400 text-[#10251d]">
          <Leaf size={23} />
        </div>

        <div>
          <h1 className="text-xl font-bold tracking-tight">Mkulima</h1>
          <p className="text-xs text-emerald-100/60">
            Agricultural intelligence
          </p>
        </div>
      </div>

      <div className="px-4 pb-3 pt-2">
        <p className="px-3 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-100/40">
          Workspace
        </p>
      </div>

      <nav className="flex gap-1 overflow-x-auto px-3 pb-4 md:flex-col">
        {navigation.map(({ label, icon: Icon, active }) => (
          <div
            key={label}
            className={`flex shrink-0 items-center gap-3 rounded-xl px-3 py-3 text-sm ${
              active
                ? "bg-lime-400 font-semibold text-[#10251d]"
                : "text-emerald-50/70"
            }`}
          >
            <Icon size={19} />
            <span>{label}</span>
          </div>
        ))}
      </nav>

      <div className="mt-auto hidden p-4 md:block">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="mb-2 flex items-center gap-2 text-lime-300">
            <Sprout size={18} />
            <span className="text-sm font-semibold">Mkulima Insights</span>
          </div>
          <p className="text-xs leading-5 text-emerald-50/60">
            Turn farm data into more informed agricultural decisions.
          </p>
        </div>

        <div className="mt-5 flex items-center gap-3 px-2 text-sm text-emerald-50/60">
          <Settings size={17} />
          <span>Settings</span>
        </div>
      </div>
    </aside>
  );
}