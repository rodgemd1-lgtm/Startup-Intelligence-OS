import XCTest

final class DeviceProbeUITests: XCTestCase {
    private let targetBundleID = "com.sbs.train"

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testPrimaryNavigationProbe() throws {
        let app = XCUIApplication(bundleIdentifier: targetBundleID)

        app.activate()
        XCTAssertTrue(
            app.wait(for: .runningForeground, timeout: 15),
            "Expected \(targetBundleID) to become foregrounded on the connected device."
        )

        capture(name: "01-launch")

        let tabSequence: [(name: String, x: CGFloat)] = [
            ("dashboard", 0.12),
            ("workout", 0.31),
            ("levels", 0.70),
            ("more", 0.89),
        ]

        for step in tabSequence {
            tap(in: app, x: step.x, y: 0.95)
            sleep(2)
            capture(name: "tab-\(step.name)")
        }
    }

    private func tap(in app: XCUIApplication, x: CGFloat, y: CGFloat) {
        let coordinate = app.coordinate(withNormalizedOffset: CGVector(dx: x, dy: y))
        coordinate.tap()
    }

    private func capture(name: String) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
