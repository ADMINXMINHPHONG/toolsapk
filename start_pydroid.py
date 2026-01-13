"""
HONGHAC LAUNCHER - Start File for Pydroid3
Mo file nay trong Pydroid3 va nhan Run
"""

print("=" * 50)
print("   HONGHAC BUILDA - LAUNCHER")
print("=" * 50)
print("\n[*] Dang tai launcher...")

try:
    import requests
    
    # Download and execute launcher
    url = "https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher_console.py"
    code = requests.get(url, timeout=30).text
    
    print("[OK] Da tai xong!")
    print("=" * 50)
    print()
    
    exec(code)
    
except ImportError:
    print("\n[X] Thiếu thư viện: requests")
    print("\n[*] Cách cài:")
    print("    1. Mở Pydroid3")
    print("    2. Menu → Pip")
    print("    3. Tìm: requests")
    print("    4. Nhấn Install")
    print("\n    Sau đó chạy lại file này!")
    input("\nNhấn Enter để thoát...")
    
except Exception as e:
    print(f"\n[X] Lỗi: {e}")
    input("\nNhấn Enter để thoát...")
