"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

const VIEW_MAP: Record<string, string> = {
  "1": "/",
  "2": "/decisions",
  "3": "/capabilities",
  "4": "/innovation",
  "5": "/agents",
  "6": "/dashboard",
};

export function useKeyboard() {
  const router = useRouter();

  useEffect(() => {
    function handleKeydown(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (VIEW_MAP[e.key]) {
        router.push(VIEW_MAP[e.key]);
      }
    }
    document.addEventListener("keydown", handleKeydown);
    return () => document.removeEventListener("keydown", handleKeydown);
  }, [router]);
}
