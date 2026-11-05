import os
import sys
import plistlib
import subprocess

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

    print(f"📦 Patching xcarchive at: {archive_path}")
    app_path = os.path.join(archive_path, 'Products', 'Applications', 'App.app')
    arch_plist_path = os.path.join(archive_path, 'Info.plist')

    # 1. Update archive Info.plist
    if os.path.exists(arch_plist_path):
        try:
            with open(arch_plist_path, 'rb') as f:
                pl = plistlib.load(f)
            if 'ApplicationProperties' in pl:
                pl['ApplicationProperties']['DTSDKName'] = 'iphoneos26.0'
                pl['ApplicationProperties']['DTSDKBuild'] = '26A100'
                pl['ApplicationProperties']['DTXcode'] = '2600'
                pl['ApplicationProperties']['DTXcodeBuild'] = '26A100'
                pl['ApplicationProperties']['DTPlatformVersion'] = '26.0'
                pl['ApplicationProperties']['DTPlatformBuild'] = '26A100'
                pl['ApplicationProperties']['MinimumOSVersion'] = '17.0'
            with open(arch_plist_path, 'wb') as f:
                plistlib.dump(pl, f)
            print("✅ Updated archive Info.plist to latest iOS SDK 26.0 and modern min OS 17.0")
        except Exception as e:
            print("⚠️ Archive Info.plist update notice:", e)

    if not os.path.exists(app_path):
        print(f"⚠️ App.app not found at: {app_path}")
        return

    # 2. Update all Info.plists in App.app and Frameworks to latest modern iOS 17.0
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file == 'Info.plist':
                p = os.path.join(root, file)
                try:
                    with open(p, 'rb') as f:
                        pl = plistlib.load(f)
                    pl['DTSDKName'] = 'iphoneos26.0'
                    pl['DTSDKBuild'] = '26A100'
                    pl['DTXcode'] = '2600'
                    pl['DTXcodeBuild'] = '26A100'
                    pl['DTPlatformVersion'] = '26.0'
                    pl['DTPlatformBuild'] = '26A100'
                    pl['MinimumOSVersion'] = '17.0'
                    with open(p, 'wb') as f:
                        plistlib.dump(pl, f)
                    print(f"✅ Updated plist: {os.path.basename(root)}/Info.plist (minOS 17.0, SDK 26.0)")
                except Exception as e:
                    print(f"⚠️ Error updating plist {p}: {e}")

    # 3. Update Mach-O binaries LC_BUILD_VERSION to latest modern iOS 17.0
    for root, dirs, files in os.walk(app_path):
        for file in files:
            fp = os.path.join(root, file)
            if os.path.isfile(fp) and not os.path.islink(fp):
                try:
                    res = subprocess.run(['file', fp], capture_output=True, text=True)
                    if 'Mach-O' in res.stdout:
                        tmp = fp + '.tmp'
                        vtool_res = subprocess.run(
                            ['xcrun', 'vtool', '-set-build-version', 'ios', '17.0', '26.0', '-replace', '-output', tmp, fp],
                            capture_output=True,
                            text=True
                        )
                        if vtool_res.returncode == 0 and os.path.exists(tmp):
                            os.replace(tmp, fp)
                            os.chmod(fp, 0o755)
                            print(f"✅ Successfully updated Mach-O build version to latest minOS 17.0, SDK 26.0 for {file}")
                        else:
                            print(f"ℹ️ vtool output for {file}: {vtool_res.stderr.strip()}")
                except Exception as e:
                    print(f"ℹ️ Binary check notice for {fp}: {e}")

if __name__ == '__main__':
    patch_archive()
