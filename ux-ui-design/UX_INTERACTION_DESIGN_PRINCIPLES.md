# UX Interaction Design Principles: A Comprehensive Reference

> Authoritative principles governing how users interact with software -- covering interaction patterns, information architecture, user flows, behavioral design, mobile interaction, and accessibility. Designed for AI agents building applications.

---

## Table of Contents

1. [Core Interaction Design Laws](#1-core-interaction-design-laws)
2. [Cognitive Psychology in Interface Design](#2-cognitive-psychology-in-interface-design)
3. [Information Architecture Frameworks](#3-information-architecture-frameworks)
4. [User Flow Design Patterns](#4-user-flow-design-patterns)
5. [Behavioral Design Frameworks](#5-behavioral-design-frameworks)
6. [Cognitive Biases in UX](#6-cognitive-biases-in-ux)
7. [Mobile-First Interaction Patterns](#7-mobile-first-interaction-patterns)
8. [Accessibility Interaction Patterns](#8-accessibility-interaction-patterns)
9. [Performance and Responsiveness](#9-performance-and-responsiveness)
10. [Practical Application Matrix](#10-practical-application-matrix)

---

## 1. Core Interaction Design Laws

These are empirically validated laws that predict how users will behave when interacting with interfaces. Every design decision should be filtered through these principles.

### Fitts's Law

**Statement:** The time to acquire a target is a function of the distance to and size of the target.

**Formula:** T = a + b * log2(D/W + 1), where D = distance to target center, W = target width.

**Practical application:**
- Make primary action buttons large and position them near likely cursor/thumb positions
- Increase the clickable area of interactive elements beyond their visible boundaries (use padding, not just the visible element)
- Place destructive actions (delete, cancel) far from constructive ones (save, submit) to prevent accidental activation
- Infinite edges and corners of a screen are the easiest targets to hit (used by OS menus, scroll bars)
- On touch devices, the minimum recommended target size is 48x48px (Google Material Design) or 44x44pt (Apple HIG)

**Source:** Paul Fitts, 1954. "The information capacity of the human motor system in controlling the amplitude of movement." [lawsofux.com/fittss-law](https://lawsofux.com/fittss-law/), [NN/g - Fitts's Law](https://www.nngroup.com/articles/fitts-law/)

---

### Hick's Law (Hick-Hyman Law)

**Statement:** The time it takes to make a decision increases with the number and complexity of choices.

**Formula:** RT = a + b * log2(n), where n = number of equally probable alternatives.

**Practical application:**
- Limit navigation menu items to 5-7 top-level categories
- Use progressive disclosure to reveal options only when relevant
- Break complex tasks into smaller, sequential steps rather than presenting all options at once
- Pricing pages should present 3 tiers (not 5+); users convert faster with fewer choices
- In form design, pre-select the most common option where appropriate
- Use smart defaults to eliminate unnecessary decisions

**Source:** William Edmund Hick and Ray Hyman, 1952. [lawsofux.com/hicks-law](https://lawsofux.com/hicks-law/)

---

### Jakob's Law

**Statement:** Users spend most of their time on other sites. This means they prefer your site to work the same way as all the other sites they already know.

**Practical application:**
- Leverage existing mental models: place navigation where users expect it (top or left), use standard icons (hamburger menu, magnifying glass for search, gear for settings)
- Follow platform conventions: iOS apps should feel like iOS apps; Android apps should follow Material Design
- Innovate on substance, not on basic interaction patterns; novel navigation schemes increase cognitive load
- When redesigning, change gradually to allow users to adapt; offer transitional states
- Use established form patterns: labels above inputs, primary action on the right (in LTR languages), error messages below the field

**Source:** Jakob Nielsen, 2000. [lawsofux.com/jakobs-law](https://lawsofux.com/jakobs-law/)

---

### Miller's Law

**Statement:** The average person can hold approximately 7 (plus or minus 2) items in working memory at one time.

**Important update:** Modern cognitive science research refines this to approximately 4 chunks for most practical tasks when users are not giving full attention.

**Practical application:**
- Chunk information into groups of 3-5 related items (e.g., phone numbers are formatted as 555-867-5309, not 5558675309)
- Limit visible navigation items, stepper indicators, and grouped form fields to manageable chunks
- Use visual hierarchy (headings, spacing, grouping) to create natural chunks in content
- Design dashboards with 4-6 key metrics visible at once, not 12+
- In data tables, group columns logically and allow users to customize which are visible

**Source:** George A. Miller, 1956. "The Magical Number Seven, Plus or Minus Two." [lawsofux.com/millers-law](https://lawsofux.com/millers-law/), [CareerFoundry - Miller's Law in UX](https://careerfoundry.com/en/blog/ux-design/what-is-millers-law/)

---

### Postel's Law (Robustness Principle)

**Statement:** Be conservative in what you do, be liberal in what you accept from others.

**Practical application:**
- Accept varied input formats: dates as "March 5", "3/5/2026", "2026-03-05" -- parse all of them
- Be generous with input validation: accept phone numbers with or without dashes, spaces, country codes
- Provide clear, precise, structured output even when accepting messy input
- Auto-format inputs for the user (e.g., auto-add hyphens to credit card numbers as they type)
- Offer smart suggestions and autocomplete rather than rejecting non-exact inputs

**Source:** Jon Postel, 1980. RFC 761. [lawsofux.com/postels-law](https://lawsofux.com/postels-law/)

---

### Tesler's Law (Law of Conservation of Complexity)

**Statement:** Every application has an inherent amount of complexity that cannot be removed. The question is: who deals with it -- the user or the developer?

**Practical application:**
- Absorb complexity on the engineering side so the user experience remains simple
- Smart defaults should handle 80% of cases without requiring user configuration
- Avoid exposing implementation details (database IDs, technical error codes, system states) to users
- If a developer can spend an extra week to save every user one minute of confusion, that is almost always the correct trade-off
- Complex features should have sensible defaults with "Advanced settings" available for power users

**Source:** Larry Tesler, mid-1980s. [lawsofux.com/teslers-law](https://lawsofux.com/teslers-law/)

---

### Doherty Threshold

**Statement:** Productivity soars when a computer and its users interact at a pace (<400ms) that ensures neither has to wait on the other.

**Practical application:**
- System responses under 100ms feel instantaneous to the user
- Responses between 100-400ms feel fast and maintain engagement flow
- Responses above 1000ms cause users to lose mental context; they begin thinking about other things
- Use optimistic UI updates: show the expected result immediately, then sync with the server in the background
- Display skeleton screens or progress indicators for any operation exceeding 400ms
- Preload content the user is likely to need next (e.g., preload the next page in a paginated list)

**Source:** Walter J. Doherty and Ahrvind J. Thadani, 1982. IBM Systems Journal. [lawsofux.com/doherty-threshold](https://lawsofux.com/doherty-threshold/)

---

## 2. Cognitive Psychology in Interface Design

These psychological effects dictate how users perceive, remember, and evaluate their experience with your product.

### Serial Position Effect

**Statement:** Users tend to best remember the first (primacy effect) and last (recency effect) items in a series.

**Application:** Place the most important navigation items and actions at the beginning and end of lists, toolbars, and menus. In mobile bottom navigation, anchor the two most critical tabs at the far left and far right positions.

**Source:** Hermann Ebbinghaus, 1885. [lawsofux.com/serial-position-effect](https://lawsofux.com/serial-position-effect/)

### Von Restorff Effect (Isolation Effect)

**Statement:** When multiple similar items are present, the one that differs from the rest is most likely to be remembered.

**Application:** Make your primary CTA visually distinct from other elements. In pricing tables, visually highlight the recommended plan. Use visual differentiation (color, size, animation) sparingly and only for the single most important element on a screen.

**Source:** Hedwig von Restorff, 1933. [lawsofux.com/von-restorff-effect](https://lawsofux.com/von-restorff-effect/)

### Peak-End Rule

**Statement:** People judge an experience based on how they felt at its most intense point (peak) and at its end, rather than the sum or average of every moment.

**Application:** Invest disproportionate design effort in the emotional peaks of your product experience (the "aha moment" of onboarding, the moment a key task is completed) and in the final interaction (confirmation screens, success states, logout flows). A delightful success animation after checkout matters more than minor improvements to mid-flow steps.

**Source:** Daniel Kahneman, 1993. [lawsofux.com/peak-end-rule](https://lawsofux.com/peak-end-rule/)

### Zeigarnik Effect

**Statement:** People remember uncompleted or interrupted tasks better than completed ones.

**Application:** Use progress indicators and incomplete-state cues to drive task completion: profile completion bars, step indicators in multi-step flows, "resume where you left off" prompts. LinkedIn's profile strength meter is a textbook application of this effect.

**Source:** Bluma Zeigarnik, 1927. [lawsofux.com/zeigarnik-effect](https://lawsofux.com/zeigarnik-effect/)

### Aesthetic-Usability Effect

**Statement:** Users perceive aesthetically pleasing designs as more usable, even when they are not objectively more usable.

**Application:** Visual polish is not superficial -- it directly impacts perceived usability and user trust. A well-designed interface makes users more tolerant of minor usability issues and more willing to explore. Invest in consistent visual design early; it is not a luxury reserved for post-launch.

**Source:** Masaaki Kurosu and Kaede Kashimura, 1995. [lawsofux.com/aesthetic-usability-effect](https://lawsofux.com/aesthetic-usability-effect/)

---

## 3. Information Architecture Frameworks

Information architecture (IA) is the structural design of shared information environments. It governs how content is organized, labeled, and surfaced to users.

### Core IA Components

| Component | Definition | Example |
|-----------|-----------|---------|
| **Organization schemes** | How information is categorized | Alphabetical, chronological, topical, audience-based |
| **Labeling systems** | How information is named | Navigation labels, headings, link text |
| **Navigation systems** | How users move through information | Global nav, local nav, breadcrumbs, faceted search |
| **Search systems** | How users look for specific information | Search algorithms, filters, autocomplete, scoped search |

### Research Methods for IA

#### Card Sorting

**What it is:** Users group content items into categories that make sense to them, revealing their mental models for how information should be organized.

**Types:**
- **Open card sort:** Users create their own category names. Use when defining a new IA from scratch.
- **Closed card sort:** Users sort into pre-defined categories. Use when validating an existing or proposed IA structure.
- **Hybrid card sort:** Users sort into pre-defined categories but can create new ones. Best balance of structure and discovery.

**When to use:** Early in the design process when deciding how to organize content, features, or navigation. Run with 15-20 participants for statistically meaningful results.

**Source:** [NN/g - Card Sorting Definition](https://www.nngroup.com/articles/card-sorting-definition/), [IxDF - Card Sorting Guide 2026](https://ixdf.org/literature/article/the-pros-and-cons-of-card-sorting-in-ux-research)

#### Tree Testing (Reverse Card Sort)

**What it is:** Users are given tasks and asked to find where they would go in a proposed navigation tree (text only, no visual design). Validates whether your IA structure enables findability.

**Key metrics:**
- **Success rate:** Did users find the correct location?
- **Directness:** Did they navigate there without backtracking?
- **Time to complete:** How long did it take?

**When to use:** After card sorting to validate the proposed IA. Run before investing in visual design or development. Always test with at least 50 participants for reliable quantitative data.

**Source:** [NN/g - Card Sorting vs Tree Testing](https://www.nngroup.com/articles/card-sorting-tree-testing-differences/), [Hubble - Tree Testing vs Card Sorting](https://www.usehubble.io/blog/tree-testing-vs-card-sorting)

#### Content Modeling

**What it is:** Defining the structure, attributes, and relationships of every content type in your system before designing screens.

**Process:**
1. Identify all content types (articles, products, user profiles, notifications)
2. Define attributes for each type (title, description, image, author, date, tags)
3. Map relationships between types (an article has an author; a product belongs to categories)
4. Define display rules (which attributes are shown in list vs. detail views)

**Why it matters:** Content modeling prevents the common failure mode where UI is designed around placeholder content and breaks when real content arrives. It ensures the IA scales as content grows.

### IA Validation Checklist

- [ ] Every piece of content has exactly one logical home
- [ ] Labels use the language of users, not internal jargon
- [ ] Navigation depth does not exceed 3-4 levels for most tasks
- [ ] The most frequently performed tasks require the fewest clicks/taps
- [ ] Search is available as an alternative to browsing for all content
- [ ] Breadcrumbs or other wayfinding cues show users where they are in the hierarchy

---

## 4. User Flow Design Patterns

### Progressive Disclosure

**Principle:** Show only the information and options relevant to the user's current context. Reveal complexity gradually as needed.

**Implementation patterns:**
- **Staged forms:** Break long forms into multi-step wizards. Display one section at a time with a progress indicator. 18% of users abandon checkout flows that appear too long or complicated (Baymard Institute).
- **Tiered menus:** Show top-level categories; reveal sub-categories on interaction.
- **Expandable sections:** Use accordions, "Show more" links, and collapsible panels for secondary information.
- **Tooltips and contextual help:** Provide inline explanations on hover/focus rather than forcing users to read documentation.
- **Feature gating:** Reveal advanced features only after users have mastered basic ones.

**Source:** [NN/g - Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/), [IxDF - Progressive Disclosure 2026](https://ixdf.org/literature/topics/progressive-disclosure)

### Onboarding Patterns

**Goal:** Get users to their "aha moment" (first experience of core value) as quickly as possible.

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Welcome tour** | Step-by-step guided walkthrough highlighting key features | Complex products with many features |
| **Checklist onboarding** | List of setup tasks with progress tracking (Zeigarnik effect) | Products requiring configuration before use |
| **Branched onboarding** | Ask users their role/goal, then customize the experience | Products serving multiple user types |
| **Empty state onboarding** | Use blank states as instructional opportunities: "No projects yet. Create your first project." | Simple products with clear primary actions |
| **Contextual onboarding** | Show tips and tooltips only when the user encounters a feature for the first time | All products, especially those with frequent updates |
| **Interactive sandbox** | Provide a pre-populated environment for users to explore safely | Data-heavy products, analytics tools |

**Key metrics:**
- Time to first key action
- Onboarding completion rate
- Day 1, Day 7, Day 30 retention by cohort
- Activation rate (% of users who reach the "aha moment")

### Conversion Funnel Design

**Principles:**
1. **Reduce friction at every step:** Every additional field, click, or decision point loses users. If a field is not required for the current step, do not show it.
2. **Show progress:** Users are more likely to complete a flow when they can see how far along they are and how many steps remain.
3. **Allow recovery:** Let users go back, edit previous steps, and save progress. Never force users to start over.
4. **Defer account creation:** Allow users to experience value before requiring sign-up. "Guest checkout" patterns consistently outperform forced-registration patterns.
5. **Social proof at decision points:** Place testimonials, reviews, or trust signals adjacent to conversion actions, not on a separate page.
6. **Use clear, specific CTAs:** "Start free trial" converts better than "Submit." "Add to cart - $29" converts better than "Continue."

### Navigation Patterns

| Pattern | When to Use | Implementation Notes |
|---------|-------------|---------------------|
| **Top horizontal nav** | Desktop web, 5-7 main sections | Most familiar pattern. Use dropdowns sparingly. |
| **Bottom tab bar** | Mobile apps, 3-5 main sections | Place the primary action in the center. Follow platform conventions (iOS: 5 max, Android: 3-5). |
| **Sidebar nav** | Data-heavy apps, dashboards | Collapsible for more screen real estate. Group items into labeled sections. |
| **Hamburger menu** | Secondary navigation, mobile web | Hides navigation; use only for non-critical paths. Items in hamburger menus get significantly fewer interactions. |
| **Breadcrumbs** | Deep content hierarchies, e-commerce | Always show the full path. Make every level clickable. |
| **Command palette** | Power user tools, developer-facing apps | Ctrl/Cmd+K pattern. Combine search + navigation + actions in one interface. |

---

## 5. Behavioral Design Frameworks

These frameworks explain why users take action (or fail to) and how to design for sustained engagement.

### Fogg Behavior Model (FBM)

**Core principle:** Behavior = Motivation x Ability x Prompt. All three must converge at the same moment for a behavior to occur.

**The three elements:**

| Element | Definition | Design Levers |
|---------|-----------|--------------|
| **Motivation** | The user's desire to perform the behavior | Core motivators: pleasure/pain, hope/fear, social acceptance/rejection |
| **Ability** | How easy it is to perform the behavior | Simplify the task: fewer steps, less thinking, less money, less time, less physical effort, less social deviance |
| **Prompt** | The cue that triggers the behavior | Must be noticeable, actionable, and timed to a moment of sufficient motivation + ability |

**Three prompt types:**
- **Spark:** For high-ability, low-motivation users. Increase desire. Example: an email showing what peers have accomplished.
- **Facilitator:** For high-motivation, low-ability users. Remove barriers. Example: a one-click signup button.
- **Signal:** For high-motivation, high-ability users. Just remind them. Example: a simple notification.

**Design implication:** When users are not converting, diagnose which element is missing. Most products over-invest in motivation (marketing) when the real problem is ability (friction in the product).

**Source:** BJ Fogg, Stanford Behavior Design Lab. [behaviormodel.org](https://www.behaviormodel.org/), [Stanford Behavior Design Lab](https://behaviordesign.stanford.edu/resources/fogg-behavior-model)

### The Hook Model

**Core principle:** Habit-forming products create a four-phase loop that, with successive cycles, makes the behavior increasingly automatic.

**The four phases:**

1. **Trigger** (External then Internal)
   - External triggers: notifications, emails, CTAs, word-of-mouth
   - Internal triggers: emotions, routines, situations (boredom triggers checking social media)
   - Goal: migrate users from external to internal triggers over time

2. **Action** (Fogg's B=MAP applied)
   - The simplest action in anticipation of reward
   - Example: scrolling a feed, opening an app, clicking "New"
   - Design for minimum friction

3. **Variable Reward** (Three types)
   - *Tribe:* Social rewards -- likes, comments, status (social validation)
   - *Hunt:* Material rewards -- relevant content, deals, new information (search for resources)
   - *Self:* Personal rewards -- mastery, completion, achievement (intrinsic satisfaction)
   - The variability is what sustains engagement; predictable rewards lose power

4. **Investment**
   - User puts something in: data, content, followers, reputation, customization
   - Stored value makes the product more valuable with use (and harder to leave)
   - Investment loads the next trigger (e.g., posting content generates notifications when others engage)

**Source:** Nir Eyal, 2014. *Hooked: How to Build Habit-Forming Products.* [Medium - BJ Fogg, Octalysis, and the Hook Model](https://medium.com/@brdelfino.work/bj-fogg-octalysis-and-the-hook-model-three-frameworks-that-changed-how-my-design-teams-think-82a807202b1f)

### Nudge Theory in UX

**Core principle:** Small changes in the choice environment ("choice architecture") significantly influence behavior without restricting options.

**Key nudge techniques in product design:**

| Technique | Description | Example |
|-----------|------------|---------|
| **Default settings** | Pre-select the preferred option | Opt-in to newsletter pre-checked; annual billing pre-selected |
| **Social proof** | Show what others are doing | "1,247 teams signed up this week" |
| **Anchoring** | First number seen sets the reference point | Show the enterprise plan price first so the team plan seems reasonable |
| **Scarcity signals** | Indicate limited availability | "Only 3 seats left at this price" |
| **Commitment devices** | Small initial commitment leads to larger ones | Free trial -> paid conversion; micro-survey -> full survey |
| **Friction addition** | Add deliberate friction to discourage undesirable actions | "Are you sure?" confirmations, cooldown periods for account deletion |

**Ethical boundary:** Nudges should align user interests with business interests. If a nudge benefits only the business at the user's expense, it is a dark pattern, not a nudge.

**Source:** Richard Thaler and Cass Sunstein, 2008. *Nudge.* [inBeat - Behavioral Science in UX 2025](https://inbeat.agency/blog/behavioral-science-in-ux-design)

---

## 6. Cognitive Biases in UX

Understanding these biases allows you to design with (not against) human psychology.

### Loss Aversion

**Principle:** People feel losses roughly 2x as strongly as equivalent gains (Kahneman & Tversky, 1979).

**Application in UX:**
- Frame upgrades as preventing loss: "Don't lose access to your data" outperforms "Gain access to more data"
- Free trials work because canceling feels like losing something, not returning to baseline
- Conversion rates increase 30-40% when upgrade CTAs are framed around loss prevention
- Show what the user will lose by not acting: "Your draft will be deleted in 7 days"

**Caution:** Overuse creates anxiety and erodes trust. Use loss framing for genuine consequences, not manufactured urgency.

**Source:** Amos Tversky and Daniel Kahneman, 1979. [IxDF - Loss Aversion](https://www.interaction-design.org/literature/topics/loss-aversion), [Designlab - Psychology in UX](https://designlab.com/blog/ux-psychology)

### Anchoring Bias

**Principle:** The first piece of information encountered (the "anchor") disproportionately influences subsequent judgments.

**Application in UX:**
- In pricing: show the highest-tier price first so the mid-tier feels affordable
- In settings: display the recommended value as the default; users will adjust from there
- In negotiations: the first number sets the frame (original price vs. discounted price)
- In dashboards: show the most important metric first; it anchors how users interpret subsequent data

**Source:** [LogRocket - 7 Cognitive Biases](https://blog.logrocket.com/ux-design/7-cognitive-biases-ux-designers-should-know/)

### Endowment Effect

**Principle:** People value things more once they feel ownership.

**Application in UX:**
- Let users customize or personalize before asking them to pay; they are now "invested"
- Freemium models work partly because users develop a sense of ownership over their free-tier data and configurations
- Progress indicators on profile completion imply existing ownership of an "incomplete" asset
- "Your workspace," "Your projects" -- possessive language increases perceived ownership

**Source:** [LogRocket - 7 Cognitive Biases](https://blog.logrocket.com/ux-design/7-cognitive-biases-ux-designers-should-know/)

### Confirmation Bias

**Principle:** People seek out information that confirms their existing beliefs.

**Application in UX:**
- Search results and filter systems should present diverse results, not just echo what the user already believes
- Error states should present the actual problem, not let users assume the issue is with the system
- Onboarding surveys should use neutral language to get accurate user intent data

### Sunk Cost Fallacy

**Principle:** People continue an activity because of previously invested resources (time, money, effort) rather than future value.

**Application in UX:**
- Show users their progress and investment: "You've completed 4 of 5 modules" encourages finishing
- Streak counters (Duolingo, GitHub contribution graphs) leverage sunk-cost psychology
- Migration tools reduce the sunk-cost barrier for switching products: "Import your data in one click"

---

## 7. Mobile-First Interaction Patterns

### Thumb Zone Design

The natural reach of a user's thumb during one-handed phone use creates three zones:

| Zone | Location | What to Place Here |
|------|----------|--------------------|
| **Easy (green)** | Bottom center and bottom-left of screen | Primary actions, frequently used controls, bottom navigation |
| **Stretch (yellow)** | Top-left, top-center | Secondary actions, less frequent controls |
| **Hard (red)** | Top-right corner | Destructive or rarely used actions (settings, overflow menus) |

**Source:** Steven Hoober, 2013. "How Do Users Really Hold Mobile Devices?" [Prateeksha - Mobile-First UX](https://prateeksha.com/blog/mobile-first-ux-designing-for-thumbs-not-just-screens)

### Touch Target Specifications

| Platform | Minimum Touch Target | Recommended |
|----------|---------------------|-------------|
| Apple HIG | 44x44 points | 44x44pt for all tappable elements |
| Google Material Design | 48x48 dp | 48x48dp with 8dp spacing between targets |
| WCAG 2.2 (Level AA) | 24x24 CSS pixels | 44x44 CSS pixels |

**Critical rule:** The tappable area should always be at least the minimum size, even if the visible element (icon, text link) is smaller. Use invisible padding to extend hit areas.

### Gesture Design Principles

| Gesture | Standard Usage | Design Rules |
|---------|---------------|--------------|
| **Tap** | Select, activate | Primary interaction. Must have clear visual feedback. |
| **Long press** | Secondary actions, context menus | Always provide an alternative way to access the same action. Never make long-press the only path. |
| **Swipe horizontal** | Navigate between views, reveal actions | Provide visual hints that swiping is possible (peek of next card, swipe indicators). |
| **Swipe vertical** | Scroll content | Natural. Do not override standard scroll behavior. |
| **Pull down** | Refresh content | Standard pattern on mobile. Show loading indicator during refresh. |
| **Pinch** | Zoom in/out | Expected on maps and images. Do not block native zoom on text content. |

**Key principles:**
- Gestures must be discoverable: if a gesture is the only way to access a feature, many users will never find it
- Always provide visible UI alternatives to gestures (buttons, menus) for the same actions
- Do not replace standard platform gestures with custom ones
- Provide haptic feedback for gestures on supported devices
- Voice and gesture features should complement touch, not replace it

**Source:** [Codebridge - Impact of Gestures](https://www.codebridge.tech/articles/the-impact-of-gestures-on-mobile-user-experience), [TensorBlue - Mobile-First UX Patterns 2026](https://tensorblue.com/blog/mobile-first-ux-patterns-driving-engagement-design-strategies-for-2026)

### Mobile-Specific Layout Principles

- **Content-first:** On mobile, content is the interface. Remove decorative elements that do not serve the user's goal.
- **Single-column layout:** Default to one column. Avoid complex grids that require horizontal scrolling.
- **Bottom sheet pattern:** Use bottom sheets for secondary content and actions. They are within thumb reach and do not obscure the primary view completely.
- **Sticky actions:** Keep primary CTAs fixed at the bottom of the screen so they are always accessible.
- **No hover states:** Never rely on hover for critical information or functionality on touch devices. Use tap, long-press, or inline disclosure instead.
- **Adaptive input methods:** Show the correct keyboard type (numeric, email, URL) for each input field.

---

## 8. Accessibility Interaction Patterns

Accessibility is not an add-on feature. These patterns are requirements for inclusive software and are increasingly legally mandated (ADA, EAA, Section 508).

### Keyboard Navigation Standards (WCAG 2.1.1)

**Fundamental rule:** Every interactive element must be operable with a keyboard alone.

| Key | Standard Function |
|-----|-------------------|
| **Tab / Shift+Tab** | Move forward/backward between focusable elements |
| **Enter** | Activate buttons, links, and submit forms |
| **Space** | Activate buttons, toggle checkboxes, select options |
| **Arrow keys** | Navigate within composite widgets (tabs, menus, radio groups, tree views) |
| **Escape** | Close modals, dismiss popovers, cancel operations |
| **Home / End** | Jump to first/last item in a list or menu |

**Implementation requirements:**
- Focus order must follow a logical, predictable sequence matching the visual layout
- Focus indicators must be visible and meet WCAG contrast requirements (3:1 minimum contrast ratio)
- No keyboard traps: the user must be able to navigate away from any component using only the keyboard
- Skip navigation links must be provided to bypass repetitive content (e.g., "Skip to main content")
- Custom widgets must implement the WAI-ARIA Authoring Practices keyboard patterns for their role

**Source:** [UXPin - WCAG 2.1.1 Keyboard Accessibility](https://www.uxpin.com/studio/blog/wcag-211-keyboard-accessibility-explained/), [Smashing Magazine - Keyboard Navigation](https://www.smashingmagazine.com/2025/04/what-mean-site-be-keyboard-navigable/)

### Screen Reader Design Patterns

- **Semantic HTML first:** Use `<nav>`, `<main>`, `<article>`, `<aside>`, `<header>`, `<footer>`, `<button>`, `<a>` with appropriate structure. Semantic elements convey meaning and role without ARIA.
- **ARIA only as a supplement:** Use ARIA roles, states, and properties when semantic HTML alone cannot convey the meaning of a custom widget. The first rule of ARIA: do not use ARIA if a native HTML element will do the job.
- **Live regions for dynamic content:** Use `aria-live="polite"` for non-urgent updates (chat messages, status changes) and `aria-live="assertive"` for urgent alerts (errors, time-sensitive notifications).
- **Meaningful alt text:** Describe the function, not the appearance, of images. "Submit button" not "blue button." Decorative images should have `alt=""`.
- **Announce state changes:** When UI state changes (tabs switch, accordions expand, modals open), the change must be communicated to screen readers through ARIA states (`aria-expanded`, `aria-selected`, `aria-hidden`).

### WCAG 2.2 Additions (Current Standard)

| Criterion | Level | Description |
|-----------|-------|-------------|
| **Focus Not Obscured (Minimum)** | AA | Focused elements must not be entirely hidden by other content (sticky headers, modals) |
| **Focus Not Obscured (Enhanced)** | AAA | Focused elements must not be even partially hidden |
| **Focus Appearance** | AAA | Focus indicators must have a minimum area and contrast |
| **Dragging Movements** | AA | Any function using dragging must have a single-pointer alternative |
| **Target Size (Minimum)** | AA | Interactive targets must be at least 24x24 CSS pixels |
| **Consistent Help** | A | Help mechanisms must appear in the same relative location across pages |
| **Redundant Entry** | A | Do not ask users to re-enter information they have already provided in the same flow |

**Source:** [WCAG.com - UX Tips for Designers](https://www.wcag.com/resource/ux-quick-tips-for-designers/), [Brand Vision - Accessible Navigation 2026](https://www.brandvm.com/post/accessible-navigation-ux-guide-2026)

### Accessibility Interaction Checklist

- [ ] All interactive elements are reachable and operable via keyboard
- [ ] Focus indicators are visible and meet 3:1 contrast ratio
- [ ] All images have appropriate alt text (or empty alt for decorative images)
- [ ] Form inputs have associated `<label>` elements
- [ ] Error messages are programmatically associated with their inputs and describe how to fix the error
- [ ] Color is never the sole means of conveying information
- [ ] Dynamic content changes are announced to screen readers via ARIA live regions
- [ ] Touch targets meet the WCAG 2.2 minimum of 24x24 CSS pixels (44x44 recommended)
- [ ] No content flashes more than 3 times per second
- [ ] Users can resize text to 200% without loss of content or functionality

---

## 9. Performance and Responsiveness

Performance directly impacts user behavior and conversion. These thresholds are based on measured human perception limits.

### Response Time Thresholds

| Threshold | User Perception | Design Response |
|-----------|----------------|-----------------|
| **0-100ms** | Instantaneous | Ideal for direct manipulation (drag, type, toggle) |
| **100-300ms** | Slight delay noticed | Acceptable for most interactions. No indicator needed. |
| **300-1000ms** | System is working | Show progress indicator (spinner, skeleton screen) |
| **1-5 seconds** | Attention wanders | Show progress bar with estimated time. Allow cancellation. |
| **5+ seconds** | Frustrating | User will likely abandon. Re-architect the interaction. |

### Optimistic UI Pattern

**Principle:** Assume the server operation will succeed. Update the UI immediately with the expected result, then reconcile when the server responds.

**When to use:** For operations with a high success rate (>99%): toggling favorites, posting comments, updating settings.

**When NOT to use:** For irreversible operations with meaningful failure rates: payments, deletion, sending messages to other users.

**Implementation:**
1. Update the UI instantly on user action
2. Send the request to the server in the background
3. If the server confirms success, do nothing (UI is already correct)
4. If the server returns an error, revert the UI and show a clear error message

### Skeleton Screens

**Principle:** Replace loading spinners with skeleton screens (gray placeholder shapes that mimic the layout of the content being loaded). Skeleton screens reduce perceived load time because they set user expectations about the incoming content structure.

**Rules:**
- Match the skeleton layout closely to the actual content layout
- Animate the skeleton with a subtle shimmer to indicate loading
- Never show skeleton screens for more than 3-5 seconds; if loading takes longer, switch to an explicit progress indicator

---

## 10. Practical Application Matrix

Quick reference for which principles apply to common design scenarios.

### Forms and Data Entry

| Principle | Application |
|-----------|------------|
| Hick's Law | Minimize visible fields. Use progressive disclosure for optional fields. |
| Miller's Law | Chunk form fields into logical groups of 3-5. |
| Postel's Law | Accept varied input formats. Auto-format as the user types. |
| Tesler's Law | Handle complexity server-side (address autocomplete, validation). |
| Progressive Disclosure | Multi-step forms with progress indicators outperform single-page long forms. |
| Loss Aversion | Auto-save progress. "Your information has been saved." |
| WCAG | Labels above fields, associated `<label>` elements, descriptive error messages. |

### E-Commerce and Conversion

| Principle | Application |
|-----------|------------|
| Fitts's Law | Large, prominent "Add to Cart" and "Checkout" buttons. |
| Hick's Law | Limit product variants shown at once. Use filters aggressively. |
| Anchoring | Show original price crossed out next to sale price. |
| Loss Aversion | "Only 3 left in stock." "Sale ends in 2 hours." |
| Social Proof | Reviews, ratings, "X people bought this" near the purchase button. |
| Peak-End Rule | Invest in the checkout success experience (confirmation page, order summary). |
| Doherty Threshold | Checkout must load in under 400ms. Preload the next step. |

### SaaS Dashboards

| Principle | Application |
|-----------|------------|
| Miller's Law | 4-6 key metrics visible at once. Tuck secondary metrics behind "View all." |
| Serial Position Effect | Place the most critical metric first (top-left) and the trend/summary last. |
| Jakob's Law | Follow established dashboard conventions (sidebar nav, top-right user menu). |
| Progressive Disclosure | Summary view by default; drill-down on click. |
| Tesler's Law | Smart defaults for date ranges, filters, and report configurations. |
| Zeigarnik Effect | Task lists, setup checklists, incomplete configurations highlighted. |

### Mobile Apps

| Principle | Application |
|-----------|------------|
| Fitts's Law | 48x48dp minimum touch targets. Primary actions at screen bottom. |
| Thumb Zone | Place primary navigation in the bottom tab bar within easy thumb reach. |
| Hick's Law | Bottom nav: 3-5 items maximum. |
| Serial Position Effect | Most important tabs at far left and far right of bottom bar. |
| Gestures | Always provide visible button alternatives. Hint at swipeable content. |
| Progressive Disclosure | Use bottom sheets for secondary actions. |
| Doherty Threshold | Skeleton screens on every view transition. Optimistic updates for all toggles. |

---

## Sources and Further Reading

### Primary References

- [Laws of UX](https://lawsofux.com/) -- Jon Yablonski's comprehensive collection of UX laws
- [Nielsen Norman Group](https://www.nngroup.com/) -- Research-based UX guidance
- [Interaction Design Foundation](https://ixdf.org/) -- Evidence-based UX education
- [Stanford Behavior Design Lab](https://behaviordesign.stanford.edu/) -- BJ Fogg's research on behavior change
- [W3C WAI](https://www.w3.org/WAI/) -- Web Accessibility Initiative standards and guidelines

### Key Books

- *The Design of Everyday Things* -- Don Norman (foundational principles of human-centered design)
- *Don't Make Me Think* -- Steve Krug (web usability principles)
- *Hooked: How to Build Habit-Forming Products* -- Nir Eyal (Hook Model)
- *Nudge* -- Richard Thaler & Cass Sunstein (choice architecture and behavioral economics)
- *Thinking, Fast and Slow* -- Daniel Kahneman (cognitive biases and decision-making)
- *Refactoring UI* -- Adam Wathan & Steve Schoger (practical visual design principles)
- *About Face: The Essentials of Interaction Design* -- Alan Cooper (comprehensive interaction design)

### Research Papers and Articles

- Fitts, P.M. (1954). "The information capacity of the human motor system in controlling the amplitude of movement." *Journal of Experimental Psychology.*
- Miller, G.A. (1956). "The Magical Number Seven, Plus or Minus Two." *Psychological Review.*
- Doherty, W.J. & Thadani, A.J. (1982). "The economic value of rapid response time." *IBM Systems Journal.*
- Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica.*
- [UX Design Institute - All 21 Laws of UX Explained](https://www.uxdesigninstitute.com/blog/laws-of-ux/)
- [inBeat - Behavioral Science in UX Design 2025](https://inbeat.agency/blog/behavioral-science-in-ux-design)
- [WCAG.com - Essential UX Accessibility Tips for Designers](https://www.wcag.com/resource/ux-quick-tips-for-designers/)
- [Smashing Magazine - Keyboard Navigation 2025](https://www.smashingmagazine.com/2025/04/what-mean-site-be-keyboard-navigable/)
- [Brand Vision - Accessible Navigation for Complex Websites 2026](https://www.brandvm.com/post/accessible-navigation-ux-guide-2026)

---

*Last updated: March 2026*
