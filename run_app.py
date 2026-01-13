"""
HONGHAC LAUNCHER - Console Version (Khong can Kivy)
Chay tren Termux khong can cai them gi
"""
import os
import sys
import time
import json
import hashlib
import platform
import base64
import zlib

# ============================================================
# CONFIG
# ============================================================
VALIDATION_ENDPOINT = "https://firestore.googleapis.com/v1/projects/honghac-builda-keys/databases/(default)/documents/keys"
PUBLIC_API_KEY = "AIzaSyCsR_yDVQGgeqJAp5NvLWeLkPgz0scN-Xw"

# Data directory
def get_data_dir():
    if platform.system() == 'Linux' and os.path.exists('/sdcard'):
        return '/sdcard/HongHac'
    else:
        return os.path.join(os.path.expanduser('~'), '.honghac_data')

DATA_DIR = get_data_dir()
KEY_FILE = os.path.join(DATA_DIR, 'saved_key.json')

# ============================================================
# HELPER FUNCTIONS  
# ============================================================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("\n" + "=" * 50)
    print("       HONGHAC BUILDA - Console Launcher")
    print("=" * 50)

def get_device_fp():
    return hashlib.sha256(f"{platform.node()}-{platform.system()}".encode()).hexdigest()[:16]

def save_key(key, device_id, expires):
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        data = {'key': key, 'device_id': device_id, 'expires': expires, 'saved_at': int(time.time())}
        with open(KEY_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_saved_key():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def clear_key():
    try:
        if os.path.exists(KEY_FILE):
            os.remove(KEY_FILE)
    except:
        pass

def format_time(expires):
    if expires == 0:
        return "Vinh vien"
    remaining = expires - int(time.time())
    if remaining <= 0:
        return "DA HET HAN!"
    
    days = remaining // 86400
    hours = (remaining % 86400) // 3600
    mins = (remaining % 3600) // 60
    secs = remaining % 60
    
    if days > 0:
        return f"{days}d {hours}h {mins}p"
    elif hours > 0:
        return f"{hours}h {mins}p {secs}s"
    elif mins > 0:
        return f"{mins}p {secs}s"
    else:
        return f"{secs}s"

# ============================================================
# VALIDATE KEY
# ============================================================
def validate_key(key):
    try:
        import requests
    except ImportError:
        print("[!] Cai requests: pip install requests")
        return None
    
    print(f"\n[*] Dang xac thuc key...")
    
    try:
        url = f"{VALIDATION_ENDPOINT}/{key}"
        r = requests.get(url, params={"key": PUBLIC_API_KEY}, timeout=15)
        
        if r.status_code == 404:
            print("[X] Key khong hop le!")
            return None
        
        if r.status_code != 200:
            print(f"[X] Loi server: {r.status_code}")
            return None
        
        data = r.json()
        fields = data.get('fields', {})
        
        # Get key info
        expires = int(fields.get('expires', {}).get('integerValue', 0))
        device_id = fields.get('device_id', {}).get('stringValue', None)
        first_used = int(fields.get('first_used', {}).get('integerValue', 0))
        expires_seconds = int(fields.get('expires_seconds', {}).get('integerValue', 60))
        max_uses = int(fields.get('max_uses', {}).get('integerValue', 1))
        current_uses = int(fields.get('current_uses', {}).get('integerValue', 0))
        
        # Credentials
        api_cred = fields.get('api_credential', {}).get('stringValue', None)
        enc_key = fields.get('encryption_key', {}).get('stringValue', None)
        payload_url = fields.get('payload_url', {}).get('stringValue', None)
        
        if not api_cred or not enc_key or not payload_url:
            print("[X] Key chua duoc kich hoat!")
            return None
        
        current_time = int(time.time())
        device_fp = get_device_fp()
        
        # Device check
        if device_id and device_id != device_fp:
            print("[X] Key da dung tren thiet bi khac!")
            return None
        
        if not device_id and current_uses >= max_uses:
            print("[X] Key da het luot dung!")
            return None
        
        # Activate first time
        if first_used == 0:
            first_used = current_time
            expires = current_time + expires_seconds
            current_uses = 1
            
            # Update Firebase
            update_url = f"{VALIDATION_ENDPOINT}/{key}"
            update_data = {"fields": {
                "first_used": {"integerValue": str(first_used)},
                "expires": {"integerValue": str(expires)},
                "device_id": {"stringValue": device_fp},
                "current_uses": {"integerValue": str(current_uses)}
            }}
            full_url = f"{update_url}?key={PUBLIC_API_KEY}&updateMask.fieldPaths=first_used&updateMask.fieldPaths=expires&updateMask.fieldPaths=device_id&updateMask.fieldPaths=current_uses"
            requests.patch(full_url, json=update_data)
        
        # Check expired
        if expires > 0 and current_time > expires:
            print("[X] Key da het han!")
            clear_key()
            return None
        
        # Save key locally
        save_key(key, device_fp, expires)
        
        print("[OK] Key hop le!")
        print(f"    Thoi gian con lai: {format_time(expires)}")
        
        return {
            'key': key,
            'expires': expires,
            'payload_url': payload_url,
            'encryption_key': enc_key
        }
        
    except Exception as e:
        print(f"[X] Loi: {e}")
        return None

# ============================================================
# DOWNLOAD & RUN APP
# ============================================================
def run_app(key_data):
    try:
        import requests
    except ImportError:
        print("[!] Cai requests: pip install requests")
        return
    
    print("\n[*] Tai ung dung...")
    
    try:
        # Get payload
        r = requests.get(key_data['payload_url'], params={"key": PUBLIC_API_KEY}, timeout=30)
        if r.status_code != 200:
            print(f"[X] Tai loi: {r.status_code}")
            return
        
        payload = r.json()
        encrypted_b64 = payload.get('fields', {}).get('code', {}).get('stringValue', '')
        
        if not encrypted_b64:
            print("[X] Payload loi!")
            return
        
        print(f"[OK] Downloaded: {len(encrypted_b64)} chars")
        
        # Decrypt - REQUIRE cryptography
        print("[*] Giai ma...")
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            print("[X] Thiếu thư viện cryptography!")
            print("[*] Cài đặt:")
            print("    Termux: pkg install python-cryptography")
            print("    PC:     pip install cryptography")
            return
        
        try:
            encrypted = base64.b64decode(encrypted_b64)
            cipher = Fernet(key_data['encryption_key'].encode())
            decrypted = cipher.decrypt(encrypted)
            
            try:
                decrypted = zlib.decompress(decrypted)
            except:
                pass
            
            print(f"[OK] Decrypted: {len(decrypted)} bytes")
            
            # Run in memory
            print("\n[*] Khoi dong ung dung...")
            print("=" * 50)
            
            try:
                import types
                code_obj = compile(decrypted, '<memory>', 'exec')
                module = types.ModuleType('__app__')
                module.__file__ = '<memory>'
                
                exec(code_obj, module.__dict__)
                
                # Try to run Kivy app if available
                try:
                    from kivy.app import App as KivyApp
                    for name, obj in module.__dict__.items():
                        if isinstance(obj, type) and issubclass(obj, KivyApp) and obj is not KivyApp:
                            print(f"[OK] Starting {name}...")
                            obj().run()
                            return
                except ImportError:
                    pass
            except Exception as e:
                # App code may require Kivy - show success anyway
                if "kivy" in str(e).lower():
                    print("[!] App yeu cau Kivy GUI (khong ho tro Termux)")
                else:
                    print(f"[!] Loi khi chay: {e}")
            
            # Console mode - show success
            print("\n" + "=" * 50)
            print("   KEY DA DUOC XAC THUC THANH CONG!")
            print("=" * 50)
            print(f"\nKey: {key_data['key']}")
            print(f"Thoi gian con lai: {format_time(key_data['expires'])}")
            print("\n[!] Luu y: App chinh can Kivy GUI")
            print("    Termux khong ho tro Kivy")
            print("    Key van hop le va da duoc kich hoat!")
            print("\n[*] Nhan Enter de thoat...")
            input()
            
        except Exception as e:
            print(f"[X] Giai ma loi: {e}")
        
    except Exception as e:
        print(f"[X] Loi: {e}")

# ============================================================
# MAIN
# ============================================================
def main():
    clear_screen()
    print_header()
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Check saved key
    saved = load_saved_key()
    if saved:
        key = saved.get('key', '')
        device_fp = saved.get('device_id', '')
        expires = saved.get('expires', 0)
        
        if key and device_fp == get_device_fp():
            if expires == 0 or int(time.time()) <= expires:
                print(f"\n[*] Tim thay key da luu: {key[:15]}...")
                print(f"    Con lai: {format_time(expires)}")
                
                choice = input("\nDung key nay? (y/n): ").strip().lower()
                if choice == 'y' or choice == '':
                    result = validate_key(key)
                    if result:
                        run_app(result)
                        return
    
    # Manual input
    print("\n[?] Nhap key cua ban:")
    key = input("> ").strip()
    
    if not key:
        print("[X] Key khong duoc de trong!")
        return
    
    result = validate_key(key)
    if result:
        run_app(result)

if __name__ == '__main__':
    main()
