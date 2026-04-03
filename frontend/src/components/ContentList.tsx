"use client";

import { useState } from "react";
import { Download, ExternalLink, PlayCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { ContentItem } from "@/types";

interface ContentListProps {
  offeringId: string;
  initialContents: ContentItem[];
  totalContents: number;
  completedContents: number;
}

export default function ContentList({
  offeringId: _offeringId,
  initialContents,
  totalContents,
  completedContents: initialCompleted,
}: ContentListProps) {
  const [contents, setContents] = useState<ContentItem[]>(initialContents);
  const [expandedVideo, setExpandedVideo] = useState<string | null>(null);

  const completedCount = contents.filter((c) => c.completed).length;
  const progressPercent = totalContents > 0 ? Math.round((completedCount / totalContents) * 100) : 0;

  // initialCompleted is used only for the initial SSR render consistency
  void initialCompleted;

  async function toggleComplete(contentId: string, currentlyCompleted: boolean) {
    try {
      if (currentlyCompleted) {
        await api.unmarkComplete(contentId);
      } else {
        await api.markComplete(contentId);
      }
      setContents((prev) =>
        prev.map((c) => (c.id === contentId ? { ...c, completed: !c.completed } : c))
      );
    } catch {
      // silently ignore — user can retry
    }
  }

  function handleContentClick(item: ContentItem) {
    if (item.content_type === "video") {
      setExpandedVideo(expandedVideo === item.id ? null : item.id);
    } else {
      window.open(item.content_url, item.content_type === "link" ? "_blank" : "_self");
    }
  }

  function getVimeoEmbedUrl(url: string): string {
    const match = /vimeo\.com\/(\d+)/.exec(url);
    return match ? `https://player.vimeo.com/video/${match[1]}` : url;
  }

  return (
    <div>
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>
            {completedCount} de {totalContents} completados
          </span>
          <span>{progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-green-600 h-2 rounded-full transition-all"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Content list */}
      <ol className="space-y-2">
        {contents.map((item) => (
          <li key={item.id} className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="flex items-center gap-3 p-4">
              {/* Completion checkbox */}
              <button
                onClick={() => toggleComplete(item.id, item.completed)}
                className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  item.completed
                    ? "bg-green-600 border-green-600"
                    : "border-gray-300 hover:border-green-600"
                }`}
                aria-label={item.completed ? "Marcar como pendiente" : "Marcar como completado"}
              >
                {item.completed && (
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                    <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>

              {/* Content type icon */}
              <button
                onClick={() => handleContentClick(item)}
                className="flex items-center gap-2 flex-1 text-left hover:text-blue-600 transition-colors"
              >
                {item.content_type === "video" && (
                  <PlayCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                )}
                {item.content_type === "download" && (
                  <Download className="w-4 h-4 text-gray-500 flex-shrink-0" />
                )}
                {item.content_type === "link" && (
                  <ExternalLink className="w-4 h-4 text-gray-500 flex-shrink-0" />
                )}

                <span
                  className={`text-sm font-medium ${item.completed ? "text-gray-400 line-through" : "text-gray-900"}`}
                >
                  {item.title}
                </span>
              </button>
            </div>

            {/* Vimeo embed */}
            {item.content_type === "video" && expandedVideo === item.id && (
              <div className="px-4 pb-4">
                <div className="aspect-video">
                  <iframe
                    src={getVimeoEmbedUrl(item.content_url)}
                    className="w-full h-full rounded"
                    allowFullScreen
                    allow="autoplay; fullscreen; picture-in-picture"
                  />
                </div>
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
