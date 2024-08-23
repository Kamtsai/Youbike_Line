import requests
from bs4 import BeautifulSoup
import os
import time
import random
import json
import re

LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.youbike.com.tw/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    print(f"正在请求 URL: {url}")
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"请求成功，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"HTML 内容长度: {len(response.text)} 字符")

    # 尝试查找包含站点数据的 JSON
    json_data = None
    scripts = soup.find_all('script')
    for script in scripts:
        if 'json/area-all.json' in script.text:
            json_match = re.search(r'(\{.*\})', script.text)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    print("找到 JSON 数据:")
                    print(json.dumps(json_data, indent=2)[:500])  # 打印前500个字符
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")

    results = []
    all_stations = []

    if json_data:
        # 尝试从 JSON 中提取站点信息
        try:
            stations = json_data.get('props', {}).get('pageProps', {}).get('fallback', {}).get('/json/area-all.json', [])
            for station in stations:
                station_name = station.get('name_tw', '')
                all_stations.append(station_name)
                if station_name in TARGET_STATIONS:
                    available_bikes = station.get('available_spaces', 'N/A')
                    results.append(f"{station_name}: {available_bikes}")
        except Exception as e:
            print(f"从 JSON 提取数据时出错: {e}")
    
    if not results:
        print("从 JSON 中未找到站点信息，尝试从 HTML 中提取...")
        # 尝试从 HTML 中直接提取站点信息
        for station in soup.find_all(['div', 'span', 'p'], string=lambda text: any(target in text for target in TARGET_STATIONS) if text else False):
            station_name = station.get_text(strip=True)
            all_stations.append(station_name)
            if station_name in TARGET_STATIONS:
                # 尝试在周围元素中查找可能的可用车辆数量
                available_bikes = 'N/A'
                next_element = station.find_next(['div', 'span', 'p'])
                if next_element:
                    available_bikes = next_element.get_text(strip=True)
                results.append(f"{station_name}: {available_bikes}")

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
