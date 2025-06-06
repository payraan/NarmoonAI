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
اصلاً! رابط کاربری نارموون ساده، تمیز و برای همه قابل استفاده‌ست --- حتی اگه تازه وارد مارکت باشی.

۹-آیا امکان دسترسی به اطلاعات آنچین BTC و ETH هست؟
بله. نارموون کوین می‌تونه آنچین بیتکوین و اتریوم، همچنین رفتار نهنگ‌ها، ورودی‌ها به صرافی‌ها و ذخایر شرکت‌ها رو تحلیل کنه.

۱۰- آیا استفاده غیرمجاز از محتوا یا کپی‌برداری مجازه؟
خیر. هرگونه کپی، انتشار، فروش مجدد یا تغییر محتوا بدون مجوز رسمی پیگرد قانونی داره و خلاف شرایط استفاده محسوب می‌شه.
"""

# لینک‌های مستقیم محصولات نارموون
NARMOON_DEX_LINK = "https://chatgpt.com/g/g-681e61f1baa88191bf50a82156694a79-narmoon-dex"
NARMOON_COIN_LINK = "https://chatgpt.com/g/g-681e68b8ccf08191b5e53b91b4f09c6e-narmoon-coin"

# === بازارها ===
MARKETS = {
    'crypto': '🔗 رمزارزها (کریپتوکارنسی)',
    'forex': '💱 فارکس (جفت ارزها)',
    'gold': '🥇 طلا',
    'international_stocks': '📈 سهام خارجی',
    'iranian_stocks': '📊 سهام ایران'
}

# === تایم فریم‌ها ===
TIMEFRAMES = ["۱ دقیقه", "۵ دقیقه", "۱۵ دقیقه", "۱ ساعته", "۴ ساعته", "روزانه", "هفتگی"]

# تغییر در EXPECTED_TIMEFRAMES - حالا شامل خود تایم فریم انتخابی هم می‌شود
EXPECTED_TIMEFRAMES = {
    "۱ دقیقه": ["۱ دقیقه", "۵ دقیقه", "۱۵ دقیقه"],
    "۵ دقیقه": ["۵ دقیقه", "۱۵ دقیقه", "۱ ساعته"],
    "۱۵ دقیقه": ["۱۵ دقیقه", "۱ ساعته", "۴ ساعته"],
    "۱ ساعته": ["۱ ساعته", "۴ ساعته", "روزانه"],
    "۴ ساعته": ["۴ ساعته", "روزانه", "هفتگی"],
    "روزانه": ["روزانه", "هفتگی", "ماهانه"],
    "هفتگی": ["هفتگی", "ماهانه", "سالانه"],
}

# === استراتژی‌های معاملاتی ===
STRATEGIES = {
    # دسته اول: استراتژی های شخصی
    'narmoon_ai': '🤖 استراتژی شخصی هوش مصنوعی نارموون',
    
    # دسته دوم: اسکالپینگ
    'ema_scalping': '⚡ اسکالپینگ با EMA',
    'rsi_scalping': '📊 اسکالپینگ با RSI',
    'squeeze_momentum': '💥 اسکوییز مومنتوم (شتاب ناگهانی)',
    'volatility_breakout': '🔥 شکست نوسان (Volatility Breakout)',
    'breakout_retest': '🔄 پولبک به شکست (Breakout Retest)',
    'mean_reversion': '⚖️ بازگشت به میانگین (Mean Reversion)',
    
    # دسته سوم: سوئینگ
    'momentum_swing': '🚀 مومنتوم سوئینگ (نوسان با شتاب)',
    'trend_following': '📈 دنبال‌کننده روند (Trend Following)',
    'trend_reversal': '🔀 برگشت روند (Trend Reversal)',
    'divergence_play': '📉 معامله بر اساس واگرایی (Divergence Play)',
    'continuation_pattern': '🔁 الگوی ادامه‌دهنده (Continuation Pattern)',
    'range_bound': '📏 معامله در محدوده رنج (Range Bound)',
    
    # دسته چهارم: پیشرفته
    'triple_confluence': '🎯 همگرایی سه‌گانه (Triple Confluence)',
    'pullback_retracement': '↩️ اصلاح پولبک (Pullback Retracement)',
    'liquidity_sweep': '🌊 لیکوئیدیتی سویپ (جارو یا شکار نقدینگی)'
}

# === پرامپت‌های اختصاصی برای هر استراتژی ===
STRATEGY_PROMPTS = {
    'narmoon_ai': """
تصویر نمودار را با تمرکز روی سطوح حمایت/مقاومت و سطوح عرضه/تقاضا تحلیل کن:

۱. پردازش اولیه:
- تایم‌فریم‌ها و جفت ارز را شناسایی کن  
- روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
- قیمت فعلی و نوع آخرین کندل

۲. شناسایی محدوده‌های کلیدی:
**محدوده‌های حمایتی:**
- محدوده ۱: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی
- محدوده ۲: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی  
- محدوده ۳: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی

**محدوده‌های مقاومتی:**
- محدوده ۱: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی
- محدوده ۲: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی
- محدوده ۳: [X.XXX - X.XXX] - قدرت: ضعیف/متوسط/قوی

قدرت بر اساس: تعداد برخورد، حجم واکنش، اهمیت تایم‌فریم

۳. سطوح عرضه و تقاضا:
- نواحی عرضه قوی (منطقه‌هایی که قیمت سریع از آن منطقه خارج شده)
- نواحی تقاضای قوی (منطقه‌هایی که قیمت سریع از آن منطقه صعود کرده)
- کیفیت هر ناحیه: تازه/کهنه، قوی/ضعیف

۴. تحلیل واگرایی (در صورت وجود RSI در تصویر):
- واگرایی مثبت: RSI صعودی در حالی که قیمت نزولی
- واگرایی منفی: RSI نزولی در حالی که قیمت صعودی
- عدم وجود واگرایی قابل توجه

۵. تحلیل چند تایم‌فریمی:
- محدوده‌های مشترک در تایم‌فریم‌های مختلف
- تأیید روند در تایم‌فریم‌های مختلف
- اولویت‌بندی محدوده‌ها بر اساس اهمیت در چند تایم‌فریم

۶. سناریوهای احتمالی:
- صعودی: شرط شکست [محدوده مقاومت]، اهداف محتمل
- نزولی: شرط شکست [محدوده حمایت]، اهداف محتمل  
- رنج: نوسان بین [محدوده حمایت] و [محدوده مقاومت]

۷. سیگنال‌های معاملاتی (فقط با R/R حداقل ۱:۳):
**نوع ۱ - برگشت از حمایت:**
- شرایط: واکنش مثبت در محدوده حمایت قوی + تأیید کندل/حجم
- ورود: در [محدوده حمایت دقیق]
- استاپ: زیر [محدوده حمایت قوی‌تر که شکستش تغییر روند دهد]  
- تارگت ۱: [نزدیک‌ترین محدوده مقاومت]
- تارگت ۲: [محدوده مقاومت بعدی یا سطح مهم بالاتر]
- R/R محاسبه شده: [عدد دقیق]

**نوع ۲ - شکست مقاومت:**
- شرایط: شکست قاطع محدوده مقاومت + تثبیت + حجم تأیید
- ورود: بعد از تثبیت بالای [محدوده مقاومت]
- استاپ: زیر [محدوده مقاومت شکسته‌شده که حال حمایت شده]
- تارگت ۱: [بر اساس اندازه محدوده رنج قبلی]  
- تارگت ۲: [محدوده مقاومت بعدی مهم]
- R/R محاسبه شده: [عدد دقیق]

منطق سیگنال: [دلیل کوتاه بر اساس قدرت محدوده، واگرایی، یا confluence]

۸. مدیریت ریسک:
- حداکثر ریسک: ۱-۲٪ سرمایه (بر اساس استاپ کامل)
- محدوده هشدار: [قیمت] برای کاهش ۳۰-۵۰% پوزیشن
- استاپ کامل: [همان استاپ ذکرشده در سیگنال]
- استراتژی خروج تدریجی در تارگت‌ها

۹. جمع‌بندی و توصیه:
- قوی‌ترین محدوده حمایت/مقاومت
- بهترین فرصت معاملاتی فعلی
- توصیه نهایی: خرید/فروش/انتظار با شرایط دقیق
- هشدارهای مهم: fake breakout، نوسانات بالا، اخبار

## اصول مهم:
- فقط محدوده‌ها [X.XXX - X.XXX] نه سطوح دقیق
- بدون استفاده از فیبوناچی
- سیگنال فقط با R/R حداقل ۱:۳
- استاپ جایی که شکستش تغییر کامل روند دهد
- هر سیگنال حداقل ۲ تارگت داشته باشد
- تمرکز روی قدرت و کیفیت محدوده‌ها
- استفاده از واگرایی RSI در صورت وجود در تصویر
""",

    'ema_scalping': """
نمودار پیوست‌شده را با استراتژی اسکالپینگ EMA تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
• وضعیت EMAهای کلیدی (مثلاً EMA 9/21/50) و کراس‌ها را بررسی کن

سناریوهای احتمالی:
- صعودی: شرط شکست مقاومت [سطح/محدوده]، اهداف محتمل
- نزولی: شرط شکست حمایت [سطح/محدوده]، اهداف محتمل
- رنج: نوسان بین حمایت و مقاومت

• مناطق ورود بر اساس کراس یا پولبک
• سیگنال پیشنهادی فقط اگر R/R ≥ ۱:۳ باشد (ورود، حد ضرر، تارگت)
• اگر ستاپ معتبر نیست، دلیل را بنویس
• تحلیل را خلاصه و بولت‌پوینت ارائه بده؛ اگر داده کافی نیست، درخواست توضیح کن.
""",

    'rsi_scalping': """
نمودار را با استراتژی اسکالپینگ RSI تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
• مقدار RSI و موقعیت آن (اشباع خرید/فروش) را بنویس
• واگرایی/همگرایی‌های RSI و قیمت

سناریوهای احتمالی:
- صعودی: شکست مقاومت و خروج RSI از اشباع فروش
- نزولی: شکست حمایت و خروج RSI از اشباع خرید
- رنج: نوسان بین دو سطح کلیدی

• سیگنال پیشنهادی فقط با R/R ≥ ۱:۳
• در صورت نبود ستاپ، علت را بنویس
• تحلیل را خلاصه و مرحله‌به‌مرحله؛ در صورت کمبود داده، توضیح بیشتر بخواه.
""",

    'squeeze_momentum': """
لطفاً نمودار را طبق استراتژی اسکوییز مومنتوم تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
• فاز فشردگی و شروع موج انفجار را مشخص کن

سناریوهای احتمالی:
- صعودی: شکست مقاومت و خروج از Squeeze
- نزولی: شکست حمایت و ریزش پس از Squeeze
- رنج: باقی‌ماندن قیمت در محدوده

• سیگنال ورود، حد ضرر و تارگت فقط با R/R ≥ ۱:۳
• اگر ستاپ کامل نبود، دلیل را بنویس
• تحلیل را خلاصه و بولت‌پوینت؛ اگر کافی نبود، توضیح بیشتر بخواه.
""",

    'volatility_breakout': """
نمودار را با استراتژی شکست نوسانی تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
• وضعیت فعلی نوسان و محدوده‌های کلیدی

سناریوهای احتمالی:
- صعودی: شکست مقاومت و ورود به روند صعودی
- نزولی: شکست حمایت و ریزش
- رنج: نوسان بین سطوح کلیدی

• سیگنال ورود، SL و TP فقط اگر R/R ≥ ۱:۳
• در نبود ستاپ معتبر، علت را بنویس
• تحلیل را خلاصه و استاندارد.
""",

    'breakout_retest': """
نمودار را با استراتژی Breakout Retest تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم: صعودی/نزولی/رنج
• سطح شکسته‌شده و رفتار قیمت پس از آن

سناریوهای احتمالی:
- صعودی: پولبک به مقاومت شکسته و ادامه صعود
- نزولی: پولبک به حمایت شکسته و ادامه نزول
- رنج: برگشت‌های سریع قیمت

• سیگنال ورود روی پولبک، SL و TP با R/R ≥ ۱:۳
• اگر ستاپ نیست، علت را بنویس
• تحلیل بولت‌پوینت و خلاصه.
""",

    'mean_reversion': """
نمودار را طبق استراتژی بازگشت به میانگین تحلیل کن:

• تایم‌فریم‌ها و جفت ارز را شناسایی کن
• روند کلی هر تایم‌فریم
• فاصله قیمت با میانگین و سیگنال بازگشت

سناریوهای احتمالی:
- صعودی: بازگشت از کف به میانگین
- نزولی: بازگشت از سقف به میانگین
- رنج: نوسان اطراف میانگین

• سیگنال ورود، SL و TP با R/R ≥ ۱:۳
• در نبود شرایط، دلیل را بنویس
• تحلیل خلاصه و بولت‌پوینت.
""",

    'momentum_swing': """
نمودار را با استراتژی Momentum Swing تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند هر تایم‌فریم
• نقاط شروع و پایان موج‌های شتاب

سناریوهای احتمالی:
- صعودی: ادامه حرکت با شتاب
- نزولی: ریزش شتاب‌دار
- رنج: تضعیف شتاب و ورود به اصلاح

• سیگنال با R/R ≥ ۱:۳
• در نبود ستاپ، علت را توضیح بده
• تحلیل مرحله‌به‌مرحله.
""",

    'trend_following': """
نمودار را با استراتژی دنبال‌کننده روند تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند کلی هر تایم‌فریم
• نقاط ورود روی پولبک یا شکست

سناریوهای احتمالی:
- صعودی: ادامه روند پس از اصلاح
- نزولی: ریزش پیوسته
- رنج: آماده‌سازی برای شکست

• سیگنال فقط با R/R ≥ ۱:۳
• در صورت نبود ستاپ، دلیل را بنویس
• تحلیل گام‌به‌گام و خلاصه.
""",

    'trend_reversal': """
نمودار را با استراتژی برگشت روند تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند کلی هر تایم‌فریم
• نشانه‌های بازگشت (واگرایی، کندل خاص، الگوی کلاسیک)

سناریوهای احتمالی:
- صعودی: پایان روند نزولی و آغاز صعود
- نزولی: پایان صعود و شروع نزول
- رنج: ورود قیمت به فاز بی‌تصمیمی

• سیگنال پیشنهادی با R/R ≥ ۱:۳
• در نبود ستاپ، علت را بنویس
• تحلیل خلاصه و مرحله‌ای.
""",

    'divergence_play': """
نمودار را با محوریت واگرایی تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند کلی
• واگرایی معمولی/مخفی بین قیمت و اندیکاتور

سناریوهای احتمالی:
- صعودی: واگرایی مثبت، احتمال رشد
- نزولی: واگرایی منفی، احتمال ریزش
- رنج: نبود سیگنال

• سیگنال با R/R ≥ ۱:۳
• در صورت نبود ستاپ، علت را بنویس
• تحلیل مرحله‌ای و مختصر.
""",

    'continuation_pattern': """
نمودار را با استراتژی الگوی ادامه‌دهنده تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند هر تایم‌فریم
• الگوی ادامه‌دهنده (تشخیص و اعتبارسنجی)

سناریوهای احتمالی:
- صعودی: شکست بالای الگو و ادامه صعود
- نزولی: شکست پایین الگو و ادامه نزول
- رنج: تثبیت در الگو

• سیگنال با R/R ≥ ۱:۳
• در صورت نبود شرایط، علت را بنویس
• تحلیل خلاصه و مرحله‌ای.
""",

    'range_bound': """
نمودار را با استراتژی رنج تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• محدوده رنج، سقف و کف

سناریوهای احتمالی:
- صعودی: شکست سقف رنج
- نزولی: شکست کف رنج
- رنج: نوسان بین دو محدوده

• سیگنال معاملاتی فقط با R/R ≥ ۱:۳
• اگر ستاپ نیست، علت را بنویس
• تحلیل مرحله‌به‌مرحله و بولت‌پوینت.
""",

    'triple_confluence': """
نمودار را با استراتژی همگرایی سه‌گانه تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• هر سه عامل تأییدکننده جهت بازار (خط روند، حمایت/مقاومت، اندیکاتور)

سناریوهای احتمالی:
- صعودی: تلاقی عوامل مثبت
- نزولی: تلاقی عوامل منفی
- رنج: نبود همگرایی

• سیگنال ورود با R/R ≥ ۱:۳
• اگر شرایط فراهم نیست، علت را بنویس
• تحلیل مرحله‌ای و خلاصه.
""",

    'pullback_retracement': """
نمودار را با استراتژی اصلاح پولبک تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• روند اصلی
• سطح اصلاح (فیبوناچی، حمایت/مقاومت، EMA)

سناریوهای احتمالی:
- صعودی: پایان اصلاح و شروع رشد
- نزولی: پایان اصلاح و شروع ریزش
- رنج: اصلاح بدون جهت

• سیگنال ورود با R/R ≥ ۱:۳
• اگر ستاپ نیست، علت را بنویس
• تحلیل مرحله‌ای و بولت‌پوینت.
""",

    'liquidity_sweep': """
نمودار را با استراتژی لیکوئیدیتی سویپ تحلیل کن:

• تایم‌فریم‌ها و جفت ارز
• مناطق انباشت نقدینگی (لو/های کلیدی)
• رفتار قیمت هنگام شکار نقدینگی (فیک‌بریک، کندل تیز)

سناریوهای احتمالی:
- صعودی: برگشت سریع پس از شکار نقدینگی کف
- نزولی: برگشت سریع پس از شکار نقدینگی سقف
- رنج: جارو در هر دو سمت

• سیگنال ورود با R/R ≥ ۱:۳
• اگر شرایط مهیا نیست، علت را بنویس
• تحلیل مرحله‌ای و خلاصه.
"""
}

# وضعیت‌های ConversationHandler - آپدیت شده
MAIN_MENU = 0
SELECTING_MARKET = 1  # جدید
SELECTING_TIMEFRAME = 2
SELECTING_STRATEGY = 3  # جدید
WAITING_IMAGES = 4
PROCESSING_ANALYSIS = 5  # جدید

# توابع پایگاه داده (بدون تغییر)
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
            # اگر اشتراک فعال دارد، به انتخاب بازار برود
            return await show_market_selection(update, context)
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

# === توابع جدید برای ورژن آپدیت شده ===

async def show_market_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست بازارها برای انتخاب"""
    market_buttons = []
    
    # اضافه کردن دکمه‌های بازار
    for market_key, market_name in MARKETS.items():
        market_buttons.append([
            InlineKeyboardButton(market_name, callback_data=f"market_{market_key}")
        ])
    
    # دکمه بازگشت
    market_buttons.append([
        InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")
    ])
    
    market_markup = InlineKeyboardMarkup(market_buttons)
    
    await update.callback_query.edit_message_text(
        "🎯 لطفاً بازار مورد نظر خود را انتخاب کنید:",
        reply_markup=market_markup
    )
    
    return SELECTING_MARKET

async def handle_market_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب بازار"""
    query = update.callback_query
    await query.answer()
    
    # استخراج کلید بازار انتخابی
    market_key = query.data.replace("market_", "")
    context.user_data['selected_market'] = market_key
    
    # انتقال به انتخاب تایم فریم
    return await show_timeframes(update, context)

async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست تایم‌فریم‌ها برای انتخاب"""
    timeframe_buttons = []
    for tf in TIMEFRAMES:
        timeframe_buttons.append([InlineKeyboardButton(tf, callback_data=f"tf_{tf}")])
    
    timeframe_buttons.append([InlineKeyboardButton("🔙 بازگشت به انتخاب بازار", callback_data="analyze_charts")])
    timeframe_markup = InlineKeyboardMarkup(timeframe_buttons)
    
    # نمایش بازار انتخابی
    selected_market = context.user_data.get('selected_market', 'نامشخص')
    market_name = MARKETS.get(selected_market, 'نامشخص')
    
    await update.callback_query.edit_message_text(
        f"📊 بازار انتخابی: {market_name}\n\n⏰ لطفاً تایم‌فریم مورد نظر خود را انتخاب کنید:",
        reply_markup=timeframe_markup
    )
    
    return SELECTING_TIMEFRAME

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب تایم‌فریم"""
    query = update.callback_query
    await query.answer()
    
    selected_tf = query.data.replace("tf_", "")
    context.user_data['selected_timeframe'] = selected_tf
    context.user_data['expected_frames'] = EXPECTED_TIMEFRAMES[selected_tf]
    context.user_data['received_images'] = []
    
    # انتقال به انتخاب استراتژی
    return await show_strategy_selection(update, context)

async def show_strategy_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست استراتژی‌های معاملاتی"""
    strategy_buttons = []
    
    # دسته‌بندی استراتژی‌ها
    strategy_categories = {
        'شخصی': ['narmoon_ai'],
        'اسکالپینگ': ['ema_scalping', 'rsi_scalping', 'squeeze_momentum', 'volatility_breakout', 'breakout_retest', 'mean_reversion'],
        'سوئینگ': ['momentum_swing', 'trend_following', 'trend_reversal', 'divergence_play', 'continuation_pattern', 'range_bound'],
        'پیشرفته': ['triple_confluence', 'pullback_retracement', 'liquidity_sweep']
    }
    
    # افزودن هدر برای هر دسته
    for category, strategies in strategy_categories.items():
        # هدر دسته
        strategy_buttons.append([InlineKeyboardButton(f"═══ {category} ═══", callback_data="ignore")])
        
        # استراتژی‌های دسته
        for strategy_key in strategies:
            strategy_name = STRATEGIES[strategy_key]
            strategy_buttons.append([
                InlineKeyboardButton(strategy_name, callback_data=f"strategy_{strategy_key}")
            ])
        
        # خط جداکننده
        strategy_buttons.append([InlineKeyboardButton("───────────", callback_data="ignore")])
    
    # حذف آخرین خط جداکننده
    strategy_buttons.pop()
    
    # دکمه بازگشت
    strategy_buttons.append([InlineKeyboardButton("🔙 بازگشت به انتخاب تایم‌فریم", callback_data="analyze_charts")])
    
    strategy_markup = InlineKeyboardMarkup(strategy_buttons)
    
    # نمایش اطلاعات انتخاب‌های قبلی
    selected_market = context.user_data.get('selected_market', 'نامشخص')
    selected_timeframe = context.user_data.get('selected_timeframe', 'نامشخص')
    market_name = MARKETS.get(selected_market, 'نامشخص')
    
    await update.callback_query.edit_message_text(
        f"📊 بازار: {market_name}\n⏰ تایم‌فریم: {selected_timeframe}\n\n🎯 لطفاً استراتژی معاملاتی مورد نظر خود را انتخاب کنید:",
        reply_markup=strategy_markup
    )
    
    return SELECTING_STRATEGY

async def handle_strategy_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب استراتژی"""
    query = update.callback_query
    await query.answer()
    
    # نادیده گیری کلیک‌های روی هدرها و خط‌های جداکننده
    if query.data == "ignore":
        return SELECTING_STRATEGY
    
    strategy_key = query.data.replace("strategy_", "")
    context.user_data['selected_strategy'] = strategy_key
    context.user_data['strategy_prompt'] = STRATEGY_PROMPTS[strategy_key]
    
    # نمایش پیام برای ارسال تصاویر
    selected_market = context.user_data.get('selected_market', 'نامشخص')
    selected_timeframe = context.user_data.get('selected_timeframe', 'نامشخص')
    selected_strategy_name = STRATEGIES.get(strategy_key, 'نامشخص')
    market_name = MARKETS.get(selected_market, 'نامشخص')
    expected_frames = context.user_data['expected_frames']
    tf_list = " - ".join(expected_frames)
    
    await query.edit_message_text(
        f"✅ **انتخاب‌های شما:**\n"
        f"📊 بازار: {market_name}\n"
        f"⏰ تایم‌فریم: {selected_timeframe}\n"
        f"🎯 استراتژی: {selected_strategy_name}\n\n"
        f"📸 **مرحله نهایی:** لطفاً **۳ اسکرین‌شات** از نمودار در تایم‌فریم‌های زیر ارسال کنید:\n\n"
        f"🔹 {tf_list}\n\n"
        f"💡 برای لغو تحلیل، دستور /cancel را بفرست.",
        parse_mode='Markdown'
    )
    
    return WAITING_IMAGES

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
    await update.message.reply_text("🔥 در حال تحلیل نمودارها با استراتژی انتخابی شما... ⏳")
    
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
        images_content.append({
            "type": "image_url", 
            "image_url": {
                "url": f"data:image/{mime};base64,{b64img}", 
                "detail": "high"
            }
        })
    
    # استفاده از پرامپت اختصاصی استراتژی انتخابی
    strategy_prompt = context.user_data.get('strategy_prompt', STRATEGY_PROMPTS['narmoon_ai'])
    
    # پیامی با چند تصویر
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": strategy_prompt}
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
        
        # نمایش خلاصه انتخاب‌ها و نتیجه
        selected_market = context.user_data.get('selected_market', 'نامشخص')
        selected_timeframe = context.user_data.get('selected_timeframe', 'نامشخص')
        selected_strategy = context.user_data.get('selected_strategy', 'نامشخص')
        market_name = MARKETS.get(selected_market, 'نامشخص')
        strategy_name = STRATEGIES.get(selected_strategy, 'نامشخص')
        
        summary = f"📊 **تحلیل شخصی‌سازی شده نارموون**\n\n"
        summary += f"🎯 **بازار:** {market_name}\n"
        summary += f"⏰ **تایم‌فریم:** {selected_timeframe}\n"
        summary += f"🔧 **استراتژی:** {strategy_name}\n"
        summary += f"{'═' * 30}\n\n"
        
        await update.message.reply_text(
            summary + result,
            reply_markup=menu_button,
            parse_mode='Markdown'
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

# === توابع منوها و بخش‌ها (بدون تغییر) ===

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

4️⃣ بازار مورد نظر خود را انتخاب کنید (رمزارز، فارکس، طلا، سهام)

5️⃣ تایم‌فریم مورد نظر را انتخاب کرده 

6️⃣ استراتژی معاملاتی خود را انتخاب کنید

7️⃣ سه تصویر از چارت در تایم‌فریم‌های مختلف ارسال کنید

8️⃣ تحلیل کامل و شخصی‌سازی‌شده را دریافت کنید
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

🔹 **سه ماهه (پیشنهاد ویژه):** ۳۹،۹۹ دلار برای سه ماه --- معادل ماهی فقط ۱۳،۳۳ دلار! 💡
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

# === دستورات مدیریتی برای ادمین (بدون تغییر) ===

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
    
    # تعریف conversation handler اصلی - آپدیت شده
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(handle_main_menu)],
            SELECTING_MARKET: [CallbackQueryHandler(handle_market_selection, pattern='^market_')],
            SELECTING_TIMEFRAME: [CallbackQueryHandler(handle_timeframe_selection, pattern='^tf_')],
            SELECTING_STRATEGY: [CallbackQueryHandler(handle_strategy_selection, pattern=r'^(strategy_.*|ignore)$')],
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
