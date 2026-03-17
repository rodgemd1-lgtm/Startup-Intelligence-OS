# Oracle Health MyJobStudio Training Hub

## Objective
Create a usable training-site surface tonight inside the Oracle Health AI Enablement repository so MyJobStudio content can be accessed, extended, and used immediately.

## Framing
The training content already existed in markdown, prompt-library, and workshop-guide form, but there was no operator-ready interface. The bottleneck was access and packaging, not source content.

## Recommendation
Use a no-build static training hub in the Oracle repo. It is fast to ship, easy to serve locally, and keeps the team in the current repository instead of waiting for a framework migration.

## Assumptions
- Local hosting is acceptable for tonight.
- The existing Oracle workshop guides remain the source of truth for Sessions 4-8.
- Track C needs MyJobStudio-native session packets for the strategist AI foundations arc.

## Risks
- The site is static, so advanced workflow features are not present yet.
- It depends on an internet connection for the CDN markdown renderer.
- The site is an access surface, not the finished training asset system.

## Artifacts Created
- [my-job-studio/README.md](/Users/mikerodgers/AI-Enablement-Oracle-Chat/my-job-studio/README.md)
- [MY_JOB_STUDIO_ACCESS_PROMPT.md](/Users/mikerodgers/AI-Enablement-Oracle-Chat/my-job-studio/MY_JOB_STUDIO_ACCESS_PROMPT.md)
- [training-site/index.html](/Users/mikerodgers/AI-Enablement-Oracle-Chat/training-site/index.html)
- [training-site/app.js](/Users/mikerodgers/AI-Enablement-Oracle-Chat/training-site/app.js)
- [training-site/styles.css](/Users/mikerodgers/AI-Enablement-Oracle-Chat/training-site/styles.css)
- [training-site/manifest.js](/Users/mikerodgers/AI-Enablement-Oracle-Chat/training-site/manifest.js)

## Next Actions
1. Expand each session into finished facilitator guide, learner handout, and deck files.
2. Add downloadable slide and handout outputs.
3. Move the site from local-serving to a preview deployment when you want broader team access.
