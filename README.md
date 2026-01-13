# HONGHAC - FILES ORGANIZATION

## 📁 userreal/ (Upload lên GitHub)
Files này user sẽ tải về và chạy:

| File | Mô tả |
|------|-------|
| `launcher_console.py` | Launcher chạy trên Termux (console mode, không cần Kivy) |

---

## ☁️ Firebase Firestore

### Collection: `keys`
- Chứa các key do admin tạo
- Mỗi key có: `api_credential`, `encryption_key`, `payload_url`

### Collection: `payloads`
Document `main_app`:
- `code`: Mã base64 của app chính (đã mã hóa)
- `app_name`: "honghac_builda"
- `version`: "1.0"

### Collection: `shortlinks`
- Chứa link rút gọn cho mỗi key

### Collection: `config`
- `shortener`: Config API rút gọn link

---

## 🔧 Thứ tự làm việc

### 1. Admin setup (chạy 1 lần)
```bash
cd d:\DONE\admin
python admin_panel.py
```
- Đăng nhập
- Setup Payload (tab Payload)
- Build và upload payload

### 2. Admin tạo key
- Vào tab "Tạo Key"
- Nhập số lượng, thời gian (giây)
- Nhấn "Bắt đầu tạo"

### 3. Upload files lên GitHub
- Upload `userreal/launcher_console.py` lên repo

### 4. User chạy (Termux)
```bash
pkg install python -y && pip install requests
python -c "import requests;exec(requests.get('https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher_console.py').text)"
```

---

## 📋 Lệnh chạy cho User

### Termux (1 click):
```bash
pkg update -y && pkg install python -y && pip install requests && python -c "import requests;exec(requests.get('https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher_console.py').text)"
```

### Lần sau:
```bash
python -c "import requests;exec(requests.get('https://raw.githubusercontent.com/ADMINXMINHPHONG/toolsapk/main/launcher_console.py').text)"
```
