import pandas as pd
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

# 读取CSV文件，并选择需要的列
df = pd.read_csv('poi_cleaned.csv', usecols=['poi_id', 'centroid'])

# 提取poi_id列
poi_ids = df['poi_id']

# 提取centroid列并解析坐标
centroids = df['centroid'].str.extract(r'POINT \((.*) (.*)\)')
points = np.array(centroids.values.tolist(), dtype=float).reshape(-1, 2)

# 计算x和y坐标的范围
x_range = points[:, 0].max() - points[:, 0].min()
y_range = points[:, 1].max() - points[:, 1].min()

# 归一化处理，使得x和y坐标都在[0, 1]区间内
points_normalized = (points - points.min(axis=0)) / np.array([x_range, y_range])

# 使用归一化后的坐标建立Delaunay三角网
tri = Delaunay(points_normalized)

# 绘制归一化后的Delaunay三角网
plt.figure(figsize=(8, 8))
plt.triplot(points_normalized[:, 0], points_normalized[:, 1], tri.simplices, 'b-', linewidth=0.1)
plt.plot(points_normalized[:, 0], points_normalized[:, 1], 'ko', markersize=0.1)  # 修改点的大小
plt.title('Delaunay Triangulation with Normalized Coordinates')
plt.xlabel('Normalized X coordinate')
plt.ylabel('Normalized Y coordinate')
plt.show()

# # 设置约束条件
constraint_distance = 0.005

# 计算每个三角形的边长，并检查是否满足约束条件
valid_simplices = []
for simplex in tri.simplices:
    valid_triangle = True
    for i in range(3):
        p1 = points_normalized[simplex[i]]
        p2 = points_normalized[simplex[(i + 1) % 3]]
        if np.linalg.norm(p1 - p2) > constraint_distance:
            valid_triangle = False
            break
    if valid_triangle:
        valid_simplices.append(simplex)

# 绘制满足约束条件的三角网
plt.figure(figsize=(8, 8))
plt.triplot(points_normalized[:, 0], points_normalized[:, 1], valid_simplices, 'b-', linewidth=0.1)
plt.plot(points_normalized[:, 0], points_normalized[:, 1], 'ko', markersize=0.1)  # 绘制归一化后的点
plt.title('Constrained Delaunay Triangulation with Normalized Data')
plt.xlabel('Normalized X coordinate')
plt.ylabel('Normalized Y coordinate')
plt.show()