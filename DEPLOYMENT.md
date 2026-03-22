# 🚀 Deployment Guide

## 📋 Quick Start

### 1. Bot Token Olish
1. [@BotFather](https://t.me/botfather) ga yozing
2. `/newbot` deb yozing
3. Bot nomi: `Fast Food Restaurant`
4. Username: `yourrestaurant_bot`
5. Token nusqalang

### 2. Admin ID Olish
1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. O'zingizning ID raqamingizni nusqalang

### 3. Konfiguratsiya
```bash
cp .env.example .env
```

`.env` fayliga:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
```

## 🌐 Platformalar

### Heroku
```bash
# 1. Heroku CLI o'rnatish
# 2. Login
heroku login

# 3. App yaratish
heroku create your-fastfood-bot

# 4. Environment variables
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_admin_id

# 5. Deploy
git push heroku main

# 6. Dyno yoqish
heroku ps:scale web=1
```

`Procfile`:
```
web: python main.py
```

### Railway
1. GitHub dan repo import qiling
2. Environment variables sozlang:
   - `BOT_TOKEN`
   - `ADMIN_ID`
3. Deploy qiling

### Render
1. New Web Service yarating
2. GitHub repo ulang
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python main.py`
5. Environment variables sozlang

### VPS (Ubuntu/Debian)
```bash
# 1. Serverga ulanish
ssh root@your-server-ip

# 2. System update
apt update && apt upgrade -y

# 3. Python o'rnatish
apt install python3 python3-pip python3-venv -y

# 4. Repo klonlash
git clone <your-repo>
cd fastfood-bot

# 5. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Dependencies
pip install -r requirements.txt

# 7. Konfiguratsiya
cp .env.example .env
nano .env  # Token va Admin ID ni kiriting

# 8. Test
python main.py

# 9. Systemd service (ixtiyoriy)
sudo nano /etc/systemd/system/fastfood-bot.service
```

`fastfood-bot.service`:
```ini
[Unit]
Description=Fast Food Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fastfood-bot
Environment=PATH=/home/ubuntu/fastfood-bot/venv/bin
ExecStart=/home/ubuntu/fastfood-bot/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Service yoqish
sudo systemctl enable fastfood-bot
sudo systemctl start fastfood-bot

# Status tekshirish
sudo systemctl status fastfood-bot
```

## 🔧 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3'
services:
  bot:
    build: .
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
    volumes:
      - ./data:/app/data
```

```bash
# Docker bilan ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f
```

## 📊 Monitoring

### Health Check
```python
# main.py ga qo'shing
@app.on_event("startup")
async def startup():
    print("Bot started successfully!")

@app.on_event("shutdown")
async def shutdown():
    print("Bot shutting down...")
```

### Loglarni sozlash
```python
import logging
from aiogram.logging import dispatch_logging

# Detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Aiogram logging
dispatch_logging.set_level(logging.DEBUG)
```

## 🔒 Security

### 1. Environment Variables
Hech qachay tokenlarni kodga yozmang!

### 2. Admin Protection
```python
# Admin ID ni tekshirish
if message.from_user.id != ADMIN_ID:
    await message.answer("❌ Access denied!")
    return
```

### 3. Rate Limiting
```python
from aiogram.filters import Command
from aiogram.types import Message
import time

# Simple rate limiter
user_last_message = {}

@dp.message()
async def rate_limit_check(message: Message):
    user_id = message.from_user.id
    now = time.time()
    
    if user_id in user_last_message:
        if now - user_last_message[user_id] < 1:  # 1 second
            await message.answer("❌ Iltimos, biroz kuting!")
            return
    
    user_last_message[user_id] = now
```

## 🚨 Troubleshooting

### Common Issues

1. **"Bot token is invalid"**
   - Tokenni tekshiring
   - Botni @BotFather dan qayta yoqing

2. **"Can't access admin"**
   - Admin ID ni tekshiring
   - @userinfobot dan ID ni qayta oling

3. **"Database locked"**
   - Fayl ruxsatlarini tekshiring
   - Boshqa process larni o'chiring

4. **"Webhook error"**
   - Port ochiqmi tekshiring
   - SSL sertifikat sozlang

### Logs
```bash
# Real-time log
tail -f bot.log

# Error log
grep ERROR bot.log
```

## 📈 Performance

### 1. Database Optimization
```python
# Index qo'shish
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
```

### 2. Memory Usage
```python
# Chunk processing
async def send_large_message(chat_id, text):
    if len(text) > 4096:
        for chunk in [text[i:i+4096] for i in range(0, len(text), 4096)]:
            await bot.send_message(chat_id, chunk)
    else:
        await bot.send_message(chat_id, text)
```

## 🔄 Backup

### Database Backup
```bash
# SQLite backup
sqlite3 fastfood.db ".backup backup_$(date +%Y%m%d).db"

# Automated backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 fastfood.db ".backup backups/backup_$DATE.db"
find backups/ -name "*.db" -mtime +7 -delete
```

### Cron Job
```bash
# Har kuni soat 2:00 da backup
0 2 * * * /path/to/backup_script.sh
```

---

**🎉 Bot muvaffaqiyatli deployment qilindi!**
