import os
import re
import sys

def find_pbx():
    candidates = [
        'ios/App/App.xcodeproj/project.pbxproj',
        'App.xcodeproj/project.pbxproj',
        os.path.join(os.getcwd(), 'ios', 'App', 'App.xcodeproj', 'project.pbxproj'),
        os.path.join(os.getcwd(), 'App.xcodeproj', 'project.pbxproj')
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None

def configure_xcode():
    team_id = os.environ.get('APPLE_TEAM_ID', '')
    pbx_path = find_pbx()

    if not pbx_path:
        print("⚠️ project.pbxproj not found. Skipping Xcode configuration.")
        return

    with open(pbx_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update IPHONEOS_DEPLOYMENT_TARGET to 17.0
    content = re.sub(r'IPHONEOS_DEPLOYMENT_TARGET = [^;]+;', 'IPHONEOS_DEPLOYMENT_TARGET = 17.0;', content)

    # Set TARGETED_DEVICE_FAMILY to 1 (iPhone only) so Apple does NOT require iPad screenshots
    content = re.sub(r'TARGETED_DEVICE_FAMILY = [^;]+;', 'TARGETED_DEVICE_FAMILY = "1";', content)

    # Inject Apple Developer Team ID if provided
    if team_id:
        print(f"Configuring Apple Developer Team ID: {team_id}")
        content = re.sub(r'DevelopmentTeam = "";', f'DevelopmentTeam = "{team_id}";', content)
        content = re.sub(r'PRODUCT_BUNDLE_IDENTIFIER = ([^;]+);', rf'PRODUCT_BUNDLE_IDENTIFIER = \1;\n\t\t\t\tDEVELOPMENT_TEAM = {team_id};', content)

    with open(pbx_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Successfully configured project.pbxproj for iOS 17.0 and Apple Team ID")

if __name__ == '__main__':
    configure_xcode()
