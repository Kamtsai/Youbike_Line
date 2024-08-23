import requests
import os
import time
import random
import json

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
    api_url = "https://apis.youbike.com.tw/api/front/station/all?location=taipei&lang=tw&type=2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.youbike.com.tw/',
        'Origin': 'https://www.youbike.com.tw',
    }
    print(f"正在请求 API URL: {api_url}")
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        print(f"API 请求成功，状态码: {response.status_code}")
        data = response.json()
        print(f"API 返回数据类型: {type(data)}")
        print(f"API 返回数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")  # 打印前500个字符
    except requests.RequestException as e:
        print(f"API 请求失败: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return []

    results = []
    all_stations = []

    if isinstance(data, dict) and 'retVal' in data:
        stations = data['retVal']
    else:
        print(f"未找到预期的数据结构")
        return []

    for station_id, station_info in stations.items():
        station_name = station_info.get('name_tw', '')
        all_stations.append(station_name)
        if station_name in TARGET_STATIONS:
            available_bikes = station_info.get('available_spaces', 'N/A')
            results.append(f"{station_name}: {available_bikes}")

    if not results:
        print("未找到任何匹配的站点信息")
    print(f"找到的所有站点数量: {len(all_stations)}")
    print(f"部分站点名称: {all_stations[:10]}")  # 只打印前10个站点名称

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
    print("开始获取 YouBike 站点信息...")
    results = scrape_youbike()
    if results:
        message = "\n".join(results)
        print("获取完成，发送 Line 通知...")
        print(f"将发送的消息:\n{message}")
        send_line_notify(f"\nYouBike站点可借车辆数量:\n{message}")
    else:
        print("未找到任何匹配的站点信息，不发送 Line 通知")

if __name__ == "__main__":
    main()
