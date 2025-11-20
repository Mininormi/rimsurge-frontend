// components/HeroVideo.tsx
export default function HeroVideo() {
    return (
      <div
        className="
          fixed top-0 left-0 
          w-screen h-screen 
          -z-10 overflow-hidden
        "
      >
        {/* Vimeo 全屏背景视频 */}
        <iframe
          src="https://player.vimeo.com/video/1115222113?dnt=1&app_id=122963&autoplay=1&muted=1&loop=1&background=1"
          className="absolute top-0 left-0 w-full h-full object-cover"
          allow="autoplay; fullscreen; picture-in-picture"
          frameBorder="0"
          style={{ pointerEvents: "none" }}
        />
  
        {/* 黑色透明遮罩，让文字可读 */}
        <div className="absolute inset-0 bg-black/40" />
      </div>
    );
  }
  