import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { ContributorField } from "../components/ContributorField";
import { useContributor } from "../lib/contributor";
import { invalidateObjectGraph } from "../lib/queries";
import { InstanceForm } from "./-components/contribute/InstanceForm";
import { MapForm } from "./-components/contribute/MapForm";
import { TypeForm } from "./-components/contribute/TypeForm";

export const Route = createFileRoute("/contribute")({
  component: ContributePage,
});

const KINDS = {
  instance: "An object",
  type: "A type",
  map: "A map",
} as const;

type Kind = keyof typeof KINDS;

function ContributePage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [contributor, setContributor] = useContributor();
  const [kind, setKind] = useState<Kind>("instance");

  const open = (id: string) => {
    invalidateObjectGraph(queryClient);
    void navigate({ to: "/objects/$objectId", params: { objectId: id } });
  };

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">Contribute</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        Add something new to the network. To add to something that already exists — a comment, a
        reference, an implementation — open its page instead.
      </p>

      <div className="mb-5">
        <ContributorField value={contributor} onChange={setContributor} />
      </div>

      <div role="tablist" className="mb-6 flex gap-1 border-b border-mist">
        {(Object.keys(KINDS) as Kind[]).map((option) => (
          <button
            key={option}
            role="tab"
            aria-selected={kind === option}
            onClick={() => {
              setKind(option);
            }}
            className={`-mb-px border-b-2 px-3 py-2 text-sm ${
              kind === option
                ? "border-pond text-ink"
                : "border-transparent text-ink-soft hover:text-ink"
            }`}
          >
            {KINDS[option]}
          </button>
        ))}
      </div>

      {kind === "instance" && <InstanceForm contributor={contributor} onCreated={open} />}
      {kind === "type" && <TypeForm contributor={contributor} onCreated={open} />}
      {kind === "map" && <MapForm contributor={contributor} onCreated={open} />}
    </div>
  );
}
