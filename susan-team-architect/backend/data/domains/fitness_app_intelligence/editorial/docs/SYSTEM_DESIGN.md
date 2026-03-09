# TransformFit System Design Document
## Master Technical Blueprint for the World's Best Fully Automated Fitness App

**Version:** 1.0
**Date:** 2026-03-03
**Status:** Architecture Phase
**Author:** Mike Rodgers / TransformFit Engineering

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Full System Architecture](#2-full-system-architecture)
3. [The "World's Best" Differentiators](#3-the-worlds-best-differentiators)
4. [Automation Architecture](#4-automation-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Data Model Design](#6-data-model-design)
7. [AI/ML Pipeline Architecture](#7-aiml-pipeline-architecture)
8. [Integration Layer](#8-integration-layer)
9. [Security and Compliance](#9-security-and-compliance)
10. [MVP to Scale Roadmap](#10-mvp-to-scale-roadmap)
11. [Research Sources](#11-research-sources)

---

## 1. Executive Summary

TransformFit is an AI-first fitness platform that unifies four pillars -- training, nutrition, recovery, and mental performance -- into a single intelligent system. Unlike every existing app on the market, which treats these pillars as siloed features, TransformFit builds a single cross-domain AI coaching engine that understands how a heavy leg day affects tonight's protein needs, how last night's poor sleep should modify today's training intensity, and how accumulated stress across weeks signals the need for an automatic deload.

The core thesis: **zero-decision fitness**. The user wakes up, receives a readiness score, and their entire day -- workout, meals, recovery protocol -- is already generated, personalized, and adaptive. The AI coach is proactive, not reactive. It does not wait for the user to ask; it anticipates, adjusts, and communicates.

This document is the master technical blueprint covering system architecture, differentiating features, automation pipelines, technology decisions, data models, and the roadmap from MVP to scale.

---

## 2. Full System Architecture

### 2.1 High-Level Architecture Overview

```
+===========================================================================+
|                         TRANSFORMFIT PLATFORM                              |
+===========================================================================+
|                                                                           |
|  +---------------------------+    +----------------------------------+    |
|  |     MOBILE CLIENTS        |    |        WEB CLIENT                |    |
|  |  (Flutter / iOS+Android)  |    |     (Next.js Dashboard)          |    |
|  |                           |    |                                  |    |
|  |  - Workout UI             |    |  - Coach Dashboard               |    |
|  |  - Nutrition Camera       |    |  - Analytics Portal              |    |
|  |  - Form Check (on-device) |    |  - Admin Panel                   |    |
|  |  - Voice Coach            |    |  - B2B Enterprise Portal         |    |
|  |  - Wearable Companion     |    |                                  |    |
|  +------------+--------------+    +----------------+-----------------+    |
|               |                                    |                      |
|               +------------------+-----------------+                      |
|                                  |                                        |
|                          [ API Gateway ]                                  |
|                          [ Kong / AWS ALB ]                               |
|                          [ Rate Limiting, Auth, Routing ]                 |
|                                  |                                        |
+===========================================================================+
|                         BACKEND SERVICES LAYER                            |
+===========================================================================+
|                                  |                                        |
|    +----------+----------+------+-------+----------+-----------+          |
|    |          |          |              |          |           |          |
|    v          v          v              v          v           v          |
| +------+ +--------+ +----------+ +---------+ +--------+ +----------+    |
| | Auth | | User   | | Workout  | | Nutri-  | | Recov- | | Social   |    |
| | Svc  | | Profil | | Engine   | | tion    | | ery    | | & Comm-  |    |
| |      | | Svc    | |          | | Engine  | | Engine | | unity    |    |
| +------+ +--------+ +----------+ +---------+ +--------+ +----------+    |
|    |          |          |              |          |           |          |
|    |     +----+----+-----+------+-------+----+-----+----+-----+         |
|    |     |         |            |             |          |               |
|    v     v         v            v             v          v               |
| +------------+ +----------+ +----------+ +----------+ +----------+      |
| | Gamifica-  | | Notifi-  | | AI Coach | | Computer | | Voice    |      |
| | tion       | | cation   | | Agent    | | Vision   | | Coach    |      |
| | Engine     | | Engine   | | (LLM)    | | Service  | | Service  |      |
| +------------+ +----------+ +----------+ +----------+ +----------+      |
|                                  |                                       |
+===========================================================================+
|                         AI / ML PIPELINE                                  |
+===========================================================================+
|                                  |                                        |
|  +------------------+  +-------------------+  +--------------------+     |
|  | Unified Coaching |  | Training Models   |  | Prediction Models  |     |
|  | Intelligence     |  |                   |  |                    |     |
|  |                  |  | - Periodization   |  | - Injury Risk      |     |
|  | - Cross-pillar   |  | - Volume Mgmt     |  | - Fatigue Detect   |     |
|  |   reasoning      |  | - Deload Detect   |  | - Plateau Predict  |     |
|  | - Context-aware  |  | - Progression     |  | - Readiness Score  |     |
|  |   coaching       |  |   Algorithms      |  | - Body Comp Pred   |     |
|  | - Behavioral     |  +-------------------+  +--------------------+     |
|  |   nudging        |                                                    |
|  +------------------+  +-------------------+  +--------------------+     |
|                        | Food Recognition  |  | Form Analysis      |     |
|                        | (Passio AI +      |  | (MediaPipe Blaze-  |     |
|                        |  Custom Models)   |  |  Pose + Custom)    |     |
|                        +-------------------+  +--------------------+     |
|                                                                          |
+===========================================================================+
|                         DATA LAYER                                        |
+===========================================================================+
|                                                                           |
|  +----------------+  +----------------+  +----------------+               |
|  |  PostgreSQL    |  | TimescaleDB    |  | Redis Cluster  |               |
|  |  (Primary DB)  |  | (Time-Series)  |  | (Cache/Pub-Sub)|               |
|  |                |  |                |  |                |               |
|  | - Users        |  | - HR / HRV     |  | - Session      |               |
|  | - Workouts     |  | - Sleep Data   |  | - Leaderboards |               |
|  | - Nutrition    |  | - Steps        |  | - Rate Limits  |               |
|  | - Plans        |  | - SpO2         |  | - AI Response  |               |
|  | - Social       |  | - Temperature  |  |   Cache        |               |
|  +----------------+  | - GPS/Activity |  +----------------+               |
|                       +----------------+                                  |
|  +----------------+  +----------------+  +----------------+               |
|  | Pinecone       |  | S3 / GCS       |  | ClickHouse     |               |
|  | (Vector DB)    |  | (Object Store) |  | (Analytics)    |               |
|  |                |  |                |  |                |               |
|  | - Exercise     |  | - Food Photos  |  | - Events       |               |
|  |   Embeddings   |  | - Form Videos  |  | - Funnels      |               |
|  | - Coaching     |  | - User Media   |  | - Retention    |               |
|  |   Context      |  | - ML Artifacts |  | - A/B Tests    |               |
|  | - Food DB      |  +----------------+  +----------------+               |
|  |   Embeddings   |                                                       |
|  +----------------+                                                       |
|                                                                           |
+===========================================================================+
|                     INTEGRATION LAYER                                     |
+===========================================================================+
|                                                                           |
|  +----------+ +----------+ +---------+ +--------+ +--------+ +-------+   |
|  | Apple    | | Google   | | Garmin  | | Whoop  | | Oura   | | Polar |   |
|  | HealthKit| | Health   | | Connect | | API    | | API    | | API   |   |
|  +----------+ +----------+ +---------+ +--------+ +--------+ +-------+   |
|                                                                           |
|  +----------+ +----------+ +---------+ +--------+ +--------+ +-------+   |
|  | Cronome- | | Open     | | Stripe  | | RevCat | | Apple  | | FCM / |   |
|  | ter API  | | FoodFact | | Billing | |        | | IAP    | | APNs  |   |
|  +----------+ +----------+ +---------+ +--------+ +--------+ +-------+   |
|                                                                           |
+===========================================================================+
|                     INFRASTRUCTURE                                        |
+===========================================================================+
|                                                                           |
|  AWS (Primary) / GCP (ML)                                                 |
|  Kubernetes (EKS) + Terraform + ArgoCD                                    |
|  Observability: Datadog / Grafana + Prometheus                            |
|  CI/CD: GitHub Actions + Docker                                           |
|  CDN: CloudFront                                                          |
|  Queues: Apache Kafka + SQS                                               |
|                                                                           |
+===========================================================================+
```

### 2.2 Service Communication Architecture

```
+=====================================================================+
|                   SERVICE MESH & COMMUNICATION                       |
+=====================================================================+
|                                                                     |
|  SYNCHRONOUS (Request/Response)                                     |
|  +------------------+         +------------------+                  |
|  | Mobile Client    | <-REST->| API Gateway      |                  |
|  +------------------+         +--------+---------+                  |
|                                        |                            |
|                               +--------+---------+                  |
|                               | Service Mesh     |                  |
|                               | (Istio/Linkerd)  |                  |
|                               +--------+---------+                  |
|                                        |                            |
|                         +--------------+--------------+             |
|                         |              |              |             |
|                    [ gRPC ]       [ gRPC ]       [ gRPC ]          |
|                    Workout        Nutrition       Recovery          |
|                    Engine         Engine          Engine            |
|                                                                     |
|  ASYNCHRONOUS (Event-Driven)                                        |
|  +------------------+                                               |
|  | Apache Kafka     |                                               |
|  | Event Bus        |                                               |
|  |                  |                                               |
|  | Topics:          |                                               |
|  |  workout.completed -----> [Nutrition Adjuster]                   |
|  |  sleep.imported --------> [Readiness Calculator]                 |
|  |  hrv.updated -----------> [Workout Modifier]                     |
|  |  food.logged -----------> [Macro Recalculator]                   |
|  |  fatigue.detected ------> [Deload Scheduler]                    |
|  |  form.analyzed ---------> [Injury Risk Scorer]                   |
|  |  milestone.achieved ----> [Gamification Engine]                  |
|  |  user.inactive ---------> [Notification Engine]                  |
|  +------------------+                                               |
|                                                                     |
|  REAL-TIME (WebSocket/SSE)                                          |
|  +------------------+         +------------------+                  |
|  | Mobile Client    | <-WS--> | Real-Time Gateway|                  |
|  +------------------+         | (Socket.io)      |                  |
|                               |                  |                  |
|                               | Channels:        |                  |
|                               |  - live_workout  |                  |
|                               |  - form_feedback |                  |
|                               |  - coach_message |                  |
|                               |  - leaderboard   |                  |
|                               +------------------+                  |
+=====================================================================+
```

### 2.3 Core Service Breakdown

| Service | Responsibility | Scale Profile |
|---------|---------------|---------------|
| **Auth Service** | JWT issuance, OAuth2 (Apple/Google), session management | Low compute, high request volume |
| **User Profile Service** | Demographics, goals, injuries, equipment, preferences, GLP-1 status | CRUD-heavy, moderate volume |
| **Workout Engine** | Program generation, periodization, exercise selection, progression logic | High compute (AI inference), moderate volume |
| **Nutrition Engine** | Macro targets, meal planning, food logging, photo recognition dispatch | Moderate compute, high volume |
| **Recovery Engine** | Readiness scoring, HRV analysis, sleep scoring, fatigue accumulation | High compute (time-series), event-driven |
| **AI Coach Agent** | LLM-powered coaching conversations, proactive messaging, weekly reports | High compute (LLM calls), variable volume |
| **Computer Vision Service** | Form analysis (pose estimation), food photo recognition | GPU-intensive, on-demand |
| **Voice Coach Service** | Speech-to-text (Whisper), text-to-speech (ElevenLabs), voice command parsing | GPU-intensive, on-demand |
| **Social & Community** | Friends, groups, challenges, activity feed, messaging | High read volume, moderate write |
| **Gamification Engine** | XP, levels, achievements, streaks, leaderboards | High read (leaderboards), event-driven writes |
| **Notification Engine** | Push (FCM/APNs), in-app, email, SMS; intelligent timing and throttling | High volume, scheduled + event-driven |

---

## 3. The "World's Best" Differentiators

### 3.1 Unified 4-Pillar AI Coaching Intelligence

**The Problem:** Every fitness app on the market treats training, nutrition, recovery, and mental performance as separate modules with separate logic. Fitbod optimizes workouts. MyFitnessPal tracks food. Whoop scores recovery. Headspace guides meditation. No app synthesizes all four into a single reasoning engine.

**The Solution: Cross-Domain Intelligence Engine (CDIE)**

```
+===================================================================+
|              CROSS-DOMAIN INTELLIGENCE ENGINE (CDIE)               |
+===================================================================+
|                                                                   |
|  INPUT STREAMS (Real-Time + Historical)                           |
|  +------------+ +------------+ +------------+ +------------+     |
|  | Training   | | Nutrition  | | Recovery   | | Mental     |     |
|  | Stream     | | Stream     | | Stream     | | Stream     |     |
|  |            | |            | |            | |            |     |
|  | - Volume   | | - Calories | | - HRV      | | - Stress   |     |
|  | - Intensty | | - Protein  | | - Sleep    | | - Mood     |     |
|  | - RPE      | | - Timing   | | - Resting  | | - Focus    |     |
|  | - Freq     | | - Hydratn  | |   HR       | | - Anxiety  |     |
|  | - History  | | - Micros   | | - SpO2     | | - Journal  |     |
|  +-----+------+ +-----+------+ +-----+------+ +-----+------+     |
|        |              |              |              |             |
|        +-------+------+------+-------+------+-------+             |
|                |             |              |                     |
|                v             v              v                     |
|  +----------------------------------------------------------+   |
|  |           UNIFIED STATE VECTOR (per user)                  |   |
|  |                                                            |   |
|  |  { training_load: 0.78, nutrition_adherence: 0.85,        |   |
|  |    recovery_score: 62, stress_level: 0.45,                |   |
|  |    fatigue_accumulation: [0.3, 0.4, 0.5, 0.6, 0.7],     |   |
|  |    sleep_debt_hours: 3.2, protein_deficit_g: 15,          |   |
|  |    muscle_group_fatigue: { legs: 0.9, chest: 0.3 },      |   |
|  |    injury_status: [{ area: "left_knee", severity: 0.4 }], |   |
|  |    glp1_status: { active: true, week: 8, dose: "1.0mg" } |   |
|  |  }                                                         |   |
|  +---------------------------+--------------------------------+   |
|                              |                                    |
|                              v                                    |
|  +----------------------------------------------------------+   |
|  |              REASONING ENGINE                              |   |
|  |                                                            |   |
|  |  Layer 1: Rule-Based Logic (deterministic guards)          |   |
|  |    - IF recovery_score < 50 AND fatigue_trend = rising     |   |
|  |      THEN block_high_intensity = true                      |   |
|  |    - IF glp1_active AND protein_intake < threshold         |   |
|  |      THEN priority_alert("muscle_preservation")            |   |
|  |                                                            |   |
|  |  Layer 2: ML Prediction Models                             |   |
|  |    - Fatigue accumulation forecaster (7-day horizon)       |   |
|  |    - Injury risk probability (78% accuracy, 3-week ahead)  |   |
|  |    - Performance plateau detector                          |   |
|  |    - Optimal training stimulus estimator                   |   |
|  |                                                            |   |
|  |  Layer 3: LLM Coaching Agent (Claude/GPT-4)                |   |
|  |    - Natural language explanation of decisions              |   |
|  |    - Motivational context and behavioral nudging           |   |
|  |    - Complex multi-factor reasoning                        |   |
|  |    - Personalized communication style                      |   |
|  +---------------------------+--------------------------------+   |
|                              |                                    |
|                              v                                    |
|  +----------------------------------------------------------+   |
|  |              OUTPUT ACTIONS                                |   |
|  |                                                            |   |
|  |  - Adjusted workout for today                              |   |
|  |  - Updated nutrition targets (macro rebalancing)           |   |
|  |  - Recovery protocol recommendation                        |   |
|  |  - Proactive coach message                                 |   |
|  |  - Deload week scheduling                                  |   |
|  |  - Mindfulness session suggestion                          |   |
|  +----------------------------------------------------------+   |
+===================================================================+
```

**Why no one does this:** Building a unified model requires time-series data from all four domains simultaneously, which means the app must be the single source of truth. Most apps are point solutions. TransformFit's moat is the compound data flywheel -- the more a user tracks across all four pillars, the smarter the AI becomes, and the harder it is to leave.

### 3.2 Adaptive Nutrition That Responds to Training

**Current state of the art:** MacroFactor and Carbon Diet Coach adjust macros every 7-10 days based on weight trends. This is reactive and slow.

**TransformFit approach: Same-day, intra-day macro adjustment.**

```
TRIGGER: workout.completed event
  |
  v
[Workout Analysis]
  - Exercise type: Compound lower body (squat, deadlift, lunges)
  - Total volume: 24,500 kg (high)
  - Estimated glycogen depletion: ~60%
  - Muscle damage score: 0.8/1.0 (high)
  |
  v
[Nutrition Adjustment Engine]
  - Base targets: 2,400 cal / 180P / 250C / 80F
  - Post-workout adjustment:
    + Protein: +25g (muscle repair demand)
    + Carbs: +40g (glycogen replenishment)
    + Total cal adjustment: +285 cal
  - Meal timing optimization:
    - Within 2hr post-workout: High-GI carbs + 40g protein
    - Dinner: Complex carbs + protein-rich
  - Updated remaining targets pushed to app in real-time
  |
  v
[Proactive Message]
  "Great leg session -- 24,500 kg total volume. I've bumped your
   protein to 205g and carbs to 290g for today to maximize recovery.
   Here's a high-protein dinner idea that fits your remaining macros."
```

**Key algorithm: Training-Nutrition Coupling Model**

```
daily_protein_target = base_protein + (muscle_damage_score * protein_multiplier)
daily_carb_target = base_carbs + (glycogen_depletion * carb_multiplier)
daily_fat_target = base_fat  -- (fat stays relatively stable)
daily_cal_target = (daily_protein * 4) + (daily_carb * 4) + (daily_fat * 9)

WHERE:
  protein_multiplier = f(training_age, body_weight, goal, glp1_status)
  carb_multiplier = f(activity_level, insulin_sensitivity, goal)
  muscle_damage_score = f(exercise_selection, volume, intensity, novelty)
  glycogen_depletion = f(exercise_duration, intensity, muscle_groups)
```

### 3.3 Recovery-Aware Programming

**How it works:**

Every morning at the user's configured wake time, the Recovery Engine runs:

```
MORNING READINESS PIPELINE
==========================

1. COLLECT overnight data (via HealthKit/wearable sync)
   - HRV (rMSSD) from overnight measurement
   - Sleep duration + sleep stage breakdown
   - Resting heart rate
   - Respiratory rate
   - Skin temperature delta
   - SpO2

2. CALCULATE Readiness Score (0-100)
   readiness = weighted_sum(
     hrv_vs_baseline:      0.30  -- HRV relative to 3-month rolling baseline
     sleep_quality:         0.25  -- (deep_sleep + rem_sleep) / total_sleep
     sleep_duration:        0.15  -- vs personalized optimal (learned over time)
     resting_hr_vs_base:   0.15  -- lower is better, relative to baseline
     subjective_wellbeing:  0.10  -- morning check-in (optional, 1-tap)
     accumulated_fatigue:   0.05  -- trailing 7-day training load trend
   )

3. CLASSIFY readiness zone
   90-100: PEAK       -- Hit it hard. PR attempt day.
   70-89:  GOOD       -- Train as programmed.
   50-69:  MODERATE   -- Reduce intensity by 10-15%, maintain volume.
   30-49:  LOW        -- Swap to recovery workout (mobility, light cardio).
   0-29:   REST       -- Full rest day. Focus on sleep and nutrition.

4. MODIFY today's workout
   IF readiness < 70:
     - Reduce working set RPE targets by (70 - readiness) / 20
     - Swap explosive movements for controlled tempo work
     - Reduce total volume by readiness_deficit_percentage
     - Add extended warm-up and cool-down
     - Insert mobility work for highest-fatigue muscle groups
   IF readiness >= 90:
     - Enable PR attempt mode
     - Add optional top set or AMRAP finisher
     - Suggest caffeine timing for peak performance

5. NOTIFY user
   Push notification at wake_time + 5 minutes:
   "[Readiness: 58/100] Your HRV is 15% below baseline and you got
    5.2hrs of sleep. I've adjusted today's workout -- swapping heavy
    squats for tempo goblet squats and adding 15 min mobility."
```

### 3.4 Deload Intelligence

**The Problem:** Most apps use a fixed 4-weeks-on/1-week-deload cycle. This is suboptimal because fatigue accumulates differently for every person.

**TransformFit: Adaptive Deload Detection using the Fitness-Fatigue Model**

The Fitness-Fatigue model (Banister, 1975) states: `Performance(t) = Fitness(t) - Fatigue(t)`. TransformFit implements a modernized, personalized version:

```
DELOAD DETECTION ALGORITHM
===========================

For each user, maintain rolling signals:

1. PERFORMANCE SIGNALS (objective)
   - Estimated 1RM trend (per lift): declining over 2+ weeks?
   - Volume capacity: unable to complete prescribed sets/reps?
   - Rep quality: form analysis showing degradation?

2. RECOVERY SIGNALS (biometric)
   - HRV trend: declining 7-day rolling average vs baseline?
   - Resting HR trend: rising 7-day rolling average?
   - Sleep quality trend: declining?

3. SUBJECTIVE SIGNALS
   - RPE drift: same weight feeling harder (RPE rising for same load)?
   - Session rating: declining session satisfaction scores?
   - Mood/motivation: check-in data trending negative?

4. FATIGUE ACCUMULATION INDEX (FAI)
   FAI = (
     performance_decline_score * 0.35 +
     recovery_decline_score * 0.35 +
     subjective_decline_score * 0.30
   )

   Scale: 0.0 (fresh) to 1.0 (overtrained)

5. DELOAD TRIGGER
   IF FAI > 0.70 for 3+ consecutive days:
     TRIGGER automatic deload week
     - Volume: reduce to 50-60% of normal
     - Intensity: reduce to 70-75% of recent working weights
     - Frequency: maintain or reduce by 1 session
     - Focus: technique work, mobility, active recovery
     - Duration: 5-7 days (adaptive based on recovery signals)

   IF FAI returns below 0.40:
     END deload, resume normal programming
     GENERATE next mesocycle with adjusted baseline

6. NOTIFICATION
   "I've detected rising fatigue over the past 10 days -- your HRV is
    trending down 12%, your squat RPE has risen from 7 to 8.5 at the
    same weight, and your sleep quality dropped. Starting a recovery
    week. Trust the process -- you'll come back stronger."
```

### 3.5 GLP-1 / Semaglutide Integration

**Market context:** As of 2026, 6%+ of US adults are on GLP-1 medications (Ozempic, Wegovy, Mounjaro). Studies show 26-40% of weight lost on GLP-1s can be lean tissue. No mainstream fitness app addresses this population's specific needs.

**TransformFit GLP-1 Module:**

```
GLP-1 USER PROFILE EXTENSION
==============================

glp1_config:
  medication: "semaglutide" | "tirzepatide" | "other"
  brand: "Ozempic" | "Wegovy" | "Mounjaro" | "Zepbound"
  current_dose: "1.0mg"
  dose_schedule: "weekly"
  injection_day: "Monday"
  start_date: "2025-11-15"
  titration_phase: false  -- still increasing dose?

SPECIAL PROGRAMMING RULES FOR GLP-1 USERS:
-------------------------------------------

1. PROTEIN PRIORITY
   - Minimum: 1.2g/kg body weight (vs 0.8g/kg standard)
   - Target: 1.6g/kg body weight
   - Absolute floor: 80g/day regardless of caloric intake
   - Protein-first meal planning (protein source selected first)
   - Protein timing: distribute across 4+ eating occasions

2. STRENGTH TRAINING EMPHASIS
   - Minimum 3x/week resistance training (non-negotiable)
   - Compound movement priority (squat, deadlift, bench, row)
   - Progressive overload tracking with muscle preservation lens
   - Volume: maintain even in caloric deficit

3. BODY COMPOSITION TRACKING
   - Weight tracked but DE-EMPHASIZED in UI
   - Primary metrics: estimated lean mass, strength trends
   - Waist/hip measurements prompted bi-weekly
   - Progress photos with AI body composition estimation
   - Alert if strength declining faster than expected

4. APPETITE MANAGEMENT
   - Smaller, more frequent meal suggestions
   - Nutrient-dense food prioritization
   - Hydration reminders (GLP-1 increases dehydration risk)
   - Side effect tracking (nausea, appetite changes by dose)

5. INJECTION TRACKING
   - Dose reminders with injection site rotation map
   - Side effect logging with pattern recognition
   - Correlation analysis: side effects vs training performance

6. REPORTING
   - Monthly GLP-1 progress report (shareable with physician)
   - Lean mass preservation score
   - Medication efficacy tracking
```

### 3.6 Injury-Aware Programming

```
INJURY MANAGEMENT SYSTEM
=========================

1. INJURY REGISTRATION
   User reports injury via:
   - Body map tap (visual skeleton diagram)
   - Voice description -> NLP classification
   - Wearable anomaly detection (unusual movement patterns)

   Injury record:
   {
     body_part: "left_knee",
     type: "patellofemoral_pain",
     severity: 3/5,
     date_onset: "2026-02-15",
     affected_movements: ["squat", "lunge", "leg_press", "running"],
     cleared_movements: ["upper_body", "swimming", "cycling_low_resistance"],
     rehab_exercises: ["terminal_knee_extension", "wall_sit", "step_down"],
     status: "active"  -- active | recovering | cleared
   }

2. EXERCISE SUBSTITUTION ENGINE
   FOR each programmed exercise:
     IF exercise.movement_pattern IN injury.affected_movements:
       FIND substitution WHERE:
         - Same target muscle groups (primary + secondary)
         - Movement pattern does not load injured area
         - Available with user's equipment
         - Ranked by effectiveness similarity score
       EXAMPLE:
         Barbell Back Squat (injured knee)
         -> Belt Squat (reduced knee stress)
         -> Leg Press (partial ROM, pain-free range)
         -> Hip Thrust + Leg Curl (isolate glutes/hams)

3. GRADUAL RETURN-TO-TRAINING PROTOCOL
   Week 1: Cleared movements only, 50% volume
   Week 2: Introduce modified versions, 60% volume
   Week 3: Partial ROM of previously affected movements, 70%
   Week 4: Full ROM if pain-free, 80% volume
   Week 5: Normal programming with monitoring

   At each stage: pain check-in after each session
   IF pain_reported > 2/10: step back one week

4. FORM MONITORING (post-injury)
   - Camera form check enabled by default for returning exercises
   - Asymmetry detection (favoring one side)
   - Alert if compensatory movement patterns detected
```

### 3.7 Real-Time Form Checking via Camera

**Technology: On-Device Pose Estimation Pipeline**

```
FORM CHECK ARCHITECTURE
========================

ON-DEVICE PIPELINE (no cloud latency):

  Camera Feed (30 FPS)
       |
       v
  [MediaPipe BlazePose / YOLO11 Pose]
  - 33 body landmarks detected per frame
  - Runs on-device via TensorFlow Lite / CoreML
  - <15ms inference per frame on modern phones
       |
       v
  [Joint Angle Calculator]
  - Compute angles: knee, hip, elbow, shoulder, spine
  - Compute distances: bar path, stance width
  - Compute velocities: concentric/eccentric speed
       |
       v
  [Exercise Classifier]
  - Identify which exercise is being performed
  - Determine rep phase (eccentric, pause, concentric)
  - Count repetitions automatically
       |
       v
  [Form Analyzer (per exercise)]
  - Compare angles/positions to ideal form model
  - Exercise-specific rules:
    SQUAT:
      - Knee tracking over toes (frontal plane)
      - Depth: hip crease below knee (sagittal plane)
      - Back angle: neutral spine maintenance
      - Knee cave detection (valgus)
      - Weight distribution (heel vs toe)
    DEADLIFT:
      - Bar path (vertical line over mid-foot)
      - Hip hinge pattern
      - Lumbar flexion detection
      - Lockout position
    BENCH PRESS:
      - Bar path (J-curve)
      - Elbow angle at bottom
      - Scapular retraction maintenance
       |
       v
  [Real-Time Feedback Engine]
  - Visual overlay: skeleton + angle annotations
  - Audio cues: "Push your knees out" / "Drive through your heels"
  - Haptic feedback: vibration on form deviation
  - Rep quality score: 0-100 per rep
       |
       v
  [Post-Set Summary]
  - Average form score for the set
  - Specific issues identified
  - Side-by-side comparison with ideal form
  - Trend: "Your squat depth has improved 15% this month"

SUPPORTED EXERCISES (MVP):
  Tier 1 (launch): Squat, Deadlift, Bench Press, Overhead Press, Row
  Tier 2 (v1): Lunge, Pull-up, Push-up, Plank, Curl, Tricep Extension
  Tier 3 (v2): Olympic lifts, Kettlebell movements, Bodyweight flows
```

---

## 4. Automation Architecture

### 4.1 Zero-Decision Morning Flow

```
ZERO-DECISION MORNING
=======================

[05:00 - Background Sync]
  Wearable data syncs overnight via HealthKit/Health Connect
  -> Sleep stages, HRV, RHR, SpO2, temperature imported
  -> Recovery Engine calculates readiness score

[User wakes up -- detected via wearable or alarm time]
  |
  v
[MORNING BRIEFING PUSH NOTIFICATION]
  "Good morning, Mike. Readiness: 74/100."
  |
  v
[User opens app -> Dashboard]

  +-------------------------------------------------------+
  |  TODAY'S PLAN                    Readiness: 74 [====] |
  +-------------------------------------------------------+
  |                                                       |
  |  WORKOUT: Upper Body Push (adjusted)          9:00 AM |
  |  - Bench Press: 4x6 @ 185 lb (RPE 7)                |
  |  - OHP: 3x8 @ 115 lb                                |
  |  - Incline DB Press: 3x10 @ 60 lb                   |
  |  - Lateral Raises: 3x15 @ 20 lb                     |
  |  - Tricep Pushdown: 3x12                             |
  |  Est. duration: 52 min                               |
  |                                                       |
  |  NUTRITION TARGETS                                    |
  |  Calories: 2,400 | P: 180g | C: 250g | F: 80g      |
  |                                                       |
  |  SUGGESTED MEALS:                                     |
  |  Breakfast: Greek yogurt bowl w/ berries (42P/35C/8F)|
  |  Lunch: Chicken rice bowl (45P/60C/15F)              |
  |  Post-workout: Protein shake + banana (35P/40C/3F)   |
  |  Dinner: Salmon, sweet potato, broccoli (48P/55C/22F)|
  |  Snack: Cottage cheese + almonds (20P/10C/18F)       |
  |                                                       |
  |  RECOVERY                                             |
  |  - 10 min morning mobility routine (auto-queued)     |
  |  - Target 7.5+ hrs sleep tonight                     |
  |  - Hydration target: 3.2L                            |
  |                                                       |
  |  MINDFULNESS                                          |
  |  - 5 min pre-workout focus session available         |
  +-------------------------------------------------------+

ZERO DECISIONS REQUIRED.
The user just follows the plan.
Everything was generated based on:
  - Their training program and periodization phase
  - Last night's sleep and recovery data
  - Yesterday's nutrition adherence
  - Their schedule and preferences
  - Current injury status
  - GLP-1 medication status (if applicable)
```

### 4.2 Automatic Food Logging Pipeline

```
PHOTO-TO-MACROS PIPELINE
==========================

User takes photo of meal
       |
       v
[On-Device Pre-Processing]
  - Image enhancement (lighting, contrast)
  - Crop to food area
  - Quality check (blurry? too dark?)
       |
       v
[Food Recognition (Passio AI SDK - on-device)]
  - Real-time food detection as camera hovers
  - Multiple food items identified per frame
  - Confidence scores per item
  - 94% accuracy (vs 60-70% manual logging)
       |
       v
[Portion Estimation]
  - Depth estimation from single image
  - Reference object detection (plate, utensil, hand)
  - Volume estimation per food item
  - Cross-reference with typical serving sizes
       |
       v
[Nutritional Lookup]
  - Match to food database (2.5M+ items)
  - Pull macro + micro nutrient data
  - Account for preparation method (fried vs grilled)
       |
       v
[User Confirmation Screen]
  +------------------------------------------+
  |  DETECTED MEAL                           |
  |                                          |
  |  [Photo]                                 |
  |                                          |
  |  Grilled Chicken Breast    1.5 servings  |
  |  Brown Rice                1 cup         |
  |  Steamed Broccoli          1.5 cups      |
  |  Olive Oil (estimated)     1 tbsp        |
  |                                          |
  |  TOTAL: 520 cal | 48P | 52C | 14F       |
  |                                          |
  |  [Looks right]  [Edit items]  [Retake]   |
  +------------------------------------------+
       |
       v
[Macro Recalculation]
  - Update daily totals
  - Recalculate remaining targets
  - Adjust dinner suggestion if needed
  - Push updated targets to dashboard
       |
       v
[Coach Message (if notable)]
  "Nice protein-rich lunch. You're at 68% of your protein target
   with dinner still to go -- you're on track."
```

### 4.3 Auto-Detected Workout Logging

```
WEARABLE AUTO-DETECTION PIPELINE
==================================

[Continuous background monitoring via HealthKit/Health Connect]
       |
       v
[Activity Classification]
  - Apple Watch / Garmin / Whoop detects activity type
  - Heart rate zone analysis
  - Accelerometer pattern matching
  - GPS for outdoor activities
       |
       v
[Activity Type Routing]

  IF type = "strength_training":
    - Prompt user to open app for detailed logging
    - Or: auto-log from Apple Watch workout data
    - Match detected exercises with programmed workout
    - Fill in sets/reps from watch sensors where possible
    - User confirms/adjusts

  IF type = "cardio" (run, cycle, swim, etc.):
    - Auto-import: duration, distance, pace, HR zones
    - Calculate caloric expenditure
    - Adjust daily nutrition targets
    - Log as cardio session

  IF type = "yoga" | "stretching" | "mobility":
    - Auto-log as recovery activity
    - Credit toward weekly recovery minutes
    - Adjust readiness model inputs

  IF type = "walking":
    - Auto-accumulate daily step count
    - Factor into TDEE calculation
    - No explicit logging needed
```

### 4.4 Proactive AI Coach Messaging

```
PROACTIVE COACHING ENGINE
===========================

The AI coach does not wait for the user to ask.
It monitors signals and initiates contact when valuable.

TRIGGER RULES:
--------------

1. RECOVERY ALERT
   WHEN: HRV drops >15% below baseline overnight
   ACTION: "Your HRV was 42ms last night (baseline: 55ms). I've
           swapped today's heavy deadlift session for a recovery-
           focused workout. Prioritize sleep tonight."

2. NUTRITION GAP
   WHEN: By 4:00 PM, protein intake < 40% of daily target
   ACTION: "You're at 65g protein so far today (target: 180g).
           Here are 3 high-protein dinner ideas that'll close the gap."

3. CONSISTENCY PRAISE
   WHEN: User completes 3 consecutive weeks of 4+ workouts
   ACTION: "12 sessions in 3 weeks -- that's elite consistency.
           Your squat 1RM estimate has gone up 8% this month."

4. PLATEAU DETECTION
   WHEN: Primary lift estimated 1RM flat for 3+ weeks
   ACTION: "Your bench press has been around 225 for three weeks.
           I'm introducing a variation block -- close-grip and pause
           reps for the next 3 weeks to break through."

5. DELOAD RECOMMENDATION
   WHEN: Fatigue Accumulation Index > 0.70 for 3+ days
   ACTION: "Your body needs a recovery week. I've programmed a
           deload -- lighter weights, focus on technique. You'll
           come back stronger."

6. GOAL MILESTONE
   WHEN: User within 5% of a stated goal
   ACTION: "You're 3 lbs from your goal weight of 185. At your
           current rate, you'll hit it by March 15. Let's stay
           dialed in."

7. GLP-1 DOSE DAY
   WHEN: It's the user's injection day
   ACTION: "Injection day reminder. Don't forget: high-protein
           meals today, stay hydrated. Track any side effects
           in the app."

8. INACTIVITY
   WHEN: No workout logged for 3+ days (outside scheduled rest)
   ACTION: "Hey Mike -- it's been 3 days. Everything okay? Even
           a 20-minute session keeps momentum going. Here's a
           quick bodyweight option."

DELIVERY:
  - Intelligent timing (not during sleep, work hours, or workouts)
  - Frequency cap: max 3 proactive messages per day
  - User can adjust coaching intensity (more/less frequent)
  - Channels: push notification + in-app message
```

### 4.5 Weekly Auto-Reports

```
WEEKLY PERFORMANCE REPORT (Auto-generated every Sunday)
=========================================================

+----------------------------------------------------------+
|  WEEK IN REVIEW: Feb 24 - Mar 2, 2026                   |
+----------------------------------------------------------+
|                                                          |
|  TRAINING                                                |
|  Sessions: 5/5 planned [=====]                           |
|  Total volume: 127,450 kg (+3.2% vs last week)          |
|  Estimated 1RM changes:                                  |
|    Squat: 315 -> 320 (+5 lb)                            |
|    Bench: 225 -> 225 (stable)                           |
|    Deadlift: 405 -> 410 (+5 lb)                         |
|  Form scores: avg 82/100 (squat depth improving)        |
|                                                          |
|  NUTRITION                                               |
|  Avg calories: 2,380/2,400 target (99% adherence)      |
|  Avg protein: 172g/180g target (96% adherence)          |
|  Best day: Thursday (perfect macro split)                |
|  Opportunity: Protein consistently low at breakfast      |
|                                                          |
|  RECOVERY                                                |
|  Avg sleep: 7.1 hrs (target: 7.5)                       |
|  Avg HRV: 52ms (trending up from 48ms last month)      |
|  Avg readiness: 71/100                                   |
|  Recovery sessions: 2 (mobility + yoga)                  |
|                                                          |
|  BODY COMPOSITION                                        |
|  Weight: 188.2 -> 187.6 lb (-0.6 lb)                   |
|  Trend: On pace for goal (185 lb by Mar 15)             |
|                                                          |
|  AI COACH NOTES                                          |
|  "Strong week. Volume is progressing well and your HRV   |
|   trend is positive -- a sign your body is adapting.     |
|   Focus areas for next week: (1) add a protein source    |
|   to breakfast, (2) aim for 7.5 hrs sleep on workout     |
|   nights, (3) bench press -- I'm adding pause reps to    |
|   break through the plateau."                            |
|                                                          |
|  NEXT WEEK PREVIEW                                       |
|  Mon: Lower Body (Squat focus)                          |
|  Tue: Upper Body Push                                   |
|  Wed: Active Recovery + Mobility                        |
|  Thu: Lower Body (Deadlift focus)                       |
|  Fri: Upper Body Pull                                   |
|  Sat: Optional Cardio / Sport                           |
|  Sun: Rest                                               |
+----------------------------------------------------------+
```

### 4.6 Monthly Periodization Auto-Adjustment

```
MONTHLY BLOCK REVIEW ENGINE
==============================

At the end of each mesocycle (typically 4-6 weeks):

1. ANALYZE current block performance
   - Volume progression rate: were sets/reps increasing appropriately?
   - Strength gains: estimated 1RM changes per lift
   - Adherence rate: sessions completed / sessions planned
   - Recovery metrics: was the user over-reaching or under-reaching?
   - Injury events: any new injuries or flare-ups?

2. DETERMINE next block parameters
   INPUTS: current_block_results + user_goals + recovery_capacity

   IF strength_gains > expected AND recovery = good:
     -> INTENSIFICATION BLOCK
     - Increase intensity (heavier weights, lower reps)
     - Slightly reduce volume
     - Introduce competition-style lifts

   IF strength_gains = expected AND recovery = moderate:
     -> ACCUMULATION BLOCK (continue progression)
     - Moderate intensity increase
     - Maintain or slightly increase volume
     - Introduce exercise variations

   IF strength_gains < expected OR recovery = poor:
     -> REALIZATION/RECOVERY BLOCK
     - Reduce volume significantly
     - Test new maxes (if recovered)
     - Address weak points with accessory focus

   IF user_goal = "hypertrophy":
     -> Bias toward volume accumulation blocks
     - Higher rep ranges (8-15)
     - More exercise variety
     - Shorter rest periods

   IF user_goal = "fat_loss" AND glp1_active:
     -> MUSCLE PRESERVATION BLOCK
     - Maintain intensity (heavy compounds)
     - Moderate volume (enough stimulus, manageable recovery)
     - Prioritize compound movements
     - Extra protein-focused nutrition targets

3. GENERATE next mesocycle
   - Select exercises per session
   - Set starting weights (based on current estimated maxes)
   - Define progression scheme (linear, undulating, step-loading)
   - Set RPE targets per week
   - Pre-program deload trigger sensitivity

4. PRESENT to user
   "Your 4-week Accumulation block is complete. Summary:
    - Squat 1RM: 305 -> 320 (+5%)
    - Total volume increased 12% across the block
    - Zero missed sessions

    Next block: Intensification (4 weeks)
    - Focus: heavy doubles and triples
    - Goal: push squat toward 335
    - Deload scheduled for Week 5 if fatigue signals appear

    [View Full Program] [Adjust Preferences] [Ask Coach]"
```

---

## 5. Technology Stack

### 5.1 Technology Decision Matrix

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Mobile** | **Flutter (Dart)** | Superior animation performance (60/120 FPS via Impeller engine), single codebase for iOS+Android, faster MVP delivery (12-16 weeks), strong on-device ML support via TFLite plugin, 46% cross-platform market share |
| **Web Dashboard** | **Next.js 14 (React)** | Coach dashboard, admin panel, B2B portal; SSR for SEO; shared component library |
| **API Gateway** | **Kong Gateway** | Rate limiting, JWT validation, request routing, analytics; cloud-native, Kubernetes-ready |
| **Backend Services** | **Go (Golang)** | High concurrency for real-time processing, low memory footprint, excellent for microservices, strong gRPC support, fast cold starts |
| **AI Coach Service** | **Python (FastAPI)** | ML ecosystem (PyTorch, scikit-learn, pandas), LLM integration (LangChain/LangGraph), Pydantic models |
| **Primary Database** | **PostgreSQL 16** | Proven reliability, JSONB for flexible schemas, row-level security, excellent tooling |
| **Time-Series DB** | **TimescaleDB** | PostgreSQL extension (no new infra), hypertables for biometric streams, automatic partitioning, compression, continuous aggregates |
| **Cache / Pub-Sub** | **Redis 7 (Cluster)** | Session storage, leaderboard sorted sets, rate limiting, LLM response caching, pub-sub for real-time |
| **Vector Database** | **Pinecone** | Exercise and food embeddings for semantic search, coaching context retrieval (RAG), managed service |
| **Object Storage** | **AWS S3** | Food photos, form check videos, ML model artifacts, user media |
| **Analytics** | **ClickHouse** | OLAP for product analytics, funnel analysis, retention cohorts; handles billions of events |
| **Event Streaming** | **Apache Kafka** | Cross-service event bus (workout.completed, sleep.imported, etc.), exactly-once semantics, replay capability |
| **Search** | **Meilisearch** | Exercise database search, food search, fast typo-tolerant full-text search |
| **LLM Provider** | **Claude (Anthropic)** | Primary coaching LLM; superior at nuanced health advice, long context for user history; fallback: GPT-4 |
| **On-Device ML** | **TensorFlow Lite + CoreML** | Pose estimation, food recognition, rep counting -- all on-device for zero-latency UX |
| **Computer Vision** | **MediaPipe BlazePose + YOLO11** | 33-landmark body tracking, real-time on mobile, exercise classification |
| **Food Recognition** | **Passio AI SDK** | On-device food detection, 2.5M+ food database, barcode scanning, portion estimation; proven SDK with Flutter support |
| **Voice - STT** | **OpenAI Whisper** | Best-in-class speech recognition, multilingual, runs on-device (distilled) or cloud |
| **Voice - TTS** | **ElevenLabs** | Natural-sounding voice for AI coach, customizable voice persona, low latency streaming |
| **Infrastructure** | **AWS (EKS)** | Kubernetes orchestration, RDS for PostgreSQL, ElastiCache for Redis, S3, CloudFront CDN |
| **ML Training** | **GCP (Vertex AI)** | Training pipeline for custom models, GPU instances, model registry |
| **IaC** | **Terraform + Pulumi** | Infrastructure-as-code, multi-cloud support |
| **CI/CD** | **GitHub Actions** | Automated testing, deployment, Flutter builds (Fastlane for app stores) |
| **Observability** | **Datadog** | APM, logs, metrics, real-user monitoring, custom dashboards |
| **Payments** | **RevenueCat + Stripe** | Subscription management, App Store / Play Store IAP, analytics |

### 5.2 Why Flutter Over React Native

The decision to use Flutter is based on specific fitness app requirements:

1. **Performance**: Form checking requires rendering a camera feed + pose overlay at 30+ FPS. Flutter's Impeller engine delivers consistent 60/120 FPS. React Native's JS bridge can drop to 45-50 FPS under heavy rendering.

2. **On-device ML**: Flutter's TFLite plugin provides direct access to GPU delegates. React Native's bridge adds latency to every ML inference call.

3. **Animations**: Workout timers, progress charts, and form overlays demand smooth animations. Flutter's widget tree renders natively without a bridge.

4. **Speed to market**: Flutter MVPs launch in 12-16 weeks vs 20-28 weeks for dual native. We need speed.

5. **Dart's type safety**: Strongly typed language catches errors at compile time -- critical for health-related data handling.

### 5.3 Why Go for Backend Services

1. **Concurrency**: goroutines handle thousands of simultaneous connections for real-time features (WebSocket coaching, live leaderboards) with minimal memory overhead.

2. **Performance**: Compiled language with predictable latency, no garbage collection pauses like Java/Kotlin.

3. **Microservice fit**: Fast startup time, small binaries, excellent for containerized microservices on Kubernetes.

4. **gRPC native**: First-class protobuf and gRPC support for efficient inter-service communication.

5. **Simplicity**: Straightforward language means faster onboarding and fewer architectural footguns.

### 5.4 Infrastructure Architecture

```
AWS INFRASTRUCTURE
===================

+---------------------------------------------------------------+
|  CloudFront CDN                                                |
|  (Static assets, API caching, global edge)                    |
+-------------------------------+-------------------------------+
                                |
                    +-----------+-----------+
                    |   Application Load    |
                    |   Balancer (ALB)      |
                    +-----------+-----------+
                                |
+-------------------------------+-------------------------------+
|  Amazon EKS (Kubernetes Cluster)                              |
|                                                               |
|  Namespace: transformfit-prod                                 |
|  +------------------+ +------------------+ +----------------+ |
|  | Workout Svc (Go) | | Nutrition Svc    | | Recovery Svc   | |
|  | 3 replicas       | | (Go) 3 replicas  | | (Go) 2 replica | |
|  +------------------+ +------------------+ +----------------+ |
|  +------------------+ +------------------+ +----------------+ |
|  | AI Coach (Python)| | CV Svc (Python)  | | Voice Svc      | |
|  | 2 replicas + GPU | | GPU nodes (spot) | | (Python) 2 rep | |
|  +------------------+ +------------------+ +----------------+ |
|  +------------------+ +------------------+ +----------------+ |
|  | Social Svc (Go)  | | Gamification(Go) | | Notification   | |
|  | 2 replicas       | | 2 replicas       | | (Go) 2 replica | |
|  +------------------+ +------------------+ +----------------+ |
|                                                               |
|  HPA: CPU/Memory autoscaling + KEDA for Kafka-driven scaling |
+-------------------------------+-------------------------------+
                                |
+-------------------------------+-------------------------------+
|  DATA LAYER                                                   |
|                                                               |
|  +--------------------+  +--------------------+               |
|  | RDS PostgreSQL 16  |  | RDS PostgreSQL 16  |               |
|  | (Primary DB)       |  | + TimescaleDB ext  |               |
|  | Multi-AZ, r6g.xl  |  | (Biometrics)       |               |
|  | Read replicas: 2   |  | Multi-AZ, r6g.xl  |               |
|  +--------------------+  +--------------------+               |
|                                                               |
|  +--------------------+  +--------------------+               |
|  | ElastiCache Redis  |  | MSK (Managed Kafka)|               |
|  | Cluster, r6g.lg   |  | 3 brokers          |               |
|  | 3 nodes            |  +--------------------+               |
|  +--------------------+                                       |
|                                                               |
|  +--------------------+  +--------------------+               |
|  | S3 Buckets         |  | Pinecone           |               |
|  | - food-photos      |  | (Managed Vector DB)|               |
|  | - form-videos      |  | Serverless tier    |               |
|  | - ml-artifacts     |  +--------------------+               |
|  +--------------------+                                       |
+---------------------------------------------------------------+
```

---

## 6. Data Model Design

### 6.1 Core Entity Relationship Diagram

```
+------------------+       +--------------------+       +------------------+
|   users          |       |  training_plans    |       |  mesocycles      |
+------------------+       +--------------------+       +------------------+
| id (PK, UUID)   |<---+  | id (PK, UUID)     |<---+  | id (PK, UUID)   |
| email            |    |  | user_id (FK)      |    |  | plan_id (FK)    |
| password_hash    |    |  | name              |    |  | name            |
| created_at       |    |  | goal              |    |  | phase           |
| onboarding_done  |    |  | start_date        |    |  | weeks           |
+------------------+    |  | status            |    |  | start_date      |
        |               |  +--------------------+    |  | end_date        |
        |               |                            |  | status          |
        v               |                            |  +------------------+
+------------------+    |                            |          |
|  user_profiles   |    |                            |          v
+------------------+    |                            |  +------------------+
| user_id (FK,PK) |    |                            |  | microcycles      |
| display_name     |    |                            |  +------------------+
| date_of_birth    |    |                            |  | id (PK, UUID)   |
| gender           |    |                            +--| meso_id (FK)    |
| height_cm        |    |                               | week_number     |
| weight_kg        |    |                               | type            |
| body_fat_pct     |    |                               | volume_modifier |
| activity_level   |    |                               +------------------+
| experience_level |    |                                       |
| primary_goal     |    |                                       v
| equipment_access |    |                               +------------------+
| available_days   |    |                               | planned_sessions |
| session_duration |    |                               +------------------+
| preferences_json |    |                               | id (PK, UUID)   |
+------------------+    |                               | micro_id (FK)   |
        |               |                               | day_of_week     |
        v               |                               | focus           |
+------------------+    |                               | target_duration |
|  user_injuries   |    |                               +------------------+
+------------------+    |                                       |
| id (PK, UUID)   |    |                                       v
| user_id (FK)    |----+                               +------------------+
| body_part        |                                    | planned_exercises|
| injury_type      |                                    +------------------+
| severity (1-5)   |                                    | id (PK, UUID)   |
| onset_date       |                                    | session_id (FK) |
| status           |                                    | exercise_id(FK) |
| affected_moves   |                                    | order_index     |
| cleared_moves    |                                    | sets            |
| notes            |                                    | reps_min        |
+------------------+                                    | reps_max        |
                                                        | rpe_target      |
                                                        | rest_seconds    |
                                                        | tempo           |
                                                        | notes           |
                                                        +------------------+
```

### 6.2 Workout Logging Tables

```sql
-- Core workout session log
CREATE TABLE workout_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    plan_session_id UUID REFERENCES planned_sessions(id),  -- NULL if ad-hoc
    started_at      TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ,
    duration_sec    INTEGER,
    session_rpe     SMALLINT CHECK (session_rpe BETWEEN 1 AND 10),
    session_rating  SMALLINT CHECK (session_rating BETWEEN 1 AND 5),
    notes           TEXT,
    source          VARCHAR(20) DEFAULT 'manual',  -- manual, auto_detected, watch
    readiness_score SMALLINT,  -- readiness at time of workout
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Individual exercise logs within a session
CREATE TABLE exercise_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES workout_sessions(id),
    exercise_id     UUID NOT NULL REFERENCES exercises(id),
    order_index     SMALLINT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Individual set logs within an exercise
CREATE TABLE set_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_log_id UUID NOT NULL REFERENCES exercise_logs(id),
    set_number      SMALLINT NOT NULL,
    set_type        VARCHAR(20) DEFAULT 'working',  -- warmup, working, drop, amrap, rest_pause
    weight_kg       DECIMAL(6,2),
    reps            SMALLINT,
    rpe             DECIMAL(3,1) CHECK (rpe BETWEEN 1.0 AND 10.0),
    rir             SMALLINT,  -- reps in reserve
    tempo           VARCHAR(10),  -- e.g., "3-1-2-0"
    rest_after_sec  SMALLINT,
    form_score      SMALLINT CHECK (form_score BETWEEN 0 AND 100),
    notes           TEXT,
    completed_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Exercise reference library
CREATE TABLE exercises (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(200) UNIQUE NOT NULL,
    category            VARCHAR(50),    -- compound, isolation, cardio, mobility
    movement_pattern    VARCHAR(50),    -- squat, hinge, push, pull, carry, etc.
    primary_muscles     TEXT[],         -- array of muscle groups
    secondary_muscles   TEXT[],
    equipment_required  TEXT[],         -- barbell, dumbbell, cable, bodyweight, etc.
    difficulty_level    SMALLINT,       -- 1-5
    instructions        TEXT,
    video_url           VARCHAR(500),
    form_check_enabled  BOOLEAN DEFAULT FALSE,
    embedding_vector    VECTOR(768),    -- for semantic search / substitution
    tags                TEXT[]
);

-- Estimated 1RM tracking (calculated, not directly measured)
CREATE TABLE estimated_maxes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    exercise_id     UUID NOT NULL REFERENCES exercises(id),
    estimated_1rm   DECIMAL(6,2) NOT NULL,  -- in kg
    method          VARCHAR(30),  -- epley, brzycki, rpe_based
    source_set_id   UUID REFERENCES set_logs(id),
    calculated_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, exercise_id, calculated_at)
);
CREATE INDEX idx_estimated_maxes_user_exercise
    ON estimated_maxes(user_id, exercise_id, calculated_at DESC);
```

### 6.3 Nutrition Logging Tables

```sql
-- Daily nutrition targets (recalculated daily by CDIE)
CREATE TABLE daily_nutrition_targets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    target_date     DATE NOT NULL,
    calories        INTEGER NOT NULL,
    protein_g       DECIMAL(5,1) NOT NULL,
    carbs_g         DECIMAL(5,1) NOT NULL,
    fat_g           DECIMAL(5,1) NOT NULL,
    fiber_g         DECIMAL(5,1),
    water_ml        INTEGER,
    adjustment_reason TEXT,  -- "post-leg-day protein bump", "rest day reduction"
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, target_date)
);

-- Meal / food logging
CREATE TABLE meal_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    meal_type       VARCHAR(20),  -- breakfast, lunch, dinner, snack, pre_workout, post_workout
    logged_at       TIMESTAMPTZ NOT NULL,
    photo_url       VARCHAR(500),
    source          VARCHAR(20) DEFAULT 'manual',  -- manual, photo_ai, barcode, voice
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Individual food items within a meal
CREATE TABLE food_log_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_log_id     UUID NOT NULL REFERENCES meal_logs(id),
    food_id         VARCHAR(100),  -- reference to food database
    food_name       VARCHAR(300) NOT NULL,
    serving_size    DECIMAL(6,2),
    serving_unit    VARCHAR(50),  -- g, oz, cup, piece, etc.
    calories        INTEGER,
    protein_g       DECIMAL(5,1),
    carbs_g         DECIMAL(5,1),
    fat_g           DECIMAL(5,1),
    fiber_g         DECIMAL(5,1),
    sugar_g         DECIMAL(5,1),
    sodium_mg       DECIMAL(6,1),
    cholesterol_mg  DECIMAL(6,1),
    micronutrients  JSONB,  -- flexible storage for vitamins/minerals
    ai_confidence   DECIMAL(3,2),  -- confidence of AI food recognition
    verified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Food database (local cache of external food data)
CREATE TABLE foods (
    id              VARCHAR(100) PRIMARY KEY,
    name            VARCHAR(300) NOT NULL,
    brand           VARCHAR(200),
    category        VARCHAR(100),
    serving_size    DECIMAL(6,2),
    serving_unit    VARCHAR(50),
    calories_per_serving    INTEGER,
    protein_per_serving     DECIMAL(5,1),
    carbs_per_serving       DECIMAL(5,1),
    fat_per_serving         DECIMAL(5,1),
    fiber_per_serving       DECIMAL(5,1),
    barcode         VARCHAR(50),
    source          VARCHAR(50),  -- usda, open_food_facts, passio, user_created
    embedding_vector VECTOR(768),  -- for semantic food search
    data_json       JSONB,  -- full nutritional profile
    verified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.4 Biometric Data (TimescaleDB Hypertables)

```sql
-- Heart rate / HRV stream (TimescaleDB hypertable)
CREATE TABLE biometric_readings (
    time            TIMESTAMPTZ NOT NULL,
    user_id         UUID NOT NULL,
    metric_type     VARCHAR(30) NOT NULL,  -- hr, hrv_rmssd, hrv_sdnn, resting_hr, spo2, temp, resp_rate
    value           DECIMAL(8,2) NOT NULL,
    source          VARCHAR(30),  -- apple_watch, garmin, oura, whoop, manual
    device_id       VARCHAR(100),
    metadata        JSONB
);
SELECT create_hypertable('biometric_readings', 'time');
CREATE INDEX idx_biometric_user_type ON biometric_readings(user_id, metric_type, time DESC);

-- Compression policy: compress chunks older than 7 days
SELECT add_compression_policy('biometric_readings', INTERVAL '7 days');
-- Retention policy: keep raw data for 2 years, aggregates forever
SELECT add_retention_policy('biometric_readings', INTERVAL '2 years');

-- Continuous aggregate: hourly averages
CREATE MATERIALIZED VIEW biometric_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    user_id,
    metric_type,
    avg(value) AS avg_value,
    min(value) AS min_value,
    max(value) AS max_value,
    count(*) AS sample_count
FROM biometric_readings
GROUP BY bucket, user_id, metric_type;

-- Sleep session data
CREATE TABLE sleep_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    sleep_start     TIMESTAMPTZ NOT NULL,
    sleep_end       TIMESTAMPTZ NOT NULL,
    duration_min    INTEGER,
    deep_sleep_min  INTEGER,
    rem_sleep_min   INTEGER,
    light_sleep_min INTEGER,
    awake_min       INTEGER,
    sleep_score     SMALLINT CHECK (sleep_score BETWEEN 0 AND 100),
    avg_hr          DECIMAL(4,1),
    avg_hrv         DECIMAL(5,1),
    avg_spo2        DECIMAL(4,1),
    min_hr          DECIMAL(4,1),
    respiratory_rate DECIMAL(4,1),
    skin_temp_delta DECIMAL(3,1),
    source          VARCHAR(30),
    raw_data        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Daily readiness scores (calculated each morning)
CREATE TABLE readiness_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    score_date      DATE NOT NULL,
    score           SMALLINT NOT NULL CHECK (score BETWEEN 0 AND 100),
    zone            VARCHAR(10),  -- peak, good, moderate, low, rest
    components      JSONB NOT NULL,
    /* components example:
    {
        "hrv_vs_baseline": { "value": 0.85, "weight": 0.30, "contribution": 25.5 },
        "sleep_quality": { "value": 0.72, "weight": 0.25, "contribution": 18.0 },
        "sleep_duration": { "value": 0.90, "weight": 0.15, "contribution": 13.5 },
        "resting_hr": { "value": 0.80, "weight": 0.15, "contribution": 12.0 },
        "subjective": { "value": 0.60, "weight": 0.10, "contribution": 6.0 },
        "fatigue_trend": { "value": 0.50, "weight": 0.05, "contribution": 2.5 }
    }
    */
    recommendation  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, score_date)
);
```

### 6.5 AI Coaching & Conversation History

```sql
-- AI coaching conversation threads
CREATE TABLE coaching_threads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    thread_type     VARCHAR(30),  -- general, workout_feedback, nutrition_advice, injury_consult
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ,
    message_count   INTEGER DEFAULT 0,
    context_summary TEXT,  -- LLM-generated summary for context window management
    status          VARCHAR(20) DEFAULT 'active'
);

-- Individual messages in coaching conversations
CREATE TABLE coaching_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id       UUID NOT NULL REFERENCES coaching_threads(id),
    role            VARCHAR(10) NOT NULL,  -- user, assistant, system
    content         TEXT NOT NULL,
    message_type    VARCHAR(30),  -- text, workout_card, nutrition_card, chart, proactive_alert
    context_used    JSONB,  -- what data the AI accessed to generate this response
    model_used      VARCHAR(50),  -- claude-3-opus, gpt-4, etc.
    tokens_in       INTEGER,
    tokens_out      INTEGER,
    latency_ms      INTEGER,
    feedback        VARCHAR(10),  -- helpful, not_helpful, null
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Proactive coaching messages (AI-initiated)
CREATE TABLE proactive_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    trigger_type    VARCHAR(50) NOT NULL,  -- recovery_alert, nutrition_gap, consistency_praise, etc.
    trigger_data    JSONB NOT NULL,  -- the data that triggered this message
    content         TEXT NOT NULL,
    channel         VARCHAR(20),  -- push, in_app, email
    delivered_at    TIMESTAMPTZ,
    opened_at       TIMESTAMPTZ,
    action_taken    BOOLEAN,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.6 GLP-1 Tracking Tables

```sql
-- GLP-1 medication configuration
CREATE TABLE glp1_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) UNIQUE,
    medication      VARCHAR(50) NOT NULL,  -- semaglutide, tirzepatide
    brand           VARCHAR(50),
    current_dose_mg DECIMAL(4,2),
    dose_schedule   VARCHAR(20) DEFAULT 'weekly',
    injection_day   VARCHAR(10),
    start_date      DATE NOT NULL,
    titration_phase BOOLEAN DEFAULT TRUE,
    prescriber_name VARCHAR(200),
    notes           TEXT,
    active          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- GLP-1 injection logs
CREATE TABLE glp1_injections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES glp1_profiles(id),
    injection_date  DATE NOT NULL,
    dose_mg         DECIMAL(4,2) NOT NULL,
    injection_site  VARCHAR(50),  -- left_abdomen, right_abdomen, left_thigh, right_thigh, upper_arm
    side_effects    JSONB,  -- { "nausea": 3, "appetite_change": 2, "fatigue": 1 }
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Body composition tracking (especially important for GLP-1 users)
CREATE TABLE body_composition_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    log_date        DATE NOT NULL,
    weight_kg       DECIMAL(5,2),
    body_fat_pct    DECIMAL(4,1),
    lean_mass_kg    DECIMAL(5,2),  -- estimated
    waist_cm        DECIMAL(5,1),
    hip_cm          DECIMAL(5,1),
    measurement_method VARCHAR(30),  -- scale, dexa, ai_photo, manual
    photo_urls      TEXT[],
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.7 Social & Gamification Tables

```sql
-- User relationships
CREATE TABLE user_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    connected_user_id UUID NOT NULL REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, accepted, blocked
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, connected_user_id)
);

-- Gamification: XP and levels
CREATE TABLE user_gamification (
    user_id         UUID PRIMARY KEY REFERENCES users(id),
    total_xp        INTEGER DEFAULT 0,
    current_level   INTEGER DEFAULT 1,
    current_streak  INTEGER DEFAULT 0,
    longest_streak  INTEGER DEFAULT 0,
    achievements    JSONB DEFAULT '[]',  -- array of achievement IDs + unlock dates
    titles          TEXT[],
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Achievements / badges
CREATE TABLE achievements (
    id              VARCHAR(50) PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    category        VARCHAR(50),  -- training, nutrition, recovery, social, milestone
    icon_url        VARCHAR(500),
    xp_reward       INTEGER,
    criteria_json   JSONB NOT NULL,  -- machine-readable unlock criteria
    rarity          VARCHAR(20)  -- common, uncommon, rare, epic, legendary
);

-- Challenges (group competitions)
CREATE TABLE challenges (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    challenge_type  VARCHAR(50),  -- volume, consistency, steps, weight_loss
    metric          VARCHAR(50),  -- total_volume_kg, sessions_completed, steps, etc.
    start_date      DATE,
    end_date        DATE,
    created_by      UUID REFERENCES users(id),
    max_participants INTEGER,
    status          VARCHAR(20) DEFAULT 'active'
);
```

---

## 7. AI/ML Pipeline Architecture

### 7.1 Multi-Agent Coaching System

```
MULTI-AGENT COACHING ARCHITECTURE
====================================

                    +----------------------------+
                    |     ORCHESTRATOR AGENT      |
                    |     (LangGraph Router)      |
                    |                            |
                    |  - Receives user input     |
                    |  - Classifies intent       |
                    |  - Routes to specialist    |
                    |  - Synthesizes responses   |
                    |  - Manages conversation    |
                    +------+-----+-------+------+
                           |     |       |
              +------------+     |       +------------+
              |                  |                     |
              v                  v                     v
    +------------------+ +------------------+ +------------------+
    | TRAINING AGENT   | | NUTRITION AGENT  | | RECOVERY AGENT   |
    |                  | |                  | |                  |
    | Context:         | | Context:         | | Context:         |
    | - Current plan   | | - Daily targets  | | - HRV data       |
    | - Workout history| | - Food logs      | | - Sleep data     |
    | - Estimated maxes| | - Preferences    | | - Readiness      |
    | - Injury status  | | - Allergies      | | - Fatigue index  |
    | - Form data      | | - GLP-1 status   | | - Stress data    |
    |                  | |                  | |                  |
    | Can:             | | Can:             | | Can:             |
    | - Modify workout | | - Adjust macros  | | - Score readiness|
    | - Swap exercises | | - Suggest meals  | | - Recommend rest |
    | - Explain logic  | | - Log food       | | - Suggest deload |
    | - Adjust volume  | | - Analyze trends | | - Modify intensity|
    +------------------+ +------------------+ +------------------+
              |                  |                     |
              +------------+     |       +------------+
                           |     |       |
                           v     v       v
                    +----------------------------+
                    |   UNIFIED STATE STORE       |
                    |   (User Context Vector)     |
                    |                            |
                    |   Redis: hot state          |
                    |   PostgreSQL: full history  |
                    |   Pinecone: semantic memory |
                    +----------------------------+

AGENT TOOL DEFINITIONS:
-----------------------

Training Agent Tools:
  - get_current_workout() -> today's planned workout
  - modify_exercise(exercise_id, params) -> swap/adjust exercise
  - get_training_history(days) -> recent workout logs
  - estimate_1rm(exercise_id) -> current estimated max
  - get_injury_status() -> active injuries
  - get_form_scores(exercise_id) -> recent form analysis

Nutrition Agent Tools:
  - get_daily_targets() -> today's macro targets
  - get_food_log(date) -> what's been eaten
  - calculate_remaining() -> remaining macros for the day
  - suggest_meal(constraints) -> generate meal suggestion
  - log_food(items) -> log food items
  - get_glp1_protein_target() -> GLP-1-adjusted protein needs

Recovery Agent Tools:
  - get_readiness_score() -> today's readiness
  - get_sleep_data(days) -> recent sleep sessions
  - get_hrv_trend(days) -> HRV trend data
  - get_fatigue_index() -> current FAI score
  - recommend_recovery_protocol() -> recovery actions
  - should_deload() -> deload recommendation
```

### 7.2 ML Model Registry

| Model | Type | Purpose | Training Data | Deployment |
|-------|------|---------|---------------|------------|
| **Readiness Scorer** | Gradient Boosted Trees (XGBoost) | Calculate daily readiness from biometric inputs | Historical HRV/sleep/performance correlation data | Cloud (Go service calls Python inference) |
| **Fatigue Accumulator** | LSTM / Temporal CNN | Predict fatigue accumulation over 7-day horizon | Time-series training load + recovery signals | Cloud (batch prediction) |
| **Injury Risk Predictor** | Random Forest + rule overlays | Predict injury probability by body region | Movement asymmetry data, load progression, form scores | Cloud (daily batch) |
| **Volume Autoregulator** | Bayesian optimization | Determine optimal training volume per muscle group per user | Individual response curves (volume -> hypertrophy/strength) | Cloud (plan generation) |
| **1RM Estimator** | Ensemble (Epley, Brzycki, RPE-based) | Estimate current 1RM from submaximal sets | Individual set data with known maxes | On-device (immediate calculation) |
| **Exercise Substitutor** | Embedding similarity (cosine) | Find equivalent exercises for injury routing | Exercise embeddings trained on muscle activation data | Cloud (Pinecone vector search) |
| **Food Recognizer** | CNN (Passio AI / custom fine-tuned) | Identify foods from photos | Passio's 2.5M food database + custom training data | On-device (TFLite) |
| **Portion Estimator** | Depth estimation CNN | Estimate food portions from single image | Labeled food images with known weights | On-device (TFLite) |
| **Pose Estimator** | MediaPipe BlazePose / YOLO11 | 33-landmark body tracking for form analysis | Pre-trained (Google/Ultralytics) + fine-tuned for gym | On-device (TFLite / CoreML) |
| **Form Scorer** | Exercise-specific rule engine + CNN | Score exercise form quality per rep | Labeled form videos (good/bad examples per exercise) | On-device (inference) + cloud (training) |
| **Rep Counter** | State machine on joint angles | Count repetitions automatically | Pose estimation landmark sequences | On-device |
| **Exercise Classifier** | CNN on accelerometer + pose data | Identify exercise being performed | Labeled exercise videos / wearable data | On-device |
| **Coaching LLM** | Claude / GPT-4 (fine-tuned system prompt) | Natural language coaching, explanations, motivation | Curated coaching dialogues, fitness knowledge base | Cloud (API) |
| **Plateau Detector** | Change-point detection (PELT algorithm) | Detect when strength/weight progress stalls | Individual progress time series | Cloud (weekly batch) |

### 7.3 ML Training Pipeline

```
ML TRAINING & DEPLOYMENT PIPELINE
====================================

[Data Sources]
  User workout logs, biometric streams, food logs, form videos
       |
       v
[Feature Store (Feast)]
  - Materialized features for each model
  - Point-in-time correct feature retrieval
  - Online (low-latency) + Offline (batch) serving
       |
       v
[Training Pipeline (GCP Vertex AI)]
  - Scheduled retraining (weekly for most models)
  - Triggered retraining on significant data changes
  - Hyperparameter tuning via Optuna
  - Cross-validation + holdout evaluation
       |
       v
[Model Registry (MLflow)]
  - Version tracking
  - A/B test assignment
  - Performance metrics per version
  - Rollback capability
       |
       v
[Deployment]
  Cloud models -> Kubernetes (Seldon / KServe)
  On-device models -> TFLite conversion -> OTA model updates via CodePush/Shorebird
       |
       v
[Monitoring (Evidently AI)]
  - Data drift detection
  - Prediction quality monitoring
  - Feature importance tracking
  - Alert on model degradation
```

---

## 8. Integration Layer

### 8.1 Wearable Integration Matrix

```
WEARABLE INTEGRATION ARCHITECTURE
====================================

+-----------------------+---------------------------------------------+
| Platform              | Data Available                              |
+-----------------------+---------------------------------------------+
| Apple HealthKit       | HR, HRV, sleep, steps, workouts, SpO2,     |
|                       | respiratory rate, walking asymmetry,        |
|                       | body temp, noise exposure                   |
+-----------------------+---------------------------------------------+
| Google Health Connect | HR, steps, sleep, workouts, SpO2,           |
|                       | body temp, nutrition (bi-directional)       |
+-----------------------+---------------------------------------------+
| Garmin Connect API    | HR, HRV, sleep, stress, Body Battery,       |
|                       | training load, VO2max, steps, GPS           |
+-----------------------+---------------------------------------------+
| Whoop API             | HRV, RHR, sleep (stages), strain score,     |
|                       | recovery score, respiratory rate             |
+-----------------------+---------------------------------------------+
| Oura Ring API         | HRV, RHR, sleep (stages), readiness score,  |
|                       | body temperature, SpO2, activity             |
+-----------------------+---------------------------------------------+
| Polar API             | HR, HRV, sleep, training load, VO2max,      |
|                       | running power, orthostatic test              |
+-----------------------+---------------------------------------------+
| WHOOP 5.0 / Ultra    | All above + blood pressure, SpO2 cont.,     |
|                       | skin temperature, blood oxygen variability   |
+-----------------------+---------------------------------------------+

SYNC ARCHITECTURE:

  [Wearable Device] --bluetooth--> [Phone Health Store]
        |                                   |
        v                                   v
  [Direct API]                    [HealthKit / Health Connect]
  (Garmin, Whoop, Oura)          (Apple Watch, Samsung, Pixel)
        |                                   |
        +----------------+------------------+
                         |
                         v
            [Integration Service (Go)]
            |
            |- Normalize data to unified schema
            |- Dedup (same data from multiple sources)
            |- Priority: Oura/Whoop HRV > Watch HRV > calculated
            |- Write to TimescaleDB biometric_readings
            |- Emit events to Kafka (sleep.imported, hrv.updated)
            |
            v
      [TimescaleDB]  -->  [Recovery Engine]  -->  [Readiness Score]
```

### 8.2 Third-Party API Integrations

| Integration | Purpose | API Type | Sync Frequency |
|-------------|---------|----------|----------------|
| **Apple HealthKit** | Biometric data import/export | On-device SDK | Real-time (background delivery) |
| **Google Health Connect** | Biometric data import/export | On-device SDK | Real-time (observer pattern) |
| **Garmin Connect** | Enhanced wearable data | REST OAuth2 | Push notifications + polling |
| **Whoop** | Recovery/strain data | REST OAuth2 | Webhook + polling |
| **Oura** | Ring biometric data | REST OAuth2 | Webhook + polling |
| **Passio AI** | Food recognition | On-device SDK + REST | On-demand (photo capture) |
| **OpenFoodFacts** | Open food database | REST | Daily sync (incremental) |
| **Cronometer** | Premium nutrition data | REST | On-demand |
| **Stripe** | Subscription billing | REST + Webhooks | Event-driven |
| **RevenueCat** | IAP management | SDK + REST | Real-time |
| **OpenAI Whisper** | Speech-to-text | REST | On-demand |
| **ElevenLabs** | Text-to-speech | REST + WebSocket | On-demand (streaming) |
| **Anthropic Claude** | LLM coaching | REST | On-demand |
| **Firebase** | Push notifications (FCM) | SDK | Event-driven |
| **APNs** | iOS push notifications | HTTP/2 | Event-driven |
| **Mixpanel** | Product analytics | SDK | Real-time event streaming |

---

## 9. Security and Compliance

### 9.1 Data Protection

```
SECURITY ARCHITECTURE
======================

1. DATA CLASSIFICATION
   CRITICAL:   Health data (HRV, sleep, weight, GLP-1 medication)
   SENSITIVE:  Personal info (email, DOB, photos)
   INTERNAL:   Workout logs, nutrition logs
   PUBLIC:     Exercise library, achievement definitions

2. ENCRYPTION
   - At rest: AES-256 (AWS RDS encryption, S3 server-side encryption)
   - In transit: TLS 1.3 (all API calls, inter-service communication)
   - Application-level: Health data encrypted with per-user keys
   - Photos: Client-side encryption before upload

3. AUTHENTICATION & AUTHORIZATION
   - Auth: JWT (RS256) with short-lived access tokens (15 min)
   - Refresh tokens: Rotating, stored server-side, 30-day expiry
   - MFA: Optional TOTP for premium users
   - OAuth2: Sign in with Apple (required for iOS), Google
   - RBAC: User, Premium User, Coach, Admin roles
   - Row-level security: PostgreSQL RLS policies per user

4. COMPLIANCE
   - HIPAA: BAA with AWS, PHI handling procedures, audit logs
   - GDPR: Data portability (export), right to erasure, consent management
   - CCPA: California privacy compliance
   - SOC 2 Type II: Target for Year 2 (enterprise readiness)
   - Apple App Store: HealthKit entitlements, privacy nutrition labels

5. DATA RETENTION
   - Active users: Full data retained
   - Deleted accounts: 30-day grace period, then permanent deletion
   - Biometric raw data: 2 years (aggregates kept indefinitely)
   - AI conversation logs: 1 year (anonymized for training after)
   - Photos: Deleted with account (not used for training without consent)

6. AI SAFETY
   - LLM guardrails: No medical diagnoses, no medication dosing advice
   - Disclaimer: "Not a substitute for medical advice"
   - GLP-1 features: Tracking only, no dose recommendations
   - Form check: "Consult a professional for injury assessment"
   - Content filtering: Block harmful fitness advice (extreme restriction, etc.)
```

---

## 10. MVP to Scale Roadmap

### Phase 1: MVP (Months 1-3)

**Goal:** Core workout tracking + AI workout generation + basic nutrition logging. Prove the AI-first value proposition.

```
MVP FEATURE SET
================

MUST HAVE:
  [x] User onboarding (goals, experience, equipment, schedule, injuries)
  [x] AI workout generation (Claude-powered, single prompt)
  [x] Workout logging (exercises, sets, reps, weight, RPE)
  [x] Exercise library (200+ exercises, searchable)
  [x] Basic progressive overload (auto-suggest weight increases)
  [x] Manual nutrition logging (search + log macros)
  [x] Daily macro targets (static calculation from profile)
  [x] Basic dashboard (today's workout, macro tracker)
  [x] Apple HealthKit integration (steps, weight, HR)
  [x] Push notifications (workout reminders)
  [x] Authentication (Apple Sign In, email)
  [x] Subscription (free tier + premium)

NICE TO HAVE:
  [ ] Barcode scanning for food
  [ ] Workout timer
  [ ] Exercise history charts
  [ ] Basic body weight tracking chart

TECH STACK (MVP):
  Mobile: Flutter
  Backend: Go monolith (modular, not microservices yet)
  Database: PostgreSQL (single instance)
  Cache: Redis (single instance)
  AI: Claude API (direct calls, no agent framework yet)
  Infra: Single AWS ECS cluster, RDS, ElastiCache
  CI/CD: GitHub Actions + Fastlane

TEAM: 2 Flutter devs, 1 Go backend dev, 1 ML/AI eng, 1 designer
COST: ~$5K/mo infra, ~$2K/mo AI API costs
TARGET: 1,000 beta users
```

### Phase 2: V1 (Months 4-6)

**Goal:** Adaptive training + wearable integration + social features. Activate the data flywheel.

```
V1 FEATURE SET
===============

TRAINING:
  [x] Adaptive workout modification (readiness-based)
  [x] Periodization (mesocycle/microcycle structure)
  [x] Estimated 1RM tracking and progression charts
  [x] Exercise substitution (injury-aware)
  [x] Workout history with volume/intensity analytics
  [x] Rest timer with auto-advance

NUTRITION:
  [x] Photo food logging (Passio AI SDK integration)
  [x] Barcode scanning
  [x] Training-responsive macro adjustment (same-day)
  [x] Meal suggestions based on remaining macros
  [x] Water tracking

RECOVERY:
  [x] Wearable integration (Apple Watch, Garmin, Oura, Whoop)
  [x] Morning readiness score
  [x] Sleep quality tracking and display
  [x] HRV trend visualization

SOCIAL:
  [x] User profiles (public/private)
  [x] Add friends
  [x] Activity feed (workouts completed, PRs hit)
  [x] Basic challenges (weekly volume, consistency)

GAMIFICATION:
  [x] XP system (earn XP for workouts, logging food, streaks)
  [x] Levels (1-100)
  [x] Achievement badges (first workout, 7-day streak, etc.)
  [x] Weekly leaderboards (friends)

TECH EVOLUTION:
  - Extract Workout Engine and Recovery Engine into separate services
  - Add TimescaleDB for biometric streams
  - Add Kafka for event-driven architecture
  - Add Pinecone for exercise embeddings
  - Move to EKS (Kubernetes)

TEAM: +1 Flutter dev, +1 Go dev, +1 data engineer
TARGET: 10,000 users
```

### Phase 3: V2 (Months 7-12)

**Goal:** Full AI coaching agent + computer vision + voice + complete automation. This is where TransformFit becomes the world's best.

```
V2 FEATURE SET
===============

AI COACHING:
  [x] Multi-agent coaching system (LangGraph orchestrator)
  [x] Proactive AI coaching messages (8 trigger types)
  [x] Weekly auto-generated performance reports
  [x] Monthly periodization auto-adjustment
  [x] Natural language workout/nutrition queries
  [x] Conversation memory and context management

COMPUTER VISION:
  [x] Real-time form checking (5 exercises at launch)
  [x] Rep counting (automatic)
  [x] Form score per set with feedback
  [x] Post-workout form review with highlights

VOICE:
  [x] Voice workout logging ("I just did 225 for 5 on bench")
  [x] Voice food logging ("I had a chicken breast with rice")
  [x] AI coach voice mode (Whisper STT + ElevenLabs TTS)

ADVANCED TRAINING:
  [x] Deload intelligence (automatic fatigue detection)
  [x] Injury management system (body map, substitution, RTT protocol)
  [x] Plateau detection and variation programming

GLP-1 MODULE:
  [x] Medication tracking (dose, schedule, site rotation)
  [x] Side effect logging with pattern recognition
  [x] Muscle preservation scoring
  [x] Protein-priority nutrition mode
  [x] Physician-ready monthly reports

MINDFULNESS:
  [x] Guided breathing exercises (pre-workout, sleep)
  [x] Stress check-ins linked to recovery model
  [x] Focus sessions (timed, with ambient sound)

AUTOMATION:
  [x] Zero-decision morning flow
  [x] Auto-detected workouts from wearables
  [x] Full same-day nutrition auto-adjustment

TECH EVOLUTION:
  - Full microservices architecture
  - GPU nodes for CV and voice (spot instances)
  - ML training pipeline (Vertex AI)
  - Model monitoring (Evidently AI)
  - Feature store (Feast)
  - Advanced observability (Datadog APM)

TEAM: +2 ML engineers, +1 CV specialist, +1 mobile dev
TARGET: 50,000 users, $500K ARR
```

### Phase 4: V3 (Year 2)

**Goal:** Multi-agent ecosystem + marketplace + B2B/enterprise. Scale to a platform.

```
V3 FEATURE SET
===============

PLATFORM:
  [ ] Coach marketplace (certified trainers create programs)
  [ ] Program marketplace (buy/sell training programs)
  [ ] Supplement integration (recommendations, tracking)
  [ ] Gym equipment integration (smart rack, smart watch sync)

B2B / ENTERPRISE:
  [ ] Corporate wellness dashboard
  [ ] Team/organization management
  [ ] Aggregated (anonymized) health insights for HR
  [ ] Custom branding (white-label option)
  [ ] API for third-party integrations

ADVANCED AI:
  [ ] Multi-modal coaching (text + voice + video feedback)
  [ ] Predictive body composition modeling
  [ ] Genetic/biomarker integration (23andMe, InsideTracker)
  [ ] Longevity score and healthspan optimization
  [ ] Custom fine-tuned LLM on TransformFit data

SOCIAL:
  [ ] Communities (subreddit-style topic groups)
  [ ] Live group workouts
  [ ] Trainer-client relationship management
  [ ] Content feed (tips, articles, videos from community)

TECH EVOLUTION:
  - Multi-region deployment (US, EU, APAC)
  - SOC 2 Type II certification
  - Custom fine-tuned models
  - Advanced A/B testing and personalization engine
  - Data lakehouse (Databricks/Snowflake) for analytics

TARGET: 500,000 users, $5M ARR, Series A
```

### Roadmap Timeline Summary

```
TIMELINE
=========

2026 Q2 (Apr-Jun):  MVP Launch -> TestFlight beta
2026 Q3 (Jul-Sep):  V1 Launch -> App Store + Play Store
2026 Q4 (Oct-Dec):  V2 Features (AI coach, CV, voice)
2027 Q1 (Jan-Mar):  V2 Complete -> Full automation achieved
2027 Q2-Q4:         V3 -> Platform, B2B, marketplace
2028:               Scale -> Multi-region, enterprise, Series A

KEY MILESTONES:
  Month 1:   Technical foundation + CI/CD + design system
  Month 2:   Core workout engine + exercise library
  Month 3:   MVP beta launch (1,000 users)
  Month 4:   Wearable integration + readiness scoring
  Month 5:   Photo food logging + adaptive nutrition
  Month 6:   V1 public launch (App Store)
  Month 8:   AI coaching agent live
  Month 10:  Form checking (computer vision) live
  Month 12:  V2 complete -- full automation platform
```

---

## 11. Research Sources

This system design was informed by research across the following domains:

### AI Fitness Apps and Adaptive Training
- [Fitbod: Best AI Fitness Apps 2026](https://fitbod.me/blog/best-ai-fitness-apps-2026-the-complete-guide-to-ai-powered-muscle-building-apps/)
- [SensAI: Evidence-Based Comparison of AI Fitness Apps](https://www.sensai.fit/blog/best-ai-fitness-apps-2026-fitbod-freeletics-future-trainiac-alternatives)
- [Gymscore: Best AI Fitness Apps 2026](https://www.gymscore.ai/best-ai-fitness-apps-2026)
- [AppStory: Adaptive AI Coaches 2025-2026](https://www.appstory.org/blog/adaptive-ai-fitness-coaches/)
- [Adamosoft: AI in Fitness 2026](https://adamosoft.com/blog/healthcare-software-development/ai-in-fitness/)

### Computer Vision and Form Checking
- [MobiDev: Human Pose Estimation Technology Guide](https://mobidev.biz/blog/human-pose-estimation-technology-guide)
- [Ultralytics: YOLO11 Smart Fitness Technology](https://www.ultralytics.com/blog/smart-fitness-technology-enabled-by-ultralytics-yolo11)
- [InDataLabs: Pose Estimation for Fitness](https://indatalabs.com/resources/human-activity-recognition-fitness-app)
- [PoseTracker: Real-Time Pose Estimation in 2025](https://www.posetracker.com/news/how-to-add-real-time-pose-estimation-in-2025)

### HRV, Recovery, and Readiness Scoring
- [AI Endurance: HRV Recovery Model](https://aiendurance.com/blog/your-heart-rate-variability-recovery-model)
- [Kubios: HRV Readiness Score](https://www.kubios.com/blog/hrv-readiness-score/)
- [Kubios: HRV-Guided Training](https://www.kubios.com/blog/hrv-guided-training/)
- [PMC: HRV Applications in Strength and Conditioning](https://pmc.ncbi.nlm.nih.gov/articles/PMC11204851/)
- [Marco Altini: On HRV and Readiness](https://medium.com/@altini_marco/on-heart-rate-variability-hrv-and-readiness-394a499ed05b)

### AI Food Recognition and Nutrition Tracking
- [Passio AI: Nutrition-AI Hub SDK](https://www.passio.ai/)
- [SnapCalorie: AI Food Recognition](https://www.snapcalorie.com/blog/ai-food-recognition-app-for-tracking-meals-the-future-of-nutrition-logging/)
- [NYU Tandon: AI Food Scanner](https://engineering.nyu.edu/news/ai-food-scanner-turns-phone-photos-nutritional-analysis)
- [CalorieMama: Food Image Recognition](https://www.caloriemama.ai/)

### GLP-1 and Muscle Preservation
- [PMC: Lean Tissue Preservation During GLP-1 Treatment](https://pmc.ncbi.nlm.nih.gov/articles/PMC12536186/)
- [MeAgain: #1 Semaglutide Tracking App](https://markets.financialcontent.com/stocks/article/abnewswire-2025-12-29-meagain-named-the-1-semaglutide-tracking-app-in-expert-review-of-top-glp-1-progress-monitoring-tools)
- [Frontiers: GLP-1 Agonists and Exercise](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2025.1720794/full)
- [MyFitnessPal: GLP-1 Journey Support](https://blog.myfitnesspal.com/how-myfitnesspal-supports-glp1-journey/)
- [LearnMuscles: Best GLP-1 Tracking Apps 2026](https://learnmuscles.com/blog/2025/11/27/6-best-glp-1-tracking-apps-compared-which-app-actually-works-in-2026/)

### Microservices Architecture
- [IJIRCT: Scalable Microservices for Health & Fitness Platforms](https://www.ijirct.org/viewPaper.php?paperId=2511026)
- [Medium: Designing a Scalable Fitness Tracking App for 100M+ Users](https://medium.com/@ankitviddya/designing-a-scalable-fitness-tracking-app-for-100m-users-a16f7cde4240)
- [WeblineIndia: Fitness App Architecture like Strava](https://www.weblineindia.com/blog/build-fitness-app-like-strava/)
- [ByteByteGo: Microservices Architecture Guide](https://blog.bytebytego.com/p/a-guide-to-microservices-architecture)

### Multi-Agent AI Systems
- [Google Research: Anatomy of a Personal Health Agent](https://research.google/blog/the-anatomy-of-a-personal-health-agent/)
- [LlamaIndex: GymNation AI Agents Case Study](https://www.llamaindex.ai/blog/case-study-gymnation-revolutionizes-fitness-with-ai-agents-powering-member-experiences)
- [Medium: Personalized Health with AI Multi-Agent using LangGraph](https://medium.com/@jalajagr/personalized-health-and-fitness-with-ai-multi-agent-using-langgraph-and-memory-529204be05ea)
- [PubMed: Multi Agent Architecture for Automated Health Coaching](https://pubmed.ncbi.nlm.nih.gov/34562163/)

### Deload and Periodization
- [Hawk Fit: Fitness-Fatigue Model and Deloading](https://hawkfitcoaching.com/blogs/news/fitness-fatigue-model-the-theory-of-deloading)
- [PMC: Deloading Practices in Strength Sports](https://pmc.ncbi.nlm.nih.gov/articles/PMC10948666/)
- [Breaking Muscle: Science Behind Deload Weeks](https://breakingmuscle.com/deload-week/)

### Framework Comparison (Flutter vs React Native)
- [TechAhead: Flutter vs React Native 2026](https://www.techaheadcorp.com/blog/flutter-vs-react-native-in-2026-the-ultimate-showdown-for-app-development-dominance/)
- [Droids on Roids: Flutter vs React Native 2025 Comparison](https://www.thedroidsonroids.com/blog/flutter-vs-react-native-comparison)
- [Foresight Mobile: Why Flutter Outperforms in 2026](https://foresightmobile.com/blog/why-flutter-will-outperform-the-competition-in-2026)
- [Adevs: React Native vs Flutter 2026 Benchmarks](https://adevs.com/blog/react-native-vs-flutter/)

### Time-Series Data and TimescaleDB
- [TimescaleDB: PostgreSQL for Real-Time Analytics](https://www.timescale.com/)
- [Supabase: TimescaleDB Extension Docs](https://supabase.com/docs/guides/database/extensions/timescaledb)

### Passio AI SDK
- [Passio AI: SDK Documentation](https://passio.gitbook.io/nutrition-ai)
- [Passio AI: Photo Food Logging](https://www.passio.ai/photo-logging)
- [Flutter: Passio Nutrition-AI SDK](https://pub.dev/documentation/nutrition_ai/latest/)

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **CDIE** | Cross-Domain Intelligence Engine -- the unified AI that reasons across all four pillars |
| **FAI** | Fatigue Accumulation Index -- composite score tracking accumulated training fatigue |
| **RPE** | Rate of Perceived Exertion (1-10 scale) |
| **RIR** | Reps in Reserve -- how many more reps you could have done |
| **HRV** | Heart Rate Variability -- time variation between heartbeats, proxy for recovery |
| **rMSSD** | Root Mean Square of Successive Differences -- primary HRV metric |
| **1RM** | One-Rep Max -- the maximum weight you can lift for one repetition |
| **Mesocycle** | Training block of 3-6 weeks with a specific goal |
| **Microcycle** | One week of training within a mesocycle |
| **Deload** | Planned reduction in training stress (volume/intensity) to dissipate fatigue |
| **GLP-1** | Glucagon-Like Peptide-1 receptor agonist medications (Ozempic, Wegovy, etc.) |
| **TDEE** | Total Daily Energy Expenditure -- total calories burned per day |
| **SWC** | Smallest Worthwhile Change -- statistical threshold for meaningful HRV variation |

## Appendix B: Cost Estimates (Monthly at Scale)

| Component | MVP (1K users) | V1 (10K users) | V2 (50K users) | V3 (500K users) |
|-----------|---------------|----------------|-----------------|------------------|
| AWS EKS/ECS | $500 | $2,000 | $8,000 | $40,000 |
| RDS PostgreSQL | $200 | $800 | $2,500 | $10,000 |
| TimescaleDB | -- | $300 | $1,200 | $5,000 |
| Redis | $100 | $300 | $800 | $3,000 |
| Kafka (MSK) | -- | $500 | $1,500 | $6,000 |
| S3 + CloudFront | $50 | $200 | $1,000 | $5,000 |
| Pinecone | $70 | $200 | $500 | $2,000 |
| Claude API | $1,500 | $8,000 | $25,000 | $100,000 |
| ElevenLabs | $200 | $1,000 | $5,000 | $20,000 |
| Passio AI | $500 | $2,000 | $5,000 | $15,000 |
| GPU (CV/Voice) | -- | $500 | $3,000 | $15,000 |
| Datadog | $200 | $500 | $2,000 | $8,000 |
| **Total** | **$3,320** | **$16,300** | **$55,500** | **$229,000** |

---

*This document is a living blueprint. It will evolve as we build, learn, and iterate. The architecture is designed for incremental adoption -- start with the MVP monolith, extract services as scale demands, and add AI capabilities progressively.*

*Last updated: 2026-03-03*
