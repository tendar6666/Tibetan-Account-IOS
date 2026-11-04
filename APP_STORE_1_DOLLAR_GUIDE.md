# 🍎 How to Download Your Native iOS App (`.ipa`) & Publish on the Apple App Store for $1 ($0.99)

Your repository now includes an automated **GitHub Actions macOS Xcode Cloud Builder** (`.github/workflows/ios-build.yml`). Every time you push to GitHub, GitHub's cloud Mac servers automatically compile your app into a **real Native iOS App (`Tibetan-Account-Book-iOS.ipa`)** where all data and bill photos are saved inside the native app container on the iPhone (completely separate from Safari).

---

## Part 1: How to Download & Install the Native `.ipa` from GitHub onto Your iPhone Today

1. **Push to GitHub**:
   - Open **GitHub Desktop**, select **`Tibetan-Account-IOS`**, commit, and click **Push origin**.
2. **Download Your Built `.ipa` from GitHub**:
   - Go to **[github.com/tendar6666/Tibetan-Account-IOS/actions](https://github.com/tendar6666/Tibetan-Account-IOS/actions)**.
   - Click the latest **"Build Native iOS App (.ipa & Xcode Project)"** run (wait ~2 minutes for the green checkmark ✅).
   - Scroll down to **Artifacts** and click **`Tibetan-Account-Book-iOS-IPA`** to download the `.zip` containing `Tibetan-Account-Book-iOS.ipa`.
3. **Install onto Your iPhone from Windows (Free via Sideloadly)**:
   - Download and open **[Sideloadly](https://sideloadly.io/)** on your Windows PC.
   - Plug your iPhone into your PC with a USB cable.
   - Drag **`Tibetan-Account-Book-iOS.ipa`** into Sideloadly, enter your Apple ID email, and click **Start**.
   - On your iPhone, go to **Settings → General → VPN & Device Management** and trust your Apple ID. *(If on iOS 16+, also enable **Settings → Privacy & Security → Developer Mode**).*

---

## Part 2: Publishing on the Apple App Store for $1 ($0.99 USD / ₹89 INR)

Making your app a **$0.99 ($1) Paid App** on the Apple App Store is the cleanest way to monetize:
- **Zero In-App Purchase code needed**: Apple collects the $0.99 payment before the user downloads the app and deposits the earnings directly into your bank account every month.
- **100% Compliant with Apple Guideline 3.1.1**: Your `Tibetan-Account-IOS` build already has zero external donation/UPI links, so it will pass Apple App Review smoothly.
- **Keep 85% of Every Dollar**: Enroll in the **[App Store Small Business Program](https://developer.apple.com/app-store/small-business-program/)** (free for developers earning under $1M/year) so Apple only takes **15%** instead of 30%.

### Step-by-Step App Store Setup
1. **Enroll in the Apple Developer Program** ($99/year): [developer.apple.com/programs](https://developer.apple.com/programs/)
2. **Create Your App in App Store Connect** ([appstoreconnect.apple.com](https://appstoreconnect.apple.com)):
   - **Platform**: iOS
   - **Name**: `Tibetan Account Book`
   - **Subtitle**: `བོད་ཀྱི་རྩིས་དེབ། • Cash & Ledger`
   - **Primary Language**: English (U.S.)
   - **Bundle ID**: `com.tenzintendar.tibetanaccountbook`
   - **SKU**: `TIBETAN-ACCOUNT-IOS-001`
3. **Set the Price to $0.99 ($1)**:
   - In the left sidebar of App Store Connect, click **Pricing and Availability**.
   - Under **Price Schedule**, click **Add Pricing** → choose **$0.99 USD** (or ₹89 INR) → click **Save**.
4. **Set App Privacy ("Data Not Collected")**:
   - In the left sidebar, click **App Privacy** → click **Get Started**.
   - Select **"No, we do not collect data from this app"** (because 100% of accounting records and receipt photos are stored locally on the user's iPhone with zero cloud tracking).
   - **Privacy Policy URL**: `https://tendar6666.github.io/Tibetan-Account-IOS/privacy.html`

---

## Part 3: Copy-Paste App Store Description & Keywords

- **Promotional Text**:
  > ༄༅། །བོད་ཀྱི་རྩིས་དེབ། — Complete Bilingual Tibetan & English Accounting App. Features Beginner Cash In/Out mode, Advance Double-Entry, Fund Accounting (མ་དངུལ།), Multi-Photo Bill Attachments, and 100% Offline Privacy.

- **Keywords**:
  > `tibetan,account,cashbook,ledger,khata,monastery,finance,bookkeeping,bilingual,offline,voucher,fund`

- **Description**:
  > **བོད་ཀྱི་རྩིས་དེབ། • Tibetan Account Book** is a complete, 100% offline bilingual (Tibetan & English) accounting and bookkeeping application built for Tibetan shops, monasteries, schools, settlements, NGOs, and households.
  >
  > **Key Features:**
  > • **Beginner & Advance Modes**: Switch anytime between a simple Cash In / Cash Out tracker (`ལས་སླ་པོ།`) and a full Double-Entry Accounting system (`ཆེད་ལས།`) with Contra Vouchers, Journal Vouchers (JV), Trial Balance, and Balance Sheet.
  > • **Fund Accounting (`མ་དངུལ།`)**: Track General Funds (`སྤྱིར་བཏང་མ་དངུལ།`), Toilet/Construction Funds (`གསང་སྤྱོད་རྒྱག་ཆེད་མ་དངུལ།`), and designated community funds with automatic Balance Sheet balancing.
  > • **Multiple Bill & Receipt Photo Attachments**: Snap or attach multiple photos of bills and supporting documents to any entry with offline storage and fullscreen zoom preview.
  > • **Khata (`ཁ་ཊ།`) Party & Advance Tracking**: Track customer receivables and supplier payables with one-tap settlement.
  > • **100% Offline & Private**: All financial records and bill photos stay strictly on your iPhone. Export portable SHA-256 verified backups directly to the iOS Files app or AirDrop anytime.
