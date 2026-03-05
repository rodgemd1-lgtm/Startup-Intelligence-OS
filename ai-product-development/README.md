# AI Product Development Resources

Everything you need to build, deploy, and scale AI products as a startup founder.

---

## 1. LLM Application Frameworks

### Core Frameworks

| Framework | GitHub | Description | Best For |
|-----------|--------|-------------|----------|
| [LangChain](https://github.com/langchain-ai/langchain) | 100k+ ★ | The most popular LLM application framework. Chains, agents, RAG, tools. | General-purpose LLM apps |
| [LlamaIndex](https://github.com/run-llama/llama_index) | 38k+ ★ | Data framework for LLM applications. Best-in-class for RAG. | Data-intensive RAG systems |
| [Haystack](https://github.com/deepset-ai/haystack) | 18k+ ★ | End-to-end NLP/LLM framework by deepset. Production-oriented. | Enterprise search & RAG |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel) | 22k+ ★ | Microsoft's LLM orchestration SDK. C#, Python, Java. | Microsoft/.NET ecosystems |
| [DSPy](https://github.com/stanfordnlp/dspy) | 20k+ ★ | Stanford's framework for programming (not prompting) LLMs. Optimizes prompts automatically. | Research-grade prompt optimization |
| [Vercel AI SDK](https://github.com/vercel/ai) | 12k+ ★ | TypeScript toolkit for building AI apps. Streaming, tool use, multi-model. | Next.js/React AI apps |

### Agent Frameworks

| Framework | GitHub | Description | Best For |
|-----------|--------|-------------|----------|
| [CrewAI](https://github.com/crewAIInc/crewAI) | 25k+ ★ | Multi-agent orchestration framework. Role-based agent design. | Team-of-agents patterns |
| [AutoGen](https://github.com/microsoft/autogen) | 35k+ ★ | Microsoft's multi-agent conversation framework. | Complex multi-agent workflows |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 8k+ ★ | Stateful, multi-actor LLM applications as graphs. By LangChain. | Stateful agent workflows |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents) | — | Anthropic's official SDK for building Claude-powered agents | Claude-based products |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | 5k+ ★ | OpenAI's agent framework with handoffs and guardrails | OpenAI-based products |
| [Phidata](https://github.com/phidatahq/phidata) | 15k+ ★ | Build AI assistants with memory, knowledge, and tools. | Production AI assistants |
| [Smolagents](https://github.com/huggingface/smolagents) | 5k+ ★ | Hugging Face's lightweight agent framework. Code-first approach. | Simple, clean agent design |

---

## 2. AI Model Providers

| Provider | Models | Strengths | API Link |
|----------|--------|-----------|----------|
| **Anthropic** | Claude 4.5/4.6 (Opus, Sonnet, Haiku) | Best reasoning, safety, long context (200k tokens) | [anthropic.com](https://www.anthropic.com) |
| **OpenAI** | GPT-4o, o1, o3, GPT-4.5 | Broadest ecosystem, multimodal, image generation | [openai.com](https://openai.com) |
| **Google** | Gemini 2.0, Gemini Ultra | Massive context (1M+ tokens), multimodal | [ai.google.dev](https://ai.google.dev) |
| **Meta** | Llama 3.x (open-source) | Best open-weight models, free to use | [llama.meta.com](https://llama.meta.com) |
| **Mistral** | Mistral Large, Mixtral, Codestral | European AI, strong coding models | [mistral.ai](https://mistral.ai) |
| **Cohere** | Command R+ | Enterprise RAG, multilingual | [cohere.com](https://cohere.com) |
| **xAI** | Grok | Real-time data access, large context | [x.ai](https://x.ai) |
| **DeepSeek** | DeepSeek-V3, DeepSeek-R1 | Open-source, competitive with closed models | [deepseek.com](https://www.deepseek.com) |

### Model Routing & Aggregators

| Service | Description | Link |
|---------|-------------|------|
| **OpenRouter** | Single API for 100+ models. Pay-per-token across providers. | [openrouter.ai](https://openrouter.ai) |
| **Together AI** | Inference platform for open-source models. Fast & cheap. | [together.ai](https://www.together.ai) |
| **Fireworks AI** | High-performance inference for open models. | [fireworks.ai](https://fireworks.ai) |
| **Groq** | Ultra-fast LPU inference. Fastest token generation. | [groq.com](https://groq.com) |
| **Replicate** | Run any ML model via API. Serverless. | [replicate.com](https://replicate.com) |
| **Hugging Face Inference** | Serverless inference for 200k+ models. | [huggingface.co](https://huggingface.co/inference-api) |

---

## 3. RAG (Retrieval-Augmented Generation)

### Vector Databases

| Database | Type | Description | Best For |
|----------|------|-------------|----------|
| [Pinecone](https://www.pinecone.io) | Managed | Fully managed vector database. Serverless option. | Easiest to start with |
| [Weaviate](https://github.com/weaviate/weaviate) | Open-source/Managed | AI-native vector database with built-in modules. | Hybrid search |
| [Qdrant](https://github.com/qdrant/qdrant) | Open-source/Managed | High-performance vector search engine in Rust. | Performance-critical apps |
| [Chroma](https://github.com/chroma-core/chroma) | Open-source | AI-native embedding database. Simple Python API. | Prototyping, small-medium scale |
| [Milvus](https://github.com/milvus-io/milvus) | Open-source | Scalable vector database. GPU-accelerated. | Large-scale production |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL extension | Vector similarity search in PostgreSQL. | Teams already using PostgreSQL |
| [LanceDB](https://github.com/lancedb/lancedb) | Open-source | Serverless vector database. Zero infra management. | Embedded/serverless use |
| [Turbopuffer](https://turbopuffer.com) | Managed | Object storage-backed vector database. Low cost at scale. | Cost-sensitive at scale |

### Embedding Models

| Model | Provider | Description |
|-------|----------|-------------|
| **text-embedding-3-large** | OpenAI | Best commercial embedding model |
| **Cohere Embed v3** | Cohere | Multilingual, compressed embeddings |
| **Voyage-3** | Voyage AI | Top-performing retrieval embeddings |
| **BGE-M3** | BAAI (open-source) | Best open-source multilingual embeddings |
| **Nomic Embed** | Nomic AI (open-source) | Strong open-source embeddings with long context |
| **Jina Embeddings v3** | Jina AI | Multilingual, 8k context, flexible dimensions |

### RAG Frameworks & Patterns

| Resource | Description | Link |
|----------|-------------|------|
| **LlamaIndex RAG** | Most comprehensive RAG framework | [docs.llamaindex.ai](https://docs.llamaindex.ai) |
| **LangChain RAG** | RAG templates and patterns | [python.langchain.com](https://python.langchain.com) |
| **RAGatouille** | ColBERT-based advanced retrieval | [github.com/bclavie/RAGatouille](https://github.com/bclavie/RAGatouille) |
| **Contextual Retrieval** | Anthropic's approach to better RAG | [anthropic.com/research](https://www.anthropic.com/research/contextual-retrieval) |
| **GraphRAG** | Microsoft's graph-based RAG approach | [github.com/microsoft/graphrag](https://github.com/microsoft/graphrag) |

---

## 4. AI Infrastructure & MLOps

### Experiment Tracking & Model Management

| Tool | Description | Link |
|------|-------------|------|
| **Weights & Biases** | ML experiment tracking, model registry, dataset versioning | [wandb.ai](https://wandb.ai) |
| **MLflow** | Open-source ML lifecycle management | [github.com/mlflow/mlflow](https://github.com/mlflow/mlflow) |
| **Neptune.ai** | Metadata store for ML experiments | [neptune.ai](https://neptune.ai) |
| **Comet ML** | ML experiment tracking and model production monitoring | [comet.com](https://www.comet.com) |

### LLM Observability & Evaluation

| Tool | Description | Link |
|------|-------------|------|
| **LangSmith** | LangChain's observability platform. Trace, evaluate, monitor. | [smith.langchain.com](https://smith.langchain.com) |
| **Braintrust** | LLM evaluation, logging, and prompt playground | [braintrust.dev](https://www.braintrust.dev) |
| **Arize Phoenix** | Open-source LLM observability | [github.com/Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) |
| **Helicone** | Open-source LLM observability proxy | [github.com/Helicone/helicone](https://github.com/Helicone/helicone) |
| **Patronus AI** | LLM evaluation and guardrails | [patronus.ai](https://www.patronus.ai) |
| **DeepEval** | Open-source LLM evaluation framework | [github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval) |
| **RAGAS** | RAG evaluation framework | [github.com/explodinggradients/ragas](https://github.com/explodinggradients/ragas) |

### Deployment & Serving

| Tool | Description | Link |
|------|-------------|------|
| **vLLM** | High-throughput LLM serving engine | [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm) |
| **TGI** | Hugging Face's text generation inference server | [github.com/huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) |
| **Ollama** | Run LLMs locally. Dead simple. | [github.com/ollama/ollama](https://github.com/ollama/ollama) |
| **llama.cpp** | LLM inference in C/C++. CPU-friendly. | [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) |
| **Modal** | Serverless GPU compute for ML | [modal.com](https://modal.com) |
| **RunPod** | GPU cloud for AI inference and training | [runpod.io](https://www.runpod.io) |
| **BentoML** | Build and deploy AI applications | [github.com/bentoml/BentoML](https://github.com/bentoml/BentoML) |

---

## 5. AI Coding Assistants & Developer Tools

| Tool | Description | Best For |
|------|-------------|----------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's agentic CLI coding assistant. Reads/writes code, runs commands. | Deep codebase understanding, complex refactors |
| [GitHub Copilot](https://github.com/features/copilot) | AI pair programmer in your IDE. Autocomplete + chat. | Inline code suggestions |
| [Cursor](https://cursor.com) | AI-native code editor. Fork of VS Code with AI built in. | AI-first development environment |
| [Windsurf](https://codeium.com/windsurf) | Codeium's AI IDE with "flows" — agentic coding. | Agentic coding experience |
| [Aider](https://github.com/paul-gauthier/aider) | AI pair programming in the terminal. Git-aware. | Terminal-based AI coding |
| [Continue](https://github.com/continuedev/continue) | Open-source AI code assistant for VS Code/JetBrains. | Open-source, customizable |
| [Cody](https://sourcegraph.com/cody) | Sourcegraph's AI coding assistant. Deep codebase understanding. | Large codebases |
| [Devin](https://devin.ai) | Autonomous AI software engineer | Full task delegation |
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) | Open-source AI software development agent | Open-source Devin alternative |

---

## 6. Fine-Tuning & Training

| Resource | Description | Link |
|----------|-------------|------|
| **Hugging Face Transformers** | Library for fine-tuning any transformer model | [github.com/huggingface/transformers](https://github.com/huggingface/transformers) |
| **Unsloth** | 2x faster fine-tuning with 80% less memory | [github.com/unslothai/unsloth](https://github.com/unslothai/unsloth) |
| **Axolotl** | Tool for fine-tuning LLMs. Supports LoRA, QLoRA, full fine-tune. | [github.com/OpenAccess-AI-Collective/axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) |
| **TRL** | Transformer Reinforcement Learning. RLHF, DPO, PPO. | [github.com/huggingface/trl](https://github.com/huggingface/trl) |
| **LitGPT** | Pretrain, fine-tune, deploy LLMs. By Lightning AI. | [github.com/Lightning-AI/litgpt](https://github.com/Lightning-AI/litgpt) |
| **Torchtune** | PyTorch-native fine-tuning library | [github.com/pytorch/torchtune](https://github.com/pytorch/torchtune) |
| **OpenAI Fine-Tuning** | Fine-tune GPT models via API | [platform.openai.com](https://platform.openai.com/docs/guides/fine-tuning) |
| **Anthropic Fine-Tuning** | Fine-tune Claude models (enterprise) | [anthropic.com](https://www.anthropic.com) |

### Key Techniques
- **LoRA** (Low-Rank Adaptation) — Efficient fine-tuning by training small adapter matrices
- **QLoRA** — Quantized LoRA, enables fine-tuning on consumer GPUs
- **RLHF** — Reinforcement Learning from Human Feedback
- **DPO** (Direct Preference Optimization) — Simpler alternative to RLHF
- **PEFT** — Parameter-Efficient Fine-Tuning methods

---

## 7. AI Safety & Responsible AI

| Resource | Description | Link |
|----------|-------------|------|
| **Anthropic Safety Research** | Leading AI safety research | [anthropic.com/research](https://www.anthropic.com/research) |
| **NIST AI RMF** | AI Risk Management Framework | [nist.gov/artificial-intelligence](https://www.nist.gov/artificial-intelligence) |
| **EU AI Act** | Comprehensive AI regulation framework | [artificialintelligenceact.eu](https://artificialintelligenceact.eu) |
| **Guardrails AI** | Add guardrails to LLM applications | [github.com/guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) |
| **NeMo Guardrails** | NVIDIA's toolkit for LLM safety | [github.com/NVIDIA/NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) |
| **LLM Guard** | Self-hardening toolkit for LLM security | [github.com/protectai/llm-guard](https://github.com/protectai/llm-guard) |
| **OWASP LLM Top 10** | Security risks for LLM applications | [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |

---

## 8. Essential Learning Resources

### Courses
| Course | Provider | Description |
|--------|----------|-------------|
| **Building AI Products** | Anthropic | How to build with Claude effectively |
| **LLM University** | Cohere | Comprehensive LLM education |
| **Full Stack LLM Bootcamp** | The Full Stack | Practical LLM application development |
| **Fast.ai** | fast.ai | Practical deep learning for coders |
| **Stanford CS229** | Stanford | Machine learning fundamentals |
| **Hugging Face NLP Course** | Hugging Face | Free NLP/transformers course |
| **DeepLearning.AI** | Andrew Ng | Short courses on LLMs, RAG, agents, fine-tuning |

### Books
- *Designing Machine Learning Systems* — Chip Huyen
- *Building LLM Apps* — Valentina Alto
- *AI Engineering* — Chip Huyen (2025)
- *Hands-On Large Language Models* — Jay Alammar & Maarten Grootendorst

---

## 9. Open-Source Models Worth Tracking

| Model Family | Organization | Why It Matters |
|-------------|-------------|----------------|
| **Llama 3/4** | Meta | Best open-weight models, massive ecosystem |
| **Mistral/Mixtral** | Mistral AI | Strong European models, MoE architecture |
| **DeepSeek** | DeepSeek | Competitive with closed models, open-source |
| **Qwen 2.5** | Alibaba | Strong multilingual, competitive benchmarks |
| **Gemma 2** | Google | Small, efficient open models |
| **Phi-3/4** | Microsoft | Small language models, edge deployment |
| **Command R** | Cohere | Enterprise RAG-optimized |
| **Stable Diffusion 3** | Stability AI | Leading open image generation |
| **Whisper** | OpenAI | Gold standard speech-to-text |

---

*Last updated: March 2026*
