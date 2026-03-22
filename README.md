# 🍔 Fast Food Telegram Bot

To'liq funksional Fast Food restoran uchun Telegram boti, foydalanuvchilar menyuni ko'rish, buyurtma berish va adminlar mahsulotlarni boshqarish imkoniyatiga ega.

## ✨ Xususiyatlar

### 👤 Foydalanuvchi tomoni:
- 🍽 Menyuni ko'rish (kategoriya bo'yicha)
- 🖼️ Mahsulot rasmlari va tavsiflari
- 🛒 Osongina buyurtma berish
- 📍 Manzil va telefon raqami kiritish
- ✅ Buyurtma holatini kuzatish
- 📞 Aloqa va manzil ma'lumotlari

### 👨‍💼 Admin paneli:
- ➕ Yangi mahsulot qo'shish (rasmlar bilan)
- ✏️ Mahsulotlarni tahrirlash
- ❌ Mahsulotlarni o'chirish
- 📦 Buyurtmalarni boshqarish
- 📂 Kategoriyalarni boshqarish
- 📊 Real vaqtli buyurtma bildirishnomalari

## 🛠️ Texnologiyalar

- **Python 3.8+**
- **aiogram 3.x** - Telegram bot framework
- **SQLite** - Ma'lumotlar bazasi
- **FSM (State Machine)** - Holatni boshqarish
- **Inline Keyboards** - Interfeys uchun

## 📦 O'rnatish

### 1. Repoziyani klonlash
```bash
git clone <repository-url>
cd fastfood-bot
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Dependentsiyalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiya
```bash
# .env faylini yaratish
cp .env.example .env
```

`.env` faylini oching va quyidagilarni kiriting:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_admin_telegram_id_here
```

### 5. Bot token olish
1. [@BotFather](https://t.me/botfather) bilan suhbat boshlang
2. `/newbot` deb yozing
3. Bot nomi va username ni kiriting
4. Token nusxalang va `.env` fayliga qo'shing

### 6. Admin ID ni olish
1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. O'zingizning Telegram ID raqamingizni nusqalang
3. `.env` fayliga qo'shing

## 🚀 Ishga tushirish

### Botni ishga tushirish
```bash
python main.py
```

### Test ma'lumotlarini qo'shish (ixtiyoriy)
```bash
python setup_data.py
```

## 📋 Foydalanish

### Foydalanuvchi uchun:
1. `/start` - Botni ishga tushirish
2. 🍽 Buyurtma berish - Menyuni ko'rish
3. Kategoriyani tanlang
4. Mahsulotni tanlang
5. Sonini, manzil va telefon raqamini kiriting
6. Buyurtmani tasdiqlang

### Admin uchun:
1. `/admin` - Admin paneliga kirish
2. ➕ Mahsulot qo'shish - Yangi mahsulotlar qo'shish
3. ✏️ Mahsulotni tahrirlash - Mavjud mahsulotlarni o'zgartirish
4. ❌ Mahsulotni o'chirish - Mahsulotlarni olib tashlash
5. 📦 Buyurtmalar - Kelayotgan buyurtmalarni ko'rish

## 🗂️ Fayl tuzilishi

```
fastfood-bot/
├── main.py              # Asosiy bot fayli
├── database.py          # Ma'lumotlar bazasi moduli
├── setup_data.py        # Test ma'lumotlarini qo'shish
├── requirements.txt     # Python paketlari
├── .env.example        # Konfiguratsiya shabloni
├── README.md           # Hujjatlar
└── fastfood.db         # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
```

## 🗄️ Ma'lumotlar bazasi tuzilishi

### Categories
- `id` - Kategoriya ID
- `name` - Kategoriya nomi

### Products
- `id` - Mahsulot ID
- `name` - Mahsulot nomi
- `description` - Tavsif
- `price` - Narx
- `image_url` - Rasm URL
- `category_id` - Kategoriya ID

### Orders
- `id` - Buyurtma ID
- `user_id` - Foydalanuvchi ID
- `user_name` - Foydalanuvchi nomi
- `phone` - Telefon raqam
- `address` - Manzil
- `product_id` - Mahsulot ID
- `quantity` - Soni
- `total_price` - Jami narx
- `status` - Holati (pending/accepted/rejected)

## 🔧 Konfiguratsiya

### Bot sozlamalari
- `BOT_TOKEN` - Telegram bot tokeni
- `ADMIN_ID` - Admin Telegram ID

### Qo'shimcha sozlamalar
`main.py` faylida quyidagilarni o'zgartirishingiz mumkin:
- Admin ID tekshiruvi
- Xabar formatlari
- Tugmalar matnlari

## 🚀 Deployment

### Heroku
1. Heroku account yarating
2. `Procfile` yarating:
```
web: python main.py
```
3. Environment variables sozlang
4. Deploy qiling

### Railway/Render
1. Repoziyani import qiling
2. Environment variables sozlang
3. Deploy qiling

### VPS (Ubuntu)
```bash
# Screen yoki tmux ishlatish tavsiya etiladi
screen -S fastfood-bot
python main.py

# Chiqish uchun: Ctrl+A, keyin D
```

## 🐛 Debugging

### Loglarni yoqish
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Umumiy xatolar:
1. **"Bot token not found"** - `.env` faylini tekshiring
2. **"Admin ID not found"** - Admin ID ni tekshiring
3. **"Database error"** - Fayl ruxsatlarini tekshiring

## 📞 Qo'llab-quvvatlash

Agar muammolarga duch kelsangiz:
1. Loglarni tekshiring
2. `.env` fayl konfiguratsiyasini tekshiring
3. Python va aiogram versiyalarini tekshiring

## 📜 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 🤝 Hissa qo'shish

1. Repoziyani fork qiling
2. O'z branchingiz yarating (`git checkout -b feature/AmazingFeature`)
3. O'zgarishlarni qo'shing (`git commit -m 'Add some AmazingFeature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull request yarating

---

**🍔 Tayyor! Fast Food botingiz endi ishga tayyor!**
