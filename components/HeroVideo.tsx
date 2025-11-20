// components/HeroVideo.tsx
export default function HeroVideo() {
    return (
      <div className="fixed inset-0 -z-10 h-screen w-screen overflow-hidden">
        <iframe
          src="https://player.vimeo.com/video/1115222113?background=1&autoplay=1&muted=1&loop=1"
          className="absolute inset-0 h-full w-full object-cover"
          allow="autoplay; fullscreen; picture-in-picture"
          frameBorder="0"
          style={{ pointerEvents: "none" }}
        />
  
        {/* 黑色遮罩让文字可读 */}
        <div className="absolute inset-0 bg-black/40" />
      </div>
    );
  }
  