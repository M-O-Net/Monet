import { Link } from "@tanstack/react-router";

import { Latex } from "../../../components/Latex";
import { describeSource } from "../../../lib/provenance";
import { buildRelationHtml } from "../../../lib/relationTemplate";
import { relativeTime } from "../../../lib/relativeTime";
import type { EventOut, ObjectOut } from "../../../lib/types";
import { RelationExpression } from "../RelationExpression";

const EXCERPT_LENGTH = 280;

function Who({ name }: { name: string | null }) {
  if (name === null) return <span className="text-ink-soft">Someone</span>;
  return (
    <Link
      to="/feed"
      search={{ contributor: name }}
      className="font-medium text-ink underline decoration-dotted underline-offset-2 hover:text-pond"
    >
      {name}
    </Link>
  );
}

function ObjectLink({ object }: { object: ObjectOut }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: object.id }}
      className="relation-tag inline-block rounded-sm px-2 py-0.5 text-xs"
    >
      <Latex>{object.latex}</Latex>
    </Link>
  );
}

function excerpt(body: string): string {
  return body.length <= EXCERPT_LENGTH ? body : `${body.slice(0, EXCERPT_LENGTH).trimEnd()}…`;
}

export function FeedEntry({ event }: { event: EventOut }) {
  return (
    <li className="rounded-sm border border-mist bg-white/40 px-4 py-3 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      <p className="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm text-ink-soft">
        <Who name={event.contributor} />
        {event.kind === "object_created" && event.object && (
          <>
            <span>added</span>
            <ObjectLink object={event.object} />
          </>
        )}
        {event.kind === "relation_created" && <span>recorded a relation</span>}
        {event.kind === "comment_created" && event.object && (
          <>
            <span>commented on</span>
            <ObjectLink object={event.object} />
          </>
        )}
      </p>

      {event.kind === "relation_created" && event.relation && (
        <div className="mt-2 text-sm">
          <RelationExpression
            html={buildRelationHtml(event.relation, event.relation.display?.template ?? null, null)}
          />
        </div>
      )}
      {event.kind === "comment_created" && event.comment && (
        <blockquote className="mt-2 border-l-2 border-gold/50 pl-3 text-sm whitespace-pre-wrap text-ink">
          {excerpt(event.comment.body)}
        </blockquote>
      )}

      <p className="mt-1.5 text-[11px] text-ink-soft/80">
        {event.kind === "comment_created" ? "" : `${describeSource(event.source)} · `}
        <time dateTime={event.at} title={new Date(event.at).toLocaleString()}>
          {relativeTime(event.at)}
        </time>
      </p>
    </li>
  );
}
