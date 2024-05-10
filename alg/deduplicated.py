import pandas as pd
import numpy as np
from collections import defaultdict

# 读取CSV文件，并选择需要的列
df = pd.read_csv('poi.csv', usecols=['poi_id', 'centroid'])

# 提取poi_id列和centroid列
poi_ids = df['poi_id']
centroids = df['centroid']

# 提取centroid列并解析坐标
points = np.array(centroids.str.extract(r'POINT \((.*) (.*)\)').values.tolist(), dtype=float).reshape(-1, 2)

# 使用字典来记录每个坐标及其出现的次数和对应的poi_id列表
points_info = defaultdict(lambda: {'count': 0, 'poi_ids': []})
for idx, (poi_id, point) in enumerate(zip(poi_ids, points)):
    points_info[tuple(point)]['count'] += 1
    points_info[tuple(point)]['poi_ids'].append(poi_id)

# 找出所有重复的点（出现次数大于1的点）
duplicate_points_info = {point: info for point, info in points_info.items() if info['count'] > 1}

# 输出所有重复的点及其对应的poi_id
print("所有重复的点及其对应的poi_id：")
for point, info in duplicate_points_info.items():
    print(f"坐标 {point} 出现了 {info['count']} 次，对应的poi_id列表: {info['poi_ids']}")