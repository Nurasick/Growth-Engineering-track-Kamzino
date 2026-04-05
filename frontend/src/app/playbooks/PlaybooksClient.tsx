"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import {
  runPlaybookMetrics,
  runPlaybookAnalysis,
  runCounterPlaybook,
  getPipelineJob,
} from "@/lib/api";
import { useJob } from "@/lib/useJob";
import { JobCard } from "@/components/JobCard";

// ─── Types ────────────────────────────────────────────────────────────────────

type Block =
  | { kind: "h1"; text: string }
  | { kind: "h2"; text: string }
  | { kind: "h3"; text: string }
  | { kind: "hr" }
  | { kind: "blockquote"; lines: string[] }
  | { kind: "codeblock"; lang: string; code: string }
  | { kind: "table"; headers: string[]; rows: string[][] }
  | { kind: "ul"; items: string[] }
  | { kind: "ol"; items: string[] }
  | { kind: "p"; text: string };

// ─── Inline renderer ──────────────────────────────────────────────────────────

const INLINE_RE =
  /!\[[^\]]*\]\([^)]*\)|\*\*([^*]+)\*\*|\*([^*\n]+)\*|`([^`]+)`|\[([^\]]+)\]\(([^)]*)\)/g;

function renderInline(text: string): ReactNode {
  const nodes: ReactNode[] = [];
  let last = 0;
  let key = 0;
  INLINE_RE.lastIndex = 0;
  let m: RegExpExecArray | null;

  while ((m = INLINE_RE.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    const full = m[0];

    if (full.startsWith("![")) {
      // skip images — they reference local file paths
    } else if (full.startsWith("**")) {
      nodes.push(
        <strong key={key++} className="text-white font-semibold">
          {m[1]}
        </strong>
      );
    } else if (full.startsWith("*")) {
      nodes.push(
        <em key={key++} className="italic text-white/60">
          {m[2]}
        </em>
      );
    } else if (full.startsWith("`")) {
      nodes.push(
        <code
          key={key++}
          className="bg-[#1a1a1a] border border-[#2a2a2a] rounded px-1.5 py-0.5 text-xs font-mono text-[#CAFF33]"
        >
          {m[3]}
        </code>
      );
    } else if (full.startsWith("[")) {
      nodes.push(
        <span key={key++} className="text-[#CAFF33]/80">
          {m[4]}
        </span>
      );
    }

    last = m.index + full.length;
  }

  if (last < text.length) nodes.push(text.slice(last));
  return nodes.length === 1 ? nodes[0] : <>{nodes}</>;
}

// ─── Parser ───────────────────────────────────────────────────────────────────

function parseRow(line: string): string[] {
  return line
    .split("|")
    .slice(1, -1)
    .map((c) => c.trim());
}

function isSeparatorRow(line: string): boolean {
  return /^\|[\s\-:|]+\|/.test(line);
}

function parse(md: string): Block[] {
  const lines = md.split("\n");
  const blocks: Block[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const code: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        code.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      blocks.push({ kind: "codeblock", lang, code: code.join("\n") });
      continue;
    }

    // Headers
    if (line.startsWith("### ")) {
      blocks.push({ kind: "h3", text: line.slice(4) });
      i++;
      continue;
    }
    if (line.startsWith("## ")) {
      blocks.push({ kind: "h2", text: line.slice(3) });
      i++;
      continue;
    }
    if (line.startsWith("# ")) {
      blocks.push({ kind: "h1", text: line.slice(2) });
      i++;
      continue;
    }

    // Horizontal rule
    if (line.trim() === "---") {
      blocks.push({ kind: "hr" });
      i++;
      continue;
    }

    // Blockquote
    if (line.startsWith(">")) {
      const bq: string[] = [];
      while (i < lines.length && lines[i].startsWith(">")) {
        bq.push(lines[i].slice(1).trim());
        i++;
      }
      blocks.push({ kind: "blockquote", lines: bq });
      continue;
    }

    // Table
    if (line.startsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const headers = parseRow(tableLines[0]);
      const rows = tableLines
        .slice(1)
        .filter((l) => !isSeparatorRow(l))
        .map(parseRow);
      blocks.push({ kind: "table", headers, rows });
      continue;
    }

    // Unordered list
    if (/^\s*-\s/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*-\s/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*-\s/, ""));
        i++;
      }
      blocks.push({ kind: "ul", items });
      continue;
    }

    // Ordered list
    if (/^\d+\.\s/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s/, ""));
        i++;
      }
      blocks.push({ kind: "ol", items });
      continue;
    }

    // Empty line
    if (line.trim() === "") {
      i++;
      continue;
    }

    // Paragraph — accumulate consecutive non-block lines
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !lines[i].startsWith("#") &&
      !lines[i].startsWith(">") &&
      !lines[i].startsWith("|") &&
      !lines[i].startsWith("```") &&
      !/^\s*-\s/.test(lines[i]) &&
      !/^\d+\.\s/.test(lines[i]) &&
      lines[i].trim() !== "---"
    ) {
      para.push(lines[i]);
      i++;
    }
    if (para.length > 0) {
      blocks.push({ kind: "p", text: para.join(" ") });
    }
  }

  return blocks;
}

// ─── Block renderer ───────────────────────────────────────────────────────────

function MarkdownRenderer({ content }: { content: string }) {
  const blocks = parse(content);

  return (
    <div className="space-y-4 text-sm leading-relaxed text-white/65">
      {blocks.map((block, idx) => {
        switch (block.kind) {
          case "h1":
            return (
              <h1
                key={idx}
                className="text-2xl font-bold text-white tracking-tight pt-4 pb-1"
              >
                {renderInline(block.text)}
              </h1>
            );

          case "h2":
            return (
              <h2
                key={idx}
                className="text-base font-bold text-[#CAFF33] uppercase tracking-widest pt-8 pb-1"
              >
                {renderInline(block.text)}
              </h2>
            );

          case "h3":
            return (
              <h3
                key={idx}
                className="text-sm font-semibold text-white/90 pt-4 pb-0.5"
              >
                {renderInline(block.text)}
              </h3>
            );

          case "hr":
            return <hr key={idx} className="border-[#242424] my-6" />;

          case "blockquote": {
            // Split on blank lines within the blockquote
            const paras = block.lines
              .join("\n")
              .split(/\n{2,}/)
              .map((p) => p.replace(/\n/g, " ").trim())
              .filter(Boolean);
            return (
              <blockquote
                key={idx}
                className="border-l-2 border-[#CAFF33]/30 pl-4 py-0.5 space-y-2 text-white/45 italic"
              >
                {paras.map((p, pi) => (
                  <p key={pi}>{renderInline(p)}</p>
                ))}
              </blockquote>
            );
          }

          case "codeblock":
            return (
              <div
                key={idx}
                className="rounded border border-[#2a2a2a] bg-[#0f0f0f] overflow-x-auto"
              >
                {block.lang && (
                  <div className="px-4 py-1.5 border-b border-[#2a2a2a] text-xs text-white/25 font-mono">
                    {block.lang}
                  </div>
                )}
                <pre className="p-4 text-xs font-mono text-[#CAFF33]/70 leading-relaxed whitespace-pre">
                  {block.code}
                </pre>
              </div>
            );

          case "table":
            return (
              <div key={idx} className="overflow-x-auto rounded border border-[#242424]">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#111]">
                      {block.headers.map((h, hi) => (
                        <th
                          key={hi}
                          className="text-left px-3 py-2.5 text-white/35 uppercase tracking-wider font-medium border-b border-[#242424]"
                        >
                          {renderInline(h)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {block.rows.map((row, ri) => (
                      <tr
                        key={ri}
                        className="border-b border-[#1a1a1a] hover:bg-[#141414] transition-colors"
                      >
                        {row.map((cell, ci) => (
                          <td key={ci} className="px-3 py-2 text-white/60">
                            {renderInline(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );

          case "ul":
            return (
              <ul key={idx} className="space-y-1.5 ml-2">
                {block.items.map((item, ii) => (
                  <li key={ii} className="flex gap-2.5 items-start">
                    <span className="text-[#CAFF33]/50 shrink-0 mt-px select-none">–</span>
                    <span>{renderInline(item)}</span>
                  </li>
                ))}
              </ul>
            );

          case "ol":
            return (
              <ol key={idx} className="space-y-1.5 ml-2">
                {block.items.map((item, ii) => (
                  <li key={ii} className="flex gap-2.5 items-start">
                    <span className="text-[#CAFF33]/50 shrink-0 font-mono tabular-nums mt-px">
                      {ii + 1}.
                    </span>
                    <span>{renderInline(item)}</span>
                  </li>
                ))}
              </ol>
            );

          case "p":
            return (
              <p key={idx} className="text-white/65 leading-relaxed">
                {renderInline(block.text)}
              </p>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}

// ─── Generate button ─────────────────────────────────────────────────────────

function GenerateButton({
  label,
  description,
  action,
  accent,
}: {
  label: string;
  description: string;
  action: () => Promise<{ job_id: string }>;
  accent?: boolean;
}) {
  const { job, loading, error, start } = useJob(getPipelineJob);
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded border border-[#242424] bg-[#141414] p-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-medium text-white">{label}</div>
          <div className="text-xs text-white/35 mt-0.5">{description}</div>
        </div>
        <button
          onClick={() => start(action)}
          disabled={busy}
          className={`shrink-0 rounded px-4 py-1.5 text-xs font-bold uppercase tracking-wide transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${
            accent
              ? "bg-[#CAFF33] text-black hover:bg-[#b3e020]"
              : "border border-[#333] text-white/60 hover:border-[#CAFF33] hover:text-[#CAFF33]"
          }`}
        >
          {busy ? "Running…" : "▶ Run"}
        </button>
      </div>
      {error && (
        <p className="text-xs text-red-400 rounded bg-red-950/20 border border-red-900/30 px-3 py-2">
          {error}
        </p>
      )}
      {job && <JobCard job={job} />}
    </div>
  );
}

// ─── Exported component ───────────────────────────────────────────────────────

const TABS = [
  { id: "analysis", label: "Playbook Analysis" },
  { id: "counter", label: "Counter Playbook" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export function PlaybooksClient({
  analysis,
  counter,
}: {
  analysis: string;
  counter: string;
}) {
  const [tab, setTab] = useState<TabId>("analysis");

  const content = tab === "analysis" ? analysis : counter;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Playbooks</h1>
        <p className="mt-1 text-sm text-white/40">
          HackNU 2026 · Growth Engineering Track · Parts 2 &amp; 4
        </p>
      </div>

      {/* Generate */}
      <div>
        <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Generate</h2>
        <div className="space-y-2">
          <GenerateButton
            label="Compute Playbook Metrics"
            description="compute_playbook_metrics.py — builds analysis_metrics.json used by generators"
            action={runPlaybookMetrics}
          />
          <GenerateButton
            label="Generate Playbook Analysis"
            description="generate_playbook_analysis.py — writes PLAYBOOK_ANALYSIS_GENERATED.md"
            action={runPlaybookAnalysis}
            accent
          />
          <GenerateButton
            label="Generate Counter Playbook"
            description="generate_counter_playbook.py — writes COUNTER_PLAYBOOK_GENERATED.md"
            action={runCounterPlaybook}
          />
        </div>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-2 flex-wrap">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`rounded px-4 py-2 text-xs font-bold tracking-wide uppercase transition-colors ${
              tab === id
                ? "bg-[#CAFF33] text-black"
                : "border border-[#333] text-white/40 hover:border-[#CAFF33] hover:text-[#CAFF33]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Markdown content */}
      <div className="rounded border border-[#242424] bg-[#141414] px-6 py-8">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
}
