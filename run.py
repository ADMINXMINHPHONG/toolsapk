"""
HONGHAC LOADER - Chay 1 lenh duy nhat
Tai background, tai launcher tu raw, giai ma va chay trong RAM
"""
import os
import sys
import platform

# ============================================================
# CONFIG - URL cua cac file tren GitHub raw
# ============================================================
BACKGROUND_URL = "https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/background.png"
LAUNCHER_BIN_URL = "https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher.bin"

# Key giai ma (phai khop voi key trong build_bin.py)
DECRYPT_KEY = b'MLvJZqbjCrNda86NCyw40yKfroWLC3gb0SFTd470oXk='

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
# MAIN LOADER
# ============================================================
def main():
    print("\n" + "=" * 50)
    print("     HONGHAC BUILDA - LOADER")
    print("=" * 50)
    
    # Tao thu muc data
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Import cac thu vien can thiet
    try:
        import requests
        from cryptography.fernet import Fernet
        import zlib
        import types
    except ImportError as e:
        print(f"\n[!] Thieu thu vien: {e}")
        print("[*] Cai dat: pip install requests cryptography")
        sys.exit(1)
    
    # 1. Tai background
    print("\n[1] Tai background...")
    try:
        if not os.path.exists(BG_FILE):
            r = requests.get(BACKGROUND_URL, timeout=30)
            if r.status_code == 200:
                with open(BG_FILE, 'wb') as f:
                    f.write(r.content)
                print(f"    [OK] Saved to {BG_FILE}")
            else:
                print(f"    [!] Loi tai: {r.status_code}")
        else:
            print(f"    [OK] Da co san: {BG_FILE}")
    except Exception as e:
        print(f"    [!] Loi: {e}")
    
    # 2. Tai launcher.bin
    print("\n[2] Tai launcher...")
    try:
        r = requests.get(LAUNCHER_BIN_URL, timeout=60)
        if r.status_code != 200:
            print(f"    [X] Loi tai: {r.status_code}")
            sys.exit(1)
        encrypted_data = r.content
        print(f"    [OK] Downloaded: {len(encrypted_data)} bytes")
    except Exception as e:
        print(f"    [X] Loi: {e}")
        sys.exit(1)
    
    # 3. Giai ma
    print("\n[3] Giai ma...")
    try:
        cipher = Fernet(DECRYPT_KEY)
        decrypted = cipher.decrypt(encrypted_data)
        print(f"    [OK] Decrypted: {len(decrypted)} bytes")
    except Exception as e:
        print(f"    [X] Giai ma loi: {e}")
        sys.exit(1)
    
    # 4. Giai nen
    print("\n[4] Giai nen...")
    try:
        decompressed = zlib.decompress(decrypted)
        print(f"    [OK] Decompressed: {len(decompressed)} bytes")
    except:
        decompressed = decrypted
        print(f"    [OK] No compression")
    
    # 5. Inject background path
    print("\n[5] Cau hinh background...")
    code_str = decompressed.decode('utf-8')
    
    # Inject background path vao code
    bg_inject = f'''
# === INJECTED BACKGROUND CONFIG ===
import os
BACKGROUND_IMAGE = "{BG_FILE.replace(chr(92), '/')}"
os.environ['HONGHAC_BACKGROUND'] = BACKGROUND_IMAGE
# === END INJECT ===

'''
    code_str = bg_inject + code_str
    
    # 6. Chay trong RAM
    print("\n[6] Khoi dong app...")
    print("=" * 50)
    
    try:
        code_obj = compile(code_str, '<memory>', 'exec')
        module = types.ModuleType('__launcher__')
        module.__file__ = '<memory>'
        
        # Execute
        exec(code_obj, module.__dict__)
        
        # Chay Kivy App
        from kivy.app import App as KivyApp
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, KivyApp) and obj is not KivyApp:
                print(f"\n[OK] Starting {name}...")
                obj().run()
                break
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[X] Loi: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
