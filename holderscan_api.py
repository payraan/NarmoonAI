import os
import requests
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()
APIKEY = os.getenv("APIKEY")
BASE_URL = "https://api.holderscan.com/v0/sol"

HEADERS = {
    "x-api-key": APIKEY
}

def list_tokens(limit=10, offset=0):
    url = f"{BASE_URL}/tokens?limit={limit}&offset={offset}"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def token_details(contract_address):
    url = f"{BASE_URL}/tokens/{contract_address}"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def token_stats(contract_address):
    url = f"{BASE_URL}/tokens/{contract_address}/stats"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def token_holders(contract_address, limit=10, offset=0):
    url = f"{BASE_URL}/tokens/{contract_address}/holders?limit={limit}&offset={offset}"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def holder_deltas(contract_address):
    url = f"{BASE_URL}/tokens/{contract_address}/holders/deltas"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def holder_breakdowns(contract_address):
    url = f"{BASE_URL}/tokens/{contract_address}/holders/breakdowns"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

if __name__ == "__main__":
    # نمونه: لیست ۵ توکن اول را بگیر
    tokens = list_tokens(limit=5)
    print("== توکن‌ها:")
    print(tokens)
    # اگه میخوای جزئیات یک توکن خاص را بگیری، از address استفاده کن:
    if tokens.get("tokens"):
        first_token = tokens["tokens"][0]["address"]
        print("\n== جزئیات توکن اول:")
        print(token_details(first_token))
        print("\n== آمار توکن:")
        print(token_stats(first_token))
        print("\n== هولدرهای توکن:")
        print(token_holders(first_token, limit=5))
        print("\n== تغییرات هولدرها:")
        print(holder_deltas(first_token))
        print("\n== دسته‌بندی هولدرها:")
        print(holder_breakdowns(first_token))

