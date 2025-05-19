import requests

API_KEY = "99cb61a372fe01b58c7db347359cf273222ba060ff911f3dd6b67faeb7535574"
BASE_URL = "https://api.holderscan.com/v0"

def test_api():
    headers = {'x-api-key': API_KEY}
    
    # تست ساده
    try:
        response = requests.get(f"{BASE_URL}/sol/tokens", 
                              headers=headers, 
                              params={'limit': 1})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
