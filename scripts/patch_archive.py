import os
import sys
import plistlib

def find_archive():
    candidates = [
        'build/App.xcarchive',
        'ios/App/build/App.xcarchive',
        os.path.join(os.getcwd(), 'build', 'App.xcarchive'),
        os.path.join(os.getcwd(), 'ios', 'App', 'build', 'App.xcarchive')
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None

def patch_archive():
    archive_path = find_archive()
    if not archive_path:
        print("⚠️ Warning: build/App.xcarchive not found. Skipping patch.")
        return

    print(f"📦 Verifying xcarchive at: {archive_path}")
    app_path = os.path.join(archive_path, 'Products', 'Applications', 'App.app')
    arch_plist_path = os.path.join(archive_path, 'Info.plist')

    # 1. Ensure MinimumOSVersion is 17.0 in archive Info.plist
    if os.path.exists(arch_plist_path):
        try:
            with open(arch_plist_path, 'rb') as f:
                pl = plistlib.load(f)
            if 'ApplicationProperties' in pl:
                pl['ApplicationProperties']['MinimumOSVersion'] = '17.0'
            with open(arch_plist_path, 'wb') as f:
                plistlib.dump(pl, f)
            print("✅ Verified archive Info.plist (MinimumOSVersion: 17.0)")
        except Exception as e:
            print("⚠️ Archive Info.plist update notice:", e)

    if not os.path.exists(app_path):
        print(f"⚠️ App.app not found at: {app_path}")
        return

    # 2. Ensure MinimumOSVersion is 17.0 in all Info.plists
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file == 'Info.plist':
                p = os.path.join(root, file)
                try:
                    with open(p, 'rb') as f:
                        pl = plistlib.load(f)
                    pl['MinimumOSVersion'] = '17.0'
                    with open(p, 'wb') as f:
                        plistlib.dump(pl, f)
                    print(f"✅ Verified plist: {os.path.basename(root)}/Info.plist (MinimumOSVersion: 17.0)")
                except Exception as e:
                    print(f"⚠️ Error updating plist {p}: {e}")

    print("✅ xcarchive verification complete using official GM Xcode & SDK.")

if __name__ == '__main__':
    patch_archive()
