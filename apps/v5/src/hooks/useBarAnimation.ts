"use client";
import { useEffect } from "react";

export function useBarAnimation() {
  useEffect(() => {
    const timer = setTimeout(() => {
      document.querySelectorAll(".bar-anim").forEach((bar) => {
        const w = bar.getAttribute("data-width");
        if (w) (bar as HTMLElement).style.width = `${w}%`;
      });
    }, 200);
    return () => clearTimeout(timer);
  }, []);
}
