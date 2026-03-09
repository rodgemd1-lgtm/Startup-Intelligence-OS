"use client";

import { useEffect, useRef } from "react";

interface ProgressBarProps {
  value: number;
  color: string;
  animated?: boolean;
}

export function ProgressBar({ value, color, animated = true }: ProgressBarProps) {
  const fillRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (animated && fillRef.current) {
      const timer = setTimeout(() => {
        if (fillRef.current) {
          fillRef.current.style.width = `${value}%`;
        }
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [value, animated]);

  return (
    <div className="progress-track">
      <div
        ref={fillRef}
        className={`progress-fill ${color}`}
        style={{ width: animated ? "0%" : `${value}%` }}
      />
    </div>
  );
}
