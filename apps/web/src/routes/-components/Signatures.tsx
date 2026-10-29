import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { ObjectPicker } from "../../components/ObjectPicker";
import { api } from "../../lib/api";
import type { ObjectOut, SignatureOut } from "../../lib/types";

function TypeLink({ type }: { type: ObjectOut }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: type.id }}
      className="rounded-full bg-willow/15 px-2.5 py-0.5 text-xs text-ink transition-colors hover:bg-willow/30"
    >
      <Latex>{type.latex}</Latex>
    </Link>
  );
}

export function Signatures({
  mapId,
  signatures,
  onChanged,
}: {
  mapId: string;
  signatures: SignatureOut[];
  onChanged: () => void;
}) {
  const addSignature = api.useMutation("post", "/objects/{object_id}/signatures");
  const removeSignature = api.useMutation("delete", "/signatures/{signature_id}");
  const [domain, setDomain] = useState<ObjectOut | null>(null);
  const [codomain, setCodomain] = useState<ObjectOut | null>(null);

  return (
    <section className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Signatures
      </h2>
      {signatures.length > 0 && (
        <ul className="mb-3 space-y-1.5">
          {signatures.map((signature) => (
            <li key={signature.id} className="flex flex-wrap items-center gap-2 text-sm">
              <TypeLink type={signature.domain} />
              <span className="text-ink-soft" aria-label="to">
                →
              </span>
              <TypeLink type={signature.codomain} />
              <button
                type="button"
                onClick={() => {
                  removeSignature.mutate(
                    { params: { path: { signature_id: signature.id } } },
                    { onSuccess: onChanged },
                  );
                }}
                className="text-xs text-ink-soft hover:text-rust"
                aria-label="Remove this signature"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      <form
        className="flex flex-wrap items-center gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (domain === null || codomain === null) return;
          addSignature.mutate(
            {
              params: { path: { object_id: mapId } },
              body: { domain_id: domain.id, codomain_id: codomain.id },
            },
            {
              onSuccess: () => {
                setDomain(null);
                setCodomain(null);
                onChanged();
              },
            },
          );
        }}
      >
        <div className="w-48">
          <ObjectPicker
            value={domain}
            onChange={setDomain}
            filter={{ role: "type" }}
            placeholder="from…"
          />
        </div>
        <span className="text-ink-soft">→</span>
        <div className="w-48">
          <ObjectPicker
            value={codomain}
            onChange={setCodomain}
            filter={{ role: "type" }}
            placeholder="to…"
          />
        </div>
        <button
          type="submit"
          disabled={domain === null || codomain === null || addSignature.isPending}
          className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
        >
          Add a signature
        </button>
      </form>
      {addSignature.isError && (
        <p className="mt-2 text-xs text-rust">{formatApiError(addSignature.error)}</p>
      )}
    </section>
  );
}
