"""Phase 7: THE IMMUNE SYSTEM — self-monitoring, error recovery, privacy guards.

Components:
  - error_recovery:    Retry failed API calls, track error budget per source
  - privacy_guard:     Classify data sensitivity, block personal data from work contexts
  - consistency_checker: Detect contradictory memories, flag for resolution
  - health_monitor:    Brain stats, API costs, error rates
  - stale_detector:    Flag memories not reinforced in 30+ days
"""
from jake_brain.immune.error_recovery import ErrorRecovery, with_retry
from jake_brain.immune.privacy_guard import PrivacyGuard, SensitivityLevel
from jake_brain.immune.consistency_checker import ConsistencyChecker
from jake_brain.immune.health_monitor import HealthMonitor
from jake_brain.immune.stale_detector import StaleDetector

__all__ = [
    "ErrorRecovery",
    "with_retry",
    "PrivacyGuard",
    "SensitivityLevel",
    "ConsistencyChecker",
    "HealthMonitor",
    "StaleDetector",
]
