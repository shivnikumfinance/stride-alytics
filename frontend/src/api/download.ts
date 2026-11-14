/** Download a CSV (or any file) from an authenticated API path. */

import client from "./client";

/** Pull the filename out of a Content-Disposition header, falling back to ``fallback``. */
export function filenameFromDisposition(header: string | undefined, fallback: string): string {
  const match = header?.match(/filename="?([^";]+)"?/i);
  return match?.[1] ?? fallback;
}

export async function downloadFile(path: string, fallbackName: string): Promise<void> {
  // The JWT is added by the axios client, so a plain <a href> would not work.
  const res = await client.get(path, { responseType: "blob" });
  const name = filenameFromDisposition(res.headers["content-disposition"] as string | undefined, fallbackName);
  const url = URL.createObjectURL(res.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
