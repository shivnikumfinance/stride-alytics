import { useAcceptDisclaimer, useSettings } from "../../hooks/queries";
import { Button } from "../ui";

/**
 * First-login disclaimer (docs: Business §2, §11). Shown until it is accepted; the acceptance is
 * stored with a timestamp. If settings cannot be loaded the modal is not shown (it never blocks
 * the app on an error), but it appears again on the next successful load.
 */
export function DisclaimerModal() {
  const settings = useSettings();
  const accept = useAcceptDisclaimer();

  if (!settings.data || settings.data.disclaimer_accepted_at !== null) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 px-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="disclaimer-title"
        className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl"
      >
        <h2 id="disclaimer-title" className="text-lg font-semibold text-gray-900">
          Before you start
        </h2>
        <div className="mt-3 space-y-2 text-sm text-gray-700">
          <p>
            StrideAlytics is an analytics and decision-support tool. <strong>It is not financial advice.</strong>
          </p>
          <p>
            All rules and thresholds are configurable defaults, and options trading can lose more than
            you expect. Paper-trade and backtest before using real capital, and consult a licensed
            financial professional before trading.
          </p>
        </div>
        {accept.isError && (
          <p role="alert" className="mt-3 text-sm text-red-600">
            Could not save your acceptance. Try again.
          </p>
        )}
        <div className="mt-5 flex justify-end">
          <Button loading={accept.isPending} onClick={() => accept.mutate()}>
            I understand
          </Button>
        </div>
      </div>
    </div>
  );
}
