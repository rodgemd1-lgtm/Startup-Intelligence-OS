# Web Experience 2026

## What Changed

- Motion has shifted from ornamental micro-interactions to narrative sequencing.
- Scroll-driven animation can increasingly be implemented with native CSS timelines instead of JavaScript-heavy orchestration.
- Apple-style glass and depth effects are influencing interface chrome, but overuse reduces clarity and trust.
- Organic layouts are replacing rigid template grids on premium, story-driven surfaces.
- Performance and reduced-motion support are now part of design credibility, not just engineering cleanup.

## Technical Patterns

- Use native scroll-driven animations when the effect is linear, simple, and should remain tightly tied to browser rendering.
- Use GSAP `ScrollTrigger` when choreography depends on pinning, scrub control, timeline coordination, or multi-state transitions.
- Use GSAP `Flip` when layout states need to feel continuous across DOM or route changes.
- Use canvas or WebGL only when visual continuity or depth cannot be achieved with DOM and CSS affordably.

## Pattern Library

### Motion Narrative

- Curiosity: slow reveal, sparse motion, one focal element
- Trust: stabilize motion near pricing, proof, and claims
- Commitment: reduce novelty, increase predictability
- Reassurance: use subtle continuity rather than attention spikes

### Organic Layouts

- Use asymmetry to create emphasis, not chaos
- Vary vertical rhythm across sections
- Give proof and reassurance content more breathing room than decorative content
- Break the grid intentionally around hero, proof, and transition moments

### Glass / Depth

- Best for navigation, utility overlays, floating controls, and lightweight framing
- Avoid behind dense copy, complex tables, or trust-sensitive medical/legal content

## Example References

- Apple Human Interface Guidelines and Liquid Glass documentation
- WebKit guidance for scroll-driven animations
- GSAP ScrollTrigger and Flip docs for coordinated storytelling transitions

## Review Checklist

- Is motion doing narrative work?
- Is there a reduced-motion fallback?
- Does visual depth improve hierarchy or just add gloss?
- Would this still convert if all motion were removed?

