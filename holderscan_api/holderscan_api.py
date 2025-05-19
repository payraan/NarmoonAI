import requests
import json
import time
from typing import Dict, List, Optional, Union

class HolderScanAPI:
    """
    کلاس برای کار با HolderScan API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.holderscan.com/v0"):
        """
        مقداردهی اولیه API
        
        Args:
            api_key (str): کلید API شما
            base_url (str): URL پایه API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        ارسال درخواست به API
        
        Args:
            method (str): متود HTTP (GET, POST, etc.)
            endpoint (str): آدرس endpoint
            params (Dict): پارامترهای query string
            
        Returns:
            Dict: پاسخ API
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("⚠️  Rate limit reached. Waiting...")
                time.sleep(60)  # منتظر یک دقیقه
                return self._make_request(method, endpoint, params)
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                raise
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            raise
    
    def list_tokens(self, chain_id: str = "sol", limit: int = 50, offset: int = 0) -> Dict:
        """
        دریافت لیست تمام توکن‌ها
        
        Args:
            chain_id (str): شناسه زنجیره (فعلاً فقط sol)
            limit (int): تعداد نتایج در هر صفحه (حداکثر 100)
            offset (int): آفست صفحه‌بندی
            
        Returns:
            Dict: لیست توکن‌ها
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', f"{chain_id}/tokens", params)
    
    def get_token_details(self, contract_address: str, chain_id: str = "sol") -> Dict:
        """
        دریافت جزئیات یک توکن
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            
        Returns:
            Dict: جزئیات توکن
        """
        return self._make_request('GET', f"{chain_id}/tokens/{contract_address}")
    
    def get_token_statistics(self, contract_address: str, chain_id: str = "sol") -> Dict:
        """
        دریافت آمار توکن شامل HHI، Gini و...
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            
        Returns:
            Dict: آمار توکن
        """
        return self._make_request('GET', f"{chain_id}/tokens/{contract_address}/stats")
    
    def get_token_holders(self, contract_address: str, chain_id: str = "sol", 
                         min_amount: Optional[int] = None, max_amount: Optional[int] = None,
                         limit: int = 50, offset: int = 0) -> Dict:
        """
        دریافت لیست نگهدارندگان توکن
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            min_amount (int): حداقل مقدار توکن
            max_amount (int): حداکثر مقدار توکن
            limit (int): تعداد نتایج
            offset (int): آفست صفحه‌بندی
            
        Returns:
            Dict: لیست نگهدارندگان
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if min_amount is not None:
            params['min_amount'] = min_amount
        if max_amount is not None:
            params['max_amount'] = max_amount
            
        return self._make_request('GET', f"{chain_id}/tokens/{contract_address}/holders", params)
    
    def get_holder_deltas(self, contract_address: str, chain_id: str = "sol") -> Dict:
        """
        دریافت تغییرات نگهدارندگان در بازه‌های زمانی مختلف
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            
        Returns:
            Dict: تغییرات نگهدارندگان
        """
        return self._make_request('GET', f"{chain_id}/tokens/{contract_address}/holders/deltas")
    
    def get_holder_breakdowns(self, contract_address: str, chain_id: str = "sol") -> Dict:
        """
        دریافت تقسیم‌بندی نگهدارندگان بر اساس ارزش نگهداری
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            
        Returns:
            Dict: تقسیم‌بندی نگهدارندگان
        """
        return self._make_request('GET', f"{chain_id}/tokens/{contract_address}/holders/breakdowns")
    
    def get_all_holder_data(self, contract_address: str, chain_id: str = "sol") -> Dict:
        """
        دریافت تمام اطلاعات نگهدارندگان یک توکن
        
        Args:
            contract_address (str): آدرس قرارداد توکن
            chain_id (str): شناسه زنجیره
            
        Returns:
            Dict: تمام اطلاعات مرتبط با نگهدارندگان
        """
        result = {}
        
        print("🔍 در حال دریافت جزئیات توکن...")
        result['token_details'] = self.get_token_details(contract_address, chain_id)
        
        print("📊 در حال دریافت آمار توکن...")
        result['token_stats'] = self.get_token_statistics(contract_address, chain_id)
        
        print("👥 در حال دریافت لیست نگهدارندگان...")
        result['holders'] = self.get_token_holders(contract_address, chain_id)
        
        print("📈 در حال دریافت تغییرات نگهدارندگان...")
        result['holder_deltas'] = self.get_holder_deltas(contract_address, chain_id)
        
        print("🏷️ در حال دریافت تقسیم‌بندی نگهدارندگان...")
        result['holder_breakdowns'] = self.get_holder_breakdowns(contract_address, chain_id)
        
        return result
    
    def search_tokens_by_name(self, search_term: str, chain_id: str = "sol") -> List[Dict]:
        """
        جستجوی توکن‌ها بر اساس نام
        
        Args:
            search_term (str): عبارت جستجو
            chain_id (str): شناسه زنجیره
            
        Returns:
            List[Dict]: لیست توکن‌های پیدا شده
        """
        all_tokens = self.list_tokens(chain_id, limit=100)
        found_tokens = []
        
        for token in all_tokens.get('tokens', []):
            if search_term.lower() in token.get('name', '').lower() or \
               search_term.lower() in token.get('ticker', '').lower():
                found_tokens.append(token)
        
        return found_tokens
    
    def pretty_print(self, data: Dict, title: str = "API Response") -> None:
        """
        نمایش زیبای داده‌ها
        
        Args:
            data (Dict): داده‌ها
            title (str): عنوان
        """
        print(f"\n{'='*50}")
        print(f"📋 {title}")
        print(f"{'='*50}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"{'='*50}\n")
