import { useEffect } from "react";
import { useUiStore } from "../../store";
import { classNames } from "../../utils";

export function Toaster() {
  const toasts = useUiStore((s) => s.toasts);
  const dismiss = useUiStore((s) => s.dismissToast);

  useEffect(() => {
    if (toasts.length === 0) return;
    const t = setTimeout(() => dismiss(toasts[0].id), 4000);
    return () => clearTimeout(t);
  }, [toasts, dismiss]);

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 w-80">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={classNames(
            "rounded-md px-4 py-3 text-sm shadow-md border",
            t.kind === "success" && "bg-green-50 border-green-200 text-green-800",
            t.kind === "error" && "bg-red-50 border-red-200 text-red-800",
            t.kind === "info" && "bg-white border-gray-200 text-gray-800",
          )}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
