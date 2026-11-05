import os
import re

def find_podfile():
    candidates = [
        "ios/App/Podfile",
        "Podfile",
        os.path.join(os.getcwd(), "ios", "App", "Podfile"),
        os.path.join(os.getcwd(), "Podfile")
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None

def patch_podfile():
    podfile_path = find_podfile()
    if not podfile_path:
        print("⚠️ Podfile not found. Skipping Podfile patch.")
        return

    with open(podfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update platform to 17.0
    content = re.sub(r"platform :ios, ['\"][^'\"]+['\"]", "platform :ios, '17.0'", content)

    # Configure pods targets for iOS 17.0 and disable codesigning for pods
    replacement = """assertDeploymentTarget(installer)
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '17.0'
      config.build_settings['CODE_SIGNING_ALLOWED'] = 'NO'
      config.build_settings['CODE_SIGNING_REQUIRED'] = 'NO'
      config.build_settings['CODE_SIGN_IDENTITY'] = ''
      config.build_settings['EXPANDED_CODE_SIGN_IDENTITY'] = ''
    end
  end"""

    if "assertDeploymentTarget(installer)" in content:
        content = content.replace("assertDeploymentTarget(installer)", replacement)

    with open(podfile_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Successfully configured Podfile for iOS 17.0")

if __name__ == '__main__':
    patch_podfile()
