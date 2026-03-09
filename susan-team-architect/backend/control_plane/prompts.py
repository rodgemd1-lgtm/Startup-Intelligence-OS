"""Prompt compilation helpers for agent authoring files."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import re

import yaml

from .schemas import PromptBundle, PromptComponent, PromptEvalResult

SYSTEM_SAFETY_POLICY = """System priorities:
1. Safety > retention > growth > features.
2. Ground claims in available evidence and say when context is missing.
3. Prefer direct, specific recommendations over generic advice.
4. Use structured outputs when the task calls for planning or execution.
"""

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROMPT_LIBRARY_DIR = BACKEND_ROOT / "data" / "prompt_library"
AGENT_CHARACTERISTICS_PATH = BACKEND_ROOT / "data" / "agent_characteristics.yaml"


def authoring_agent_id(path_or_stem: Path | str) -> str:
    stem = path_or_stem.stem if isinstance(path_or_stem, Path) else path_or_stem
    if stem.startswith("researcher-"):
        return stem
    return stem.split("-", 1)[0]


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        _, _, remainder = text.partition("\n")
        frontmatter, sep, body = remainder.partition("\n---\n")
        if sep:
            return yaml.safe_load(frontmatter) or {}, body
    return {}, text


def _parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    chunks = re.split(r"(?=^##\s+)", body, flags=re.MULTILINE)
    for chunk in chunks:
        match = re.match(r"^##\s+(.*)$", chunk.strip(), flags=re.MULTILINE)
        if not match:
            continue
        heading = match.group(1).strip()
        content = chunk.split("\n", 1)[1].strip() if "\n" in chunk else ""
        sections[heading] = content
    return sections


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def _compose_sections(sections: dict[str, str], names: list[str]) -> str:
    blocks: list[str] = []
    for name in names:
        content = sections.get(name, "").strip()
        if content:
            blocks.append(f"{name}:\n{content}")
    return "\n\n".join(blocks).strip()


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_shared_prompt_library() -> tuple[str, str]:
    meta_prompt_path = PROMPT_LIBRARY_DIR / "meta_prompts.md"
    workflow_tree_path = PROMPT_LIBRARY_DIR / "workflow_trees.yaml"

    meta_prompt_text = _load_text(meta_prompt_path).strip()
    workflow_trees = _load_yaml(workflow_tree_path).get("trees", [])
    workflow_summary = "\n".join(
        f"- {tree['id']}: {' -> '.join(tree.get('nodes', []))}"
        for tree in workflow_trees
        if tree.get("id")
    ).strip()
    return meta_prompt_text, workflow_summary


def load_agent_characteristics(agent_id: str) -> dict:
    profiles = _load_yaml(AGENT_CHARACTERISTICS_PATH).get("agents", {})
    return profiles.get(agent_id, {})


def _component_list(frontmatter: dict, sections: dict[str, str], agent_id: str) -> list[PromptComponent]:
    name = frontmatter.get("name", agent_id)
    description = frontmatter.get("description", "")
    shared_meta_prompts, workflow_summary = _load_shared_prompt_library()
    characteristics = load_agent_characteristics(agent_id)
    conversation_style = _first_non_empty(
        sections.get("Conversation Style"),
        characteristics.get("conversation_style"),
    )
    debate_protocol = _first_non_empty(
        sections.get("Debate Protocol"),
        characteristics.get("debate_protocol"),
    )
    uncertainty_protocol = _first_non_empty(
        sections.get("Uncertainty Protocol"),
        characteristics.get("uncertainty_protocol"),
    )
    habits = characteristics.get("meeting_habits", [])
    trait_line = ", ".join(characteristics.get("traits", []))

    meta_policy = SYSTEM_SAFETY_POLICY + "\n" + _first_non_empty(
        sections.get("Output Standards"),
        "Deliver evidence-first output. Flag uncertainties and safety concerns explicitly.",
    )
    if shared_meta_prompts:
        meta_policy += "\n\nShared meta-prompts:\n" + shared_meta_prompts
    agent_kernel = _first_non_empty(
        f"You are {name}. {description}".strip(),
        sections.get("Identity"),
        f"You are {agent_id}.",
    ) + "\n\n" + _first_non_empty(sections.get("Identity"))
    if trait_line:
        agent_kernel += f"\n\nTraits: {trait_line}"
    task_program = _first_non_empty(
        sections.get("Your Role"),
        sections.get("Role"),
    ) + "\n\n" + _first_non_empty(
        sections.get("Specialization"),
        sections.get("Specializations"),
    )
    doctrine_blocks = _compose_sections(
        sections,
        [
            "Cognitive Architecture",
            "Doctrine",
            "Contrarian Beliefs",
            "Innovation Heuristics",
            "Reasoning Modes",
            "Value Detection",
            "Experiment Logic",
            "5 Whys Protocol",
            "JTBD Frame",
            "Moments of Truth",
            "Emotional Outcome Map",
            "Science Router",
        ],
    )
    if doctrine_blocks:
        task_program += "\n\n" + doctrine_blocks
    if conversation_style:
        task_program += "\n\nConversation style:\n" + conversation_style
    if habits:
        task_program += "\n\nMeeting habits:\n" + "\n".join(f"- {habit}" for habit in habits)
    if debate_protocol:
        task_program += "\n\nDebate protocol:\n" + debate_protocol
    context_pack = _first_non_empty(sections.get("Context"))
    strategic_context = _compose_sections(
        sections,
        [
            "What Changed",
            "Canonical Frameworks",
            "Design Principles",
            "Best-in-Class References",
            "RAG Knowledge Types",
        ],
    )
    if strategic_context:
        context_pack = (context_pack + "\n\n" + strategic_context).strip() if context_pack else strategic_context
    if not context_pack:
        context_pack = "Use the knowledge base and tools configured for this agent."
    if workflow_summary:
        context_pack += "\n\nWorkflow trees:\n" + workflow_summary
    critic_program = _first_non_empty(
        _compose_sections(
            sections,
            [
                "Output Contract",
                "Failure Modes",
                "Collaboration Triggers",
                "Output Standards",
            ],
        ),
        "Before finalizing, check factual grounding, actionability, and missing evidence.",
    ) + "\n\nCritique checklist:\n- Is the recommendation grounded?\n- Are missing facts called out?\n- Is the next step specific?"
    if uncertainty_protocol:
        critic_program += "\n\nUncertainty protocol:\n" + uncertainty_protocol
    if shared_meta_prompts:
        critic_program += "\n\nShared review behaviors:\nAdmit missing information, surface disagreements, and propose the next evidence to acquire."

    return [
        PromptComponent(name="meta_policy", content=meta_policy.strip()),
        PromptComponent(name="agent_kernel", content=agent_kernel.strip()),
        PromptComponent(name="task_program", content=task_program.strip()),
        PromptComponent(name="context_pack", content=context_pack.strip()),
        PromptComponent(name="critic_program", content=critic_program.strip()),
    ]


def compile_prompt_bundle(path: Path) -> PromptBundle:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)
    sections = _parse_sections(body)
    agent_id = authoring_agent_id(path)
    components = _component_list(frontmatter, sections, agent_id)

    digest = sha256(raw.encode("utf-8")).hexdigest()
    version = digest[:12]

    failures: list[str] = []
    schema_valid = all(component.content.strip() for component in components)
    if not schema_valid:
        failures.append("One or more prompt stack components are empty.")

    citations_present = bool(re.search(r"https?://|\[[^\]]+\]\(", raw))
    if not citations_present:
        failures.append("Prompt authoring file contains no inline citations or links.")

    eval_passed = schema_valid and len(components[1].content.split()) >= 20 and len(components[2].content.split()) >= 20
    if not eval_passed:
        failures.append("Prompt lint requires richer identity and task sections before promotion.")

    ready_for_promotion = schema_valid and citations_present and eval_passed
    status = "ready" if ready_for_promotion else "blocked"

    evaluation = PromptEvalResult(
        bundle_id=agent_id,
        version=version,
        schema_valid=schema_valid,
        citations_present=citations_present,
        eval_passed=eval_passed,
        ready_for_promotion=ready_for_promotion,
        failures=failures,
    )

    return PromptBundle(
        id=agent_id,
        name=frontmatter.get("name", agent_id),
        source_agent=agent_id,
        version=version,
        digest=digest,
        status=status,
        compiled_at=datetime.now(UTC),
        source_paths=[str(path)],
        components=components,
        eval=evaluation,
    )


def compile_prompt_bundle_for_agent(
    agent_id: str,
    authoring_dir: Path,
    fallback_name: str | None = None,
    fallback_role: str | None = None,
    fallback_system_prompt: str | None = None,
) -> PromptBundle:
    for path in sorted(authoring_dir.glob("*.md")):
        if authoring_agent_id(path) == agent_id or path.stem == agent_id or path.stem.startswith(f"{agent_id}-"):
            return compile_prompt_bundle(path)

    fallback_source = "\n".join(
        part for part in [
            fallback_name or agent_id,
            fallback_role or "",
            fallback_system_prompt or "",
        ] if part
    ).strip()
    raw = f"---\nname: {fallback_name or agent_id}\n---\n## Identity\n{fallback_source}\n\n## Your Role\n{fallback_role or 'Provide specialist support.'}\n\n## RAG Knowledge Types\nUse configured knowledge retrieval.\n\n## Output Standards\nBe specific and evidence-first.\n"
    temp_path = authoring_dir / f"{agent_id}.generated.md"
    return compile_prompt_bundle_from_text(agent_id, raw, temp_path)


def compile_prompt_bundle_from_text(agent_id: str, raw: str, source_path: Path) -> PromptBundle:
    frontmatter, body = _parse_frontmatter(raw)
    sections = _parse_sections(body)
    components = _component_list(frontmatter, sections, agent_id)
    digest = sha256(raw.encode("utf-8")).hexdigest()
    version = digest[:12]
    evaluation = PromptEvalResult(
        bundle_id=agent_id,
        version=version,
        schema_valid=True,
        citations_present=False,
        eval_passed=True,
        ready_for_promotion=False,
        failures=["Generated fallback manifest has no source citations."],
    )
    return PromptBundle(
        id=agent_id,
        name=frontmatter.get("name", agent_id),
        source_agent=agent_id,
        version=version,
        digest=digest,
        status="blocked",
        compiled_at=datetime.now(UTC),
        source_paths=[str(source_path)],
        components=components,
        eval=evaluation,
    )


def render_runtime_prompt(bundle: PromptBundle) -> str:
    rendered: list[str] = []
    for component in bundle.components:
        rendered.append(f"<{component.name}>\n{component.content}\n</{component.name}>")
    return "\n\n".join(rendered)
