"""
HONGHAC LOADER - Khong can cryptography
Tai ve va chay truc tiep tren Android
"""
import os
import sys
import platform
import base64
import zlib

# ============================================================
# CONFIG
# ============================================================
BACKGROUND_URL = "https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/background.png"
LAUNCHER_URL = "https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher_b64.txt"

# ============================================================
# DATA DIRECTORY
# ============================================================
def get_data_dir():
    if platform.system() == 'Linux' and os.path.exists('/sdcard'):
        return '/sdcard/HongHac'
    else:
        return os.path.join(os.path.expanduser('~'), '.honghac_data')

DATA_DIR = get_data_dir()
BG_FILE = os.path.join(DATA_DIR, 'background.png')

# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "=" * 50)
    print("     HONGHAC BUILDA - LOADER (Simple)")
    print("=" * 50)
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    try:
        import requests
    except ImportError:
        print("[!] Can cai: pip install requests")
        sys.exit(1)
    
    # 1. Tai background
    print("\n[1] Tai background...")
    try:
        if not os.path.exists(BG_FILE):
            r = requests.get(BACKGROUND_URL, timeout=30)
            if r.status_code == 200:
                with open(BG_FILE, 'wb') as f:
                    f.write(r.content)
                print(f"    [OK] Saved: {BG_FILE}")
        else:
            print(f"    [OK] Da co: {BG_FILE}")
    except Exception as e:
        print(f"    [!] Loi: {e}")
    
    # 2. Tai launcher code
    print("\n[2] Tai launcher...")
    try:
        r = requests.get(LAUNCHER_URL, timeout=60)
        if r.status_code != 200:
            print(f"    [X] Loi: {r.status_code}")
            sys.exit(1)
        encoded_data = r.text.strip()
        print(f"    [OK] Downloaded: {len(encoded_data)} chars")
    except Exception as e:
        print(f"    [X] Loi: {e}")
        sys.exit(1)
    
    # 3. Giai ma base64
    print("\n[3] Giai ma...")
    try:
        decoded = base64.b64decode(encoded_data)
        print(f"    [OK] Decoded: {len(decoded)} bytes")
    except Exception as e:
        print(f"    [X] Giai ma loi: {e}")
        sys.exit(1)
    
    # 4. Giai nen
    print("\n[4] Giai nen...")
    try:
        decompressed = zlib.decompress(decoded)
        print(f"    [OK] Decompressed: {len(decompressed)} bytes")
    except:
        decompressed = decoded
        print(f"    [OK] No compression")
    
    # 5. Inject background
    print("\n[5] Cau hinh...")
    code_str = decompressed.decode('utf-8')
    
    bg_inject = f'''
import os
BACKGROUND_IMAGE = "{BG_FILE.replace(chr(92), '/')}"
os.environ['HONGHAC_BACKGROUND'] = BACKGROUND_IMAGE
'''
    code_str = bg_inject + code_str
    
    # 6. Chay
    print("\n[6] Khoi dong...")
    print("=" * 50)
    
    try:
        import types
        code_obj = compile(code_str, '<memory>', 'exec')
        module = types.ModuleType('__launcher__')
        module.__file__ = '<memory>'
        
        exec(code_obj, module.__dict__)
        
        from kivy.app import App as KivyApp
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, KivyApp) and obj is not KivyApp:
                print(f"[OK] Starting {name}...")
                obj().run()
                break
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[X] Loi: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
