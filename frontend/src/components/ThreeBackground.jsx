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
      mousePos.current = {
        x: e.clientX,
        y: e.clientY
      };
    };
    window.addEventListener('pointermove', handlePointerMove);

    const draw = () => {
      // Add new point with timestamp for fading
      points.current.push({ 
        x: mousePos.current.x, 
        y: mousePos.current.y,
        time: Date.now()
      });
      
      // Keep trail short (15 points instead of 40)
      if (points.current.length > 15) points.current.shift();
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (points.current.length < 3) {
        animationFrameId = requestAnimationFrame(draw);
        return;
      }

      // Draw smooth curve using quadratic bezier
      ctx.beginPath();
      ctx.moveTo(points.current[0].x, points.current[0].y);
      
      for (let i = 1; i < points.current.length - 1; i++) {
        const p0 = points.current[i - 1];
        const p1 = points.current[i];
        const p2 = points.current[i + 1];
        
        // Calculate control point for smooth curve
        const cpX = p1.x;
        const cpY = p1.y;
        const endX = (p1.x + p2.x) / 2;
        const endY = (p1.y + p2.y) / 2;
        
        ctx.quadraticCurveTo(cpX, cpY, endX, endY);
      }
      
      // Connect to last point
      const lastPoint = points.current[points.current.length - 1];
      ctx.lineTo(lastPoint.x, lastPoint.y);
      
      // Gradient stroke for fading effect
      const gradient = ctx.createLinearGradient(
        points.current[0].x, points.current[0].y,
        lastPoint.x, lastPoint.y
      );
      gradient.addColorStop(0, 'rgba(255, 255, 255, 0)');
      gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.4)');
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0.8)');
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
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