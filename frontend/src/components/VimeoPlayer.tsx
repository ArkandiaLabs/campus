const VIMEO_REGEX = /vimeo\.com\/(?:video\/)?(\d+)/;

interface VimeoPlayerProps {
  url: string | null | undefined;
  title: string;
}

export default function VimeoPlayer({ url, title }: VimeoPlayerProps) {
  const match = url ? url.match(VIMEO_REGEX) : null;
  const videoId = match?.[1];

  if (!videoId) {
    return (
      <div className="w-full aspect-video rounded-md bg-surface flex items-center justify-center">
        <p className="font-body text-body text-secondary">
          Grabación no disponible aún
        </p>
      </div>
    );
  }

  return (
    <div className="w-full aspect-video rounded-md overflow-hidden bg-surface">
      <iframe
        src={`https://player.vimeo.com/video/${videoId}`}
        title={`Grabación: ${title}`}
        allow="autoplay; fullscreen; picture-in-picture"
        allowFullScreen
        className="w-full h-full border-0"
      />
    </div>
  );
}
