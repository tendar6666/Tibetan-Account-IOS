import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SWIFT_APP_DELEGATE = """import UIKit
import Capacitor
import WebKit
import StoreKit

public extension WKWebView {
    func triggerNativePrintAndPdf(jobName: String) {
        let printInfo = UIPrintInfo(dictionary: nil)
        printInfo.jobName = jobName
        printInfo.outputType = .general
        let printController = UIPrintInteractionController.shared
        printController.printInfo = printInfo
        printController.printFormatter = self.viewPrintFormatter()
        printController.present(animated: true, completionHandler: nil)
    }
}

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?
    private var isBridgeAttached = false
    private var bridgeHandler: NativeBridgeMessageHandler?
    private var updatesTask: Task<Void, Never>?
    let auditPackProductId = "com.tenzintendar.tibetanaccountbook.auditpack"

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Listen for StoreKit 2 transaction updates
        let productId = self.auditPackProductId
        updatesTask = Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    if transaction.productID == productId {
                        await MainActor.run {
                            self?.notifyWebViewPurchaseSuccess()
                        }
                    }
                    await transaction.finish()
                }
            }
        }

        for delay in [0.2, 0.6, 1.5, 3.0] {
            DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                self.attachNativeBridges()
            }
        }
        return true
    }

    func notifyWebViewPurchaseSuccess() {
        guard let rootVC = self.window?.rootViewController as? CAPBridgeViewController,
              let webView = rootVC.webView else {
            return
        }
        let js = "if (typeof handleIAPPurchaseSuccess === 'function') { handleIAPPurchaseSuccess(); }"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    func notifyWebViewProductPrice(_ price: String) {
        guard let rootVC = self.window?.rootViewController as? CAPBridgeViewController,
              let webView = rootVC.webView else {
            return
        }
        let escaped = price.replacingOccurrences(of: "\\\\", with: "\\\\\\\\").replacingOccurrences(of: "'", with: "\\\\'")
        let js = "window.storeKitDisplayPrice = '\\(escaped)'; if (typeof renderAll === 'function') { renderAll(); }"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    func notifyWebViewToast(_ text: String) {
        guard let rootVC = self.window?.rootViewController as? CAPBridgeViewController,
              let webView = rootVC.webView else {
            return
        }
        let escaped = text.replacingOccurrences(of: "\\\\", with: "\\\\\\\\").replacingOccurrences(of: "'", with: "\\\\'")
        let js = "if (typeof showToast === 'function') { showToast('\\(escaped)'); }"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    private func attachNativeBridges() {
        guard !isBridgeAttached,
              let rootVC = self.window?.rootViewController as? CAPBridgeViewController,
              let webView = rootVC.webView else {
            return
        }
        isBridgeAttached = true

        let handler = NativeBridgeMessageHandler(webView: webView, appDelegate: self)
        self.bridgeHandler = handler

        let ucc = webView.configuration.userContentController
        ucc.removeScriptMessageHandler(forName: "iosNativePrint")
        ucc.removeScriptMessageHandler(forName: "purchaseIAP")
        ucc.removeScriptMessageHandler(forName: "restoreIAP")

        ucc.add(handler, name: "iosNativePrint")
        ucc.add(handler, name: "purchaseIAP")
        ucc.add(handler, name: "restoreIAP")

        let scriptSource = \"\"\"
        window.print = function() {
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iosNativePrint) {
                window.webkit.messageHandlers.iosNativePrint.postMessage(document.title || 'Tibetan Account Book');
            }
        };
        \"\"\"
        let userScript = WKUserScript(source: scriptSource, injectionTime: .atDocumentEnd, forMainFrameOnly: false)
        ucc.addUserScript(userScript)
        webView.evaluateJavaScript(scriptSource, completionHandler: nil)

        // Fetch localized StoreKit 2 price and check existing entitlements on launch
        let productId = self.auditPackProductId
        Task { [weak self] in
            if let products = try? await Product.products(for: [productId]),
               let product = products.first {
                let displayPrice = product.displayPrice
                await MainActor.run {
                    self?.notifyWebViewProductPrice(displayPrice)
                }
            }

            for await result in Transaction.currentEntitlements {
                if case .verified(let transaction) = result {
                    if transaction.productID == productId {
                        await MainActor.run {
                            self?.notifyWebViewPurchaseSuccess()
                        }
                    }
                }
            }
        }
    }

    func applicationWillResignActive(_ application: UIApplication) {}
    func applicationDidEnterBackground(_ application: UIApplication) {}
    func applicationWillEnterForeground(_ application: UIApplication) {}
    func applicationDidBecomeActive(_ application: UIApplication) {
        self.attachNativeBridges()
    }
    func applicationWillTerminate(_ application: UIApplication) {
        updatesTask?.cancel()
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }
}

class NativeBridgeMessageHandler: NSObject, WKScriptMessageHandler {
    weak var webView: WKWebView?
    weak var appDelegate: AppDelegate?
    let defaultProductId = "com.tenzintendar.tibetanaccountbook.auditpack"

    init(webView: WKWebView, appDelegate: AppDelegate) {
        self.webView = webView
        self.appDelegate = appDelegate
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        if message.name == "iosNativePrint" {
            DispatchQueue.main.async {
                let title = (message.body as? String) ?? "Tibetan Account Book"
                self.webView?.triggerNativePrintAndPdf(jobName: title)
            }
        } else if message.name == "purchaseIAP" {
            var productId = defaultProductId
            if let dict = message.body as? [String: Any], let pid = dict["productId"] as? String {
                productId = pid
            }
            Task {
                await self.handlePurchase(productId: productId)
            }
        } else if message.name == "restoreIAP" {
            Task {
                await self.handleRestore()
            }
        }
    }

    @MainActor
    private func handlePurchase(productId: String) async {
        do {
            let products = try await Product.products(for: [productId])
            guard let product = products.first else {
                self.appDelegate?.notifyWebViewToast("App Store product unavailable. Please ensure In-App Purchase is active.")
                return
            }
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                switch verification {
                case .verified(let transaction):
                    self.appDelegate?.notifyWebViewPurchaseSuccess()
                    await transaction.finish()
                case .unverified(_, _):
                    self.appDelegate?.notifyWebViewToast("Purchase verification could not be completed.")
                }
            case .userCancelled:
                self.appDelegate?.notifyWebViewToast("Purchase cancelled.")
            case .pending:
                self.appDelegate?.notifyWebViewToast("Purchase is pending approval.")
            @unknown default:
                break
            }
        } catch {
            self.appDelegate?.notifyWebViewToast("App Store connection error: \\(error.localizedDescription)")
        }
    }

    @MainActor
    private func handleRestore() async {
        do {
            try await AppStore.sync()
            var found = false
            for await result in Transaction.currentEntitlements {
                if case .verified(let transaction) = result {
                    if transaction.productID == defaultProductId {
                        found = true
                        self.appDelegate?.notifyWebViewPurchaseSuccess()
                    }
                }
            }
            if !found {
                self.appDelegate?.notifyWebViewToast("No previous purchases found for this Apple ID.")
            }
        } catch {
            self.appDelegate?.notifyWebViewToast("Restore error: \\(error.localizedDescription)")
        }
    }
}
"""

def inject_storekit():
    candidates = [
        "ios/App/App/AppDelegate.swift",
        os.path.join(os.getcwd(), "ios", "App", "App", "AppDelegate.swift")
    ]
    target = None
    for c in candidates:
        if os.path.exists(os.path.dirname(c)):
            target = os.path.abspath(c)
            break

    if not target:
        print("⚠️ ios/App/App directory not found. Skipping AppDelegate StoreKit 2 injection.")
        return

    with open(target, "w", encoding="utf-8") as f:
        f.write(SWIFT_APP_DELEGATE)

    print(f"✅ Injected native Apple StoreKit 2 + Print bridge into {target}")

if __name__ == "__main__":
    inject_storekit()
