import json
import base64
from openpyxl import Workbook
import requests
import jsonpath


# 替换为自己的API Key
headers = {
    "X-QuakeToken": ""
}

# 读取IP列表
print ('请输入文件名字：')
name = input()
with open(name+".txt", "r", encoding='utf-8') as f:
    ip_list = f.read().splitlines()

# 设置Excel文件名和工作表名
exname = name+".xlsx"
excel_filename = exname
sheet_name = "IP Data"

# 创建Excel工作簿和工作表
workbook = Workbook()
sheet = workbook.active
results = []
for ip in ip_list:
    data = {
        "query": ip,
        "start": 0,
        "size": 6000
    }
    response = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers, json=data)
    result_list = jsonpath.jsonpath(response.json(), "$.data[*]")
    if result_list is None or not result_list:
        continue
    for result in result_list:
        if len(result.get('components', [])) < 3:
            continue
        row = {
            "ip": result.get('ip', ''),
            "port": result.get('port', ''),
            "设备": result['components'][0].get('product_name_cn', ''),
            "中间件": result['components'][2].get('product_name_cn', None),
            "中间件版本": result['components'][2].get('product_version', None),
            "url": result.get('service', {}).get('http', {}).get('http_load_url', ''),
            "title": result.get('service', {}).get('http', {}).get('title', ''),
            "location_diqu": result.get('location', {}).get('province_cn', None),
            "location_isp": result.get('location', {}).get('isp', None),
            "location_city": result.get('location', {}).get('city_cn', None),
            "location_country_cn": result.get('location', {}).get('country_cn', None),
            "location_scene_cn": result.get('location', {}).get('scene_cn', None),
        }
        results.append(row)
    print(f"共搜索到{len(results)}条记录！")
    # 写入IP信息到Excel
    if len(results) == 0:
        continue
    if sheet.max_row == 1:
        header = list(results[0].keys())
        sheet.append(header)
    for result in results:
        row = [str(value) if value is not None else "" for value in result.values()]
        sheet.append(row)
    # 清空results
    results = []
# 保存Excel文件
workbook.save(filename=excel_filename)
print(f"数据已成功保存到 {excel_filename}")
