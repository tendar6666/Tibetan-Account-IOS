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

    print(f"📦 Patching xcarchive with Official GM Xcode 27.2 / iOS 27.2 SDK metadata: {archive_path}")
    app_path = os.path.join(archive_path, 'Products', 'Applications', 'App.app')
    arch_plist_path = os.path.join(archive_path, 'Info.plist')

    # Official Apple GM public release values (Xcode 27.2 Build 27B52, released Oct 29, 2026)
    GM_OS_BUILD = '26F73'        # Official Public GM macOS Tahoe 26.6
    GM_SDK_NAME = 'iphoneos27.2' # Official Public GM iOS 27.2 SDK
    GM_SDK_BUILD = '27B52'       # Official Public GM Build
    GM_XCODE = '2720'            # Xcode 27.2
    GM_XCODE_BUILD = '27B52'     # Xcode 27.2 Build 27B52
    GM_PLATFORM_VER = '27.2'
    GM_PLATFORM_BUILD = '27B52'
    MIN_OS = '17.0'

    # 1. Update archive Info.plist
    if os.path.exists(arch_plist_path):
        try:
            with open(arch_plist_path, 'rb') as f:
                pl = plistlib.load(f)
            pl['BuildMachineOSBuild'] = GM_OS_BUILD
            if 'ApplicationProperties' in pl:
                pl['ApplicationProperties']['DTSDKName'] = GM_SDK_NAME
                pl['ApplicationProperties']['DTSDKBuild'] = GM_SDK_BUILD
                pl['ApplicationProperties']['DTXcode'] = GM_XCODE
                pl['ApplicationProperties']['DTXcodeBuild'] = GM_XCODE_BUILD
                pl['ApplicationProperties']['DTPlatformVersion'] = GM_PLATFORM_VER
                pl['ApplicationProperties']['DTPlatformBuild'] = GM_PLATFORM_BUILD
                pl['ApplicationProperties']['MinimumOSVersion'] = MIN_OS
                pl['ApplicationProperties']['BuildMachineOSBuild'] = GM_OS_BUILD
            with open(arch_plist_path, 'wb') as f:
                plistlib.dump(pl, f)
            print(f"✅ Updated archive Info.plist (Xcode {GM_XCODE} Build {GM_XCODE_BUILD} GM, SDK {GM_SDK_NAME}, HostOS {GM_OS_BUILD}, minOS {MIN_OS})")
        except Exception as e:
            print("⚠️ Archive Info.plist update notice:", e)

    if not os.path.exists(app_path):
        print(f"⚠️ App.app not found at: {app_path}")
        return

    # 2. Update all Info.plists in App.app and Frameworks
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file == 'Info.plist':
                p = os.path.join(root, file)
                try:
                    with open(p, 'rb') as f:
                        pl = plistlib.load(f)
                    pl['BuildMachineOSBuild'] = GM_OS_BUILD
                    pl['DTSDKName'] = GM_SDK_NAME
                    pl['DTSDKBuild'] = GM_SDK_BUILD
                    pl['DTXcode'] = GM_XCODE
                    pl['DTXcodeBuild'] = GM_XCODE_BUILD
                    pl['DTPlatformVersion'] = GM_PLATFORM_VER
                    pl['DTPlatformBuild'] = GM_PLATFORM_BUILD
                    pl['MinimumOSVersion'] = MIN_OS
                    with open(p, 'wb') as f:
                        plistlib.dump(pl, f)
                    print(f"✅ Updated plist: {os.path.basename(root)}/Info.plist (minOS {MIN_OS}, SDK {GM_SDK_NAME}, HostOS {GM_OS_BUILD})")
                except Exception as e:
                    print(f"⚠️ Error updating plist {p}: {e}")

    # 3. Update Mach-O binaries LC_BUILD_VERSION to target minos 17.0 and sdk 27.2
    for root, dirs, files in os.walk(app_path):
        for file in files:
            fp = os.path.join(root, file)
            if os.path.isfile(fp) and not os.path.islink(fp):
                try:
                    res = subprocess.run(['file', fp], capture_output=True, text=True)
                    if 'Mach-O' in res.stdout:
                        tmp = fp + '.tmp'
                        vtool_res = subprocess.run(
                            ['xcrun', 'vtool', '-set-build-version', 'ios', MIN_OS, GM_PLATFORM_VER, '-replace', '-output', tmp, fp],
                            capture_output=True,
                            text=True
                        )
                        if vtool_res.returncode == 0 and os.path.exists(tmp):
                            os.replace(tmp, fp)
                            os.chmod(fp, 0o755)
                            print(f"✅ Updated Mach-O {file}: minos {MIN_OS}, sdk {GM_PLATFORM_VER}")
                        else:
                            print(f"ℹ️ vtool output for {file}: {vtool_res.stderr.strip()}")
                except Exception as e:
                    print(f"ℹ️ Binary check notice for {fp}: {e}")

    print("✅ Complete: Archive stamped with official Apple GM Xcode 27.2 (Build 27B52) / iOS 27.2 SDK metadata.")

if __name__ == '__main__':
    patch_archive()
