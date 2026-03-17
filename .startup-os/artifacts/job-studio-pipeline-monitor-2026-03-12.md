# Job Studio Pipeline Monitor

This file is updated automatically every 15 minutes while the corpus extraction and ingest jobs are active.
## Update 2026-03-13T00:54:13.904058+00:00
- status: `running`
- active processes: `4`
- process table:
  - ` 9904       00:00   0.0  0.0 zsh -lc ps -o pid,etime,%cpu,%mem,command -ax | rg 'scripts.build_job_studio_training_factory_corpus|scripts.ingest_job_studio_training_factory' || true`
  - ` 9907       00:00   0.0  0.0 rg scripts.build_job_studio_training_factory_corpus|scripts.ingest_job_studio_training_factory`
  - `77456       15:45   0.2  0.3 /opt/homebrew/Cellar/python@3.13/3.13.11_1/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/MacOS/Python -m scripts.ingest_job_studio_training_factory`
  - `56347       40:08   0.8 13.2 /Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m scripts.build_job_studio_training_factory_corpus`
- corpus summary:
  - seen=1612 extracted=1292 cached=43 skipped=92 failed=185 chars=2287690344
  - summary_generated_at: `2026-03-13T00:54:05.210281+00:00`
  - active_group: `oracle_health_extracted`

## Update 2026-03-13T00:55:05.876723+00:00
- status: `running`
- active processes: `3`
- process table:
  - `10238 /bin/zsh -c ps -o pid,etime,%cpu,%mem,command -ax | rg 'scripts.build_job_studio_training_factory_corpus|scripts.ingest_job_studio_training_factory'`
  - `10241 rg scripts.build_job_studio_training_factory_corpus|scripts.ingest_job_studio_training_factory`
  - `56347 /Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m scripts.build_job_studio_training_factory_corpus`
- corpus summary:
  - seen=1622 extracted=1295 cached=43 skipped=93 failed=191 chars=2287716367
  - summary_generated_at: `2026-03-13T00:54:54.484915+00:00`
  - active_group: `oracle_health_extracted`

## Update 2026-03-13T00:55:44.293139+00:00
- status: `running`
- active processes: `1`
- process table:
  - `56347 /Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m scripts.build_job_studio_training_factory_corpus`
- corpus summary:
  - seen=1627 extracted=1299 cached=43 skipped=93 failed=192 chars=2287764947
  - summary_generated_at: `2026-03-13T00:55:12.217710+00:00`
  - active_group: `oracle_health_extracted`

## Update 2026-03-13T01:10:44.382979+00:00
- status: `completed`
- active processes: `0`
- corpus summary:
  - seen=1717 extracted=1355 cached=43 skipped=93 failed=226 chars=2303899845
  - summary_generated_at: `2026-03-13T01:01:42.203966+00:00`
  - active_group: `None`

