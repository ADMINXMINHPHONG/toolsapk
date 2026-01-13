"""
HONGHAC LAUNCHER - Android (Pydroid3)
Validate key -> Download app -> Run
"""
import os, sys, time, json, hashlib, platform, base64, zlib

print("\n" + "=" * 50)
print("   HONGHAC BUILDA - Launcher")
print("=" * 50)

# ============================================================
# CONFIG
# ============================================================
ENDPOINT = "https://firestore.googleapis.com/v1/projects/honghac-builda-keys/databases/(default)/documents/keys"
API_KEY = "AIzaSyCsR_yDVQGgeqJAp5NvLWeLkPgz0scN-Xw"

def get_data_dir():
    if platform.system() == 'Linux' and os.path.exists('/sdcard'):
        return '/sdcard/HongHac'
    return os.path.join(os.path.expanduser('~'), '.honghac_data')

DATA_DIR = get_data_dir()
KEY_FILE = os.path.join(DATA_DIR, 'saved_key.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_fp():
    return hashlib.sha256(f"{platform.node()}-{platform.system()}".encode()).hexdigest()[:16]

def fmt_time(exp):
    if exp == 0: return "Vinh vien"
    r = exp - int(time.time())
    if r <= 0: return "DA HET HAN"
    m, s = divmod(r, 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h}h {m}p {s}s"
    if m > 0: return f"{m}p {s}s"
    return f"{s}s"

def save_key(key, fp, exp):
    try:
        with open(KEY_FILE, 'w') as f:
            json.dump({'key': key, 'device_id': fp, 'expires': exp}, f)
    except: pass

def load_key():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE) as f:
                return json.load(f)
    except: pass
    return None

# ============================================================
# VALIDATE KEY
# ============================================================
def validate(key):
    import requests
    
    print(f"\n[*] Xac thuc: {key[:15]}...")
    
    try:
        r = requests.get(f"{ENDPOINT}/{key}", params={"key": API_KEY}, timeout=15)
        
        if r.status_code == 404:
            print("[X] Key khong ton tai!")
            return None
        if r.status_code != 200:
            print(f"[X] Loi: {r.status_code}")
            return None
        
        data = r.json()
        f = data.get('fields', {})
        
        exp = int(f.get('expires', {}).get('integerValue', 0))
        dev = f.get('device_id', {}).get('stringValue', None)
        first = int(f.get('first_used', {}).get('integerValue', 0))
        exp_sec = int(f.get('expires_seconds', {}).get('integerValue', 60))
        
        # Credentials for payload
        api_cred = f.get('api_credential', {}).get('stringValue', None)
        enc_key = f.get('encryption_key', {}).get('stringValue', None)
        payload_url = f.get('payload_url', {}).get('stringValue', None)
        
        if not api_cred or not enc_key or not payload_url:
            print("[X] Key chua duoc kich hoat!")
            return None
        
        fp = get_fp()
        ct = int(time.time())
        
        # Device check
        if dev and dev != fp:
            print("[X] Key da dung tren thiet bi khac!")
            return None
        
        # Activate first time
        if first == 0:
            exp = ct + exp_sec
            update = {"fields": {
                "first_used": {"integerValue": str(ct)},
                "expires": {"integerValue": str(exp)},
                "device_id": {"stringValue": fp}
            }}
            url = f"{ENDPOINT}/{key}?key={API_KEY}"
            url += "&updateMask.fieldPaths=first_used&updateMask.fieldPaths=expires&updateMask.fieldPaths=device_id"
            requests.patch(url, json=update, timeout=10)
        
        # Check expired
        if exp > 0 and ct > exp:
            print("[X] Key da het han!")
            return None
        
        save_key(key, fp, exp)
        print(f"[OK] Key hop le! Con lai: {fmt_time(exp)}")
        
        return {
            'key': key, 
            'expires': exp,
            'api_credential': api_cred,
            'encryption_key': enc_key,
            'payload_url': payload_url
        }
        
    except Exception as e:
        print(f"[X] Loi: {e}")
        return None

# ============================================================
# LOAD AND RUN APP
# ============================================================
def load_app(key_data):
    import requests
    from cryptography.fernet import Fernet
    import types
    
    print("\n[*] Tai ung dung...")
    
    try:
        # Download payload
        r = requests.get(key_data['payload_url'], params={"key": API_KEY}, timeout=30)
        if r.status_code != 200:
            print(f"[X] Tai loi: {r.status_code}")
            return False
        
        payload = r.json()
        encrypted_b64 = payload.get('fields', {}).get('code', {}).get('stringValue', '')
        
        if not encrypted_b64:
            print("[X] Payload rong!")
            return False
        
        print(f"[OK] Downloaded: {len(encrypted_b64)} chars")
        
        # Decrypt
        print("[*] Giai ma...")
        encrypted = base64.b64decode(encrypted_b64)
        cipher = Fernet(key_data['encryption_key'].encode())
        decrypted = cipher.decrypt(encrypted)
        
        # Decompress
        try:
            decrypted = zlib.decompress(decrypted)
        except:
            pass
        
        print(f"[OK] Giai ma: {len(decrypted)} bytes")
        
        # Run app
        print("\n[*] Khoi dong giao dien...")
        print("=" * 50)
        
        code_obj = compile(decrypted, '<memory>', 'exec')
        module = types.ModuleType('__app__')
        module.__file__ = '<memory>'
        
        exec(code_obj, module.__dict__)
        
        # Find and run Kivy App
        from kivy.app import App as KivyApp
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, KivyApp) and obj is not KivyApp:
                print(f"[OK] Starting {name}...")
                obj().run()
                return True
        
        print("[X] Khong tim thay app!")
        return False
        
    except ImportError as e:
        print(f"\n[X] Thieu thu vien: {e}")
        print("[!] Cai them: pip install kivy cryptography")
        return False
    except Exception as e:
        print(f"\n[X] Loi: {e}")
        return False

# ============================================================
# MAIN
# ============================================================
def main():
    try:
        import requests
    except ImportError:
        print("[X] Cai requests: pip install requests")
        return
    
    # Check saved key
    saved = load_key()
    key = None
    
    if saved:
        skey = saved.get('key', '')
        sdev = saved.get('device_id', '')
        sexp = saved.get('expires', 0)
        
        if skey and sdev == get_fp():
            if sexp == 0 or int(time.time()) <= sexp:
                print(f"\n[*] Key da luu: {skey[:15]}...")
                print(f"    Con lai: {fmt_time(sexp)}")
                key = skey
    
    # Input if no saved key
    if not key:
        print("\n[?] Nhap key:")
        try:
            key = input("> ").strip()
        except EOFError:
            print("[!] Chay tu Terminal de nhap key")
            return
    
    if not key:
        print("[X] Key trong!")
        return
    
    # Validate
    result = validate(key)
    
    if result:
        # Load and run app
        success = load_app(result)
        
        if not success:
            print("\n" + "=" * 50)
            print("   KEY HOP LE - NHUNG APP LOI")
            print("=" * 50)
            print(f"\nKey: {result['key']}")
            print(f"Con lai: {fmt_time(result['expires'])}")
            print("\n[!] Pydroid3 co the khong ho tro Kivy GUI")
            print("    Thu chay lai hoac build APK")

if __name__ == '__main__':
    main()
