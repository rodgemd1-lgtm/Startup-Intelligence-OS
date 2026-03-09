# Hevy -- Workout Tracker & Planner Gym Log

> Competitive Intelligence Profile | Last Updated: 2026-03-03

---

## 1. Overview

| Field | Detail |
|-------|--------|
| **Full Name** | Hevy -- Workout Tracker & Planner Gym Log |
| **Website** | [hevyapp.com](https://www.hevyapp.com/) / [hevy.com](https://hevy.com/) |
| **Founded** | 2019 (launched July 2019; built in 75 days) |
| **Co-Founders** | Guillem Ros (CEO, Barcelona) & Desmond McNamee (Ottawa) |
| **Company** | Hevy (bootstrapped, no VC funding) |
| **Headquarters** | Incorporated in Spain; distributed team (Barcelona, Ottawa, remote) |
| **Platforms** | iOS, Android, Apple Watch, Wear OS, Web (hevy.com) |
| **Technology** | React Native (cross-platform) |
| **Tagline** | "#1 Free Gym Workout Tracker & Planner" |
| **Category** | Strength training tracker + social fitness platform |
| **Positioning** | "The Strava of Weightlifting" |

Hevy is the fastest-growing workout tracker in the strength training space, combining robust logging functionality with a built-in social network. The founders met while working at 8fit (a fitness app in Berlin). McNamee identified the core insight: running and cycling had Strava for community, but weight lifting had no equivalent social layer. They left 8fit and incorporated in Spain (Ros's home country) for convenience, built the MVP in 75 days, and launched in July 2019. Apple featured Hevy in "Apps We Love" at launch -- a critical early credibility signal. The app has grown to 11+ million users with only ~$15K in total ad spend, making it one of the most capital-efficient consumer app stories in fitness.

### Founder Background
- **Guillem Ros:** Barcelona-based. App builder since age 16 (started with mobile gaming). Former product manager at 8fit. CEO of Hevy. Appeared on Sub Club Podcast and RevenueCat podcast sharing the organic growth playbook.
- **Desmond McNamee:** Grew up in Ottawa, Canada. Previously worked at LiveQoS. Co-founded Hevy with Ros. Returned to Ottawa where 3 of the team members are based.
- Both own 50% of the company. Bootstrapped from day one. Philosophically opposed to VC funding -- pursuing growth and profitability without external pressure.

---

## 2. User Demographics

### Scale
- **11+ million users** (as of early 2026, per Hevy's own site)
- Growth trajectory: single-digit daily downloads at launch --> 1M downloads by Dec 2021 --> 2M by May 2023 --> 9M+ by late 2025 --> 11M+ by 2026
- ~300K new installs per month (current run rate)

### Who Uses It
- **Primary audience:** Young-to-mid lifters (18-35) who want both tracking and social motivation
- **Secondary audience:** Beginners entering strength training who benefit from the free tier and community routines
- **Persona archetype:** The social lifter who wants to share PRs, follow friends, and be part of a fitness community
- **Also attracts:** Adults returning to fitness, including people with moderate gym anxiety who find motivation in the community feed
- **Fitness coaches:** Hevy Coach product extends into B2B (personal trainers managing clients)
- **Not ideal for:** Privacy-focused minimalists, advanced powerlifters needing detailed periodization, users wanting AI-driven programming (though Hevy Trainer, launched Feb 2026, begins addressing this)

### Target Demographics by Use Case
- **Social fitness enthusiasts** -- want to see friends' workouts, share progress, compete
- **Budget-conscious lifters** -- attracted by the generous free tier that actually works
- **Program explorers** -- browse and import community-shared routines
- **Beginners** -- benefit from exercise demos, pre-built programs, community support
- **Less suitable for:** Minimalists, privacy-focused users, advanced periodization needs

### Community Sentiment (Reddit / Forums)
- **Overwhelmingly positive** on Reddit -- frequently the #1 recommendation in "best workout app" threads
- Dedicated subreddit: r/Hevy (active community, doubles as organic marketing channel)
- Popular in r/fitness, r/gym, r/weightroom, r/weightlifting, r/bodybuilding
- Key Reddit praise: "Hevy has a slightly better free tier, nicer UI, more free templates, better device integrations... Hevy has shown a lot more development" (vs. Strong)
- Reddit consensus in 2025-2026: "Best free weightlifting app"
- **Typical Reddit debate:** FitNotes for absolute simplicity/privacy, Strong for speed and minimal UX, Hevy for social features and generous free tier
- **Criticisms on Reddit:**
  - Requires internet connection for many features (frustrates lifters in low-signal gyms)
  - Some users find the social feed distracting for a "pure" workout tracker
  - Premium upselling can feel aggressive
  - Powerlifters find it less detailed than specialized trackers for advanced programming
  - No exercise selection guidance -- tells you HOW to do exercises but not WHICH ones to do
  - "Good enough at everything without excelling at anything specific"

---

## 3. Core Features

### 3.1 Workout Logging
- Log sets, reps, weight, and RPE (Rate of Perceived Exertion)
- Set types: Warm-up, Normal, Drop sets, Failure sets
- Superset support (group exercises together)
- Previous workout values displayed inline for progressive overload
- Custom exercise notes per workout
- Warm-up set calculator and weight plate calculator
- Automatic rest timer (customizable per exercise, push notification when complete)
- Live personal record notifications during workouts
- Live Activity feature (iOS Dynamic Island / Lock Screen)
- Duration tracking per set
- Calories burned tracking
- Heart rate integration (via Apple Watch)
- Reorder or replace exercises mid-workout (drag and drop)
- Ability to duplicate exercises, replace default animation with own photo

### 3.2 Templates & Routines
- Create and save unlimited routines (even on free tier)
- Pre-built routine library: 26+ training programs across 8 categories
- Categories: beginner, intermediate, advanced, at-home, dumbbell-only, travel circuits, etc.
- Organize routines into folders (custom folders on Pro)
- Share routines and folders with other users
- Import routines from community or friends
- Community-shared workout programs (user-generated, unmoderated quality)
- 12 customizable workout settings per routine

### 3.3 Progress Charts & Analytics
- Comprehensive analytics dashboard
- Individual exercise graphs: volume, best weight, total reps, estimated 1RM
- Muscle group activity charts (sets-per-muscle-group weekly breakdown)
- Muscle distribution visualization
- Training frequency and consistency trends
- Workout consistency streaks
- Monthly performance reports (auto-generated, shareable)
- "Year in Review" annual summary (shareable)
- Automatic PR detection and tracking
- **Pro only:** Advanced analytics, enhanced progress charts, CSV data export

### 3.4 Body Measurements
- Body measurements tracking (weight, circumference data points)
- Progress photos (before/after with overlays)
- Body composition data points

### 3.5 Social Features (Major Differentiator)
- **Home Feed:** Instagram-like social feed showing workouts from people you follow (session name, description, stats, duration, volume, PRs)
- **Likes and Comments:** Like sessions, leave comments, reply
- **Discovery Feed:** Browse recent workouts from users outside your network
- **User Profiles:** Public athlete profiles with workout history and stats
- **Leaderboards:** Gamified head-to-head comparison tool (muscle group focus, workout stats)
- **Performance Comparison:** Side-by-side stats with other users
- **Social Media Shareables:** Auto-generated shareable cards after each workout (multiple style options) for Instagram Stories, etc.
- **Strava Integration:** Auto-post workouts to Strava
- **Photo/Video Uploads:** Gym selfies and training footage in feed
- **Follow System:** Follow friends, athletes, and discoverable users for motivation
- **Routine Sharing:** Share workout programs and folders with the community

### 3.6 Apple Watch & Wearables
- Full Apple Watch companion app (watchOS 8.0+)
- Wear OS support (Android watches)
- Log workouts directly from the wrist (phone stays in locker)
- Heart rate data synced to workout details (visible to user and friends)
- Live sync between Watch and phone
- Custom Apple Watch face designs
- Apple Health integration (bidirectional sync)

### 3.7 Exercise Library
- **400+ built-in exercises** with animated 3D model demonstrations (looping, clean backgrounds)
- Exercises categorized by muscle group and equipment type
- Equipment coverage: barbells, dumbbells, kettlebells, machines, resistance bands, bodyweight
- Custom exercises: **7 on free tier, unlimited on Pro**
- Duplicate and modify existing exercises
- Replace default animations with personal photos
- Contextual form tips appear during logging

### 3.8 AI & Smart Features (New, 2026)
- **Hevy Trainer** (launched ~Feb 2026, included in Pro at no extra cost):
  - Personalized workout plan generator based on goals, experience, equipment, frequency, time constraints
  - Generates complete programs with exercises, rep ranges, rest periods, starting weight recommendations
  - Ongoing performance analysis and adaptive guidance
  - Weekly progress reports: consistency, volume distribution, individual exercise progress
  - Muscle group distribution tracking
- **HevyGPT:** ChatGPT-powered workout plan builder that imports directly into Hevy

### 3.9 Hevy Coach (B2B Product)
- Separate platform for personal trainers and coaching businesses
- Create and assign workout programs to clients
- Monitor client activity, adherence, and body metrics
- In-app chat with clients (instant notifications)
- Lead generation forms
- Team management (multiple trainers under one account)
- 400+ exercises plus custom exercise creation
- Clients use the Hevy app for free; coaches pay subscription
- 30-day free trial, no credit card required
- Scales from 1 to 500 clients
- Monthly subscription, cancel anytime

### 3.10 Cross-Platform & Integrations
- Full web app at hevy.com (review workouts, create routines, edit profile, social feed)
- Live sync between mobile, web, and Apple Watch
- Offline workout logging (syncs when back online)
- Apple Health integration
- Strava integration
- Home screen widgets (iOS/Android)
- Home Assistant community integration (third-party)

---

## 4. UX/UI Flow

### 4.1 Onboarding (10 Steps)
1. **Welcome/splash screen** with branded loading state (Hevy logo, not generic spinner)
2. **Account creation** with real-time field validation (green checkmarks appear instantly as fields are correctly filled)
   - Sign-up required before accessing ANY features (no guest mode)
   - Email or social login
   - **Friction point:** Forced sign-up before core experience; allowing guest trial could reduce drop-off
3. **Basic profile setup** (name, photo)
4. **Fitness experience level** selection
5. **Goal setting** questions
6. **Equipment availability**
7. **Branded loading transition**
8. **Soft paywall** (appears at ~00:39 mark, right after initial setup but before core app interaction)
   - Three tiers presented: Monthly ($8.99), Yearly ($59.99), Lifetime
   - "Save 33%" badge on annual plan
   - Heavy social proof: user testimonials, star ratings, Apple "Apps We Love" badge
   - Feature comparison table (free vs. Pro)
   - FAQ section directly on the paywall screen (addresses objections upfront)
   - No free trial offered in this flow
   - Dismissible (soft paywall -- not forced)
9. **Core app introduction** with contextual tooltips
10. **First workout prompt**

### 4.2 Core Workout Logging Flow

**Step 1 -- Start Workout**
- Tap "Start Workout" from main screen or select a saved routine
- Option to start an empty workout or use a template
- Templates show previous weights/reps for reference

**Step 2 -- Add Exercises**
- Search through 400+ exercise library
- Filter by muscle group, equipment, or exercise type
- Each exercise shows animated 3D demonstration with form cues
- Add custom exercises on-the-fly
- Contextual pop-ups appear at relevant moments (e.g., "How to log dumbbell weights correctly")

**Step 3 -- Log Sets / Reps / Weight**
- Swipeable exercise cards with set tables
- Fields: Set number, Previous (last workout's data), Weight, Reps, RPE
- Tap to enter weight and reps
- Completing a set triggers a **smooth checkmark animation** (micro-interaction for dopamine hit)
- Rest timer auto-starts on set completion
- Live PR notification fires if a personal record is broken mid-workout
- Reorder or replace exercises without leaving the workout screen (drag and drop)
- Superset grouping available
- **UX gap noted:** No "Next" button to auto-advance cursor to next input field
- **UX gap noted:** Cannot save/update routine if you change an exercise mid-workout

**Step 4 -- Finish Workout**
- Tap "Finish" to complete
- Summary screen with: duration, total volume, exercises performed, PRs hit, muscle group distribution
- Auto-generated shareable cards for social media (multiple style options, customizable backgrounds)
- Option to share to Instagram Stories (auto-tags @hevyapp)
- Workout auto-posts to social feed for followers to see
- Auto-post to Strava if connected

### 4.3 Social Features Flow
- **Home tab:** Social feed showing recent workouts from followed users
- Tap any workout for full exercise/set/weight/heart rate/duration details
- Like and comment inline
- **Head-to-head comparison tool:** Tap a user's profile for gamified stat comparison (muscle group focus, workout volume, frequency)
- **Discovery tab:** Surfaces active users via basic recommendation algorithm (creates "micro-influencers" within the app)
- Follow friends via search, contacts, or discovery
- Share workout cards to Instagram Stories and other platforms

### 4.4 Progress Tracking Flow
- Dedicated analytics tab with filterable charts
- Filter by exercise, muscle group, or time range
- Body measurements and progress photos in separate section
- Monthly report cards delivered automatically (designed to be screenshot-worthy and shareable)
- Year in Review feature (annual recap with highlights)
- Exercise detail view: per-exercise progress charts, PR timeline, volume trends

### 4.5 History & Analytics Screens
- **History tab:** Chronological list of all completed workouts
- **Analytics/Stats:** Muscle group distribution charts, volume trends, consistency streaks
- **Exercise detail:** Tap any exercise to see per-exercise progress charts
- **Leaderboards:** Compare stats with friends and community

---

## 5. Design Language

### Visual Identity
| Element | Detail |
|---------|--------|
| **Default Mode** | Dark mode (flagship experience) |
| **Color Palette** | Deep navy/black backgrounds with electric blue accent color |
| **Typography** | Uni Sans -- clean, geometric sans-serif conveying strength and precision |
| **Card Design** | Sharp-edged card components creating a dynamic, powerful aesthetic |
| **Mode Support** | Light and dark mode available |
| **Iconography** | Clean, minimal line icons consistent with modern iOS/Android conventions |
| **Exercise Demos** | High-quality 3D animated models (looping, clean backgrounds) |
| **App Size** | ~193 MB (heavier due to social features and 3D animations) |

### Design Pillars
1. **Clarity** -- Information hierarchy prioritizes what matters during a workout
2. **Motivation** -- Badges, ranks, streaks, PR celebrations reward consistency
3. **Simplicity** -- Core logging is fast despite feature density
4. **Energy** -- Dark background with electric blue accents creates "gym at night" atmosphere

### Micro-Interactions & Gamification
- Smooth checkmark animation on set completion (rewarding tactile feedback)
- PR celebration effects when records are broken
- Green checkmarks during onboarding field validation
- Animated transitions between screens
- Badges, ranks, and streaks for consistent logging and milestones
- Head-to-head comparison animations

### Chart Styles
- Muscle group distribution visualizations (pie/radar charts)
- Volume trend line graphs
- Sets per muscle group per week bar charts
- Progress photos with before/after overlay tools
- Monthly report infographic-style summaries (designed to be screenshot-worthy)

### Shareable Content Design
- Auto-generated post-workout cards with multiple style options
- Customizable backgrounds and branded overlays
- Designed for Instagram Stories format
- Monthly reports and Year in Review graphics are share-optimized

### Overall Feel
- "What happens when Instagram meets a workout tracker -- in mostly good ways"
- Dark, bold, energetic without being aggressive; feels premium but accessible
- More visually rich than Strong, with richer animations and social elements
- Designed to make users want to share their workouts
- The dark background with electric blue accents reduces eye strain during gym use while conveying serious-lifter energy

---

## 6. Monetization

### Free Tier (Very Generous -- Strategic Weapon)
- Unlimited workout logging (no cap)
- Unlimited routines and templates
- Progressive overload tracking
- Automatic PR detection
- Full exercise library with 3D video demonstrations
- Basic analytics and progress charts
- Social features (feed, likes, comments, follows)
- Community workout programs
- Rest timer
- Cloud backup
- Apple Watch / Wear OS support
- Cross-device sync
- **Limitations:** 7 custom exercises max, no CSV export, no advanced analytics, ads present, no custom folders, no workout attachments

### Hevy Pro Pricing
| Plan | Price | Notes |
|------|-------|-------|
| Monthly | $8.99/month | Best for trial before committing |
| Annual | $59.99/year (~$5/month) | "Save 44%" vs. monthly; "Save 33%" marketed on paywall |
| Lifetime | $74.99 (one-time) | Availability varies; historically offered but not always visible |

*Note: Some sources cite lower prices ($3.99/month, $23.99/year) -- pricing may vary by region, promotional period, or have increased over time. Older data from Sub Club podcast cited $3/month and $24/year.*

### Pro Features Unlocked
- Advanced analytics and deeper insight charts
- Unlimited custom exercises (vs. 7 on free)
- Workout notes and attachments
- CSV data export
- Warmup set tracking
- Custom routine folders
- Ad-free experience
- Priority support
- **Hevy Trainer** (AI programming) -- included at no extra cost (launched Feb 2026)

### Hevy Coach (B2B Revenue Stream)
- Separate subscription for personal trainers
- 30-day free trial, no credit card required
- Scales from 1 to 500 clients
- Clients use Hevy for free (coach pays)
- Monthly subscription, cancel anytime
- Exact pricing tiers vary (visit hevycoach.com/pricing)

### Pricing Strategy Analysis
- **Significantly undercuts competitors:** Hevy Pro ~$5/month (annual) vs. Strong ~$7.49/month vs. Fitbod ~$12.99/month
- Low pricing reflects near-zero customer acquisition costs from organic growth
- **No consistent lifetime purchase option** -- subscription-only model maximizes recurring revenue but creates an opening for competitors like Strong ($99.99 lifetime)
- The generous free tier is the primary acquisition tool; conversion relies on users wanting deeper analytics after establishing a workout habit
- Soft paywall at 39 seconds during onboarding -- early but dismissible

---

## 7. Business Metrics

### Key Stats
| Metric | Value |
|--------|-------|
| **Total Users** | 11+ million |
| **Founding Team** | 2 co-founders (50/50 split) |
| **Team Size** | ~13 people |
| **Funding** | Bootstrapped ($0 VC) |
| **Total Ad Spend** | ~$15K (lifetime) |
| **Profitable** | Yes |
| **Days to Build MVP** | 75 |
| **Time to Ramen Profitability** | ~18 months |
| **Technology** | React Native |

### Revenue Trajectory
| Period | Revenue / Milestone | Source |
|--------|---------------------|--------|
| 2019-2020 | Early stage, 5-10 daily downloads | Sub Club Podcast |
| 2021 | ~$1M ARR (estimated) | OBJ.ca (implied from 2022 doubling) |
| Jan 2022 | **Cracked top 5 on Google Play** -- inflection point | OBJ.ca |
| 2022 | ~$2M ARR projected | OBJ.ca |
| Mid-2022 | ~$20K/month per platform (~$40K total) | BoringCashCow |
| Late 2022 | 1.5M users | OBJ.ca |
| Nov 2023 | ~$160K MRR (~$1.9M ARR) | Starter Story |
| 2025 (est.) | ~$250K-$300K/month (~$3M-$3.6M ARR) | ScreensDesign |
| 2025-2026 (est.) | Potentially higher based on 300K installs/month | Extrapolated |

### Downloads & Growth Milestones
| Milestone | Date |
|-----------|------|
| Launch | July 2019 |
| Apple "Apps We Love" feature | July 2019 (at launch) |
| Ramen profitability | ~January 2021 |
| 1 million downloads | December 2021 |
| Top 5 Google Play Store | January 2022 (inflection point) |
| 1.5 million users | Late 2022 |
| 2 million downloads | May 2023 |
| 9+ million downloads | Late 2025 |
| 11+ million users | Early 2026 |
| ~300K installs/month | Current run rate |

### App Store Performance
| Platform | Rating | Notes |
|----------|--------|-------|
| iOS (App Store) | 4.9 stars | 395K+ ratings |
| Google Play | 4.9 stars | Consistently top-ranked in Health & Fitness |

### Website Traffic
- 725.6K monthly visits (September 2023 data)
- 77% of traffic from organic search (SEO-first strategy)
- Strong organic search presence for workout-related keywords

---

## 8. Go-to-Market Strategy

### The Organic Growth Playbook
Hevy achieved 11M+ users with only ~$15K in total ad spend. Their growth is a masterclass in product-led organic acquisition.

#### Phase 1: Launch & Early Credibility (July 2019)
- Built MVP in 75 days
- Secured Apple "Apps We Love" feature at launch -- massive credibility signal
- Started at 5-10 downloads per day
- Focused entirely on product quality over marketing
- ASO strategy: "Just do what everyone else is doing" (80% strategy) -- basic keyword targeting, but nothing advanced

#### Phase 2: Product-Market Fit Signal (2020-2021)
- COVID initially created headwinds (gyms closed)
- Social features created organic user clusters -- people followed each other without company intervention
- This organic community formation was the founders' key signal of product-market fit
- Guillem Ros's key insight: "Even the behemoths didn't pay to acquire users in the early days"
- Reached ramen profitability ~18 months post-launch
- Hit 1M downloads by December 2021

#### Phase 3: Viral Inflection (January 2022)
- Cracked top 5 on Google Play Store during New Year's resolution wave
- Critical: strong retention meant the January spike SUSTAINED rather than crashing post-resolution
- Downloads went from 1M to 2M in just 5 months
- McNamee: "All of a sudden, we weren't scraping by financially"
- High ratings (4.9 stars) fed app store algorithms, which drove more organic discovery

#### Phase 4: Compounding Network Effects (2022-Present)
- Social features function as viral loops: users invite gym partners, friends see workouts, new users join
- Each new user adds value to existing users (classic network effect)
- Users invest in both personal data (workout history) AND social relationships, creating **dual switching costs**
- Basic recommendation algorithm surfaces highly active users, creating discoverable "micro-influencers" within the app
- Shareable workout cards turn every user into a free billboard on Instagram

### How Hevy Overtook Strong
Strong was the incumbent workout tracker with a loyal user base. Hevy displaced it through a multi-vector strategy:

1. **Generous free tier:** Strong aggressively paywalled features (3-routine limit); Hevy gave away unlimited workouts, routines, and social features for free
2. **Social layer:** Strong is solo-only; Hevy added Instagram-like social features that created network effects Strong cannot replicate without a ground-up rebuild
3. **Lower price point:** Hevy Pro significantly undercuts Strong Pro
4. **Faster development velocity:** Hevy shipped features faster and more visibly iterated, earning community trust
5. **Community engagement:** Active Reddit presence (r/Hevy), responsive to user feedback
6. **Modern design:** Hevy's UI feels more contemporary and polished than Strong's utilitarian aesthetic
7. **Cross-platform parity:** Full web app + Apple Watch + Wear OS + seamless sync vs. Strong's more limited ecosystem

### Viral Loop Mechanics (Engineered Into Product)
1. **Post-workout shareable cards:** Auto-generated, branded cards prompt sharing to Instagram Stories (free impressions for Hevy)
2. **Monthly report shareables:** Training summaries designed to be screenshot-worthy and shared on social
3. **In-app social feed:** Following friends creates network effects -- follow-back prompts and friend invitations
4. **Routine sharing:** Users share workout programs with friends, bringing new users into the ecosystem
5. **Strava integration:** Cross-posting to Strava exposes Hevy to the broader endurance sports community
6. **Year in Review:** Annual recap graphics designed for social sharing (similar to Spotify Wrapped effect)

### Reddit as a Growth Channel
- r/Hevy subreddit serves as community hub and organic marketing channel
- Users organically recommend Hevy in fitness subreddits (not official brand accounts -- authentic advocacy)
- The generous free tier makes it easy for Redditors to recommend without caveats
- Users frequently post "switched from Strong/JEFIT to Hevy" testimonials
- Founders' philosophy: "Building a fantastic workout logging and social experience is our best form of marketing"

---

## 9. Content Strategy

### Blog & SEO (Primary Channel)
- hevyapp.com blog generates 725K+ monthly visits
- 77% of traffic from organic search (SEO-first strategy)
- Content pillars:
  - Workout guides and exercise tutorials
  - Training program explanations
  - Feature announcements and how-to tutorials
  - Fitness science content (claims to reference only peer-reviewed studies)
  - "How we built Hevy" founder story
  - Comparison articles positioning Hevy favorably
- Content reviewed by certified personal trainers

### User-Generated Content Engine (Built Into Product)
The app itself generates shareable content at scale:
- Post-workout summary cards (multiple style options, customizable backgrounds)
- Monthly training reports (designed to be screenshot-worthy)
- Year-in-Review graphics (annual recap)
- PR celebration cards
- Every shareable includes Hevy branding, turning users into micro-influencers
- This UGC flywheel is the primary growth loop and would be extremely expensive to replicate with paid marketing

### Community Building (In-App)
- The social feed IS the community -- no need for external Discord or forums
- Discovery feed helps users find and follow new athletes
- Leaderboards create competitive engagement
- Routine sharing creates a content library built by users
- Photo/video uploads add personality to workout logs

### Podcast & Press Appearances
- Guillem Ros has appeared on Sub Club Podcast (RevenueCat) and other startup/app podcasts
- Shares organic growth story as case study for bootstrapped app development
- Coverage in Ottawa Business Journal, Starter Story, BoringCashCow

### Social Media Presence
- Instagram is primary channel (users tag @hevyapp in Stories)
- Hiring Social Media Specialists (Barcelona, hybrid-remote)
- Editorial calendar aligned with product and marketing activities

### Notable Content Gaps
- Limited YouTube presence (no prominent branded channel strategy)
- No podcast of their own (despite co-founder appearing on industry podcasts)
- No visible TikTok-native content strategy
- Minimal influencer marketing or creator partnerships
- No newsletter or email content program visible

---

## 10. Strengths & Weaknesses

### Strengths
1. **Best-in-class free tier:** Unlimited workouts, routines, and social features at $0 -- most competitors paywall these. This is the #1 strategic weapon for user acquisition.
2. **Social network effect:** Instagram-like social layer creates viral loops, retention moats, and dual switching costs (personal data + social relationships). The more friends on Hevy, the harder it is to leave.
3. **Exceptional app store ratings:** 4.9 stars across both platforms with 395K+ ratings -- strong trust signal that feeds algorithmic discovery.
4. **Organic growth engine:** ~$15K total ad spend for 11M+ users -- nearly unheard-of CAC efficiency. Product quality IS the marketing.
5. **Modern, polished UI:** Dark mode aesthetic with smooth micro-interactions feels premium. Attracts younger demographics.
6. **Aggressive pricing:** Pro at ~$5/month (annual) significantly undercuts every major competitor.
7. **Cross-platform sync:** Mobile + Watch + Wear OS + Web with seamless live sync and offline support.
8. **Exercise library quality:** 400+ exercises with 3D animated demos (not just static images or text).
9. **SEO dominance:** 77% organic traffic to 725K+ monthly blog visits creates a compounding content moat.
10. **Lean operations:** ~13-person team, bootstrapped, profitable -- exceptional unit economics and capital efficiency.
11. **Hevy Coach B2B expansion:** Second revenue stream targeting personal trainers; creates ecosystem lock-in (trainer requires clients to use Hevy).
12. **Hevy Trainer (Feb 2026):** AI programming included in Pro at no extra cost -- beginning to close the "no intelligent programming" gap.
13. **Shareable content engine:** Every workout generates branded, share-ready cards -- turns users into free billboards.

### Weaknesses
1. **No AI coaching (historically):** Until Hevy Trainer (Feb 2026), zero intelligent programming. Trainer is brand new and unproven. Still lacks real-time form feedback or auto-regulation.
2. **Not for advanced powerlifters:** Lacks detailed periodization tools, block programming, velocity-based training, deload planning, auto-regulation.
3. **Cloud-only data storage:** User data lives on Hevy servers, not locally -- privacy concern for some users. Less control vs. Strong's CSV export + local backup.
4. **Requires internet for most features:** Offline mode limited to basic logging. No social, no sync, no analytics offline. Critical gap for low-signal gyms.
5. **Forced sign-up friction:** Cannot try the app without creating an account -- no guest mode. Potential drop-off point.
6. **Social features can distract:** Feed browsing, likes, comments can pull focus from actual training. Privacy-conscious and "just let me lift" users are turned off.
7. **No exercise selection guidance:** Tells you HOW to do exercises but not WHICH ones to do (Trainer may partially address this).
8. **Subscription-only model:** No consistent lifetime purchase option. Loses cost-conscious users who compare against Strong's $99.99 lifetime deal.
9. **Community-generated routine quality varies:** No curation or quality control on shared programs -- variable quality.
10. **Reported bugs:** Occasional black screen issues, sync glitches mentioned in reviews.
11. **No nutrition tracking:** Purely workout-focused -- no food logging, calorie tracking, or macro support.
12. **Aggressive onboarding paywall:** Paywall at 39 seconds feels early. Combined with forced sign-up, the first minute can feel transactional.
13. **No "Next" button in logging:** Cannot auto-advance cursor to next input field when entering set data -- minor but real UX friction during workouts.
14. **Larger app size:** ~193 MB (vs. Strong's ~106 MB) due to social features and 3D animations.

---

## 11. Key Takeaways

### What Hevy Does Right (Learn From)

1. **Generous free tier drives viral adoption.** Hevy's biggest strategic weapon is giving away what competitors charge for. This creates massive top-of-funnel, and social features convert free users into paying users through network effects, not paywalls. The free tier IS the marketing budget.

2. **Social features are a growth engine, not a nice-to-have.** The follow/feed/like system creates viral loops (acquisition), retention hooks (switching costs from social relationships), and organic marketing (shareable workout cards). This triple function makes social the most valuable feature category in the app.

3. **Product quality IS the marketing strategy.** 4.9-star ratings feed app store algorithms, which drive organic discovery. High retention signals = algorithmic boost = more free downloads. The $15K total ad spend proves that when the product is good enough, paid marketing becomes optional.

4. **SEO-first content strategy compounds.** 77% organic traffic at 725K visits/month is a massive competitive moat that grows over time. Every blog post about workout guides and exercise tutorials is a permanent acquisition channel.

5. **Micro-interactions matter.** Checkmark animations, PR celebrations, streak badges -- these small touches make logging feel rewarding, not tedious. The emotional design drives the behavior loop.

6. **Dark mode as identity.** The dark UI is not just an option -- it is the brand identity. It signals "serious lifter" and reduces eye strain during gym use. It is a design decision that communicates positioning.

7. **Dual switching costs create a moat.** Users accumulate both personal data (years of workout history, PRs, body measurements) AND social relationships (followers, friends, routine shares). Leaving means losing both.

### Where TransformFit Can Differentiate

1. **AI-first from day one.** Hevy bolted on AI (Trainer) in February 2026 after nearly 7 years. TransformFit can be AI-native -- intelligent programming, adaptive progression, exercise selection, recovery management, and real-time coaching from the start. Hevy's AI is an afterthought; make it the core.

2. **Nutrition integration.** Hevy is workout-only. Combining workout tracking with nutrition coaching creates a more complete fitness operating system and captures the holistic health segment Hevy ignores.

3. **Advanced periodization.** Hevy loses advanced lifters to niche apps (JuggernautAI, Bromley, etc.). Building proper block periodization, velocity-based training support, and load management captures the underserved serious athlete segment.

4. **Privacy-first option.** Hevy's cloud-only model is a weakness. Offering local-first data with optional cloud sync could capture the privacy-conscious segment that currently defaults to Strong.

5. **Guided onboarding for beginners.** Hevy assumes gym knowledge. A "simple mode" or guided first-workout experience (exercise recommendations, weight suggestions, form guidance) could dramatically reduce the intimidation factor for beginners.

6. **Quality-controlled programming.** Unlike Hevy's unmoderated community routines, curated expert-designed programs with clear progression paths and quality guarantees add real value.

7. **Coaching + AI hybrid.** Hevy Coach is a separate product. Integrating human coaching and AI recommendations into one unified app creates a differentiated experience that neither Hevy nor Hevy Coach currently offers.

8. **Offline-first architecture.** A competitor that combines Hevy's social features with Strong's offline reliability and data ownership would be compelling. Build for the gym-signal-dead-zone user.

### Competitive Positioning Summary
- Hevy is the "social gym tracker" -- its moat is network effects and free-tier generosity
- It is vulnerable at both ends: **too basic for advanced athletes, too manual for beginners who want guidance**
- The AI programming gap (only just addressed in Feb 2026 with Trainer) represents a window of opportunity for AI-native competitors
- Hevy's social moat is real but not unbreakable -- it took them 3+ years to build meaningful network density
- The subscription-only pricing creates an opening for one-time-purchase alternatives

### Risk Assessment for a New Entrant
| Dimension | Risk Level | Notes |
|-----------|------------|-------|
| Competing on workout logging | **HIGH** | Hevy has 7 years of iteration and 11M users |
| Competing on social features | **MEDIUM** | Network effects create real switching costs, but take time to build |
| Competing on AI/intelligent programming | **LOW** | Hevy is a newcomer here; TransformFit can lead |
| Competing on nutrition/holistic fitness | **LOW** | Hevy has zero presence here |
| Competing on advanced periodization | **LOW** | Hevy deliberately avoids this segment |
| Competing on offline/privacy | **LOW** | Hevy's cloud-only model is a known weakness |

---

## Appendix: Head-to-Head Comparison -- Hevy vs. Strong

| Dimension | Hevy | Strong |
|-----------|------|--------|
| **Founded** | 2019 | 2014 |
| **Users** | 11M+ | 5M+ |
| **Free tier** | Generous (unlimited everything) | Restrictive (3 routines) |
| **Social features** | Full social network | None |
| **Exercise database** | 400+ with 3D demos | Hundreds |
| **Logging speed** | Fast | Fastest |
| **Offline support** | Limited | Full |
| **Data ownership** | Cloud-only | CSV export + local backup |
| **Lifetime purchase** | Not consistently available | Yes ($99.99) |
| **Monthly price** | $8.99 | $4.99 |
| **Annual price** | $59.99 | $29.99 |
| **Design** | Modern, polished, dark mode | Functional, minimal |
| **Apple Watch** | Yes | Yes (with Live Sync) |
| **AI features** | Hevy Trainer (new, Feb 2026) | None |
| **Growth rate** | Hypergrowth | Steady |
| **Funding** | Bootstrapped | Unfunded |
| **Moat** | Network effects + free tier | Simplicity + offline + data ownership |

---

## Sources
- [Hevy Official Site](https://www.hevyapp.com/)
- [Hevy Feature List](https://www.hevyapp.com/features/)
- [Hevy About Us](https://www.hevyapp.com/about-us/)
- [How We Built Hevy](https://www.hevyapp.com/how-we-built-hevy/)
- [Hevy Pricing](https://hevy.com/pricing)
- [Hevy App Store](https://apps.apple.com/us/app/hevy-workout-tracker-gym-log/id1458862350)
- [Hevy Google Play](https://play.google.com/store/apps/details?id=com.hevy&hl=en_US)
- [OBJ: Fitness app entrepreneur pumped by Hevy's progress to $2M](https://obj.ca/fitness-app-entrepreneur-pumped-by-hevys-progress-to-2m-in-annual-revenue/)
- [Sub Club: Cultivating Organic Growth with Viral Loops -- Guillem Ros Salvador](https://subclub.com/episode/cultivating-organic-growth-with-viral-loops-guillem-ros-salvador-hevy)
- [RevenueCat: Hevy Two Million Downloads No Paid Marketing](https://www.revenuecat.com/blog/growth/guillem-ros-hevy-podcast/)
- [Starter Story: How Hevy Achieved $160K MRR](https://www.starterstory.com/hevy-breakdown)
- [BoringCashCow: Workout Tracking App Makes $40K a Month](https://boringcashcow.com/view/workout-tracking-app-makes-40k-a-month)
- [ScreensDesign: Hevy Showcase](https://screensdesign.com/showcase/hevy-workout-tracker-gym-log)
- [PRPath: Hevy App Review 2026](https://www.prpath.app/blog/hevy-app-review-2026.html)
- [GymGod: Strong vs Hevy 2026](https://gymgod.app/blog/strong-vs-hevy)
- [Hevy 2025 Features Guide](https://help.hevyapp.com/hc/en-us/articles/33106320824727-Everything-You-Need-to-Know-About-the-Hevy-App-2025-Features-Guide)
- [Hevy Exercise Library: 400+ Exercises](https://help.hevyapp.com/hc/en-us/articles/35688251991575-Hevy-Exercise-Library-400-Exercises-and-Custom-Exercises)
- [Announcing Hevy Trainer](https://www.hevyapp.com/announcing-hevy-trainer/)
- [Hevy Coach](https://hevycoach.com/)
- [HotelGyms: Hevy App Review](https://www.hotelgyms.com/blog/hevy-workout-app-review-the-up-and-comer-taking-the-fitness-world-by-storm)
- [Hevy Pro Subscription Details](https://help.hevyapp.com/hc/en-us/articles/35119778922263-Hevy-Pro-Subscription-How-to-get-Pro-and-What-Does-It-Include)
- [Hevy Crunchbase](https://www.crunchbase.com/organization/hevy)
- [Hevy Coach -- Capterra Reviews](https://www.capterra.com/p/10015732/Hevy-Coach/reviews/)
- [SmartRabbitFitness: Fitbod vs Hevy vs Strong 2026 Prices](https://www.smartrabbitfitness.com/blog/en/fitness-ai-apps-price-comparison-fitbod-strong-hevy-2025)
- [SensAI: Fitbod, Strong, Hevy, and SensAI 2025 Feature Showdown](https://www.sensai.fit/blog/fitness-app-comparison)
