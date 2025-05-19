#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from holderscan_api import HolderScanAPI
import os

# API Key شما
API_KEY = "99cb61a372fe01b58c7db347359cf273222ba060ff911f3dd6b67faeb7535574"

def main():
    """
    مثال‌های استفاده از HolderScan API
    """
    
    # ایجاد نمونه API
    api = HolderScanAPI(API_KEY)
    
    print("🚀 شروع تست HolderScan API...")
    
    # مثال ۱: دریافت لیست توکن‌ها
    print("\n1️⃣ دریافت لیست توکن‌ها...")
    try:
        tokens = api.list_tokens(limit=5)
        api.pretty_print(tokens, "لیست توکن‌ها")
        
        # ذخیره آدرس اولین توکن برای مثال‌های بعدی
        if tokens.get('tokens'):
            sample_token_address = tokens['tokens'][0]['address']
            sample_token_name = tokens['tokens'][0]['name']
            print(f"✅ از توکن {sample_token_name} برای مثال‌های بعدی استفاده می‌کنیم")
        
    except Exception as e:
        print(f"❌ خطا در دریافت لیست توکن‌ها: {e}")
        return
    
    # مثال ۲: جزئیات توکن
    print(f"\n2️⃣ دریافت جزئیات توکن {sample_token_name}...")
    try:
        token_details = api.get_token_details(sample_token_address)
        api.pretty_print(token_details, f"جزئیات توکن {sample_token_name}")
    except Exception as e:
        print(f"❌ خطا در دریافت جزئیات توکن: {e}")
    
    # مثال ۳: آمار توکن
    print(f"\n3️⃣ دریافت آمار توکن {sample_token_name}...")
    try:
        token_stats = api.get_token_statistics(sample_token_address)
        api.pretty_print(token_stats, f"آمار توکن {sample_token_name}")
    except Exception as e:
        print(f"❌ خطا در دریافت آمار توکن: {e}")
    
    # مثال ۴: لیست نگهدارندگان
    print(f"\n4️⃣ دریافت تاپ نگهدارندگان {sample_token_name}...")
    try:
        holders = api.get_token_holders(sample_token_address, limit=10)
        api.pretty_print(holders, f"تاپ نگهدارندگان {sample_token_name}")
    except Exception as e:
        print(f"❌ خطا در دریافت نگهدارندگان: {e}")
    
    # مثال ۵: تغییرات نگهدارندگان
    print(f"\n5️⃣ دریافت تغییرات نگهدارندگان {sample_token_name}...")
    try:
        deltas = api.get_holder_deltas(sample_token_address)
        api.pretty_print(deltas, f"تغییرات نگهدارندگان {sample_token_name}")
    except Exception as e:
        print(f"❌ خطا در دریافت تغییرات: {e}")
    
    # مثال ۶: تقسیم‌بندی نگهدارندگان
    print(f"\n6️⃣ دریافت تقسیم‌بندی نگهدارندگان {sample_token_name}...")
    try:
        breakdowns = api.get_holder_breakdowns(sample_token_address)
        api.pretty_print(breakdowns, f"تقسیم‌بندی نگهدارندگان {sample_token_name}")
    except Exception as e:
        print(f"❌ خطا در دریافت تقسیم‌بندی: {e}")

def search_example():
    """
    مثال جستجوی توکن
    """
    api = HolderScanAPI(API_KEY)
    
    search_term = input("\n🔍 نام یا تیکر توکن را وارد کنید: ")
    
    print(f"🔍 در حال جستجوی '{search_term}'...")
    try:
        found_tokens = api.search_tokens_by_name(search_term)
        
        if found_tokens:
            print(f"✅ {len(found_tokens)} توکن پیدا شد:")
            for i, token in enumerate(found_tokens, 1):
                print(f"{i}. {token['name']} ({token['ticker']}) - {token['address']}")
            
            # انتخاب توکن برای بررسی بیشتر
            while True:
                try:
                    choice = int(input("\nکدام توکن را برای بررسی بیشتر انتخاب می‌کنید؟ (شماره): ")) - 1
                    if 0 <= choice < len(found_tokens):
                        selected_token = found_tokens[choice]
                        print(f"\n📊 در حال دریافت تمام اطلاعات {selected_token['name']}...")
                        
                        all_data = api.get_all_holder_data(selected_token['address'])
                        api.pretty_print(all_data, f"تمام اطلاعات {selected_token['name']}")
                        break
                    else:
                        print("❌ شماره نامعتبر!")
                except ValueError:
                    print("❌ لطفاً یک شماره معتبر وارد کنید!")
        else:
            print("❌ توکنی با این نام پیدا نشد!")
            
    except Exception as e:
        print(f"❌ خطا در جستجو: {e}")

def custom_analysis():
    """
    تحلیل سفارشی توکن
    """
    api = HolderScanAPI(API_KEY)
    
    contract_address = input("\n📝 آدرس قرارداد توکن را وارد کنید: ")
    
    print(f"📈 در حال تحلیل توکن...")
    try:
        # دریافت تمام اطلاعات
        token_details = api.get_token_details(contract_address)
        token_stats = api.get_token_statistics(contract_address)
        breakdowns = api.get_holder_breakdowns(contract_address)
        deltas = api.get_holder_deltas(contract_address)
        
        # تحلیل داده‌ها
        print(f"\n{'='*60}")
        print(f"📊 گزارش تحلیل توکن: {token_details['name']} ({token_details['ticker']})")
        print(f"{'='*60}")
        
        # آمار کلی
        total_supply = int(token_details['supply']) / (10 ** token_details['decimals'])
        total_holders = breakdowns['total_holders']
        
        print(f"🪙 کل عرضه: {total_supply:,}")
        print(f"👥 کل نگهدارندگان: {total_holders:,}")
        
        # توزیع نگهدارندگان
        categories = breakdowns['categories']
        print(f"\n🏷️ دسته‌بندی نگهدارندگان:")
        for category, count in categories.items():
            percentage = (count / total_holders) * 100
            print(f"   {category.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # تمرکز
        if 'gini' in token_stats:
            gini = token_stats['gini']
            print(f"\n📈 ضریب جینی: {gini:.3f} ({'بالا' if gini > 0.8 else 'متوسط' if gini > 0.5 else 'پایین'} - تمرکز)")
        
        # تغییرات اخیر
        print(f"\n📊 تغییرات نگهدارندگان:")
        print(f"   ۷ روز گذشته: {deltas.get('7days', 'N/A')}")
        print(f"   ۱۴ روز گذشته: {deltas.get('14days', 'N/A')}")
        print(f"   ۳۰ روز گذشته: {deltas.get('30days', 'N/A')}")
        
        # نگهدارندگان بزرگ
        over_1m = breakdowns.get('holders_over_1m_usd', 0)
        over_100k = breakdowns.get('holders_over_100k_usd', 0)
        print(f"\n🐋 نگهدارندگان بزرگ:")
        print(f"   بالای ۱ میلیون دلار: {over_1m}")
        print(f"   بالای ۱۰۰ هزار دلار: {over_100k}")
        
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ خطا در تحلیل: {e}")

def interactive_menu():
    """
    منوی تعاملی
    """
    while True:
        print(f"\n{'='*50}")
        print("🔥 HolderScan API - منوی اصلی")
        print(f"{'='*50}")
        print("1. اجرای مثال‌های کلی")
        print("2. جستجوی توکن بر اساس نام")
        print("3. تحلیل سفارشی توکن")
        print("4. خروج")
        print(f"{'='*50}")
        
        choice = input("انتخاب شما: ")
        
        if choice == '1':
            main()
        elif choice == '2':
            search_example()
        elif choice == '3':
            custom_analysis()
        elif choice == '4':
            print("👋 خداحافظ!")
            break
        else:
            print("❌ انتخاب نامعتبر!")

if __name__ == "__main__":
    interactive_menu()
