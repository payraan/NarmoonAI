import os
import base64
import random
import sqlite3
import datetime
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

# بارگذاری env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # آیدی ادمین اصلی ربات

# خواندن آدرس‌های کیف پول از متغیر محیطی
solana_wallets_str = os.getenv("SOLANA_WALLETS", "")
SOLANA_WALLETS = [wallet.strip() for wallet in solana_wallets_str.split(",") if wallet.strip()]
if not SOLANA_WALLETS:
    print("هشدار: هیچ آدرس کیف پولی در متغیرهای محیطی تعریف نشده است.")
    # یک آدرس پیش‌فرض برای جلوگیری از خطا
    SOLANA_WALLETS = ["WALLET_ADDRESS_NOT_CONFIGURED"]

client = OpenAI(api_key=OPENAI_API_KEY)

# متغیرهای گلوبال
TUTORIAL_VIDEO_LINK = "https://youtube.com/your_future_video_link"  # بعدا اصلاح شود

# متن قوانین و مقررات - متن کامل
TERMS_AND_CONDITIONS = """
از شما کاربر گرامی دعوت می‌کنیم پیش از استفاده از پلتفرم تحلیل‌گر و سیگنال‌ده هوشمند نارموون، این شرایط را با دقت مطالعه نمایید. استفاده از خدمات نارموون به منزله‌ی پذیرش کامل موارد زیر خواهد بود. هدف ما حفظ امنیت کاربران، شفافیت خدمات و ارائه تجربه‌ای حرفه‌ای و قابل اعتماد در فضای تحلیل بازارهای رمزارزی است.

۱- امنیت اطلاعات:
نارموون به هیچ‌وجه اطلاعات حساب کاربری شما در صرافی‌ها (از جمله API، یوزرنیم، پسورد، کلید خصوصی و...) را درخواست نمی‌کند. لطفاً هیچ‌گونه اطلاعات حساسی را در اختیار هیچ فرد یا پلتفرمی قرار ندهید، حتی اگر خود را نماینده نارموون معرفی کند.

۲- ماهیت پلتفرم:
نارموون یک دستیار هوشمند تحلیل‌گر است، نه صرافی یا بستر انجام معاملات. هیچ خرید یا فروش مستقیم رمزارزی در این پلتفرم انجام نمی‌شود.

۳- عدم ارائه مشاوره مالی:
اگرچه نارموون با استفاده از قویترین مدل های هوش مصنوعی، سیگنال‌ها و تحلیل‌های دقیقی ارائه می‌دهد، اما این داده‌ها مشاوره سرمایه‌گذاری شخصی یا تضمین سود نیستند. هر کاربر پیش از اقدام به خرید یا فروش، موظف است با بررسی شخصی خود تصمیم‌گیری کند.

۴- مسئولیت ریسک معاملات:
کلیه سیگنال‌ها و تحلیل‌ها در نارموون مبتنی بر الگوریتم‌های داده‌محور و پردازش هوشمند هستند، اما نتیجه نهایی معاملات به عهده کاربر است. پذیرش ریسک سرمایه‌گذاری، بر عهده استفاده‌کننده از سیگنال است.

۵- بروزرسانی و بهبود سامانه:
نارموون ممکن است به‌صورت دوره‌ای یا نامنظم بروزرسانی شود. در صورت تغییرات مهم یا قطعی موقت، اطلاع‌رسانی از طریق کانال رسمی یا ایمیل انجام خواهد شد.

۶- تغییر قوانین و اطلاع‌رسانی:
در صورت تغییر در شرایط و ضوابط، نسخه جدید از طریق کانال رسمی اطلاع‌رسانی خواهد شد. مسئولیت پیگیری این تغییرات با کاربران است.

۷- ارتقاء قابلیت‌ها:
اشتراک شما شامل امکاناتی است که در بخش معرفی پلن‌ها درج شده‌اند. در صورت افزودن قابلیت‌های جدید در آینده، تیم نارموون حق دریافت هزینه مجزا برای استفاده از این ویژگی‌ها را محفوظ می‌داند.

۸- حقوق محتوا و مالکیت معنوی:
کپی‌برداری، ذخیره‌سازی، بازنشر یا فروش محتوا، خدمات یا اطلاعات ارائه‌شده توسط نارموون بدون مجوز کتبی رسمی ممنوع است. در صورت سوءاستفاده، پیگرد قانونی و مسئولیت کیفری و مدنی متوجه متخلف خواهد بود.

⚠️ با ادامه استفاده از ربات و خرید اشتراک، شما تأیید می‌کنید که تمامی موارد فوق را مطالعه کرده و با آن موافق هستید. ✅
"""

# محتوای بخش محصولات نارموون
NARMOON_PRODUCTS = """
🌟 **محصولات نارموون** 🌟

۱. **نارموون دکس (رایگان): **
این محصول در واقع یک افزرنه در چت جی پی تی هستش مخصوص توکن های دکس که کاربران برای استفاده از این افزونه حتما باید اپلیکیشن چت جی پی تی رو دانلود و نصب کنن و براحتی با کلیک بر روی لینک زیر ازش استفاده کنن.

۲. **نارموون کوین (رایگان): **
این محصول در واقع یک افزرنه در چت جی پی تی هستش مخصوص آلتکوین ها و توکن های خارج از فضای دکس که کاربران برای استفاده از این افزونه حتما باید اپلیکیشن چت جی پی تی رو دانلود و نصب کنن و براحتی با کلیک بر روی لینک زیر ازش استفاده کنن.

۳. **نارموون TNT (ویژه Pro): **
پیشرفته‌ترین ابزار تحلیل چارت، مخصوص کاربران پرو با دسترسی به مدل‌های AI اختصاصی و ستاپ معاملاتی دقیق. برای فعال‌سازی، اشتراک پرو رو تهیه کن!

برای استفاده از هر محصول، گزینه مربوطه را انتخاب کنید:
"""

# محتوای بخش قابلیت‌های دستیار هوش مصنوعی
AI_ASSISTANT_FEATURES = """
🧠 **قابلیت‌های دستیار هوش مصنوعی نارموون** 🧠

🔹 **تحلیل تکنیکال پیشرفته**
- آنالیز سه‌تایم‌فریمی برای درک جامع روند
- شناسایی دقیق الگوهای قیمتی (مثلث، سر و شانه، کف دوقلو و...)
- ترسیم خودکار سطوح فیبوناچی و محاسبه نقاط بازگشت احتمالی
- تشخیص واگرایی‌ها و هشدار به معامله‌گر

🔹 **سیگنال‌دهی هوشمند**
- ارائه سیگنال‌های معاملاتی با R/R (ریسک به ریوارد) مشخص
- تعیین نقاط دقیق ورود، حد ضرر و اهداف قیمتی
- پیشنهاد استراتژی‌های کم‌ریسک و پرریسک با توجه به شرایط بازار
- بروزرسانی‌های خودکار بر اساس آخرین داده‌های بازار

🔹 **پشتیبانی از انواع بازارها**
- ارزهای دیجیتال (بیت‌کوین، اتریوم و صدها رمزارز دیگر)
- فارکس (جفت ارزهای اصلی و فرعی)
- طلا، نقره و سایر فلزات گرانبها
- سهام (بازارهای ایران، آمریکا و سایر بورس‌های جهانی)

🔹 **هوش مصنوعی پیشرفته**
- پردازش تصویر برای تحلیل نمودارها در هر فرمت
- یادگیری مداوم و بهبود دقت تحلیل‌ها
- استفاده از الگوریتم‌های پیشرفته برای پیش‌بینی حرکات قیمت
- قابلیت تشخیص شرایط خاص بازار مانند نوسانات شدید یا روندهای کاذب

🔹 **تجربه کاربری راحت**
- رابط کاربری ساده و بدون پیچیدگی
- پاسخگویی سریع به درخواست‌های تحلیل
- امکان استفاده در هر زمان و مکان
- قابلیت ذخیره و مرور تحلیل‌های قبلی
"""

# محتوای بخش سوالات متداول
FAQ_CONTENT = """
❓ **سوالات متداول** ❓

۱- نارموون دقیقاً چیه و چه کاری برام انجام می‌ده؟
نارموون یک دستیار هوش مصنوعی تحلیل‌گر بر پایه و Grok3 GPT-4o هست که بازار رمزارزها رو به‌صورت لحظه‌ای رصد می‌کنه، توکن‌های ترند رو پیدا می‌کنه، سیگنال خرید/فروش می‌ده و همه چیز از تحلیل تکنیکال، آنچین تا بررسی امنیت و اخبار رو توی یک ابزار برات جمع می‌کنه. البته این تمام ماجرا نیست،استفاده از قویترین مدل های هوش مصنوعی باعث شده که این ابزار بتونه در تمامی بازار ها از جمله فارکس-طلا-سهام امریکا و ایران تحلیل های بی نظری برای شما ارائه بده.

۲- آیا نارموون امکان خرید یا فروش مستقیم رمزارز داره؟
خیر. نارموون صرفاً یک ابزار تحلیل و سیگنال‌دهی هوشمنده. خرید یا فروش رمزارز باید از طریق صرافی‌هایی که باهاشون کار می‌کنید انجام بشه.

۳- چطور مطمئن باشم که توکن‌ها اسکم یا راگ نیستن؟
نارموون با بررسی سن پروژه، تعداد هولدرها، حجم معاملات، نقدینگی، اسمارت کانترکت و تحلیل چارت راگ‌پول احتمال اسکم بودن توکن‌ها رو کاهش می‌ده و حتی هشدارهای امنیتی نشون می‌ده.

۴- سیگنال‌هایی که نارموون می‌ده قابل اطمینان هستن؟
ابزار هوش مصنوعی نارموون با بیش از ۵۰ الگوریتم‌ تحلیلی بهترین پیش بینی رو از بازار برای شما ارائه میکنه؛ اما تصمیم نهایی برای معامله با کاربره و نارموون هیچ‌گونه مسئولیت مالی نداره.

۵- آیا برای استفاده باید اطلاعات حساب صرافی و یا بروکر رو وارد کنم؟
نه! نارموون هیچ اطلاعاتی مثل API، یوزرنیم یا رمز عبور صرافی یا بروکر ازت نمی‌خواد. اطلاعاتت همیشه محرمانه و امن باقی می‌مونه.

۶- تفاوت بین نارموون دکس و نارموون کوین و نارموون تی ان تی چیه؟
نارموون دکس: مخصوص تحلیل توکن‌های دکس (مثل سولانا، میم‌کوین‌ها)
نارموون کوین: مخصوص تحلیل کوین‌های بزرگ در صرافی‌های متمرکز (BTC, ETH, SOL و آلتکوین‌ها)
نارموون تی ان تی:بر پایه جدیدترین و قویترین مدل های هوش مصنوعی جهت تحلیل تصویر نمودارها و ارائه ستاپ های معاملاتی دقیق هستش.

۷- آیا نارموون به‌روزرسانی می‌شه؟
بله. نارموون به‌صورت پیوسته بروزرسانی می‌شه. اگه قطعی یا تغییرات مهم باشه، از طریق کانال رسمی اطلاع‌رسانی می‌کنیم.

۸- آیا استفاده از نارموون پیچیده‌ست؟
اصلاً! رابط کاربری نارموون ساده، تمیز و برای همه قابل استفاده‌ست — حتی اگه تازه وارد مارکت باشی.

۹-آیا امکان دسترسی به اطلاعات آنچین BTC و ETH هست؟
بله. نارموون کوین می‌تونه آنچین بیتکوین و اتریوم، همچنین رفتار نهنگ‌ها، ورودی‌ها به صرافی‌ها و ذخایر شرکت‌ها رو تحلیل کنه.

۱۰- آیا استفاده غیرمجاز از محتوا یا کپی‌برداری مجازه؟
خیر. هرگونه کپی، انتشار، فروش مجدد یا تغییر محتوا بدون مجوز رسمی پیگرد قانونی داره و خلاف شرایط استفاده محسوب می‌شه.
"""

# لینک‌های مستقیم محصولات نارموون
NARMOON_DEX_LINK = "https://chatgpt.com/g/g-681e61f1baa88191bf50a82156694a79-narmoon-dex"
NARMOON_COIN_LINK = "https://chatgpt.com/g/g-681e68b8ccf08191b5e53b91b4f09c6e-narmoon-coin"

# گزینه‌های تایم‌فریم و بالاتر
TIMEFRAMES = ["۱ دقیقه", "۵ دقیقه", "۱۵ دقیقه", "۱ ساعته", "۴ ساعته", "روزانه", "هفتگی"]
HIGHER_TIMEFRAMES = {
    "۱ دقیقه": ["۵ دقیقه", "۱۵ دقیقه", "۱ ساعته"],
    "۵ دقیقه": ["۱۵ دقیقه", "۱ ساعته", "۴ ساعته"],
    "۱۵ دقیقه": ["۱ ساعته", "۴ ساعته", "روزانه"],
    "۱ ساعته": ["۴ ساعته", "روزانه", "هفتگی"],
    "۴ ساعته": ["روزانه", "هفتگی", "ماهانه"],
    "روزانه": ["هفتگی", "ماهانه", "سالانه"],
    "هفتگی": ["ماهانه", "سالانه", "ده‌ساله"],
}

# وضعیت‌های ConversationHandler
MAIN_MENU, SELECTING_TIMEFRAME, WAITING_IMAGES = range(3)

# دستورالعمل تحلیل
VISION_PROMPT = """
تصویر نمودار را فقط با داده تصویری و طبق ساختار زیر، به صورت بولت‌پوینت و بدون جدول تحلیل کن:

۱. پردازش اولیه:
- تایم‌فریم (W1/D1/4H) و جفت ارز را شناسایی کن
- روند هر تایم‌فریم: صعودی/نزولی/رنج
- قیمت فعلی و نوع آخرین کندل (مثلاً مارابوزو، دوجی، پین‌بار)

۲. تحلیل سطوح و الگوها:
- سه حمایت و سه مقاومت کلیدی با قیمت دقیق (مثلاً "۱.۲۰۰۰")
- قدرت هر سطح: ضعیف/متوسط/قوی (بر اساس برخورد و حجم)
- سطوح فیبوناچی اصلی با قیمت دقیق (۳۸.۲٪، ۵۰٪، ۶۱.۸٪، ۱۶۱.۸٪)
- مهم‌ترین الگو یا کندل ویژه (مثل انگالفینگ یا پین‌بار روی سطح)
- حجم معاملات و واگرایی‌ها در نقاط کلیدی

۳. تحلیل چندتایم‌فریمی:
- روند غالب و محدوده‌های همپوشان (Confluence)
- سطح کلیدی مشترک بین تایم‌فریم‌ها (در صورت وجود)
- تأیید یا تناقض سیگنال‌ها بین تایم‌فریم‌ها

۴. سناریوهای احتمالی:
- صعودی: شرط شکست مقاومت [عدد دقیق]، اهداف [عدد فیبوناچی و مقاومت بعدی]، احتمال (در صورت امکان)
- نزولی: شرط شکست حمایت [عدد دقیق]، اهداف [عدد فیبوناچی و حمایت بعدی]، احتمال
- رنج: محدوده حرکت [X تا Y] و نقاط حساس شکست

۵. سیگنال عملی (در صورت وجود همه شرایط زیر):
- ورود (Entry): [عدد دقیق]
- استاپ داینامیک:  
    • محدوده هشدار (Stop Warning): [مثلاً ۲-۳٪ زیر سطح کلیدی]
    • محدوده خروج کامل (Hard Stop): [مثلاً زیر حمایت اصلی/سوینگ لو یا بالای مقاومت]
- تارگت ۱: [عدد دقیق یا سطح مقاومت]
- تارگت ۲: [عدد دقیق یا فیبو (مثلاً "۱.۵۱۸ (فیبو ۱۶۱.۸٪)")]
- R/R: حداقل ۱:۲ (بر اساس Hard Stop)
- منطق کوتاه سیگنال (مثلاً "برگشت از حمایت قوی + تایید حجم")

۶. مدیریت ریسک و هشدار:
- حداکثر ریسک هر معامله: ۱-۲٪
- محدوده هشدار و خروج کامل را در مدیریت ریسک تکرار کن (کاملاً هماهنگ با بخش سیگنال)
- هشدار ویژه: احتمال فیک بریک‌اوت، نوسانات شدید، خبر مهم

۷. جمع‌بندی و توصیه نهایی:
- خلاصه روند و نکته کلیدی معامله (تا ۵ بولت‌پوینت کوتاه)
- توصیه نهایی: خرید/فروش/انتظار (با شرط عددی دقیق)

**مهم:**
- فقط بولت‌پوینت (بدون جدول یا توضیح اضافه)
- تحلیل فقط با داده تصویر و قیمت‌های عددی دقیق
- عبارات تردیدی ("شاید"، "ممکن است") ممنوع
- اگر شرایط سیگنال کامل نبود فقط تحلیل و سناریو ارائه بده
- تارگت‌های فیبوناچی حتماً با قیمت دقیق ذکر شود
- استاپ داینامیک همیشه شامل محدوده هشدار و محدوده خروج باشد
- خروجی حرفه‌ای، مختصر و کاملاً قابل اجرا باشد
"""

# توابع پایگاه داده
def init_db():
    """ایجاد پایگاه داده و جداول مورد نیاز"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # ایجاد جدول کاربران
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        subscription_end DATE,
        subscription_type TEXT,
        is_active BOOLEAN DEFAULT 0
    )
    ''')
    
    # ایجاد جدول تراکنش‌ها
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        txid TEXT,
        wallet_address TEXT,
        amount REAL,
        subscription_type TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def check_subscription(user_id):
    """بررسی وضعیت اشتراک کاربر"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT subscription_end, is_active FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False
    
    end_date_str, is_active = result
    if not is_active:
        conn.close()
        return False
    
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    today = datetime.date.today()
    
    conn.close()
    return end_date >= today

def register_user(user_id, username):
    """ثبت کاربر جدید در دیتابیس"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.commit()
    
    conn.close()

def activate_subscription(user_id, duration_months, sub_type):
    """فعال‌سازی اشتراک کاربر"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=30 * duration_months)
    
    cursor.execute(
        "UPDATE users SET subscription_end = ?, subscription_type = ?, is_active = 1 WHERE user_id = ?",
        (end_date.strftime('%Y-%m-%d'), sub_type, user_id)
    )
    
    conn.commit()
    conn.close()
    return end_date.strftime('%Y-%m-%d')

# توابع اصلی ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات و نمایش منوی اصلی"""
    # ریست وضعیت کاربر
    context.user_data.clear()
    
    # ثبت کاربر در دیتابیس
    user_id = update.effective_user.id
    username = update.effective_user.username
    register_user(user_id, username)
    
    # ایجاد منوی اصلی
    main_menu_buttons = [
        [InlineKeyboardButton("📊 تحلیل نمودارها", callback_data="analyze_charts")],
        [InlineKeyboardButton("📚 راهنمای استفاده", callback_data="guide")],
        [InlineKeyboardButton("🛒 محصولات نارموون", callback_data="narmoon_products")],
        [InlineKeyboardButton("💳 خرید اشتراک", callback_data="subscription")],
        [InlineKeyboardButton("🧠 قابلیت‌های دستیار هوش مصنوعی", callback_data="ai_features")],
        [InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")],
        [InlineKeyboardButton("📜 قوانین و مقررات", callback_data="terms")],
        [InlineKeyboardButton("👨‍💻 ارتباط با پشتیبانی", callback_data="support")]
    ]
    
    main_menu_markup = InlineKeyboardMarkup(main_menu_buttons)
    
    # پیام خوشامدگویی با منوی اصلی
    # دریافت نام کاربر برای شخصی‌سازی پیام
    user_name = update.effective_user.first_name if update.effective_user.first_name else "کاربر"
    
    welcome_text = f"""
سلام {user_name} عزیز! 👋✨ به دستیار هوش مصنوعی معامله‌گری **نارموون** خوش اومدی!

🚀 اینجا جاییه که می‌تونی بازار رمزارزها، فارکس، طلا، سهام(ایران و آمریکا و یا هر کشور دیگه) رو با قدرت هوش مصنوعی تحلیل کنی، سیگنال بگیری و همیشه یک قدم جلوتر از بازار باشی.

🔹 برای شروع می‌تونی از منوی پایین یکی از گزینه‌ها رو انتخاب کنی!
"""
    
    # اگر callback_query داریم (برگشت به منوی اصلی) از آن استفاده کنیم، در غیر این صورت پیام جدید بفرستیم
    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=main_menu_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=main_menu_markup,
            parse_mode='Markdown'
        )
    
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دکمه‌های فشرده شده در منوی اصلی"""
    
    query = update.callback_query
    await query.answer()  # پاسخ به کلیک دکمه
    
    # بررسی کدام دکمه فشرده شده است
    if query.data == "main_menu":
        return await start(update, context)
    elif query.data == "guide":
        return await usage_guide(update, context)
    elif query.data == "terms":
        return await terms_and_conditions(update, context)
    elif query.data == "subscription":
        return await subscription_plans(update, context)
    elif query.data == "support":
        return await support_contact(update, context)
    elif query.data == "narmoon_products":
        return await show_narmoon_products(update, context)
    elif query.data == "ai_features":
        return await show_ai_features(update, context)
    elif query.data == "faq":
        return await show_faq(update, context)
    elif query.data == "analyze_charts":
        # بررسی وضعیت اشتراک کاربر
        user_id = update.effective_user.id
        if check_subscription(user_id):
            # اگر اشتراک فعال دارد، به منوی تایم‌فریم‌ها برود
            return await show_timeframes(update, context)
        else:
            # اگر اشتراک ندارد، پیام خطا و پیشنهاد خرید نمایش داده شود
            subscription_buttons = [
                [InlineKeyboardButton("💳 خرید اشتراک", callback_data="subscription")],
                [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
            ]
            await query.edit_message_text(
                "⚠️ برای استفاده از بخش تحلیل نمودارها نیاز به اشتراک فعال دارید.",
                reply_markup=InlineKeyboardMarkup(subscription_buttons)
            )
            return MAIN_MENU
    elif query.data == "free_trial":
        # اشتراک رایگان
        context.user_data['selected_plan'] = "رایگان"
        context.user_data['plan_duration'] = 0.1  # حدود 3 روز
        
        # فعال‌سازی مستقیم اشتراک رایگان
        user_id = update.effective_user.id
        end_date = activate_subscription(user_id, 0.1, "رایگان")
        
        free_buttons = [
            [InlineKeyboardButton("📊 شروع تحلیل", callback_data="analyze_charts")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            f"🎉 اشتراک رایگان شما با موفقیت فعال شد!\n\nتاریخ پایان: {end_date}\n\nمی‌توانید از همین حالا از امکانات ربات استفاده کنید.",
            reply_markup=InlineKeyboardMarkup(free_buttons)
        )
        return MAIN_MENU
    elif query.data == "sub_1month":
        # اشتراک ماهانه
        context.user_data['selected_plan'] = "ماهانه"
        context.user_data['plan_amount'] = 14.99
        context.user_data['plan_duration'] = 1
        return await show_payment_info(update, context)
    elif query.data == "sub_3month":
        # اشتراک سه ماهه
        context.user_data['selected_plan'] = "سه ماهه"
        context.user_data['plan_amount'] = 39.99
        context.user_data['plan_duration'] = 3
        return await show_payment_info(update, context)
    
    return MAIN_MENU

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب تایم‌فریم"""
    query = update.callback_query
    await query.answer()
    
    selected_tf = query.data.replace("tf_", "")
    context.user_data['selected_timeframe'] = selected_tf
    context.user_data['expected_frames'] = HIGHER_TIMEFRAMES[selected_tf]
    context.user_data['received_images'] = []
    tf_list = ", ".join(HIGHER_TIMEFRAMES[selected_tf])
    
    await query.edit_message_text(
        f"عالیه! 👏 حالا لطفاً **۳ اسکرین‌شات** از چارت {tf_list} رو (در هر فرمتی) یکی‌یکی ارسال کن 📸\n\nبرای لغو تحلیل، دستور /cancel را بفرست.",
        parse_mode='Markdown'
    )
    
    return WAITING_IMAGES

# توابع منوها و بخش‌ها
async def show_narmoon_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش محصولات نارموون"""
    products_buttons = [
        [InlineKeyboardButton("🔄 نارموون دکس (رایگان)", url=NARMOON_DEX_LINK)],
        [InlineKeyboardButton("💰 نارموون کوین (رایگان)", url=NARMOON_COIN_LINK)],
        [InlineKeyboardButton("🤖 نارموون TNT (ویژه Pro)", callback_data="subscription")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    
    products_markup = InlineKeyboardMarkup(products_buttons)
    
    await update.callback_query.edit_message_text(
        NARMOON_PRODUCTS,
        reply_markup=products_markup,
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def show_ai_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قابلیت‌های دستیار هوش مصنوعی"""
    features_buttons = [
        [InlineKeyboardButton("💳 خرید اشتراک", callback_data="subscription")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    
    features_markup = InlineKeyboardMarkup(features_buttons)
    
    await update.callback_query.edit_message_text(
        AI_ASSISTANT_FEATURES,
        reply_markup=features_markup,
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سوالات متداول"""
    faq_buttons = [
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    
    faq_markup = InlineKeyboardMarkup(faq_buttons)
    
    await update.callback_query.edit_message_text(
        FAQ_CONTENT,
        reply_markup=faq_markup,
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش راهنمای استفاده از ربات"""
    guide_text = f"""
📚 راهنمای استفاده از ربات تحلیل چارت

برای آشنایی کامل با نحوه استفاده از ربات، لطفاً ویدیوی آموزشی زیر را مشاهده کنید:

🎬 [مشاهده ویدیوی آموزشی]({TUTORIAL_VIDEO_LINK})

راهنمای سریع:
1️⃣ ابتدا اشتراک خود را از بخش «خرید اشتراک» تهیه کنید
2️⃣ بعد از پرداخت، TXID را به پشتیبان ارسال کنید
3️⃣ پس از تأیید، می‌توانید از بخش «تحلیل نمودارها» استفاده کنید
4️⃣ تایم‌فریم مورد نظر را انتخاب کرده و سه تصویر از چارت در تایم‌فریم‌های مختلف ارسال کنید
5️⃣ تحلیل کامل را دریافت کنید
"""
    
    guide_buttons = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]]
    guide_markup = InlineKeyboardMarkup(guide_buttons)
    
    await update.callback_query.edit_message_text(
        guide_text, 
        reply_markup=guide_markup,
        parse_mode='Markdown',
        disable_web_page_preview=False  # اجازه می‌دهد پیش‌نمایش ویدیو نمایش داده شود
    )
    
    return MAIN_MENU

async def terms_and_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قوانین و مقررات"""
    
    terms_buttons = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]]
    terms_markup = InlineKeyboardMarkup(terms_buttons)
    
    await update.callback_query.edit_message_text(
        TERMS_AND_CONDITIONS, 
        reply_markup=terms_markup,
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def subscription_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پلن‌های اشتراکی"""
    subscription_text = """
💳 پلن‌های اشتراکی دستیار هوش مصنوعی نارموون

لطفاً یکی از پلن‌های زیر را انتخاب کنید:

🔄 **نارموون دکس (رایگان)**: افزونه چت‌جی‌پی‌تی مخصوص تحلیل توکن‌های دکس

💰 **نارموون کوین (رایگان)**: افزونه چت‌جی‌پی‌تی مخصوص تحلیل آلتکوین‌ها

🤖 **نارموون TNT (ویژه Pro)**:
🔹 **ماهانه:** ۱۴،۹۹ دلار برای یک ماه دسترسی کامل به تمام امکانات ربات
🔹 **سه ماهه (پیشنهاد ویژه):** ۳۹،۹۹ دلار برای سه ماه — معادل ماهی فقط ۱۳،۳۳ دلار! 💡
"""
    
    subscription_buttons = [
        [InlineKeyboardButton("🔄 نارموون دکس (رایگان)", url=NARMOON_DEX_LINK)],
        [InlineKeyboardButton("💰 نارموون کوین (رایگان)", url=NARMOON_COIN_LINK)],
        [InlineKeyboardButton("🤖 نارموون TNT ماهانه (۱۴،۹۹ دلار)", callback_data="sub_1month")],
        [InlineKeyboardButton("🤖 نارموون TNT سه ماهه (۳۹،۹۹ دلار)", callback_data="sub_3month")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    
    subscription_markup = InlineKeyboardMarkup(subscription_buttons)
    
    # اگر callback_query داریم از آن استفاده کنیم، در غیر این صورت مستقیم پیام بفرستیم
    if update.callback_query:
        await update.callback_query.edit_message_text(
            subscription_text, 
            reply_markup=subscription_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            subscription_text,
            reply_markup=subscription_markup,
            parse_mode='Markdown'
        )
    
    return MAIN_MENU

async def show_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات پرداخت و کیف پول"""
    try:
        # انتخاب تصادفی یک آدرس کیف پول
        wallet_address = random.choice(SOLANA_WALLETS)
        
        # ذخیره آدرس انتخاب شده در دیتای کاربر
        context.user_data['selected_wallet'] = wallet_address
        
        plan = context.user_data['selected_plan']
        amount = context.user_data['plan_amount']
        
        payment_text = f"""
💎 اطلاعات پرداخت اشتراک {plan}

مبلغ: {amount} دلار
آدرس کیف پول سولانا:

<code>{wallet_address}</code>

لطفا پس از پرداخت، با پشتیبان تماس بگیرید و شناسه تراکنش (TXID) را برای فعال‌سازی اشتراک ارسال کنید.

@Sultan_immortal
"""
        
        payment_buttons = [[InlineKeyboardButton("🔙 بازگشت", callback_data="subscription")]]
        payment_markup = InlineKeyboardMarkup(payment_buttons)
        
        await update.callback_query.edit_message_text(
            payment_text, 
            reply_markup=payment_markup,
            parse_mode='HTML'  # استفاده از HTML بجای Markdown
        )
    except Exception as e:
        print(f"Error in show_payment_info: {str(e)}")
        try:
            # روش جایگزین در صورت بروز خطا
            await update.callback_query.message.reply_text(
                payment_text,
                reply_markup=payment_markup,
                parse_mode='HTML'
            )
        except Exception as e2:
            print(f"Second attempt also failed: {str(e2)}")
    
    return MAIN_MENU

async def support_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات تماس با پشتیبان"""
    support_text = """
\U0001F468\u200D\U0001F4BB پشتیبانی ربات تحلیل چارت

برای ارتباط با پشتیبان و ارسال TXID پرداخت، لطفاً با آیدی زیر در تلگرام تماس بگیرید:

@Sultan_immortal

می‌توانید روی لینک زیر کلیک کنید:
https://t.me/Sultan_immortal

\U0001F4DD راهنمای ارسال TXID به پشتیبان:
1. پس از پرداخت، شناسه تراکنش (TXID) را کپی کنید
2. به پشتیبان پیام بدهید و TXID را ارسال کنید
3. آیدی تلگرام خود را هم ذکر کنید
4. پس از تأیید تراکنش، اشتراک شما فعال خواهد شد
"""
    
    # دکمه بازگشت به منوی اصلی
    back_button = [[InlineKeyboardButton("\U0001F519 بازگشت به منوی اصلی", callback_data="main_menu")]]
    back_markup = InlineKeyboardMarkup(back_button)
    
    await update.callback_query.edit_message_text(
        support_text, 
        reply_markup=back_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    return MAIN_MENU

async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست تایم‌فریم‌ها برای انتخاب"""
    timeframe_buttons = []
    for tf in TIMEFRAMES:
        timeframe_buttons.append([InlineKeyboardButton(tf, callback_data=f"tf_{tf}")])
    
    timeframe_buttons.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")])
    timeframe_markup = InlineKeyboardMarkup(timeframe_buttons)
    
    await update.callback_query.edit_message_text(
        "لطفاً تایم‌فریم مورد نظر خود را انتخاب کنید:",
        reply_markup=timeframe_markup
    )
    
    return SELECTING_TIMEFRAME

async def receive_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت تصاویر چارت از کاربر"""
    # بررسی اشتراک کاربر
    user_id = update.effective_user.id
    if not check_subscription(user_id):
        subscription_buttons = [
            [InlineKeyboardButton("💳 خرید اشتراک", callback_data="subscription")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        await update.message.reply_text(
            "⚠️ اشتراک شما منقضی شده یا فعال نیست. لطفاً اشتراک خود را تمدید کنید.",
            reply_markup=InlineKeyboardMarkup(subscription_buttons)
        )
        return MAIN_MENU
    
    file = None
    ext = "jpeg"
    # پشتیبانی از عکس یا داکیومنت عکس
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
    elif update.message.document and update.message.document.mime_type.startswith('image/'):
        file = await update.message.document.get_file()
        ext = update.message.document.mime_type.split('/')[-1]
    else:
        await update.message.reply_text("فقط عکس ارسال کن رفیق! 😅")
        return WAITING_IMAGES

    photo_bytes = await file.download_as_bytearray()
    context.user_data['received_images'].append((photo_bytes, ext))

    received = len(context.user_data['received_images'])
    expected = 3

    if received < expected:
        await update.message.reply_text(f"عالی! {expected-received} عکس دیگه از تایم‌فریم‌های بعدی رو بفرست 🤩")
        return WAITING_IMAGES

    # وقتی هر سه عکس رسید...
    await update.message.reply_text("در حال تحلیل هر سه چارت... ⏳🔥")

    # آماده‌سازی عکس‌ها برای openai vision
    images_content = []
    for img_bytes, ext in context.user_data['received_images']:
        # تعیین mime type
        if ext in ["jpeg", "jpg"]:
            mime = "jpeg"
        elif ext == "png":
            mime = "png"
        elif ext == "webp":
            mime = "webp"
        else:
            mime = "jpeg"
        b64img = base64.b64encode(img_bytes).decode('utf-8')
        images_content.append({"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{b64img}", "detail": "high"}})

    # پیامی با چند تصویر
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": VISION_PROMPT}
            ] + images_content
        }
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1300,
            temperature=0.2
        )
        result = response.choices[0].message.content

        # دکمه بازگشت به منوی اصلی
        menu_button = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]])
        
        await update.message.reply_text(
            "✅ نتیجه تحلیل سه‌تایم‌فریم:\n\n" + result,
            reply_markup=menu_button
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در تحلیل! دوباره تلاش کن یا /start رو بزن.\n{str(e)}")

    context.user_data.clear()
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات جاری و بازگشت به منوی اصلی"""
    context.user_data.clear()
    
    # دکمه بازگشت به منوی اصلی
    menu_button = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]])
    
    await update.message.reply_text(
        "عملیات لغو شد. می‌توانید به منوی اصلی بازگردید.",
        reply_markup=menu_button
    )
    return MAIN_MENU

# دستورات مدیریتی برای ادمین
async def admin_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فعال‌سازی اشتراک کاربر توسط ادمین (فرمت: /activate user_id duration plan_type)"""
    # بررسی دسترسی ادمین
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("شما دسترسی به این دستور را ندارید.")
        return
    
    try:
        # بررسی پارامترها
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("فرمت صحیح: /activate user_id duration plan_type\nمثال: /activate 123456789 3 سه_ماهه")
            return
        
        user_id = int(args[0])
        duration = int(args[1])
        plan_type = args[2]
        
        # فعال‌سازی اشتراک
        end_date = activate_subscription(user_id, duration, plan_type)
        
        # ارسال پیام به ادمین
        await update.message.reply_text(f"اشتراک کاربر {user_id} با موفقیت فعال شد.\nتاریخ پایان: {end_date}")
        
        # ارسال پیام به کاربر
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 اشتراک شما با موفقیت فعال شد!\n\nنوع اشتراک: {plan_type}\nتاریخ پایان: {end_date}\n\nاز خرید شما متشکریم! برای شروع تحلیل چارت، دستور /start را بزنید."
            )
        except Exception as e:
            await update.message.reply_text(f"اشتراک فعال شد اما ارسال پیام به کاربر با خطا مواجه شد: {str(e)}")
    
    except Exception as e:
        await update.message.reply_text(f"خطا در فعال‌سازی اشتراک: {str(e)}")

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای دستورات ادمین"""
    # بررسی دسترسی ادمین
    if update.effective_user.id != ADMIN_ID:
        return
    
    help_text = """
\U0001F468\u200D\U0001F4BB راهنمای دستورات مدیریتی:

/adminhelp - نمایش این راهنما
/activate user_id duration plan_type - فعال‌سازی اشتراک کاربر
مثال: /activate 123456789 3 سه_ماهه

/userinfo user_id - نمایش اطلاعات کاربر
مثال: /userinfo 123456789
"""
    
    await update.message.reply_text(help_text)

async def admin_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات کاربر برای ادمین"""
    # بررسی دسترسی ادمین
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        # بررسی پارامترها
        args = context.args
        if not args:
            await update.message.reply_text("فرمت صحیح: /userinfo user_id\nمثال: /userinfo 123456789")
            return
        
        user_id = int(args[0])
        
        # دریافت اطلاعات کاربر از دیتابیس
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            await update.message.reply_text(f"کاربری با شناسه {user_id} یافت نشد.")
            conn.close()
            return
        
        # نمایش اطلاعات کاربر
        user_info = f"""
👤 اطلاعات کاربر:

شناسه: {user_data[0]}
نام کاربری: {user_data[1] or 'نامشخص'}
تاریخ پایان اشتراک: {user_data[2] or 'ندارد'}
نوع اشتراک: {user_data[3] or 'ندارد'}
وضعیت اشتراک: {'فعال' if user_data[4] else 'غیرفعال'}
"""
        
        # نمایش تراکنش‌های کاربر
        cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
        transactions = cursor.fetchall()
        
        if transactions:
            user_info += "\n💰 تراکنش‌های اخیر:\n"
            for tx in transactions:
                user_info += f"TXID: {tx[2]}\nکیف پول: {tx[3]}\nمبلغ: {tx[4]}\nوضعیت: {tx[6]}\nتاریخ: {tx[7]}\n\n"
        
        conn.close()
        await update.message.reply_text(user_info)
        
    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت اطلاعات کاربر: {str(e)}")

def main():
    # ایجاد پایگاه داده
    init_db()
    
    # ایجاد اپلیکیشن
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # تعریف conversation handler اصلی
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(handle_main_menu)],
            SELECTING_TIMEFRAME: [CallbackQueryHandler(handle_timeframe_selection, pattern='^tf_')],
            WAITING_IMAGES: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_images)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    
    # افزودن هندلرها
    app.add_handler(conv_handler)
    
    # دستورات مدیریتی
    app.add_handler(CommandHandler("activate", admin_activate))
    app.add_handler(CommandHandler("adminhelp", admin_help))
    app.add_handler(CommandHandler("userinfo", admin_user_info))
    
    print("ربات آماده است! اجرا شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
