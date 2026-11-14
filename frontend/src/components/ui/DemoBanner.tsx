/** Shown on pages that still render static sample content instead of real data. */
export function DemoBanner() {
  return (
    <div
      role="note"
      className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900"
    >
      <strong className="font-semibold">Demo data.</strong> This page shows static sample content,
      not your positions or live market data. Do not use it for trading decisions.
    </div>
  );
}
