# AI-Powered Rep Counting in Fitness Apps — Research Summary

**Scraped:** 2026-03-10 | **Depth:** Shallow | **Engines:** Web Search + WebFetch | **Sources:** 3 extracted / 10 discovered

---

## Key Themes

### 1. Computer Vision is the Core Technology
Pose estimation (MediaPipe, OpenPose, custom CNNs) powers real-time rep counting. The smartphone camera serves as the primary sensor — no wearables needed. Key players: Fittonic (SDK/API), Agit, Motra, and Ray.

### 2. Beyond Rep Counting → Form Analysis
The market has moved past basic counting. Leading apps now assess movement quality, flag compensations, predict injury risk, and provide real-time corrective cues. This is the differentiation frontier.

### 3. SDK/API Ecosystem Emerging
Fittonic offers a plug-and-play SDK for fitness apps to add computer vision rep counting without building it in-house. This creates a build-vs-buy decision for TransformFit.

### 4. Market Demand is Strong
McKinsey (2025) reports 68% of fitness app users prefer platforms that adapt to their performance. Computer vision is the enabler for this personalization.

## Competitive Landscape

| App | CV Capability | Differentiator |
|-----|---------------|----------------|
| Fittonic | Full SDK — rep count + form | B2B API play |
| Agit | Smartphone camera tracking | Real-time postural feedback |
| Motra | Automatic exercise tracking | Passive detection |
| Ray | Rep counting + voice coaching | Multi-modal (vision + voice) |

## Gaps in Research

- No academic benchmarks on rep counting accuracy across exercise types
- Limited data on user adoption/retention impact of CV features
- Privacy concerns around camera-based tracking not well-addressed
- No clear winner in the SDK space yet

## Relevance to TransformFit

This is a **high-signal** research area. CV-based rep counting could be a V2 differentiator for TransformFit's exercise tracking. The build-vs-buy decision (Fittonic SDK vs. custom MediaPipe implementation) is worth a decision room session.

## Recommended Next Steps

1. `/scrape "Fittonic SDK pricing and integration" --depth deep` — evaluate the B2B option
2. `/scrape "MediaPipe pose estimation fitness app tutorial" --depth deep --data-type technical_docs` — evaluate the build option
3. Run a decision room session on build vs. buy for computer vision
