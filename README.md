# 🍎 Tibetan Account Book — iOS Edition (བོད་ཀྱི་རྩིས་དེབ།)

This directory contains the standalone **iOS edition** of Tibetan Account Book, specifically optimized and compliant for Apple App Store guidelines and iOS Safari / WebKit PWA.

---

### 🛡️ Apple App Store Review Compliance
* **No External Payment / Donation Links (Guideline 3.1.1 & 3.2.2)**:
  * Excludes all "Buy me tea / momo", UPI IDs, PayPal links, and payment QR codes to prevent rejection under Apple's In-App Purchase and anti-steering rules.
  * The app is positioned as **100% Free Community Software** for monasteries, community shops, and Tibetan families.
* **Community Sharing**:
  * Users can share the app link freely using iOS native sharing (`navigator.share` / `UIActivityViewController`) and WhatsApp.
* **Storage & Privacy**:
  * 100% offline, persistent local storage (`localStorage`) with full JSON/CSV export and import.
  * Includes Apple-compliant [privacy.html](privacy.html).

---

### 🚀 Running the iOS Edition
You can open `index.html` directly or serve via local server:
```bash
# From workspace root
node server.js
```
Then visit:
* Local: `http://localhost:3000/ios/`
* iPhone on same Wi-Fi: `http://<YOUR_IP>:3000/ios/`
