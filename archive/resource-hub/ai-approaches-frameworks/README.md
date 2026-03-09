# AI Approaches, Frameworks & Skill Sets

A comprehensive guide to AI architectures, engineering approaches, team building, and the techniques that power modern AI products.

---

## 1. AI Architecture Approaches

### Model Architectures

| Architecture | Description | Key Models | Use Case |
|-------------|-------------|------------|----------|
| **Transformers** | Attention-based architecture. Foundation of all modern LLMs. | GPT-4, Claude, Gemini, Llama | Text generation, reasoning, code |
| **Mixture of Experts (MoE)** | Route tokens to specialized sub-networks. More efficient at scale. | Mixtral, DeepSeek-V3, GPT-4 (rumored) | Scaling with efficiency |
| **State Space Models (SSMs)** | Linear-time sequence modeling. Alternative to attention. | Mamba, Jamba, Zamba | Long sequences, efficiency |
| **Diffusion Models** | Iterative denoising process for generation. | Stable Diffusion, DALL-E 3, Midjourney | Image/video/audio generation |
| **Neurosymbolic AI** | Combine neural networks with symbolic reasoning. | Various research | Reasoning, explainability |
| **Retrieval-Augmented Generation** | Ground LLM outputs in retrieved knowledge. | RAG systems | Knowledge-intensive tasks |
| **Vision Transformers (ViT)** | Apply transformers to image patches. | CLIP, DINOv2, SAM | Computer vision |
| **Multimodal Models** | Process text, image, audio, video in one model. | GPT-4o, Gemini, Claude 4.5 | Cross-modal understanding |
| **Graph Neural Networks** | Process graph-structured data. | GCN, GAT, GraphSAGE | Social networks, molecules |
| **Flow Matching** | Newer generation paradigm, faster than diffusion. | Stable Diffusion 3, Flux | Image generation |

### Architecture Decision Framework

```
Text-only tasks? → Transformer (GPT, Claude, Llama)
Need efficiency at scale? → MoE (Mixtral) or SSM (Mamba)
Image generation? → Diffusion or Flow Matching
Need grounding in facts? → RAG architecture
Reasoning + rules? → Neurosymbolic or tool-use agents
Multi-modal? → Multimodal transformers (GPT-4o, Gemini)
```

---

## 2. Agent Frameworks Comparison

### Detailed Framework Comparison

| Framework | Language | Architecture | Multi-Agent | Tool Use | Memory | Production-Ready |
|-----------|----------|-------------|-------------|----------|--------|-----------------|
| [CrewAI](https://github.com/crewAIInc/crewAI) | Python | Role-based crews | Yes (core feature) | Yes | Yes | Yes |
| [AutoGen](https://github.com/microsoft/autogen) | Python | Conversational agents | Yes (core feature) | Yes | Yes | Yes |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Python/JS | Graph-based state machines | Yes | Yes | Yes | Yes |
| [Claude Agent SDK](https://docs.anthropic.com) | Python/TS | Single/multi-agent | Yes | Yes (MCP) | Yes | Yes |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Python | Handoff-based | Yes | Yes | Limited | Yes |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel) | C#/Py/Java | Plugin-based | Yes | Yes | Yes | Yes |
| [Phidata](https://github.com/phidatahq/phidata) | Python | Assistant-based | Yes | Yes | Yes | Yes |
| [Smolagents](https://github.com/huggingface/smolagents) | Python | Code-first | Limited | Yes | Limited | Growing |

### When to Use What

| Scenario | Best Framework | Why |
|----------|---------------|-----|
| Team of specialized agents | **CrewAI** | Built for role-based agent teams |
| Complex stateful workflows | **LangGraph** | Graph-based state management |
| Multi-turn conversations | **AutoGen** | Conversational agent design |
| Claude-powered products | **Claude Agent SDK** | Native Claude integration, MCP |
| Enterprise/.NET | **Semantic Kernel** | Microsoft ecosystem, multi-language |
| Quick prototypes | **Phidata** | Fastest to get started |
| Research/experimentation | **Smolagents** | Clean, simple, Hugging Face models |

---

## 3. Multi-Agent & Orchestration Patterns

### Core Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Sequential Chain** | Agent A → Agent B → Agent C | Linear workflows, pipelines |
| **Parallel Fan-Out** | Coordinator → [Agent A, B, C] → Aggregator | Independent tasks, speed-critical |
| **Hierarchical** | Manager Agent → Worker Agents → Sub-Workers | Complex projects, super nesting |
| **Debate/Adversarial** | Agent A argues for, Agent B argues against | Quality assurance, red teaming |
| **Consensus** | Multiple agents vote on best answer | High-stakes decisions |
| **Router** | Classifier routes to specialized agents | Multi-domain applications |
| **Swarm** | Self-organizing agent collective | Emergent problem solving |
| **Handoff** | Agent transfers conversation to specialist | Customer service, escalation |

### Super Nesting Architecture

```
Orchestrator Agent (Level 0)
├── Research Agent (Level 1)
│   ├── Web Search Sub-Agent (Level 2)
│   ├── Code Analysis Sub-Agent (Level 2)
│   └── Data Extraction Sub-Agent (Level 2)
├── Analysis Agent (Level 1)
│   ├── Financial Modeling Sub-Agent (Level 2)
│   └── Risk Assessment Sub-Agent (Level 2)
├── Implementation Agent (Level 1)
│   ├── Frontend Sub-Agent (Level 2)
│   ├── Backend Sub-Agent (Level 2)
│   └── Testing Sub-Agent (Level 2)
└── Review Agent (Level 1)
    ├── Code Review Sub-Agent (Level 2)
    └── Security Audit Sub-Agent (Level 2)
```

**Key Principles for Super Nesting:**
1. Each level should have clear responsibility boundaries
2. Parent agents should only communicate goals, not implementation details
3. Sub-agents should be stateless when possible
4. Use structured output schemas between levels
5. Implement circuit breakers to prevent infinite recursion
6. Log at every level for observability

---

## 4. Prompt Engineering Techniques

### Foundational Techniques

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| **Zero-Shot** | Direct instruction, no examples | Simple, well-defined tasks |
| **Few-Shot** | Provide examples of input/output pairs | Pattern learning, formatting |
| **Chain of Thought (CoT)** | "Think step by step" — force explicit reasoning | Math, logic, multi-step reasoning |
| **Tree of Thought (ToT)** | Explore multiple reasoning paths, evaluate each | Complex problem-solving |
| **ReAct** | Reason + Act. Interleave thinking with tool use. | Agentic tasks with tools |
| **Self-Consistency** | Generate multiple CoT paths, take majority vote | High-stakes reasoning |
| **Structured Output** | Force JSON/XML/schema output | API responses, data extraction |
| **System Prompts** | Define persona, rules, context upfront | All production applications |

### Advanced Techniques

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| **Meta-Prompting** | Use LLM to generate/optimize prompts | Prompt optimization |
| **Constitutional AI** | Self-critique against principles | Safety, alignment |
| **Prompt Chaining** | Output of prompt A becomes input of prompt B | Multi-step workflows |
| **Retrieval-Augmented Prompting** | Inject retrieved context into prompts | Knowledge-grounded tasks |
| **Tool Use / Function Calling** | LLM calls external tools/APIs | Agentic applications |
| **Reflection/Self-Correction** | LLM reviews and improves its own output | Quality improvement |
| **Skeleton of Thought** | Generate outline first, then expand | Long-form content |

### Resources
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) — 52k+ ★ on GitHub

---

## 5. Fine-Tuning Approaches

| Technique | Description | Compute Needed | When to Use |
|-----------|-------------|---------------|-------------|
| **Full Fine-Tuning** | Update all model parameters | Very high (multi-GPU) | Maximum customization, large budgets |
| **LoRA** | Train small adapter matrices | Medium (single GPU) | Most common. Best efficiency/quality tradeoff |
| **QLoRA** | LoRA on quantized models | Low (consumer GPU) | Budget-constrained, experimentation |
| **PEFT** | Parameter-efficient methods (umbrella term) | Low-Medium | Any resource-constrained scenario |
| **RLHF** | Train reward model, then PPO | Very high | Alignment, instruction following |
| **DPO** | Direct preference optimization (no reward model) | High | Simpler alternative to RLHF |
| **ORPO** | Odds ratio preference optimization | Medium | Newest, promising results |
| **Continued Pre-Training** | Extend pre-training on domain data | Very high | Domain adaptation |
| **Instruction Tuning** | Fine-tune on instruction-response pairs | Medium | General instruction following |
| **Distillation** | Train small model to mimic large model | Medium | Cost reduction, edge deployment |

### Decision Guide
```
Have <$100 GPU budget? → QLoRA with Unsloth
Have a single A100? → LoRA with Axolotl
Enterprise budget? → Full fine-tune or RLHF
Want behavior alignment? → DPO (simpler) or RLHF (best quality)
Need domain knowledge? → Continued pre-training + LoRA
Want smaller model? → Distillation from large teacher
```

---

## 6. AI Evaluation & Benchmarking

### LLM Evaluation Frameworks

| Framework | Description | Link |
|-----------|-------------|------|
| [LMSYS Chatbot Arena](https://chat.lmsys.org) | Crowdsourced LLM comparison via blind voting | Gold standard for model ranking |
| [HELM](https://crfm.stanford.edu/helm) | Stanford's Holistic Evaluation of Language Models | Comprehensive academic benchmarks |
| [OpenCompass](https://github.com/open-compass/opencompass) | Open-source LLM evaluation platform | 50+ benchmarks |
| [Eleuther Eval Harness](https://github.com/EleutherAI/lm-evaluation-harness) | Framework for evaluating LLMs across tasks | Standard eval framework |
| [DeepEval](https://github.com/confident-ai/deepeval) | Unit testing for LLM outputs | CI/CD friendly |
| [RAGAS](https://github.com/explodinggradients/ragas) | RAG evaluation (faithfulness, relevance, etc.) | RAG-specific |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Test and evaluate LLM prompts | Prompt engineering |

### Key Metrics for AI Products

| Metric | What It Measures | How to Measure |
|--------|-----------------|----------------|
| **Accuracy/Correctness** | Does the AI give right answers? | Ground truth comparison |
| **Faithfulness** | Is the output grounded in provided context? | RAGAS, human eval |
| **Relevance** | Is the response relevant to the query? | Embedding similarity, human eval |
| **Latency** | Time to first token / full response | Monitoring tools |
| **Cost per query** | Token usage × price | API monitoring |
| **User satisfaction** | Do users find it useful? | Thumbs up/down, NPS |
| **Hallucination rate** | How often does it make things up? | Fact-checking against sources |
| **Task completion rate** | Does the AI successfully complete the user's task? | End-to-end testing |

---

## 7. AI Engineering Skill Sets

### Roles for an AI Startup Team

| Role | Core Skills | When to Hire |
|------|------------|-------------|
| **AI/ML Engineer** | PyTorch, training, fine-tuning, model optimization | When building custom models |
| **LLM Engineer** | Prompt engineering, RAG, agent frameworks, API integration | Day 1 — core role for AI products |
| **MLOps Engineer** | Kubernetes, model serving, CI/CD for ML, monitoring | When scaling to production |
| **Data Engineer** | Data pipelines, ETL, vector DBs, data quality | When data is a competitive moat |
| **Full-Stack AI Engineer** | Frontend + backend + LLM integration. Unicorn role. | Startups (0-10 employees) |
| **AI Product Manager** | Understands LLM capabilities/limitations, can write prompts | From product-market fit stage |
| **AI Safety/Red Team** | Adversarial testing, guardrails, compliance | Before shipping to users |
| **Research Engineer** | Papers → production. Implements latest research. | When innovation is key |

### Must-Have Technical Skills (2025-2026)

**For Founders:**
- Prompt engineering (intermediate level minimum)
- Understanding of RAG vs fine-tuning tradeoffs
- Agent architecture patterns
- AI cost estimation and optimization
- Basic understanding of model capabilities and limitations

**For Engineers:**
- Python + TypeScript
- At least one LLM framework (LangChain, LlamaIndex, or Vercel AI SDK)
- Vector databases (at least one: Pinecone, Qdrant, pgvector)
- API design for AI products (streaming, tool use)
- Testing and evaluation of LLM outputs
- Claude/OpenAI API proficiency

---

## 8. MLOps & AI Process Frameworks

### CI/CD for ML

| Tool | Description | Link |
|------|-------------|------|
| **GitHub Actions** | Standard CI/CD, works for ML pipelines | [github.com/features/actions](https://github.com/features/actions) |
| **DVC** | Data Version Control. Git for data and models. | [github.com/iterative/dvc](https://github.com/iterative/dvc) |
| **CML** | CI/CD for ML. By the DVC team. | [github.com/iterative/cml](https://github.com/iterative/cml) |
| **Metaflow** | Human-friendly ML framework. By Netflix. | [github.com/Netflix/metaflow](https://github.com/Netflix/metaflow) |
| **Prefect** | Workflow orchestration for data and ML. | [github.com/PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) |
| **Airflow** | Workflow orchestration. Industry standard. | [github.com/apache/airflow](https://github.com/apache/airflow) |
| **ZenML** | MLOps framework for reproducible pipelines. | [github.com/zenml-io/zenml](https://github.com/zenml-io/zenml) |

### Recommended AI Development Process

```
1. PROBLEM DEFINITION
   └── Define success metrics before writing code

2. DATA COLLECTION & PREPARATION
   └── Curate evaluation datasets first (before building)

3. PROTOTYPE (1-2 weeks)
   └── Start with prompts + RAG, NOT fine-tuning
   └── Use the best model (Claude/GPT-4) first, optimize later

4. EVALUATE
   └── Build eval suite early — this is your "test suite"
   └── Measure accuracy, latency, cost

5. ITERATE
   └── Prompt optimization → RAG tuning → fine-tuning (only if needed)
   └── Each iteration should improve eval metrics

6. PRODUCTIONIZE
   └── Add guardrails, monitoring, error handling
   └── Implement fallbacks (e.g., fallback to larger model)

7. MONITOR & IMPROVE
   └── Track production quality with LLM observability tools
   └── Collect user feedback for continuous improvement
```

---

## 9. Emerging Capabilities & What's Coming

### 2025-2026 Trends to Watch

| Trend | Description | Impact |
|-------|-------------|--------|
| **Agentic AI** | AI that can autonomously plan, execute multi-step tasks, use tools | Transformative for productivity |
| **Computer Use** | AI that can control a computer (mouse, keyboard, screen) | Anthropic Claude, OpenAI |
| **Long Context** | 1M+ token context windows becoming standard | Reduces need for RAG in some cases |
| **Multimodal Native** | Models that natively process text, image, audio, video | Richer AI products |
| **Small Language Models** | Phi-4, Gemma 2, Qwen — competitive in small packages | Edge deployment, cost reduction |
| **AI Reasoning** | o1/o3-style "thinking" models that reason before answering | Complex problem-solving |
| **Model Merging** | Combine multiple fine-tuned models without retraining | Rapid model customization |
| **MCP (Model Context Protocol)** | Standard protocol for AI tool use (by Anthropic) | Interoperability between AI tools |
| **AI-Native Development** | Building software with AI as a core primitive, not an add-on | New development paradigm |
| **Synthetic Data** | AI-generated training data for other AI models | Reduces data bottleneck |

---

*Last updated: March 2026*
