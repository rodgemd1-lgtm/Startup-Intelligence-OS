import SwiftUI

@main
struct DeviceProbeApp: App {
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 16) {
                Image(systemName: "iphone.gen3.radiowaves.left.and.right")
                    .font(.system(size: 44))
                Text("Device Probe")
                    .font(.title2.bold())
                Text("This host app only exists so the UI test runner can be signed and deployed to a real device.")
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
            }
            .padding(24)
        }
    }
}
