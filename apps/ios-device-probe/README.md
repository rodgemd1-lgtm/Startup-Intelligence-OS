# iOS Device Probe

This project is a minimal real-device XCTest harness for probing an installed iPhone app without driving the `iPhone Mirroring` window on macOS.

## What it does

- builds a tiny signed host app (`DeviceProbe`)
- installs a UI test runner on the connected iPhone
- activates the target app directly on the device
- taps through the primary tab bar positions using normalized on-device coordinates
- keeps screenshots in the `.xcresult` bundle for later review

The current target app bundle identifier is hard-coded in [DeviceProbeUITests.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbeUITests/DeviceProbeUITests.swift) as `com.sbs.train`.

## Files

- [project.yml](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/project.yml): XcodeGen source of truth
- [run_probe.sh](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/run_probe.sh): generates the Xcode project and runs the UI test on the connected iPhone
- [DeviceProbeApp.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbe/DeviceProbeApp.swift): minimal host app
- [DeviceProbeUITests.swift](/Users/mikerodgers/Startup-Intelligence-OS/apps/ios-device-probe/DeviceProbeUITests/DeviceProbeUITests.swift): direct-on-device automation script

## Prerequisites

- Xcode installed
- device visible to `xcrun xcdevice list`
- Developer Disk Image usable on the device
- a valid Apple Development identity
- an active Xcode account session for the signing team, or existing provisioning profiles for the probe bundle ids

## Run

```bash
./apps/ios-device-probe/run_probe.sh
```

Optional device override:

```bash
DEVICE_ID=<iphone-udid> ./apps/ios-device-probe/run_probe.sh
```

## Current blocker

The probe project builds structurally, but command-line deployment is currently blocked because Xcode does not have an active account session for team `3343A3GQAT`, so it cannot create provisioning profiles for:

- `os.startupintelligence.deviceprobe`
- `os.startupintelligence.deviceprobe.uitests.xctrunner`

Once the Apple ID/team is active in Xcode Accounts, rerun the script and the test runner should be able to deploy to the phone directly.
