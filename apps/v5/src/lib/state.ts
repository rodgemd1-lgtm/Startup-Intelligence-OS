import { getGreeting } from "./utils";

export interface AppContext {
  name: string;
  mode: string;
  front_door: string;
  foundry: string;
  active_company: string;
  active_project: string;
  active_decision: string;
  active_branch: string;
}

export interface AppStatus {
  decisions: number;
  capabilities: number;
  projects: number;
  companies: number;
  runs: number;
  evidence: number;
  artifacts: number;
}

export interface Debrief {
  greeting: string;
  actions: Record<string, string[]>;
}

export interface DecisionOption {
  title: string;
  scores: Record<string, number>;
  total: number;
}

export interface Decision {
  id: string;
  title: string;
  status: string;
  context: string;
  options: DecisionOption[];
}

export interface Capability {
  name: string;
  maturity: number;
  target: number;
  gaps: string[];
  wave: number;
}

export interface Agent {
  name: string;
  group: string;
  role: string;
}

export interface VisionItem {
  year: string;
  label: string;
  title: string;
  desc: string;
  current?: boolean;
}

export interface AppState {
  context: AppContext;
  status: AppStatus;
  debrief: Debrief;
  decisions: Decision[];
  capabilities: Capability[];
  agents: Agent[];
  vision: VisionItem[];
}

export const defaultState: AppState = {
  context: {
    name: "startup-intelligence-os",
    mode: "decision-capability-os",
    front_door: "jake",
    foundry: "susan",
    active_company: "founder-intelligence-os",
    active_project: "decision-capability-os",
    active_decision: "phase-a-runtime-foundation",
    active_branch: "main",
  },
  status: {
    decisions: 2,
    capabilities: 6,
    projects: 1,
    companies: 1,
    runs: 2,
    evidence: 0,
    artifacts: 0,
  },
  debrief: {
    greeting: getGreeting(),
    actions: {
      mike: [
        "Run Innovation Studio for 5-year strategic vision",
        "Review 25X capability assessment (12 domains mapped)",
        "Audit 6 capabilities for maturity progression",
        "Wire decision engine debate to Claude API",
      ],
    },
  },
  decisions: [
    {
      id: "dec-87215ce29d09",
      title: "Adopt event-driven architecture for data pipeline",
      status: "proposed",
      context:
        "Current batch processing creates 4-hour lag. Event-driven could reduce to minutes.",
      options: [
        {
          title: "Kafka-based streaming",
          scores: { feasibility: 72, impact: 88, risk: 65, speed: 60 },
          total: 76,
        },
        {
          title: "Scoped CDC experiment",
          scores: { feasibility: 85, impact: 75, risk: 80, speed: 82 },
          total: 84,
        },
        {
          title: "Defer and optimize batch",
          scores: { feasibility: 90, impact: 40, risk: 95, speed: 90 },
          total: 61,
        },
      ],
    },
    {
      id: "dec-motion-ui-v1",
      title: "Motion UI narrative strategy for TransformFit",
      status: "draft",
      context:
        "Define the motion language that communicates progress, effort, and recovery.",
      options: [
        {
          title: "Minimal motion shell",
          scores: { feasibility: 90, impact: 55, risk: 90, speed: 88 },
          total: 72,
        },
        {
          title: "Motion narrative + telemetry",
          scores: { feasibility: 78, impact: 85, risk: 75, speed: 70 },
          total: 80,
        },
        {
          title: "Full adaptive coaching now",
          scores: { feasibility: 45, impact: 92, risk: 50, speed: 35 },
          total: 58,
        },
      ],
    },
  ],
  capabilities: [
    {
      name: "Decision Kernel",
      maturity: 2,
      target: 4,
      gaps: ["LLM debate", "evidence scoring", "outcome tracking"],
      wave: 1,
    },
    {
      name: "Capability Management",
      maturity: 2,
      target: 4,
      gaps: ["automated discovery", "outcome-based scoring"],
      wave: 1,
    },
    {
      name: "Innovation & Strategy",
      maturity: 1.8,
      target: 4,
      gaps: [
        "future-back planning",
        "scenario branching",
        "assumption register",
      ],
      wave: 2,
    },
    {
      name: "UX & Design",
      maturity: 2.2,
      target: 4,
      gaps: ["design system", "Figma integration", "visual artifacts"],
      wave: 2,
    },
    {
      name: "Agent Orchestration",
      maturity: 2,
      target: 4.5,
      gaps: ["semantic routing", "agent memory", "multi-agent reasoning"],
      wave: 1,
    },
    {
      name: "Studio Operations",
      maturity: 1.8,
      target: 4,
      gaps: [
        "studio writeback",
        "case libraries",
        "experiment tracking",
      ],
      wave: 2,
    },
    {
      name: "Intelligence & Research",
      maturity: 2.8,
      target: 4.5,
      gaps: [
        "triangulation",
        "contradiction detection",
        "coverage mapping",
      ],
      wave: 1,
    },
    {
      name: "Portfolio Management",
      maturity: 1.8,
      target: 4,
      gaps: ["multi-company orchestration", "cross-pollination"],
      wave: 3,
    },
    {
      name: "Operator Experience",
      maturity: 1.5,
      target: 4,
      gaps: ["real-time dashboard", "proactive suggestions"],
      wave: 1,
    },
    {
      name: "Platform Infrastructure",
      maturity: 1.3,
      target: 4,
      gaps: ["auth", "CI/CD", "monitoring", "WebSockets"],
      wave: 1,
    },
    {
      name: "Content & Marketing",
      maturity: 1.8,
      target: 4,
      gaps: ["publishing pipeline", "asset cascade", "proof spines"],
      wave: 3,
    },
    {
      name: "Data & Analytics",
      maturity: 1.2,
      target: 4,
      gaps: ["outcome tracking", "feedback loops", "A/B testing"],
      wave: 1,
    },
  ],
  agents: [
    { name: "Susan", group: "orchestration", role: "Team architect & orchestrator" },
    { name: "Steve", group: "strategy", role: "Business strategy" },
    { name: "Shield", group: "strategy", role: "Legal compliance" },
    { name: "Bridge", group: "strategy", role: "Partnerships" },
    { name: "Ledger", group: "strategy", role: "Finance & unit economics" },
    { name: "Vault", group: "strategy", role: "Fundraising" },
    { name: "Herald", group: "growth", role: "PR & communications" },
    { name: "Marcus", group: "product", role: "UX/UI design" },
    { name: "Mira", group: "product", role: "Emotional experience" },
    { name: "Lens", group: "product", role: "Accessibility" },
    { name: "Echo", group: "product", role: "Neuroscience-informed design" },
    { name: "Compass", group: "product", role: "Product management" },
    { name: "Prism", group: "product", role: "Brand strategy" },
    { name: "Atlas", group: "engineering", role: "Full-stack engineering" },
    { name: "Nova", group: "engineering", role: "AI/ML strategy" },
    { name: "Pulse", group: "engineering", role: "Data science" },
    { name: "Sentinel", group: "engineering", role: "Security" },
    { name: "Forge", group: "engineering", role: "QA & testing" },
    { name: "Coach", group: "science", role: "Exercise science" },
    { name: "Sage", group: "science", role: "Nutrition science" },
    { name: "Drift", group: "science", role: "Sleep & recovery" },
    { name: "Freya", group: "psychology", role: "Behavioral economics" },
    { name: "Flow", group: "psychology", role: "Sports psychology" },
    { name: "Quest", group: "psychology", role: "Gamification" },
    { name: "Aria", group: "growth", role: "Growth strategy" },
    { name: "Haven", group: "growth", role: "Community" },
    { name: "Guide", group: "growth", role: "Customer success" },
    { name: "Beacon", group: "growth", role: "ASO & SEO" },
    { name: "Research-Web", group: "research", role: "Web research" },
    { name: "Research-Reddit", group: "research", role: "Reddit intelligence" },
    { name: "Research-ArXiv", group: "research", role: "Academic papers" },
    { name: "Research-AppStore", group: "research", role: "App store analysis" },
    { name: "Design Studio Director", group: "studio", role: "Design doctrine & critique" },
    { name: "Landing Page Studio", group: "studio", role: "Acquisition surfaces" },
    { name: "App Experience Studio", group: "studio", role: "Onboarding & retention" },
    { name: "Marketing Studio Director", group: "studio", role: "Message architecture" },
    { name: "Deck Studio", group: "studio", role: "Executive decks" },
    { name: "Article Studio", group: "studio", role: "Thought leadership" },
    { name: "Social Media Studio", group: "studio", role: "Social content" },
    { name: "Algorithm Lab", group: "engineering", role: "Algorithm R&D" },
  ],
  vision: [
    {
      year: "2026",
      label: "Year 0 \u2014 Now",
      title: "Stabilize + Ship",
      desc: "Decision kernel stable. TransformFit prototype. Agent evaluation framework. 40K+ RAG chunks.",
      current: true,
    },
    {
      year: "2027",
      label: "Year 1",
      title: "Foundation",
      desc: "TransformFit ships to app stores. 50K+ chunks. Susan foundry proven for 3+ companies. Agent eval live.",
    },
    {
      year: "2028",
      label: "Year 2",
      title: "Portfolio Expansion",
      desc: "5+ companies. 30-day launch protocol. Automated daily ops. Agent memory v1. Cross-company intel v1.",
    },
    {
      year: "2029",
      label: "Year 3",
      title: "Inflection Point",
      desc: "Multi-operator alpha. Agent memory v2. Studios 70% autonomous. Decision rooms automated. 80+ agents.",
    },
    {
      year: "2030",
      label: "Year 4",
      title: "Platform Maturity",
      desc: "5+ paying operators. Agent factory ships. $100K+ ARR. 3 domain packs published.",
    },
    {
      year: "2031",
      label: "Year 5",
      title: "North Star",
      desc: "10+ companies. $500K+ ARR. 120+ agents. Autonomous operations. Capability marketplace.",
    },
  ],
};
