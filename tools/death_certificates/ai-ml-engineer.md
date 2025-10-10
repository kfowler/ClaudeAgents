# Death Certificate: ai-ml-engineer

**Agent Name:** ai-ml-engineer
**Date of Creation:** 2024 (early agent)
**Date of Death:** 2025-10-10
**Lifespan:** ~12-18 months
**Tier:** Core (formerly)
**Cause of Death:** Superseded by superior pattern-based specialization

## Detailed Autopsy

**Symptoms Leading to Death:**
- Created as broad "AI/ML" generalist when LLM ecosystem was nascent
- Tried to cover too many domains: LLM integration, RAG, fine-tuning, image generation, inference optimization
- Jack-of-all-trades approach led to shallow expertise in each subdomain
- Could not keep pace with rapid specialization in AI/ML field (6+ distinct disciplines emerged)
- DECISION-006 (Creative Triad Implementation) exposed architectural weakness: monolithic agent design doesn't scale

**Root Causes:**
- **Insufficient Granularity**: One agent covering 6+ distinct AI/ML disciplines (LLM routing, prompt engineering, RAG architecture, fine-tuning, inference optimization, image generation)
- **Vendor-Lock Risk**: Early design coupled too tightly to specific vendors (OpenAI, Anthropic)
- **Rapid Field Evolution**: AI/ML specialized faster than agent could adapt
- **Pattern Permanence > Vendor Temporality**: Pattern-based agents (RAG architecture, prompt optimization) are durable; vendor-specific agents (OpenAI specialist) become obsolete

## Lessons Learned

1. **Specialize by Pattern, Not Vendor:** Pattern-based agents (`rag-systems-engineer`, `prompt-engineering-specialist`) outlive vendor-specific agents. RAG architecture patterns persist across vendors; vendor APIs change monthly.

2. **Monolithic Agents Don't Scale:** When a single agent tries to cover 6+ distinct disciplines, it becomes a bottleneck. Specialized agents allow parallel work and deeper expertise.

3. **Field Velocity Dictates Granularity:** Fast-moving fields (AI/ML, frontend frameworks) require fine-grained specialists. Slow-moving fields (POSIX systems programming) can use broader agents.

## Migration Path

**For users who might have used ai-ml-engineer:**

**Use Case 1: Multi-model LLM integration, routing, cost optimization**
→ **Replacement:** `llm-integration-architect`
→ **Why:** Vendor-neutral patterns for model routing, fallback chains, cost optimization across OpenAI/Anthropic/open-source models. Durable expertise that survives vendor churn.

**Use Case 2: Prompt engineering, chain-of-thought, few-shot learning**
→ **Replacement:** `prompt-engineering-specialist`
→ **Why:** Deep expertise in prompting techniques that work across all LLM providers. Focused on optimization patterns, not vendor APIs.

**Use Case 3: RAG system design, vector databases, hybrid search**
→ **Replacement:** `rag-systems-engineer`
→ **Why:** Specializes in RAG architecture patterns (chunking strategies, reranking, hybrid search) that remain stable as vendors change.

**Use Case 4: Model fine-tuning, LoRA, custom training**
→ **Replacement:** `fine-tuning-specialist`
→ **Why:** Covers LoRA, QLoRA, dataset engineering, RLHF, DPO across all platforms (OpenAI fine-tuning, HuggingFace, custom training).

**Use Case 5: Self-hosted LLM, inference optimization, quantization**
→ **Replacement:** `inference-optimization-specialist`
→ **Why:** Deep expertise in vLLM, TensorRT-LLM, llama.cpp, quantization techniques. Critical for cost reduction and data privacy.

**Use Case 6: Image generation, Stable Diffusion, LoRA training**
→ **Replacement:** `generative-image-specialist`
→ **Why:** Focused entirely on diffusion models, ControlNet, ComfyUI, LoRA training. Covers both hosted (Midjourney, DALL-E) and self-hosted (Stable Diffusion).

**Use Case 7: General AI/ML strategy, tool selection**
→ **Replacement:** `project-orchestrator` coordinates multiple AI specialists
→ **Why:** Complex AI projects require orchestration of multiple specialists, not a single generalist.

**Search Keyword Redirects:**
- "AI integration", "LLM integration", "multi-model" → `llm-integration-architect`
- "prompt engineering", "chain-of-thought", "few-shot" → `prompt-engineering-specialist`
- "RAG", "vector database", "semantic search" → `rag-systems-engineer`
- "fine-tuning", "LoRA", "custom model" → `fine-tuning-specialist`
- "inference optimization", "quantization", "self-hosted LLM" → `inference-optimization-specialist`
- "image generation", "Stable Diffusion", "DALL-E" → `generative-image-specialist`

## Final Notes

The death of `ai-ml-engineer` is not a failure—it's an evolution. This agent served its purpose during the early LLM era when "AI/ML" was one discipline. Now that AI/ML has exploded into 6+ distinct specializations, the field demands pattern-based specialists with deep expertise.

**Users gain:**
- **Deeper Expertise**: Each specialist has 10x depth in their domain
- **Parallel Work**: Multiple AI projects can proceed simultaneously with different specialists
- **Future-Proof**: Pattern-based agents survive vendor API changes and model deprecations
- **Clearer Selection**: "I need RAG architecture help" → rag-systems-engineer (vs. vague "AI help" → ai-ml-engineer)

**Platform gains:**
- **Vendor Neutrality**: No lock-in to specific LLM providers
- **Durability**: Pattern-based expertise outlives vendor-specific APIs
- **Scalability**: Specialists can be added as new AI patterns emerge (multimodal, agents, reasoning)

This deprecation validates DECISION-006: **Specialization by durable patterns beats monolithic generalization.**

---

**Death Certificate prepared by:** code-architect, product-manager, project-orchestrator
**Date:** 2025-10-10
**Related Decision:** DECISION-006 (Creative Triad Implementation: Specialization over Sprawl)
