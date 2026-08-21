import { Link } from "@tanstack/react-router";

export function Header() {
  return (
    <header className="mb-10">
      <div className="flex items-start justify-between">
        <div>
          {/* Hovering (or keyboard-focusing) anywhere on the wordmark expands all three
              segments together: "M·O·Net" -> "Mathematical·Object·Network". The hidden
              remainder of each word is `max-width: 0` + `overflow-hidden`, transitioning to
              a generous cap on group-hover/focus — Tailwind can't express an animated
              max-width target sized to each word's actual content, so the cap is a
              hand-picked arbitrary value per segment rather than something derived.
              `align-bottom` on every piece, not `align-baseline`: an inline-block with
              `overflow: hidden` uses its bottom margin edge as its baseline per spec instead
              of its text's baseline, so mixing baseline-aligned plain text with
              baseline-aligned-but-actually-bottom-aligned overflow:hidden boxes made
              "Mathematical" float above "·O·Net" — aligning everything to the bottom edge
              instead sidesteps the mismatch entirely. `aria-label` gives screen readers the
              full name regardless of hover/focus state, since the visible text content alone
              ("M·O·Net") would otherwise be all they get. Each cap is close to that word's
              actual rendered width, not a round/generous number — `max-width` past the point
              content is fully visible is animation time that never shows on screen, so a
              loose cap makes the reveal look done well before the transition finishes while
              the collapse (which always travels the full visible distance back to 0) plays
              out its whole duration — the same duration value, but a visibly faster-feeling
              expand. Timing function is `steps(N, end)` (N = that word's letter count), not
              `ease`/`ease-in-out` — max-width moves in N discrete jumps instead of one
              continuous swipe, reading as a typewriter both typing in on hover and
              backspacing out on hover-end, in both directions since it's the base timing
              function rather than only a `group-hover` override. */}
          <Link
            to="/"
            className="group font-display text-3xl font-medium tracking-tight text-ink"
            style={{ textWrap: "balance" }}
            aria-label="M·O·Net — Mathematical Object Network"
          >
            <span className="inline-block align-bottom">M</span>
            <span className="inline-block max-w-0 overflow-hidden align-bottom whitespace-nowrap transition-[max-width] duration-500 [transition-timing-function:steps(11,end)] group-hover:max-w-[7em] group-focus-visible:max-w-[7em]">
              athematical
            </span>
            <span className="text-gold">·</span>
            <span className="inline-block align-bottom">O</span>
            <span className="inline-block max-w-0 overflow-hidden align-bottom whitespace-nowrap transition-[max-width] duration-[220ms] delay-75 [transition-timing-function:steps(5,end)] group-hover:max-w-[3.5em] group-focus-visible:max-w-[3.5em]">
              bject
            </span>
            <span className="text-gold">·</span>
            <span className="inline-block align-bottom">Net</span>
            <span className="inline-block max-w-0 overflow-hidden align-bottom whitespace-nowrap transition-[max-width] duration-[180ms] delay-150 [transition-timing-function:steps(4,end)] group-hover:max-w-[3em] group-focus-visible:max-w-[3em]">
              work
            </span>
          </Link>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="font-display text-sm italic text-ink-soft">
            a field journal of mathematics
          </span>
          <Link
            to="/map"
            className="text-xs text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond"
          >
            the network
          </Link>
        </div>
      </div>
      <div
        className="mt-3 h-px w-full"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to right, var(--color-mist) 0 6px, transparent 6px 10px)",
        }}
      />
    </header>
  );
}
