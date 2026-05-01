import { Download, ExternalLink, PlayCircle } from "lucide-react";
import type { ContentItem } from "@/types";

interface ContentListProps {
  contents: ContentItem[];
}

export default function ContentList({ contents }: ContentListProps) {
  return (
    <ol className="space-y-sm">
      {contents.map((item) => {
        const isLink = item.content_type === "link";
        const isVideo = item.content_type === "video";

        return (
          <li
            key={item.id}
            className="bg-surface rounded-sm border border-secondary/20"
          >
            <div className="flex items-center gap-sm p-md min-h-11">
              {isVideo && (
                <PlayCircle className="w-4 h-4 text-tertiary flex-shrink-0" />
              )}
              {item.content_type === "download" && (
                <Download className="w-4 h-4 text-secondary flex-shrink-0" />
              )}
              {isLink && (
                <ExternalLink className="w-4 h-4 text-secondary flex-shrink-0" />
              )}

              {isVideo ? (
                <span className="font-label text-label text-foreground">
                  {item.title}
                </span>
              ) : (
                <a
                  href={item.content_url}
                  target={isLink ? "_blank" : "_self"}
                  rel={isLink ? "noopener noreferrer" : undefined}
                  className="font-label text-label text-foreground hover:text-tertiary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring transition-colors"
                >
                  {item.title}
                </a>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}