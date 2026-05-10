from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# 直接读取 CSV 文件，不需要 MySQL！
df = pd.read_csv("aqi_raw.csv")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    # ---------------------- 地图数据 ------------------------
    map_df = df.groupby("city")["aqi"].mean().reset_index()

    city_map = {
        'beijing': '北京', 'shanghai': '上海', 'guangzhou': '广州', 'shenzhen': '深圳',
        'hangzhou': '杭州', 'chengdu': '成都', 'wuhan': '武汉', 'nanjing': '南京',
        'xian': '西安', 'suzhou': '苏州', 'tianjin': '天津', 'chongqing': '重庆'
    }
    CITY_COORDINATES = {
        'beijing': [116.4074, 39.9042], 'shanghai': [121.4737, 31.2304], 'guangzhou': [113.2644, 23.1291],
        'shenzhen': [114.0859, 22.547], 'hangzhou': [120.1551, 30.2741], 'chengdu': [104.0668, 30.5728],
        'wuhan': [114.3054, 30.5931], 'nanjing': [118.7969, 32.0603], 'xian': [108.9398, 34.3416],
        'suzhou': [120.5853, 31.2989], 'tianjin': [117.2008, 39.0842], 'chongqing': [106.5516, 29.5630]
    }

    map_data = []
    for _, row in map_df.iterrows():
        city = row["city"]
        if city in CITY_COORDINATES:
            map_data.append({
                "name": city_map.get(city, city),
                "value": CITY_COORDINATES[city] + [round(row["aqi"])]
            })

    # ---------------------- 趋势数据 ------------------------
    beijing = df[df["city"] == "beijing"].sort_values("date")
    trend_data = {
        "dates": beijing["date"].tolist(),
        "aqi": beijing["aqi"].tolist()
    }

    # ---------------------- TOP10 ---------------------------
    top_df = df.groupby("city")["aqi"].mean().nlargest(10).reset_index()
    bar_data = {
        "cities": [city_map.get(c, c) for c in top_df["city"]],
        "values": [round(v) for v in top_df["aqi"]]
    }

    # ---------------------- 污染物占比 ------------------------
    comp_data = [
        {"name": "PM2.5", "value": round(df["pm2_5"].mean(), 1)},
        {"name": "PM10", "value": round(df["pm10"].mean(), 1)},
        {"name": "SO2", "value": round(df["so2"].mean(), 1)},
        {"name": "NO2", "value": round(df["no2"].mean(), 1)},
        {"name": "O3", "value": round(df["o3"].mean(), 1)}
    ]

    # ---------------------- 总数 ----------------------------
    total_count = len(df)

    return jsonify({
        "map_data": map_data,
        "trend_data": trend_data,
        "bar_data": bar_data,
        "comp_data": comp_data,
        "total_count": total_count
    })

if __name__ == '__main__':
    app.run(debug=True)