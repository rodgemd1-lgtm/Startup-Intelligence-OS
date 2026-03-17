# iPhone Workouts Direct Automation Setup

**Date:** 2026-03-12
**Assessor:** Jake
**Company:** Founder Intelligence OS
**Project:** Decision & Capability OS

## Objective
Stand up a direct-on-device automation path for the installed iPhone workout app so we can assess the product without taking over the Mac mouse through `iPhone Mirroring`.

## Framing
The mirrored-window approach works for quick reconnaissance, but it commandeers the desktop cursor and interrupts other work. The higher-leverage solution is a real-device XCTest harness that runs on the iPhone itself and targets the installed app by bundle identifier.

## Options

### Option A
Keep driving the app through `iPhone Mirroring`.

### Option B
Build a minimal signed iOS host app plus UI test runner that activates the target app on the device and navigates it with XCTest coordinates.

## Recommendation
Choose **Option B**.

The probe runner already exists in the repo and is the right long-term surface for repeatable, no-mouse app exploration. The remaining blocker is provisioning, not product or code design.

## Verified State

- Connected iPhone visible in Xcode tooling:
  - device name: `Superman`
  - UDID: `00008150-000C4D343480401C`
  - platform: `iOS`
  - OS version: `26.3.1`
- Developer Disk Image services are usable on the device.
- Local Apple Development signing identity exists:
  - `Apple Development: Michael Rodgers (3343A3GQAT)`
- Candidate target app identified from device metadata:
  - app name: `Workouts`
  - bundle id: `com.sbs.train`
  - version: `1.1.4`
- Xcode GUI account state:
  - Apple account visible in Xcode Settings as `Michael Rodgers`
  - team details page shows `Developer Team`
  - `Certificates, Identifiers, & Profiles` is marked healthy
  - `On Device Testing` shows `1 Provisioned Device`

## Implementation Added

- [README.md](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/README.md)
- [project.yml](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/project.yml)
- [DeviceProbeApp.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbe/DeviceProbeApp.swift)
- [DeviceProbeUITests.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbeUITests/DeviceProbeUITests.swift)
- [run_probe.sh](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/run_probe.sh)

## What The Probe Does

- generates a tiny Xcode project from `project.yml` using `xcodegen`
- builds a minimal signed iOS host app
- deploys a UI test runner to the connected iPhone
- activates `com.sbs.train` directly on the phone
- taps the primary tab bar positions:
  - dashboard
  - workout
  - levels
  - more
- stores screenshots in the `.xcresult` bundle

## Current Blocker

The runner could not complete deployment because Xcode does not currently have an active account session for team `3343A3GQAT`.

Observed failure:

```text
No Account for Team "3343A3GQAT"
No profiles for 'os.startupintelligence.deviceprobe'
No profiles for 'os.startupintelligence.deviceprobe.uitests.xctrunner'
```

This means:

- the code scaffold is in place
- the device is reachable
- signing identity exists
- provisioning cannot be created from the command line until the Xcode account session is restored
- the Xcode GUI reproduces the same failure in `Signing & Capabilities`
- the probe target currently renders its team as `Unknown Name (3343A3GQAT)` instead of binding to the visible `Michael Rodgers` developer team entry

## Assumptions

- `com.sbs.train` is the correct installed workout app to target.
- Once Xcode account access is restored, automatic provisioning should be sufficient for the probe bundle ids.
- Coordinate-based XCTest taps are acceptable for first-pass navigation even without accessibility identifiers in the target app.

## Risks

- The target app may require more coordinate tuning as deeper screens are automated.
- Provisioning may still require manual device registration if team settings changed.
- Direct automation will take over the phone itself while tests run, even though it will not move the Mac cursor.

## Artifacts Created Or Updated

- [README.md](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/README.md)
- [project.yml](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/project.yml)
- [DeviceProbeApp.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbe/DeviceProbeApp.swift)
- [DeviceProbeUITests.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbeUITests/DeviceProbeUITests.swift)
- [run_probe.sh](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/run_probe.sh)
- [enable-direct-iphone-automation-for-workout-app-recon.yaml](/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/decisions/enable-direct-iphone-automation-for-workout-app-recon.yaml)

## Next Actions

1. Open Xcode and confirm the Apple ID for team `3343A3GQAT` is signed in under Accounts.
2. Rerun `./apps/ios-device-probe/run_probe.sh`.
3. If provisioning succeeds, extend the test to drill into rows, detail screens, and settings flows.
4. Run `rvictl` alongside the direct probe to capture backend/API behavior without using the mirrored window.
