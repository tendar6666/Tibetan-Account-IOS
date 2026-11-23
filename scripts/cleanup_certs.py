import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def cleanup_certificates():
    try:
        import jwt
        import requests
    except ImportError:
        print("⚠️ PyJWT or requests not installed. Skipping automated certificate cleanup.")
        return

    key_id = os.environ.get("APP_STORE_KEY_ID", "").strip()
    issuer_id = os.environ.get("APP_STORE_ISSUER_ID", "").strip()
    key_path = os.path.expanduser(f"~/.private_keys/AuthKey_{key_id}.p8")

    if not key_id or not issuer_id or not os.path.exists(key_path):
        print("ℹ️ App Store Connect API credentials not found. Skipping certificate cleanup.")
        return

    try:
        with open(key_path, "r", encoding="utf-8") as f:
            private_key = f.read()

        now = int(time.time())
        payload = {
            "iss": issuer_id,
            "iat": now - 30,
            "exp": now + 900,
            "aud": "appstoreconnect-v1"
        }
        headers = {
            "alg": "ES256",
            "kid": key_id,
            "typ": "JWT"
        }

        token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
        auth_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        resp = requests.get("https://api.appstoreconnect.apple.com/v1/certificates?limit=50", headers=auth_headers, timeout=20)
        if resp.status_code != 200:
            print(f"⚠️ Certificate list query returned {resp.status_code}: {resp.text}")
            return

        certs = resp.json().get("data", [])
        print(f"🔎 Found {len(certs)} existing certificates in Apple Developer account.")

        for c in certs:
            cert_id = c.get("id")
            attrs = c.get("attributes", {})
            cert_type = attrs.get("certificateType", "")
            display_name = attrs.get("displayName", "")
            print(f" - [{cert_type}] {display_name} (ID: {cert_id})")
            if "DEVELOPMENT" in cert_type or "DISTRIBUTION" in cert_type:
                del_resp = requests.delete(f"https://api.appstoreconnect.apple.com/v1/certificates/{cert_id}", headers=auth_headers, timeout=20)
                if del_resp.status_code in (200, 204):
                    print(f"   ✅ Revoked ephemeral certificate {cert_id} ({cert_type}) to free slot for fresh cloud signing.")
                else:
                    print(f"   ⚠️ Could not revoke {cert_id}: {del_resp.status_code}")
    except Exception as e:
        print(f"⚠️ Certificate cleanup notice: {e}")

if __name__ == "__main__":
    cleanup_certificates()
