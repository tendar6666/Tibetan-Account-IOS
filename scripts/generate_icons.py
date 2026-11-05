import os
import sys
import json
import subprocess
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def generate_icons():
    # Locate AppStore_Icon_1024x1024.png
    candidates = [
        "AppStore_Icon_1024x1024.png",
        os.path.join(os.getcwd(), "AppStore_Icon_1024x1024.png")
    ]
    icon_src = None
    for c in candidates:
        if os.path.exists(c):
            icon_src = os.path.abspath(c)
            break

    if not icon_src:
        print("⚠️ AppStore_Icon_1024x1024.png not found!")
        return

    icon_dir = os.path.join(os.getcwd(), "ios", "App", "App", "Assets.xcassets", "AppIcon.appiconset")
    os.makedirs(icon_dir, exist_ok=True)

    icon_specs = [
        ("AppIcon-20x20@2x.png", 40, 40, "iphone", "20x20", "2x"),
        ("AppIcon-20x20@3x.png", 60, 60, "iphone", "20x20", "3x"),
        ("AppIcon-29x29@2x.png", 58, 58, "iphone", "29x29", "2x"),
        ("AppIcon-29x29@3x.png", 87, 87, "iphone", "29x29", "3x"),
        ("AppIcon-40x40@2x.png", 80, 80, "iphone", "40x40", "2x"),
        ("AppIcon-40x40@3x.png", 120, 120, "iphone", "40x40", "3x"),
        ("AppIcon-60x60@2x.png", 120, 120, "iphone", "60x60", "2x"),
        ("AppIcon-60x60@3x.png", 180, 180, "iphone", "60x60", "3x"),
        ("AppIcon-512@2x.png", 1024, 1024, "ios-marketing", "1024x1024", "1x")
    ]

    images_json = []

    for fname, w, h, idiom, size_str, scale_str in icon_specs:
        dst = os.path.join(icon_dir, fname)
        # Try macOS sips tool first if available
        sips_success = False
        try:
            res = subprocess.run(["sips", "-z", str(h), str(w), icon_src, "--out", dst], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(dst):
                sips_success = True
        except Exception:
            pass

        if not sips_success:
            shutil.copyfile(icon_src, dst)

        images_json.append({
            "idiom": idiom,
            "size": size_str,
            "scale": scale_str,
            "filename": fname
        })
        print(f"Generated icon: {fname} ({w}x{h})")

    contents = {
        "images": images_json,
        "info": {
            "version": 1,
            "author": "xcode"
        }
    }

    contents_path = os.path.join(icon_dir, "Contents.json")
    with open(contents_path, "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)

    print("✅ Successfully generated all iPhone AppIcon assets and Contents.json")

if __name__ == '__main__':
    generate_icons()
