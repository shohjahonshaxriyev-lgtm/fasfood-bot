import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
db = Database()

# Admin ID from environment
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# States for ordering
class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    entering_quantity = State()
    entering_address = State()
    entering_phone = State()
    confirming_order = State()

# States for admin
class AdminStates(StatesGroup):
    choosing_action = State()
    adding_product_category = State()
    adding_product_name = State()
    adding_product_description = State()
    adding_product_price = State()
    adding_product_image = State()
    editing_product = State()
    deleting_product = State()
    adding_category_name = State()
    deleting_category = State()

# Main menu keyboard
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽 Buyurtma berish")],
            [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="📍 Manzil")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Admin menu keyboard
def get_admin_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mahsulot qo'shish")],
            [KeyboardButton(text="📂 Kategoriya qo'shish"), KeyboardButton(text="🗑️ Kategoriya o'chirish")],
            [KeyboardButton(text="✏️ Mahsulotni tahrirlash")],
            [KeyboardButton(text="❌ Mahsulotni o'chirish")],
            [KeyboardButton(text="📦 Buyurtmalar")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Start command
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🍔 Xush kelibsiz! Fast Food botimizga\n\n"
        "Quyidagi menyulardan birini tanlang:",
        reply_markup=get_main_menu()
    )

# Admin command
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    # Log admin access attempt
    user_id = message.from_user.id
    user_name = message.from_user.full_name or message.from_user.first_name
    
    if user_id != ADMIN_ID:
        logging.warning(f"Unauthorized admin access attempt - User: {user_name} (ID: {user_id})")
        await message.answer(
            "❌ *Siz admin emassiz!*\n\n"
            "Bu funktsiyadan faqat admin foydalanishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    logging.info(f"Admin panel accessed - User: {user_name} (ID: {user_id})")
    await message.answer(
        "👨‍💼 *Admin paneliga xush kelibsiz!*\n\n"
        "🔐 *Xavfsizlik tasdiqlandi*\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=get_admin_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# Order button handler
@dp.message(F.text == "🍽 Buyurtma berish")
async def start_order(message: Message, state: FSMContext):
    categories = db.get_categories()
    
    if not categories:
        await message.answer("❌ Hozircha mahsulotlar mavjud emas. Iltimos, keyinroq urinib ko'ring.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for cat_id, cat_name in categories:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"category_{cat_id}")])
    
    # Add back button
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main_menu")])
    
    await message.answer(
        "🍽 Kategoriyani tanlang:",
        reply_markup=keyboard
    )
    await state.set_state(OrderStates.choosing_category)

# Category selection handler
@dp.callback_query(F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    products = db.get_products_by_category(category_id)
    
    if not products:
        await callback.message.answer("❌ Bu kategoriyada mahsulotlar mavjud emas.")
        await callback.answer()
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product_id, name, description, price, image_url in products:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} - {price} so'm",
                callback_data=f"product_{product_id}"
            )
        ])
    
    # Add back button
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    
    await callback.message.edit_text(
        "🍔 Mahsulotni tanlang:",
        reply_markup=keyboard
    )
    await state.update_data(category_id=category_id)
    await state.set_state(OrderStates.choosing_product)
    await callback.answer()

# Product selection handler
@dp.callback_query(F.data.startswith("product_"))
async def product_selected(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.message.answer("❌ Mahsulot topilmadi.")
        await callback.answer()
        return
    
    prod_id, name, description, price, image_url, category_id = product
    
    text = f"🍔 *{name}*\n\n"
    if description:
        text += f"📝 Tarkibi: {description}\n"
    text += f"💰 Narxi: {price} so'm"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Buyurtma qilish", callback_data=f"order_{product_id}")]
    ])
    
    if image_url and image_url.startswith("http"):
        # Send with image URL
        await callback.message.answer_photo(
            photo=image_url,
            caption=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    elif image_url and len(image_url) < 100:  # It's a file_id
        # Send with Telegram file_id
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            # If photo fails, send text only
            await callback.message.answer(
                text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        # Send without image
        await callback.message.answer(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    await callback.answer()

# Order initiation handler
@dp.callback_query(F.data.startswith("order_"))
async def start_order_process(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.message.answer("❌ Mahsulot topilmadi.")
        await callback.answer()
        return
    
    await state.update_data(product_id=product_id, product_name=product[1], price=product[3])
    
    # Send new message instead of editing (can't edit photo messages)
    await callback.message.answer("🔢 Nechta olasiz?")
    await state.set_state(OrderStates.entering_quantity)
    await callback.answer()

# Quantity input handler
@dp.message(OrderStates.entering_quantity)
async def quantity_entered(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            await message.answer("❌ Iltimos, musbat son kiriting!")
            return
        
        data = await state.get_data()
        total_price = data['price'] * quantity
        await state.update_data(quantity=quantity, total_price=total_price)
        
        await message.answer("📍 Manzilingizni kiriting (lokatsiya yoki matn):")
        await state.set_state(OrderStates.entering_address)
    except ValueError:
        await message.answer("❌ Iltimos, son kiriting!")

# Address input handler
@dp.message(OrderStates.entering_address)
async def address_entered(message: Message, state: FSMContext):
    address_text = ""
    
    if message.location:
        # Handle location message
        lat = message.location.latitude
        lon = message.location.longitude
        address_text = f"📍 Lokatsiya: {lat:.6f}, {lon:.6f}"
        
        # Also send Google Maps link for convenience
        maps_link = f"https://maps.google.com/?q={lat},{lon}"
        await message.answer(f"✅ Lokatsiya qabul qilindi!\n\n🗺️ Xarita: {maps_link}")
    elif message.text:
        # Handle text address
        address_text = message.text
        await message.answer("✅ Manzil qabul qilindi!")
    
    await state.update_data(address=address_text)
    await message.answer("📞 Telefon raqamingizni kiriting:")
    await state.set_state(OrderStates.entering_phone)

# Phone input handler
@dp.message(OrderStates.entering_phone)
async def phone_entered(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    
    confirmation_text = (
        f"📋 *Buyurtma tasdiqlash*\n\n"
        f"🍔 Mahsulot: {data['product_name']}\n"
        f"🔢 Soni: {data['quantity']}\n"
        f"💰 Jami narxi: {data['total_price']} so'm\n"
        f"📍 Manzil: {data['address']}\n"
        f"📞 Telefon: {message.text}\n\n"
        f"Tasdiqlaysizmi?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, tasdiqlayman", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")]
    ])
    
    await message.answer(confirmation_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    await state.set_state(OrderStates.confirming_order)

# Order confirmation handler
@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    
    # Save order to database
    success = db.create_order(
        user_id=user.id,
        user_name=user.full_name or user.first_name,
        phone=data['phone'],
        address=data['address'],
        product_id=data['product_id'],
        quantity=data['quantity'],
        total_price=data['total_price']
    )
    
    if success:
        await callback.message.edit_text("✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.")
        
        # Send notification to admin
        address = data['address']
        
        # Format address for admin display
        if "📍 Lokatsiya:" in address:
            # Extract coordinates and create map link
            try:
                coords = address.split("📍 Lokatsiya: ")[1]
                lat, lon = coords.split(", ")
                map_link = f"https://maps.google.com/?q={lat},{lon}"
                address_display = f"📍 Lokatsiya: {coords}\n🗺️ Xarita: {map_link}"
            except:
                address_display = address
        else:
            address_display = address
        
        admin_text = (
            f"📥 *Yangi buyurtma!*\n\n"
            f"👤 Ism: {user.full_name or user.first_name}\n"
            f"📱 Telefon: {data['phone']}\n"
            f"🍔 Mahsulot: {data['product_name']}\n"
            f"🔢 Soni: {data['quantity']}\n"
            f"💰 Jami: {data['total_price']} so'm\n"
            f"📍 Manzil: {address_display}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_order_{user.id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_order_{user.id}")]
        ])
        
        try:
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        except:
            pass  # Admin might not have started the bot
    else:
        await callback.message.edit_text("❌ Buyurtmani saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    
    await state.clear()
    await callback.answer()

# Order cancellation handler
@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await state.clear()
    await callback.answer()

# Contact button handler
@dp.message(F.text == "📞 Aloqa")
async def show_contact(message: Message):
    contact_text = (
        "📞 *Aloqa*\n\n"
        "📱 Telefon: +998 93 155-11-04\n"
        "🕐 Ish vaqti: 09:00 - 23:00\n"
        "📍 Manzil: toyloq tumani sariosiyo mahallasi\n\n"
        "🚐 Yetkazib berish bepul!"
    )
    await message.answer(contact_text, parse_mode=ParseMode.MARKDOWN)

# Location button handler
@dp.message(F.text == "📍 Manzil")
async def show_location(message: Message):
    location_text = (
        "📍 *Manzilimiz*\n\n"
        " toyloq tunani sariosiyo mahallasi\n\n"
        "🗺️ Xaritada ko'rish uchun pastdagi tugmani bosing!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺️ Xaritada ko'rish", url="https://maps.app.goo.gl/6ktzTSwdb3ts3MUb7")]
    ])
    
    await message.answer(location_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

# Admin panel handlers

# Admin menu handlers
@dp.message(F.text == "➕ Mahsulot qo'shish")
async def add_product_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin mahsulot qo'shishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    categories = db.get_categories()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for cat_id, cat_name in categories:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"addcat_{cat_id}")])
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="➕ Yangi kategoriya", callback_data="new_category")])
    
    await message.answer("📂 Kategoriyani tanlang:", reply_markup=keyboard)
    await state.set_state(AdminStates.adding_product_category)

@dp.message(F.text == "✏️ Mahsulotni tahrirlash")
async def edit_product_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin mahsulot tahrirlashi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    products = db.get_all_products()
    
    if not products:
        await message.answer("❌ Mahsulotlar mavjud emas!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product_id, name, description, price, image_url, category_name in products:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{category_name} - {name}",
                callback_data=f"edit_{product_id}"
            )
        ])
    
    await message.answer("✏️ Tahrirlash uchun mahsulotni tanlang:", reply_markup=keyboard)
    await state.set_state(AdminStates.editing_product)

@dp.message(F.text == "❌ Mahsulotni o'chirish")
async def delete_product_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin mahsulot o'chirishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    products = db.get_all_products()
    
    if not products:
        await message.answer("❌ Mahsulotlar mavjud emas!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product_id, name, description, price, image_url, category_name in products:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{category_name} - {name}",
                callback_data=f"delete_{product_id}"
            )
        ])
    
    await message.answer("❌ O'chirish uchun mahsulotni tanlang:", reply_markup=keyboard)
    await state.set_state(AdminStates.deleting_product)

@dp.message(F.text == "📦 Buyurtmalar")
async def show_orders(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin buyurtmalarni ko'rishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    orders = db.get_pending_orders()
    
    if not orders:
        await message.answer("📦 Kutilayotgan buyurtmalar yo'q.")
        return
    
    for order_id, user_id, user_name, phone, address, product_name, quantity, total_price, created_at in orders:
        order_text = (
            f"📋 *Buyurtma #{order_id}*\n\n"
            f"👤 Mijoz: {user_name}\n"
            f"📞 Tel: {phone}\n"
            f"🍔 Mahsulot: {product_name}\n"
            f"🔢 Soni: {quantity}\n"
            f"💰 Jami: {total_price} so'm\n"
            f"📍 Manzil: {address}\n"
            f"🕐 Vaqt: {created_at}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_order_{order_id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_order_{order_id}")]
        ])
        
        await message.answer(order_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "� Kategoriya qo'shish")
async def add_category_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin kategoriya qo'shishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await message.answer("📂 Yangi kategoriya nomini kiriting:")
    await state.set_state(AdminStates.adding_category_name)

@dp.message(F.text == "🗑️ Kategoriya o'chirish")
async def delete_category_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ *Ruxsat berilmagan!*\n\n"
            "Faqat admin kategoriya o'chirishi mumkin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    categories = db.get_categories()
    
    if not categories:
        await message.answer("❌ Kategoriyalar mavjud emas!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for cat_id, cat_name in categories:
        # Check if category has products
        products = db.get_products_by_category(cat_id)
        status = "🔒" if products else "✅"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {cat_name} ({len(products)} mahsulot)",
                callback_data=f"delcat_{cat_id}"
            )
        ])
    
    await message.answer("🗑️ O'chirish uchun kategoriyani tanlang:", reply_markup=keyboard)
    await state.set_state(AdminStates.deleting_category)

@dp.message(AdminStates.adding_category_name)
async def add_category_name_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    category_name = message.text.strip()
    
    if not category_name:
        await message.answer("❌ Kategoriya nomi bo'sh bo'lmasin! Iltimos, qayta kiriting:")
        return
    
    if db.add_category(category_name):
        await message.answer(f"✅ Kategoriya '{category_name}' muvaffaqiyatli qo'shildi!")
    else:
        await message.answer("❌ Bu kategoriya allaqachon mavjud! Boshqa nom kiriting:")
        return
    
    await state.clear()
    await message.answer("👨‍💼 Admin menu:", reply_markup=get_admin_menu())

@dp.message(F.text == "� Orqaga")
async def back_to_admin_menu(message: Message, state: FSMContext):
    """Admin back button handler"""
    if message.from_user.id != ADMIN_ID:
        # If not admin, use the universal back handler
        return await back_to_main_from_anywhere(message, state)
    
    await state.clear()
    await message.answer("🍽 Asosiy menu:", reply_markup=get_admin_menu())

# Admin callback handlers
@dp.callback_query(F.data.startswith("addcat_"))
async def add_product_category_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)
    await callback.message.edit_text("📝 Mahsulot nomini kiriting:")
    await state.set_state(AdminStates.adding_product_name)
    await callback.answer()

@dp.callback_query(F.data == "new_category")
async def new_category_request(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    await callback.message.edit_text("📂 Yangi kategoriya nomini kiriting:")
    await state.set_state(AdminStates.adding_product_category)
    await callback.answer()

@dp.callback_query(F.data.startswith("delcat_"))
async def delete_category_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[1])
    category = db.get_category_by_id(category_id)
    
    if not category:
        await callback.message.edit_text("❌ Kategoriya topilmadi.")
        await callback.answer()
        return
    
    cat_id, cat_name = category
    products = db.get_products_by_category(category_id)
    
    if products:
        await callback.message.edit_text(
            f"❌ *'{cat_name}' kategoriyasini o'chirib bo'lmadi!*\n\n"
            f"📦 Bu kategoriyada {len(products)} ta mahsulot mavjud.\n"
            f"Avval mahsulotlarni o'chirishingiz kerak.",
            parse_mode=ParseMode.MARKDOWN
        )
        await callback.answer()
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chiraman", callback_data=f"confirm_delcat_{category_id}")],
        [InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delcat")]
    ])
    
    await callback.message.edit_text(
        f"🗑️ *'{cat_name}' kategoriyasini o'chirmoqchimisiz?*\n\n"
        f"⚠️ Bu amalni qaytarib bo'lmaydi!",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("confirm_delcat_"))
async def confirm_delete_category(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[2])
    category = db.get_category_by_id(category_id)
    
    if not category:
        await callback.message.edit_text("❌ Kategoriya topilmadi.")
        await callback.answer()
        return
    
    cat_id, cat_name = category
    
    if db.delete_category(category_id):
        await callback.message.edit_text(f"✅ Kategoriya '{cat_name}' muvaffaqiyatli o'chirildi!")
    else:
        await callback.message.edit_text("❌ Kategoriyani o'chirishda xatolik!")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "cancel_delcat")
async def cancel_delete_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Kategoriya o'chirish bekor qilindi.")
    await state.clear()
    await callback.answer()

@dp.message(AdminStates.adding_product_category)
async def new_category_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    # Check if this is a new category name or if we should proceed with product name
    categories = [name for _, name in db.get_categories()]
    
    if message.text in categories:
        # Existing category selected
        category_id = next(cat_id for cat_id, name in db.get_categories() if name == message.text)
        await state.update_data(category_id=category_id)
        await message.answer("📝 Mahsulot nomini kiriting:")
        await state.set_state(AdminStates.adding_product_name)
    else:
        # New category
        if db.add_category(message.text):
            category_id = next(cat_id for cat_id, name in db.get_categories() if name == message.text)
            await state.update_data(category_id=category_id)
            await message.answer(f"✅ Kategoriya qo'shildi! Endi mahsulot nomini kiriting:")
            await state.set_state(AdminStates.adding_product_name)
        else:
            await message.answer("❌ Kategoriyani qo'shishda xatolik. Boshqa nom kiriting:")

@dp.message(AdminStates.adding_product_name)
async def product_name_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.update_data(name=message.text)
    await message.answer("📄 Mahsulot tavsifini kiriting (yoki 'skip' deb yozing):")
    await state.set_state(AdminStates.adding_product_description)

@dp.message(AdminStates.adding_product_description)
async def product_description_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    description = None if message.text.lower() == 'skip' else message.text
    await state.update_data(description=description)
    await message.answer("💰 Mahsulot narxini kiriting (so'mda):")
    await state.set_state(AdminStates.adding_product_price)

@dp.message(AdminStates.adding_product_price)
async def product_price_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        price = float(message.text)
        if price <= 0:
            await message.answer("❌ Iltimos, musbat narx kiriting!")
            return
        
        await state.update_data(price=price)
        await message.answer("🖼️ Mahsulot rasmini yuboring (yoki 'skip' deb yozing):")
        await state.set_state(AdminStates.adding_product_image)
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri narx kiriting!")

@dp.message(AdminStates.adding_product_image)
async def product_image_entered(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    image_url = None
    
    if message.photo:
        # Get the highest quality photo
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        # Store the file_id for later use
        image_url = photo.file_id
    elif message.text and message.text.lower() != 'skip':
        # Assume it's a URL
        image_url = message.text
    
    # Add product to database
    success = db.add_product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        image_url=image_url,
        category_id=data['category_id']
    )
    
    if success:
        await message.answer("✅ Mahsulot muvaffaqiyatli qo'shildi!")
        
        # Show the added product with image if available
        if image_url:
            product = db.get_product_by_name(data['name'])
            if product:
                prod_id, name, description, price, stored_image_url, category_id = product
                text = f"🍔 *{name}*\n\n"
                if description:
                    text += f"📝 Tarkibi: {description}\n"
                text += f"💰 Narxi: {price} so'm"
                
                if stored_image_url and len(stored_image_url) < 100:  # It's a file_id
                    try:
                        await message.answer_photo(
                            photo=stored_image_url,
                            caption=text,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        await message.answer(text, parse_mode=ParseMode.MARKDOWN)
                elif stored_image_url and stored_image_url.startswith("http"):
                    await message.answer(
                        f"🖼️ Rasm: {stored_image_url}\n\n{text}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await message.answer(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("❌ Mahsulotni qo'shishda xatolik yuz berdi.")
    
    await state.clear()
    await message.answer("👨‍💼 Admin menu:", reply_markup=get_admin_menu())

# Edit product handlers
@dp.callback_query(F.data.startswith("edit_"))
async def edit_product_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.message.edit_text("❌ Mahsulot topilmadi.")
        await callback.answer()
        return
    
    prod_id, name, description, price, image_url, category_id = product
    
    await state.update_data(product_id=product_id, current_data={
        'name': name,
        'description': description,
        'price': price,
        'image_url': image_url,
        'category_id': category_id
    })
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Nomi", callback_data="edit_name")],
        [InlineKeyboardButton(text="📄 Tavsif", callback_data="edit_description")],
        [InlineKeyboardButton(text="💰 Narxi", callback_data="edit_price")],
        [InlineKeyboardButton(text="🖼️ Rasm", callback_data="edit_image")],
        [InlineKeyboardButton(text="📂 Kategoriya", callback_data="edit_category")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
    ])
    
    await callback.message.edit_text(
        f"✏️ *{name}* - Tahrirlash\n\n"
        f"Nimani o'zgartirmoqchisiz?",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_name"))
async def edit_product_name(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    await state.update_data(editing_field='name')
    await callback.message.edit_text("📝 Yangi nomni kiriting:")
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_description"))
async def edit_product_description(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    await state.update_data(editing_field='description')
    await callback.message.edit_text("📄 Yangi tavsifni kiriting:")
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_price"))
async def edit_product_price(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    await state.update_data(editing_field='price')
    await callback.message.edit_text("💰 Yangi narxni kiriting:")
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_image"))
async def edit_product_image(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    await state.update_data(editing_field='image')
    await callback.message.edit_text("🖼️ Yangi rasm yuboring yoki URL kiriting:")
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_category"))
async def edit_product_category(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    categories = db.get_categories()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for cat_id, cat_name in categories:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"setcat_{cat_id}")])
    await callback.message.edit_text("📂 Yangi kategoriyani tanlang:", reply_markup=keyboard)
    await callback.answer()

# Handle field updates for editing
@dp.message(AdminStates.editing_product)
async def handle_edit_field(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    product_id = data['product_id']
    editing_field = data.get('editing_field')
    
    if not editing_field:
        return
    
    update_data = {}
    
    if editing_field == 'name':
        update_data['name'] = message.text
    elif editing_field == 'description':
        update_data['description'] = message.text
    elif editing_field == 'price':
        try:
            price = float(message.text)
            if price <= 0:
                await message.answer("❌ Iltimos, musbat narx kiriting!")
                return
            update_data['price'] = price
        except ValueError:
            await message.answer("❌ Iltimos, to'g'ri narx kiriting!")
            return
    elif editing_field == 'image':
        if message.photo:
            photo = message.photo[-1]
            file_info = await bot.get_file(photo.file_id)
            update_data['image_url'] = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file_info.file_path}"
        else:
            update_data['image_url'] = message.text
    
    # Update the product
    success = db.update_product(product_id, **update_data)
    
    if success:
        await message.answer("✅ Mahsulot muvaffaqiyatli tahrirlandi!")
    else:
        await message.answer("❌ Mahsulotni tahrirlashda xatolik!")
    
    await state.clear()
    await message.answer("👨‍💼 Admin menu:", reply_markup=get_admin_menu())

@dp.callback_query(F.data.startswith("setcat_"))
async def set_new_category(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    category_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    product_id = data['product_id']
    
    if db.update_product(product_id, category_id=category_id):
        await callback.message.edit_text("✅ Kategoriya muvaffaqiyatli o'zgartirildi!")
    else:
        await callback.message.edit_text("❌ Kategoriyani o'zgartirishda xatolik!")
    
    await state.clear()
    await callback.answer()

# Delete product handlers
@dp.callback_query(F.data.startswith("delete_"))
async def delete_product_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.message.edit_text("❌ Mahsulot topilmadi.")
        await callback.answer()
        return
    
    prod_id, name, description, price, image_url, category_id = product
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chiraman", callback_data=f"confirm_delete_{product_id}")],
        [InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delete")]
    ])
    
    await callback.message.edit_text(
        f"❌ *{name}* mahsulotini o'chirmoqchimisiz?\n\n"
        f"Bu amalni qaytarib bo'lmaydi!",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_product(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    product_id = int(callback.data.split("_")[2])
    
    if db.delete_product(product_id):
        await callback.message.edit_text("✅ Mahsulot muvaffaqiyatli o'chirildi!")
    else:
        await callback.message.edit_text("❌ Mahsulotni o'chirishda xatolik!")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ O'chirish bekor qilindi.")
    await state.clear()
    await callback.answer()

# Order management handlers
@dp.callback_query(F.data.startswith("accept_order_"))
async def accept_order(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    if callback.data.startswith("accept_order_"):
        try:
            order_id = int(callback.data.split("_")[2])
        except (IndexError, ValueError):
            # Handle user notification case
            user_id = int(callback.data.split("_")[2])
            await callback.message.edit_text("✅ Buyurtmangiz qabul qilindi! Tez orada yetkazib beramiz.")
            await callback.answer()
            return
    
    if db.update_order_status(order_id, "accepted"):
        await callback.message.edit_text("✅ Buyurtma qabul qilindi!")
    else:
        await callback.message.edit_text("❌ Buyurtmani qabul qilishda xatolik!")
    
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_order_"))
async def reject_order(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    
    order_id = int(callback.data.split("_")[2])
    
    if db.update_order_status(order_id, "rejected"):
        await callback.message.edit_text("❌ Buyurtma rad etildi!")
    else:
        await callback.message.edit_text("❌ Buyurtmani rad etishda xatolik!")
    
    await callback.answer()

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👨‍💼 Admin menu:", reply_markup=get_admin_menu())
    await callback.answer()

# Back button handlers for user navigation
@dp.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🍔 Xush kelibsiz! Fast Food botimizga\n\n"
        "Quyidagi menyulardan birini tanlang:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    categories = db.get_categories()
    
    if not categories:
        await callback.message.edit_text("❌ Hozircha mahsulotlar mavjud emas. Iltimos, keyinroq urinib ko'ring.")
        await callback.answer()
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for cat_id, cat_name in categories:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"category_{cat_id}")])
    
    # Add back button
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main_menu")])
    
    await callback.message.edit_text(
        "🍽 Kategoriyani tanlang:",
        reply_markup=keyboard
    )
    await state.set_state(OrderStates.choosing_category)
    await callback.answer()

@dp.message(F.text == "🔙 Orqaga")
async def back_to_main_from_anywhere(message: Message, state: FSMContext):
    """Universal back button handler for all users"""
    current_state = await state.get_state()
    
    if current_state:
        # Check if user is in order states
        if "OrderStates" in str(current_state):
            # Get current state data to determine where to go back
            data = await state.get_data()
            
            if "category_id" in data and "choosing_product" in str(current_state):
                # User is in product selection, go back to categories
                categories = db.get_categories()
                
                if not categories:
                    await message.answer("❌ Hozircha mahsulotlar mavjud emas.", reply_markup=get_main_menu())
                    await state.clear()
                    return
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[])
                for cat_id, cat_name in categories:
                    keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"category_{cat_id}")])
                
                keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main_menu")])
                
                await message.answer("� Kategoriyani tanlang:", reply_markup=keyboard)
                await state.set_state(OrderStates.choosing_category)
            else:
                # User is in other order state, go to main menu
                await state.clear()
                await message.answer(
                    "�� Xush kelibsiz! Fast Food botimizga\n\n"
                    "Quyidagi menyulardan birini tanlang:",
                    reply_markup=get_main_menu()
                )
        elif "AdminStates" in str(current_state):
            # Admin users go back to admin menu
            if message.from_user.id == ADMIN_ID:
                await state.clear()
                await message.answer("👨‍💼 Admin menu:", reply_markup=get_admin_menu())
            else:
                await message.answer("❌ Siz admin emassiz!", reply_markup=get_main_menu())
                await state.clear()
        else:
            # Unknown state, go to main menu
            await state.clear()
            await message.answer(
                "🍔 Xush kelibsiz! Fast Food botimizga\n\n"
                "Quyidagi menyulardan birini tanlang:",
                reply_markup=get_main_menu()
            )
    else:
        # No state, just show main menu
        await message.answer(
            "🍔 Xush kelibsiz! Fast Food botimizga\n\n"
            "Quyidagi menyulardan birini tanlang:",
            reply_markup=get_main_menu()
        )

# Error handling and general handlers
@dp.message()
async def handle_unknown_message(message: Message, state: FSMContext):
    """Handle messages that don't match any specific handler"""
    current_state = await state.get_state()
    
    if current_state:
        # User is in a process, provide guidance
        if "OrderStates" in str(current_state):
            await message.answer("❌ Iltimos, buyurtma jarayonini davom ettiring yoki /start ni bosing.")
        elif "AdminStates" in str(current_state):
            if message.from_user.id == ADMIN_ID:
                await message.answer("❌ Iltimos, admin jarayonini davom ettiring yoki 🔙 Orqaga ni bosing.")
            else:
                await message.answer("❌ Siz admin emassiz!")
        else:
            await message.answer("❌ Noma'lum holat. /start ni bosing.")
    else:
        # User is not in any specific process
        await message.answer(
            "❌ Bunday buyruq topilmadi!\n\n"
            "🍽 Asosiy menyuga qaytish uchun /start ni bosing.",
            reply_markup=get_main_menu()
        )

# Help command
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🍔 *Fast Food Bot - Yordam*\n\n"
        "📋 *Buyruqlar:*\n"
        "/start - Botni qayta ishga tushirish\n"
        "/admin - Admin paneli (faq admin uchun)\n"
        "/help - Yordam\n\n"
        "🍽 *Funksiyalar:*\n"
        "• 🍽 Buyurtma berish - Menyuni ko'rish va buyurtma qilish\n"
        "• 📞 Aloqa - Biz bilan bog'lanish\n"
        "• 📍 Manzil - Manzilimizni ko'rish\n\n"
        "📱 *Buyurtma qilish tartibi:*\n"
        "1. 🍽 Kategoriyani tanlang\n"
        "2. 🍔 Mahsulotni tanlang\n"
        "3. 🔢 Sonini kiriting\n"
        "4. 📍 Manzilni kiriting\n"
        "5. 📞 Telefon raqamini kiriting\n"
        "6. ✅ Buyurtmani tasdiqlang\n\n"
        "🚀 Tez orada siz bilan bog'lanamiz!"
    )
    
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

# General callback handler - moved to the end to catch only unmatched callbacks
@dp.callback_query()
async def handle_unknown_callback(callback: CallbackQuery, state: FSMContext):
    """Handle callback queries that don't match any specific handler"""
    # Don't catch known callback patterns
    known_patterns = [
        "category_", "product_", "order_", "edit_", "delete_", 
        "addcat_", "setcat_", "confirm_", "accept_order_", "reject_order_",
        "back_to_main_menu", "back_to_categories", "back_to_admin", 
        "new_category", "cancel_delete", "delcat_", "confirm_delcat_", "cancel_delcat"
    ]
    
    for pattern in known_patterns:
        if callback.data.startswith(pattern):
            return  # Let specific handlers handle these
    
    # Only handle truly unknown callbacks
    await callback.answer("❌ Bu amal mavjud emas!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
