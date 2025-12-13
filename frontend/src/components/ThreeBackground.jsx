import React, { useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars, Sparkles } from '@react-three/drei';

function Nebula() {
  // Simple nebula effect using sparkles
  return (
    <Sparkles
      count={120}
      speed={0.5}
      size={2.5}
      color="#a855f7"
      opacity={0.18}
      scale={[8, 4, 8]}
      position={[0, 0, 0]}
    />
  );
}

function MouseTrailCanvas() {
  const canvasRef = useRef();
  const points = useRef([]);
  const mousePos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      canvas.style.width = '100vw';
      canvas.style.height = '100vh';
    };
    resize();
    window.addEventListener('resize', resize);

    const handlePointerMove = (e) => {
      // Use clientX/clientY for viewport tracking
      mousePos.current = {
        x: e.clientX,
        y: e.clientY
      };
    };
    window.addEventListener('pointermove', handlePointerMove);

    const draw = () => {
      points.current.push({ x: mousePos.current.x, y: mousePos.current.y });
      if (points.current.length > 40) points.current.shift();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      for (let i = 0; i < points.current.length; i++) {
        const p = points.current[i];
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = 'rgba(255,255,255,0.85)';
      ctx.lineWidth = 2;
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
      ctx.stroke();
      animationFrameId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('pointermove', handlePointerMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ position: 'fixed', left: 0, top: 0, zIndex: 20, pointerEvents: 'none', width: '100vw', height: '100vh' }}
    />
  );
}

const ThreeBackground = () => (
  <>
    <div className="fixed inset-0 -z-10 w-full h-full pointer-events-none">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
        {/* Star field */}
        <Stars radius={120} depth={60} count={8000} factor={6} saturation={0.8} fade speed={2.5} />
        {/* Nebula */}
        <Nebula />
        <ambientLight intensity={0.9} />
        <directionalLight position={[8, 8, 8]} intensity={1.5} />
      </Canvas>
    </div>
    <MouseTrailCanvas />
  </>
);

export default ThreeBackground;