"use client";
import { useCallback, useRef } from "react";

interface DragHandleProps {
  onResize: (terminalPercent: number) => void;
}

export function DragHandle({ onResize }: DragHandleProps) {
  const dragging = useRef(false);

  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      dragging.current = true;

      const mainEl = (e.target as HTMLElement).closest(".main");
      if (!mainEl) return;
      const rect = mainEl.getBoundingClientRect();
      // Subtract topbar height (~52px)
      const topbarHeight = 52;
      const availableHeight = rect.height - topbarHeight;

      const onMouseMove = (moveEvent: MouseEvent) => {
        if (!dragging.current) return;
        const relativeY = moveEvent.clientY - rect.top - topbarHeight;
        const percent = Math.min(90, Math.max(30, (relativeY / availableHeight) * 100));
        onResize(percent);
      };

      const onMouseUp = () => {
        dragging.current = false;
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    },
    [onResize]
  );

  return <div className="drag-handle" onMouseDown={onMouseDown} />;
}
