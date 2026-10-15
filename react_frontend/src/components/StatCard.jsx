export default function StatCard({
  label,
  value,
  description,
  icon: Icon,
  accent = "green",
}) {
  const accents = {
    green: "bg-emerald-50 text-emerald-700",
    lime: "bg-lime-50 text-lime-700",
    blue: "bg-sky-50 text-sky-700",
    amber: "bg-amber-50 text-amber-700",
  };

  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-stone-500">{label}</p>
          <h3 className="mt-3 text-2xl font-bold tracking-tight text-stone-900">
            {value}
          </h3>
        </div>

        <div className={`rounded-xl p-3 ${accents[accent] || accents.green}`}>
          {Icon && <Icon size={21} />}
        </div>
      </div>

      <p className="mt-4 text-xs leading-5 text-stone-400">{description}</p>
    </div>
  );
}