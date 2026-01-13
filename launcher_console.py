"""
HONGHAC - Simple Key Validator (No Kivy Required)
Chay tren Pydroid3 / Termux
"""
import os, sys, time, json, hashlib, platform, base64, zlib

print("\n" + "=" * 50)
print("   HONGHAC BUILDA - Key Validator")
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
    d, r = divmod(r, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    if d > 0: return f"{d}d {h}h {m}p"
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
    try:
        import requests
    except ImportError:
        print("[X] Cai requests: pip install requests")
        return None
    
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
        max_uses = int(f.get('max_uses', {}).get('integerValue', 1))
        current = int(f.get('current_uses', {}).get('integerValue', 0))
        
        # Check credentials
        api_cred = f.get('api_credential', {}).get('stringValue', None)
        if not api_cred:
            print("[X] Key chua duoc kich hoat!")
            return None
        
        fp = get_fp()
        ct = int(time.time())
        
        # Device check
        if dev and dev != fp:
            print("[X] Key da dung tren thiet bi khac!")
            return None
        
        if not dev and current >= max_uses:
            print("[X] Key da het luot dung!")
            return None
        
        # Activate first time
        if first == 0:
            exp = ct + exp_sec
            update = {"fields": {
                "first_used": {"integerValue": str(ct)},
                "expires": {"integerValue": str(exp)},
                "device_id": {"stringValue": fp},
                "current_uses": {"integerValue": str(current + 1)}
            }}
            url = f"{ENDPOINT}/{key}?key={API_KEY}"
            url += "&updateMask.fieldPaths=first_used&updateMask.fieldPaths=expires"
            url += "&updateMask.fieldPaths=device_id&updateMask.fieldPaths=current_uses"
            requests.patch(url, json=update, timeout=10)
            print("[OK] Key da duoc kich hoat!")
        
        # Check expired
        if exp > 0 and ct > exp:
            print("[X] Key da het han!")
            return None
        
        # Save locally
        save_key(key, fp, exp)
        
        return {'key': key, 'expires': exp}
        
    except Exception as e:
        print(f"[X] Loi: {e}")
        return None

# ============================================================
# MAIN
# ============================================================
def main():
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
            # Pydroid3 Editor mode - hardcode test or exit
            print("\n[!] Khong the nhap tu Editor")
            print("    Chay tu Terminal hoac dung key da luu")
            return
    
    if not key:
        print("[X] Key trong!")
        return
    
    # Validate
    result = validate(key)
    
    if result:
        print("\n" + "=" * 50)
        print("   KEY HOP LE - DA XAC THUC!")
        print("=" * 50)
        print(f"\nKey: {result['key']}")
        print(f"Con lai: {fmt_time(result['expires'])}")
        print("\n[!] Luu y: App chinh can Kivy GUI")
        print("    Pydroid3/Termux chi xac thuc key")
        print("    Chay app day du tren PC hoac APK")
        print("=" * 50)
    else:
        print("\n[X] Xac thuc that bai!")

if __name__ == '__main__':
    main()
