# 📦 Installation Guide

## 🚀 Quick Installation

### 1. System Requirements
- Python 3.8+
- Git
- Internet connection

### 2. Bot Token Oling (5 daqiqa)
1. Telegramda [@BotFather](https://t.me/botfather) ni toping
2. `/newbot` deb yozing
3. Bot nomi: `Fast Food Restaurant`
4. Username: `yourrestaurant_bot` (unikal bo'lishi kerak)
5. Token nusqalang (masalan: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Admin ID Oling (1 daqiqa)
1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. O'zingizning ID raqamingizni nusqalang (masalan: `123456789`)

### 4. Installation (5 daqiqa)

#### Windows:
```powershell
# 1. Repo klonlash
git clone <repository-url>
cd fastfood-bot

# 2. Python virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Konfiguratsiya
copy .env.example .env
```

#### Linux/Mac:
```bash
# 1. Repo klonlash
git clone <repository-url>
cd fastfood-bot

# 2. Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Konfiguratsiya
cp .env.example .env
```

### 5. Configuration (2 daqiqa)

`.env` faylini oching va quyidagilarni kiriting:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
```

### 6. Test Data (ixtiyoriy, 1 daqiqa)

```bash
python setup_data.py
```

### 7. Start Bot (1 daqiqa)

```bash
python main.py
```

## ✅ Test

1. Telegramda botingizni toping
2. `/start` deb yozing
3. Menyuni tekshiring
4. Admin panelini tekshirish uchun `/admin` deb yozing

## 🔧 Troubleshooting

### "python not found"
```bash
# Python o'rnatish
# Windows: python.org dan download qiling
# Linux: sudo apt install python3 python3-pip
# Mac: brew install python3
```

### "pip not found"
```bash
# Pip o'rnatish
python -m ensurepip --upgrade
```

### "ModuleNotFoundError"
```bash
# Dependencies qayta o'rnatish
pip install -r requirements.txt
```

### "Bot token invalid"
- Tokenni to'g'ri nusqalaganingizni tekshiring
- @BotFather dan qayta token oling

### "Admin access denied"
- Admin ID ni tekshiring
- @userinfobot dan ID ni qayta oling

## 📱 Mobile Installation

### Termux (Android):
```bash
# Termux o'rnatish
# Play Store dan Termux download qiling

# Installation
pkg update && pkg upgrade
pkg install python git
pip install aiogram python-dotenv

# Repo klonlash
git clone <repository-url>
cd fastfood-bot

# Konfiguratsiya
cp .env.example .env
# .env faylini tahrirlang

# Start
python main.py
```

## 🐳 Docker Installation (Advanced)

### 1. Docker o'rnatish
[Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Build va run
```bash
# Build
docker build -t fastfood-bot .

# Run
docker run -d --name fastfood-bot \
  -e BOT_TOKEN=your_token \
  -e ADMIN_ID=your_admin_id \
  fastfood-bot
```

### 3. Docker Compose
```bash
# docker-compose.yml faylini yarating
docker-compose up -d
```

## 🎯 Next Steps

1. **Customization** - Bot nomi, rasmlar, menyular
2. **Deployment** - Heroku, Railway, VPS
3. **Monitoring** - Loglarni sozlash
4. **Backup** - Ma'lumotlar bazasini backup qilish

## 📞 Support

Agar muammolarga duch kelsangiz:
1. Loglarni tekshiring
2. `.env` faylni tekshiring
3. Python versiyasini tekshiring (`python --version`)
4. README.md ni o'qing

---

**🍔 Bot tayyor! Fast Food restoraningiz uchun!**
