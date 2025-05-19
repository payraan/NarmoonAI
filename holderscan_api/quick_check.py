x#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from holderscan_api import HolderScanAPI

API_KEY = "99cb61a372fe01b58c7db347359cf273222ba060ff911f3dd6b67faeb7535574"

def quick_check(token_address):
    """
    بررسی سریع یک توکن
    """
    api = HolderScanAPI(API_KEY)
    
    try:
        print(f"🔍 در حال بررسی {token_address}...")
        
        # دریافت اطلاعات اصلی
        details = api.get_token_details(token_address)
        breakdowns = api.get_holder_breakdowns(token_address)
        deltas = api.get_holder_deltas(token_address)
        
        # نمایش خلاصه
        print(f"\n📋 خلاصه توکن: {details['name']} ({details['ticker']})")
        print(f"{'='*60}")
        print(f"👥 کل نگهدارندگان: {breakdowns['total_holders']:,}")
        print(f"🐋 نهنگ‌ها (>$1M): {breakdowns['holders_over_1m_usd']:,}")
        print(f"🐬 دلفین‌ها ($100K-$1M): {breakdowns['holders_over_100k_usd'] - breakdowns['holders_over_1m_usd']:,}")
        print(f"🏃 فعال (>$10): {breakdowns['holders_over_10_usd']:,} ({breakdowns['holders_over_10_usd']/breakdowns['total_holders']*100:.1f}%)")
        print(f"\n📈 تغییرات:")
        print(f"   ۷ روز: {deltas.get('7days', 'N/A')}")
        print(f"   ۳۰ روز: {deltas.get('30days', 'N/A')}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("استفاده: python3 quick_check.py TOKEN_ADDRESS")
        sys.exit(1)
    
    token_address = sys.argv[1]
    quick_check(token_address)
