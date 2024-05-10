import pandas as pd
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

# 读取CSV文件，并选择需要的列
df = pd.read_csv('poi.csv', usecols=['poi_id', 'centroid'])

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


# 设置基本约束条件和循环次数
# base_constraint_distance = 0.0015
constraint_distance = 0.0015
num_iterations = 3

# 初始化无效三角形的顶点
current_points = points_normalized

for iteration in range(num_iterations):

    # 根据迭代次数更新约束距离
    # constraint_distance = base_constraint_distance * (iteration / 5 + 1)

    # 使用当前的点建立无约束的Delaunay三角网
    current_tri = Delaunay(current_points)

    # 初始化invalid_point_mask为True
    invalid_point_mask = np.ones(current_points.shape[0], dtype=bool)
    valid_point_mask = np.zeros(current_points.shape[0], dtype=bool)

    # 计算每个三角形的边长，并检查是否满足约束条件
    valid_simplices = []
    for simplex in current_tri.simplices:
        valid_triangle = True
        for j in range(3):
            p1 = current_points[simplex[j]]
            p2 = current_points[simplex[(j + 1) % 3]]
            if np.linalg.norm(p1 - p2) > constraint_distance:
                valid_triangle = False
                break
        if valid_triangle:
            valid_simplices.append(simplex)
            print(simplex)
            # 将有效三角形的顶点在invalid_point_mask中标记为False
            invalid_point_mask[simplex] = False
            valid_point_mask[simplex] = True

    # 当前迭代没有有效的三角形时，退出循环
    if len(valid_simplices) == 0:
        print(f"No valid simplices in iteration {iteration+1}")
        break

    # 提取当前迭代的满足约束条件的顶点到valid_points
    valid_points_indices = np.where(valid_point_mask)[0]
    valid_points = current_points[valid_points_indices]
    print(len(valid_points))

    # 绘制当前迭代的满足约束条件的三角网
    plt.figure(figsize=(8, 8))
    plt.triplot(current_points[:, 0], current_points[:, 1], valid_simplices, 'r-', linewidth=0.05)
    scatter = plt.scatter(valid_points[:, 0], valid_points[:, 1], c='k', s=0.02, edgecolors='none')  # 修改点的大小
    plt.title(f'Constrained Delaunay Triangulation - Iteration {iteration+1}')
    plt.xlabel('Normalized X coordinate')
    plt.ylabel('Normalized Y coordinate')
    plt.show()

    # 更新当前的点集为无效三角形的顶点
    invalid_points_indices = np.where(invalid_point_mask)[0]
    print(f"Invalid points indices: {invalid_points_indices}")
    # 此时currnet_points中的点为本轮迭代的散点集
    current_points = current_points[invalid_points_indices]
    print(len(current_points))

    # 如果无效点集为空，则退出循环
    if len(current_points) == 0:
        break