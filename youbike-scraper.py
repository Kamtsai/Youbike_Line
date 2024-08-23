import requests
from bs4 import BeautifulSoup
import os

# 從環境變量獲取Line Notify token
LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']

# 目標站點列表
TARGET_STATIONS = [
    "捷運忠孝新生站(3號出口)",
    "捷運忠孝新生站(4號出口)",
    "捷運忠孝新生站(2號出口)",
    "捷運忠孝新生站(1號出口)",
    "捷運忠孝復興站(2號出口)",
    "忠孝東路四段49巷口",
    "捷運忠孝復興站(3號出口)",
    "信義大安路口(信維大樓)",
    "敦化信義路口(東南側)",
    "信義敦化路口"
]

def scrape_youbike():
    url = "https://www.youbike.com.tw/region/main/stations/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    
    for station in soup.find_all('div', class_='station-item'):
        station_name = station.find('h1').text.strip()
        if station_name in TARGET_STATIONS:
            available_bikes = station.find('div', class_='available-bike').text.strip()
            results.append(f"{station_name}: {available_bikes}")
    
    return results

def send_line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    print(f"Line Notify Response: {response.status_code}")

def main():
    print("開始爬取 YouBike 站點資訊...")
    results = scrape_youbike()
    if results:
        message = "\n".join(results)
        print("爬取完成，發送 Line 通知...")
        send_line_notify(f"\nYouBike站點可借車輛數量:\n{message}")
        print("Line 通知已發送")
    else:
        print("未找到任何匹配的站點資訊")

if __name__ == "__main__":
    main()
