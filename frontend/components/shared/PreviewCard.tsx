interface PreviewCardProps {
  title: string;
  id?: string;
  contentId?: string;
  initialHtml?: string;
  children?: React.ReactNode;
}

export default function PreviewCard({ title, id, contentId, initialHtml, children }: PreviewCardProps) {
  return (
    <div
      id={id}
      className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm
                 overflow-auto max-h-96"
    >
      <div className="text-xs text-gray-400 font-sans font-semibold mb-2 uppercase tracking-wide">
        {title}
      </div>
      {initialHtml ? (
        <pre id={contentId} dangerouslySetInnerHTML={{ __html: initialHtml }} />
      ) : (
        children
      )}
    </div>
  );
}
