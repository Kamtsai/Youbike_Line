import requests
from bs4 import BeautifulSoup
import os

# 从环境变量获取Line Notify token
LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']

# 目标站点列表
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
    print(f"正在请求 URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果请求不成功，这将引发异常
        print(f"请求成功，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"HTML 内容长度: {len(response.text)} 字符")
    print(f"HTML 内容前 500 字符: {response.text[:500]}")  # 打印 HTML 内容的前 500 个字符

    results = []
    all_stations = []
    
    for station in soup.find_all('div', class_='station-item'):
        station_name = station.find('h1')
        if station_name:
            station_name = station_name.text.strip()
            all_stations.append(station_name)
            if station_name in TARGET_STATIONS:
                available_bikes = station.find('div', class_='available-bike')
                if available_bikes:
                    available_bikes = available_bikes.text.strip()
                    results.append(f"{station_name}: {available_bikes}")
                else:
                    print(f"未找到可用单车信息: {station_name}")
    
    if not results:
        print("未找到任何匹配的站点信息")
        print(f"找到的所有站点: {all_stations}")
    
    return results

def send_line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        print(f"Line Notify 发送成功，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"Line Notify 发送失败: {e}")

def main():
    print("开始爬取 YouBike 站点信息...")
    results = scrape_youbike()
    if results:
        message = "\n".join(results)
        print("爬取完成，发送 Line 通知...")
        print(f"将发送的消息:\n{message}")
        send_line_notify(f"\nYouBike站点可借车辆数量:\n{message}")
    else:
        print("未找到任何匹配的站点信息，不发送 Line 通知")

if __name__ == "__main__":
    main()
