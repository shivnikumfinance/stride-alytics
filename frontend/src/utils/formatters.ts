/** Small formatting helpers (numbers, currency, IV, dates). */

const USD = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});

const NUM = new Intl.NumberFormat("en-US", { maximumFractionDigits: 4 });

export const fmtUsd = (v: number | null | undefined) =>
  v === null || v === undefined ? "—" : USD.format(v);

export const fmtNum = (v: number | null | undefined, digits = 4) =>
  v === null || v === undefined ? "—" : NUM.format(Number(v.toFixed(digits)));

export const fmtPct = (v: number | null | undefined, digits = 2) =>
  v === null || v === undefined ? "—" : `${(v * 100).toFixed(digits)}%`;

export const fmtIv = (v: number | null | undefined) => fmtPct(v, 1);

export const fmtDate = (iso: string | null | undefined) =>
  !iso ? "—" : new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });

export const classNames = (...c: (string | false | null | undefined)[]) =>
  c.filter(Boolean).join(" ");
