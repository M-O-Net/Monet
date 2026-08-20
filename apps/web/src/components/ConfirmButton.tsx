import { AlertDialog } from "@base-ui/react/alert-dialog";
import type { ReactNode } from "react";

export function ConfirmButton({
  label,
  title,
  description,
  confirmLabel,
  tone = "neutral",
  pending = false,
  className,
  onConfirm,
}: {
  label: ReactNode;
  title: string;
  description: ReactNode;
  confirmLabel: string;
  tone?: "neutral" | "danger";
  pending?: boolean;
  className?: string;
  onConfirm: () => void;
}) {
  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger className={className} disabled={pending}>
        {label}
      </AlertDialog.Trigger>
      <AlertDialog.Portal>
        <AlertDialog.Backdrop className="fixed inset-0 min-h-dvh bg-ink/25 backdrop-blur-[1px] transition-opacity duration-150 data-ending-style:opacity-0 data-starting-style:opacity-0" />
        <AlertDialog.Popup className="fixed top-1/2 left-1/2 flex w-[22rem] max-w-[calc(100vw-2rem)] -translate-x-1/2 -translate-y-1/2 flex-col gap-4 rounded-sm border border-mist bg-paper p-5 shadow-[0_8px_30px_rgba(35,50,43,0.18)] transition-[scale,opacity] duration-100 ease-out outline-none data-ending-style:scale-[0.98] data-ending-style:opacity-0 data-starting-style:scale-[0.98] data-starting-style:opacity-0">
          <div className="flex flex-col gap-1">
            <AlertDialog.Title className="font-display text-base text-ink">
              {title}
            </AlertDialog.Title>
            <AlertDialog.Description className="text-sm text-ink-soft">
              {description}
            </AlertDialog.Description>
          </div>
          <div className="flex justify-end gap-2">
            <AlertDialog.Close className="rounded-sm border border-mist px-3 py-1 text-xs text-ink-soft hover:bg-paper-deep">
              Cancel
            </AlertDialog.Close>
            <AlertDialog.Close
              onClick={onConfirm}
              className={
                tone === "danger"
                  ? "rounded-sm bg-rust px-3 py-1 text-xs font-medium text-paper hover:bg-rust/85"
                  : "rounded-sm bg-pond px-3 py-1 text-xs font-medium text-paper hover:bg-pond-deep"
              }
            >
              {confirmLabel}
            </AlertDialog.Close>
          </div>
        </AlertDialog.Popup>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
