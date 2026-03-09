export function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning, Mike";
  if (h < 17) return "Good afternoon, Mike";
  return "Evening, Mike";
}

export function maturityLabel(n: number): string {
  if (n <= 1) return "nascent";
  if (n <= 2) return "emerging";
  if (n <= 3) return "scaling";
  if (n <= 4) return "optimizing";
  return "leading";
}

export function maturityColor(n: number): string {
  if (n <= 1.5) return "danger";
  if (n <= 2.5) return "warning";
  if (n <= 3.5) return "accent";
  return "success";
}

export const groupColors: Record<string, string> = {
  orchestration: "#a78bfa",
  strategy: "#f0b45a",
  product: "#5b8def",
  engineering: "#5cd4a0",
  science: "#e88a5a",
  psychology: "#e06565",
  growth: "#5abbe8",
  research: "#8ba4cc",
  studio: "#d48aef",
};

export function delay(i: number) {
  return { style: { "--d": `${i * 60}ms` } as Record<string, string> };
}
