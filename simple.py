"""
HONGHAC - Console Only (No Kivy)
Chay tren Pydroid3
"""
import os, sys, time, json, hashlib, platform, base64, zlib

# Config
ENDPOINT = "https://firestore.googleapis.com/v1/projects/honghac-builda-keys/databases/(default)/documents/keys"
API_KEY = "AIzaSyCsR_yDVQGgeqJAp5NvLWeLkPgz0scN-Xw"
DATA_DIR = os.path.join(os.path.expanduser('~'), '.honghac_data')
KEY_FILE = os.path.join(DATA_DIR, 'key.json')

def get_fp():
    return hashlib.sha256(f"{platform.node()}-{platform.system()}".encode()).hexdigest()[:16]

def fmt_time(exp):
    if exp == 0: return "Vinh vien"
    r = exp - int(time.time())
    if r <= 0: return "HET HAN"
    m, s = divmod(r, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}p {s}s" if h else f"{m}p {s}s"

print("\n" + "=" * 50)
print("   HONGHAC - Console Mode")
print("=" * 50)

# Input key
key = input("\nNhap key: ").strip()
if not key:
    print("[X] Key trong!")
    sys.exit(1)

print("\n[*] Xac thuc...")

try:
    import requests
    
    # Validate
    r = requests.get(f"{ENDPOINT}/{key}", params={"key": API_KEY}, timeout=15)
    if r.status_code != 200:
        print(f"[X] Loi: {r.status_code}")
        sys.exit(1)
    
    data = r.json()
    f = data.get('fields', {})
    
    exp = int(f.get('expires', {}).get('integerValue', 0))
    dev = f.get('device_id', {}).get('stringValue', None)
    first = int(f.get('first_used', {}).get('integerValue', 0))
    exp_sec = int(f.get('expires_seconds', {}).get('integerValue', 60))
    
    fp = get_fp()
    ct = int(time.time())
    
    # Check device
    if dev and dev != fp:
        print("[X] Key da dung tren thiet bi khac!")
        sys.exit(1)
    
    # Activate
    if first == 0:
        exp = ct + exp_sec
        update = {"fields": {
            "first_used": {"integerValue": str(ct)},
            "expires": {"integerValue": str(exp)},
            "device_id": {"stringValue": fp}
        }}
        requests.patch(f"{ENDPOINT}/{key}?key={API_KEY}&updateMask.fieldPaths=first_used&updateMask.fieldPaths=expires&updateMask.fieldPaths=device_id", json=update)
    
    # Check expired
    if exp > 0 and ct > exp:
        print("[X] Key da het han!")
        sys.exit(1)
    
    print("[OK] Key hop le!")
    print(f"    Con lai: {fmt_time(exp)}")
    
    print("\n" + "=" * 50)
    print("   KEY DA DUOC XAC THUC!")
    print("=" * 50)
    print(f"\nKey: {key}")
    print(f"Thoi gian: {fmt_time(exp)}")
    print("\n[!] App chinh can Kivy GUI")
    print("    Pydroid3 khong ho tro Kivy")
    print("    Key van hop le!")
    
except ImportError:
    print("[X] Cai requests: Menu > Pip > requests")
except Exception as e:
    print(f"[X] Loi: {e}")

input("\nNhan Enter...")
