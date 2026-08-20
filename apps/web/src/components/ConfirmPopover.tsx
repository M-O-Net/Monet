import { Popover } from "@base-ui/react/popover";
import { useState } from "react";

export function ConfirmPopover({
  trigger,
  triggerClassName,
  label,
  question,
  confirmLabel,
  onConfirm,
  disabled,
}: {
  trigger: React.ReactNode;
  triggerClassName: string;
  label: string;
  question: string;
  confirmLabel: string;
  onConfirm: () => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger
        disabled={disabled}
        title={label}
        aria-label={label}
        className={triggerClassName}
      >
        {trigger}
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner sideOffset={6} align="end" className="z-20 outline-none">
          <Popover.Popup className="w-60 rounded-sm border border-mist bg-paper p-3 shadow-[0_6px_20px_rgba(35,50,43,0.16)] outline-none">
            <Popover.Description className="text-xs text-ink">{question}</Popover.Description>
            <div className="mt-3 flex justify-end gap-2">
              <Popover.Close className="rounded-sm px-2 py-1 text-xs text-ink-soft transition-colors hover:bg-paper-deep hover:text-ink">
                Keep it
              </Popover.Close>
              <button
                onClick={() => {
                  setOpen(false);
                  onConfirm();
                }}
                className="rounded-sm bg-rust px-3 py-1 text-xs font-medium text-paper transition-colors hover:bg-rust/85"
              >
                {confirmLabel}
              </button>
            </div>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
