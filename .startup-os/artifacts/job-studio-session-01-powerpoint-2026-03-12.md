# Job Studio Session 1 PowerPoint Build

## Objective

Ship Session 1 as a facilitator-ready PowerPoint deck that can be opened tonight, edited directly in Microsoft PowerPoint, and reused as the visual and instructional template for the rest of Track C.

## Framing

The source content already existed as:

- Oracle workshop markdown for Week 1
- a detailed facilitation guide
- MyJobStudio Session 1 content for strategist AI foundations
- Oracle design and executive standards

The missing layer was the actual training delivery surface: an editable deck with a defined look and feel and adult-learning structure embedded into the slide architecture.

## Recommendation

Use a single executive-workshop style for Track C:

- Oracle Navy header strip for authority and consistency
- Oracle Red as the primary accent for emphasis and learning-stage signaling
- warm neutral background to keep the deck from feeling like a sales presentation
- one-message-per-slide layout
- visible learning-layer chips to show the facilitation arc
- speaker notes embedded directly in the `.pptx`

## Adult-Learning System Used

Session 1 now explicitly follows these layers:

1. Relevance
2. Mental model
3. Demonstration
4. Guided practice
5. Reflection
6. Transfer

That structure shows up in both slide sequencing and speaker notes, so the deck teaches behavior change rather than only presenting information.

## Outputs

- Editable PowerPoint:
  - `/Users/mikerodgers/AI-Enablement-Oracle-Chat/my-job-studio/decks/SESSION_01_MYJOBSTUDIO_TRAINING_FACTORY.pptx`
- Rebuildable deck source:
  - `/Users/mikerodgers/AI-Enablement-Oracle-Chat/.build/session-01-deck/session_01_training_deck.js`
  - `/Users/mikerodgers/AI-Enablement-Oracle-Chat/my-job-studio/decks/src/session_01_training_deck.js`
- Rendered preview montage:
  - `/Users/mikerodgers/AI-Enablement-Oracle-Chat/my-job-studio/decks/rendered/session-01-montage.png`

## Validation

- Deck build completed successfully through PptxGenJS.
- Overflow check passed with no out-of-bounds content.
- Rendered slide previews completed successfully.

## Risks

- The bundled font-inspection helper is blocked by the local Python version, so font validation was done by render review rather than the helper script.
- Session 1 is now strong enough to use tonight, but the facilitator guide and learner handout still need parity updates if you want a fully matched asset bundle.

## Next Actions

1. Build Session 2 and Session 3 in the same PowerPoint system.
2. Convert Session 1 handout and activity script into finished collateral.
3. Reuse the design system for Track B after Ellen transition materials are finalized.
