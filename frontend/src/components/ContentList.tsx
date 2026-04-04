import { Download, ExternalLink, PlayCircle } from "lucide-react";
import type { ContentItem } from "@/types";

interface ContentListProps {
  contents: ContentItem[];
}

export default function ContentList({ contents }: ContentListProps) {
  return (
    <ol className="space-y-2">
      {contents.map((item) => (
        <li key={item.id} className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="flex items-center gap-3 p-4">
            {item.content_type === "video" && (
              <PlayCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
            )}
            {item.content_type === "download" && (
              <Download className="w-4 h-4 text-gray-500 flex-shrink-0" />
            )}
            {item.content_type === "link" && (
              <ExternalLink className="w-4 h-4 text-gray-500 flex-shrink-0" />
            )}

            {item.content_type === "video" ? (
              <span className="text-sm font-medium text-gray-900">{item.title}</span>
            ) : (
              <a
                href={item.content_url}
                target={item.content_type === "link" ? "_blank" : "_self"}
                rel={item.content_type === "link" ? "noopener noreferrer" : undefined}
                className="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors"
              >
                {item.title}
              </a>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
