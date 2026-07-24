// Minimal markdown renderer for LLM output (headings, bullets, bold, paragraphs).
// Avoids pulling a full markdown dependency for our constrained output shape.

function inline(text: string) {
  // **bold**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={i} className="text-terminal-text">
        {p.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}

export function Markdown({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="space-y-2 text-sm leading-relaxed text-terminal-text/90">
      {lines.map((raw, i) => {
        const line = raw.trim();
        if (!line) return <div key={i} className="h-1" />;
        if (line.startsWith("# "))
          return (
            <h1 key={i} className="text-lg font-bold text-terminal-amber">
              {line.slice(2)}
            </h1>
          );
        if (line.startsWith("## "))
          return (
            <h2 key={i} className="mt-3 text-sm font-semibold uppercase tracking-wide text-terminal-amber">
              {line.slice(3)}
            </h2>
          );
        if (line.startsWith("### "))
          return (
            <h3 key={i} className="mt-2 font-semibold">
              {line.slice(4)}
            </h3>
          );
        if (/^[-*]\s/.test(line))
          return (
            <li key={i} className="ml-5 list-disc">
              {inline(line.replace(/^[-*]\s/, ""))}
            </li>
          );
        return <p key={i}>{inline(line)}</p>;
      })}
    </div>
  );
}
