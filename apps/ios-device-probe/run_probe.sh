#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="IOSDeviceProbe"
SCHEME="DeviceProbe"
DEVICE_ID="${DEVICE_ID:-00008150-000C4D343480401C}"
DERIVED_DATA_PATH="${ROOT_DIR}/DerivedData"
RESULT_BUNDLE_PATH="${ROOT_DIR}/results/DeviceProbe.xcresult"

mkdir -p "${ROOT_DIR}/results"
rm -rf "${RESULT_BUNDLE_PATH}"

cd "${ROOT_DIR}"
xcodegen --spec project.yml

xcodebuild \
  -project "${PROJECT_NAME}.xcodeproj" \
  -scheme "${SCHEME}" \
  -destination "platform=iOS,id=${DEVICE_ID}" \
  -derivedDataPath "${DERIVED_DATA_PATH}" \
  -resultBundlePath "${RESULT_BUNDLE_PATH}" \
  -allowProvisioningUpdates \
  -allowProvisioningDeviceRegistration \
  test

echo "Result bundle: ${RESULT_BUNDLE_PATH}"
