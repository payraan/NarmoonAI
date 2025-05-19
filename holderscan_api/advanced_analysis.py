#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from holderscan_api import HolderScanAPI
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import json

# نصب کتابخانه‌های اضافی: pip install matplotlib pandas numpy

class AdvancedHolderAnalysis:
    """
    کلاس تحلیل پیشرفته نگهدارندگان
    """
    
    def __init__(self, api_key: str):
        self.api = HolderScanAPI(api_key)
    
    def analyze_token_distribution(self, contract_address: str, save_chart: bool = True):
        """
        تحلیل توزیع نگهدارندگان و رسم نمودار
        """
        try:
            # دریافت داده‌ها
            token_details = self.api.get_token_details(contract_address)
            breakdowns = self.api.get_holder_breakdowns(contract_address)
            
            # آماده‌سازی داده‌ها برای نمودار
            categories = breakdowns['categories']
            labels = list(categories.keys())
            sizes = list(categories.values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
            
            # رسم نمودار دایره‌ای
            plt.figure(figsize=(12, 8))
            
            # نمودار دایره‌ای
            plt.subplot(2, 2, 1)
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title(f'توزیع نگهدارندگان - {token_details["name"]}')
            
            # نمودار میله‌ای
            plt.subplot(2, 2, 2)
            plt.bar(labels, sizes, color=colors)
            plt.title('تعداد نگهدارندگان بر حسب دسته')
            plt.xticks(rotation=45)
            plt.ylabel('تعداد')
            
            # نمودار توزیع بر اساس ارزش
            value_ranges = [
                ('کمتر از ۱۰$', breakdowns['total_holders'] - breakdowns['holders_over_10_usd']),
                ('۱۰$ - ۱۰۰$', breakdowns['holders_over_10_usd'] - breakdowns['holders_over_100_usd']),
                ('۱۰۰$ - ۱K$', breakdowns['holders_over_100_usd'] - breakdowns['holders_over_1000_usd']),
                ('۱K$ - ۱۰K$', breakdowns['holders_over_1000_usd'] - breakdowns['holders_over_10000_usd']),
                ('۱۰K$ - ۱۰۰K$', breakdowns['holders_over_10000_usd'] - breakdowns['holders_over_100k_usd']),
                ('۱۰۰K$ - ۱M$', breakdowns['holders_over_100k_usd'] - breakdowns['holders_over_1m_usd']),
                ('بیش از ۱M$', breakdowns['holders_over_1m_usd'])
            ]
            
            plt.subplot(2, 2, 3)
            ranges, counts = zip(*value_ranges)
            plt.barh(ranges, counts, color='skyblue')
            plt.title('توزیع بر اساس ارزش نگهداری')
            plt.xlabel('تعداد نگهدارندگان')
            
            # جدول آمار
            plt.subplot(2, 2, 4)
            plt.axis('off')
            stats_text = f"""
آمار کلی {token_details["name"]}:

• کل نگهدارندگان: {breakdowns['total_holders']:,}
• نگهدارندگان بالای ۱۰$: {breakdowns['holders_over_10_usd']:,}
• نگهدارندگان بالای ۱K$: {breakdowns['holders_over_1000_usd']:,}  
• نگهدارندگان نهنگ: {breakdowns['holders_over_1m_usd']:,}

• درصد نگهدارندگان فعال: {(breakdowns['holders_over_10_usd']/breakdowns['total_holders']*100):.1f}%
• درصد نگهدارندگان جدی: {(breakdowns['holders_over_1000_usd']/breakdowns['total_holders']*100):.1f}%
            """
            plt.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            
            plt.tight_layout()
            
            if save_chart:
                filename = f"{token_details['ticker']}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"💾 نمودار در فایل {filename} ذخیره شد")
            
            plt.show()
            
            return {
                'token_details': token_details,
                'breakdowns': breakdowns,
                'analysis': {
                    'active_holder_percentage': (breakdowns['holders_over_10_usd']/breakdowns['total_holders']*100),
                    'serious_holder_percentage': (breakdowns['holders_over_1000_usd']/breakdowns['total_holders']*100),
                    'whale_count': breakdowns['holders_over_1m_usd'],
                    'concentration_score': self._calculate_concentration_score(breakdowns)
                }
            }
            
        except Exception as e:
            print(f"❌ خطا در تحلیل توزیع: {e}")
            return None
    
    def _calculate_concentration_score(self, breakdowns):
        """
        محاسبه امتیاز تمرکز (۰ تا ۱۰۰)
        """
        total = breakdowns['total_holders']
        whales = breakdowns['holders_over_1m_usd']
        dolphins = breakdowns['holders_over_100k_usd'] - whales
        
        # هرچه نگهدارندگان بزرگ بیشتر باشند، تمرکز بالاتر است
        whale_score = min((whales / total) * 1000, 50)
        dolphin_score = min((dolphins / total) * 500, 30)
        
        # هرچه نگهدارندگان کوچک بیشتر باشند، تمرکز پایین‌تر است
        shrimp_ratio = breakdowns['categories']['shrimp'] / total
        decentralization_score = max(20 - (shrimp_ratio * 20), 0)
        
        concentration_score = whale_score + dolphin_score + decentralization_score
        return min(concentration_score, 100)
    
    def compare_tokens(self, contract_addresses: list, token_names: list = None):
        """
        مقایسه چندین توکن
        """
        if not token_names:
            token_names = [f"Token {i+1}" for i in range(len(contract_addresses))]
        
        comparison_data = []
        
        for i, address in enumerate(contract_addresses):
            try:
                print(f"📊 در حال تحلیل {token_names[i]}...")
                
                token_details = self.api.get_token_details(address)
                breakdowns = self.api.get_holder_breakdowns(address)
                stats = self.api.get_token_statistics(address)
                
                token_data = {
                    'name': token_details['name'],
                    'ticker': token_details['ticker'],
                    'total_holders': breakdowns['total_holders'],
                    'whales': breakdowns['holders_over_1m_usd'],
                    'dolphins': breakdowns['holders_over_100k_usd'] - breakdowns['holders_over_1m_usd'],
                    'active_holders': breakdowns['holders_over_10_usd'],
                    'active_percentage': (breakdowns['holders_over_10_usd']/breakdowns['total_holders']*100),
                    'concentration_score': self._calculate_concentration_score(breakdowns),
                    'gini_coefficient': stats.get('gini', 'N/A')
                }
                
                comparison_data.append(token_data)
                
            except Exception as e:
                print(f"❌ خطا در تحلیل {token_names[i]}: {e}")
        
        # رسم نمودار مقایسه‌ای
        if len(comparison_data) > 1:
            self._plot_comparison(comparison_data)
        
        return comparison_data
    
    def _plot_comparison(self, comparison_data):
        """
        رسم نمودار مقایسه‌ای
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        names = [token['name'] for token in comparison_data]
        
        # مقایسه تعداد کل نگهدارندگان
        total_holders = [token['total_holders'] for token in comparison_data]
        axes[0, 0].bar(names, total_holders, color='lightblue')
        axes[0, 0].set_title('تعداد کل نگهدارندگان')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # مقایسه درصد نگهدارندگان فعال
        active_percentages = [token['active_percentage'] for token in comparison_data]
        axes[0, 1].bar(names, active_percentages, color='lightgreen')
        axes[0, 1].set_title('درصد نگهدارندگان فعال (>$10)')
        axes[0, 1].set_ylabel('درصد')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # مقایسه تعداد نهنگ‌ها
        whales = [token['whales'] for token in comparison_data]
        axes[1, 0].bar(names, whales, color='coral')
        axes[1, 0].set_title('تعداد نهنگ‌ها (>$1M)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # مقایسه امتیاز تمرکز
        concentration_scores = [token['concentration_score'] for token in comparison_data]
        axes[1, 1].bar(names, concentration_scores, color='gold')
        axes[1, 1].set_title('امتیاز تمرکز (0-100)')
        axes[1, 1].set_ylabel('امتیاز')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def export_data_to_excel(self, contract_address: str, filename: str = None):
        """
        صادرات داده‌ها به فایل اکسل
        """
        try:
            # دریافت تمام داده‌ها
            token_details = self.api.get_token_details(contract_address)
            breakdowns = self.api.get_holder_breakdowns(contract_address)
            holders = self.api.get_token_holders(contract_address, limit=100)
            deltas = self.api.get_holder_deltas(contract_address)
            stats = self.api.get_token_statistics(contract_address)
            
            if not filename:
                filename = f"{token_details['ticker']}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # ساخت DataFrame ها
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # برگه جزئیات توکن
                token_df = pd.DataFrame([token_details])
                token_df.to_excel(writer, sheet_name='Token Details', index=False)
                
                # برگه آمار
                stats_df = pd.DataFrame([stats])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
                # برگه تقسیم‌بندی
                breakdowns_df = pd.DataFrame([breakdowns])
                breakdowns_df.to_excel(writer, sheet_name='Breakdowns', index=False)
                
                # برگه تغییرات
                deltas_df = pd.DataFrame([deltas])
                deltas_df.to_excel(writer, sheet_name='Deltas', index=False)
                
                # برگه نگهدارندگان
                holders_list = holders.get('holders', [])
                if holders_list:
                    holders_df = pd.DataFrame(holders_list)
                    holders_df.to_excel(writer, sheet_name='Top Holders', index=False)
            
            print(f"💾 داده‌ها در فایل {filename} ذخیره شدند")
            return filename
            
        except Exception as e:
            print(f"❌ خطا در صادرات داده‌ها: {e}")
            return None

def main():
    """
    مثال استفاده از تحلیل پیشرفته
    """
    API_KEY = "99cb61a372fe01b58c7db347359cf273222ba060ff911f3dd6b67faeb7535574"
    
    analyzer = AdvancedHolderAnalysis(API_KEY)
    
    print("🔥 تحلیل پیشرفته HolderScan")
    print("="*50)
    
    # نمونه آدرس توکن (می‌توانید تغییر دهید)
    sample_address = "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9"
    
    # تحلیل توزیع
    print("📊 در حال تحلیل توزیع نگهدارندگان...")
    analysis_result = analyzer.analyze_token_distribution(sample_address)
    
    if analysis_result:
        print("✅ تحلیل کامل شد!")
        print(f"امتیاز تمرکز: {analysis_result['analysis']['concentration_score']:.1f}/100")
        print(f"درصد نگهدارندگان فعال: {analysis_result['analysis']['active_holder_percentage']:.1f}%")
    
    # صادرات به اکسل
    print("\n💾 در حال صادرات داده‌ها...")
    excel_file = analyzer.export_data_to_excel(sample_address)
    
    print("✅ تحلیل پیشرفته کامل شد!")

if __name__ == "__main__":
    main()
