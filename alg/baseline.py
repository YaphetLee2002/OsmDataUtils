import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
from sklearn.metrics.pairwise import rbf_kernel

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

# 设置聚类数量，这里以3为例
n_clusters = 500

# 记录开始时间
start_time = time.time()

# K-Means 聚类
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans_labels = kmeans.fit_predict(points_normalized)

# 打印K-Means聚类的耗时
print(f"K-Means clustering took {time.time() - start_time:.3f} seconds")

# 重置开始时间
start_time = time.time()

# 层次聚类
hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
hierarchical_labels = hierarchical.fit_predict(points_normalized)

# 打印层次聚类的耗时
print(f"Hierarchical clustering took {time.time() - start_time:.3f} seconds")

# 重置开始时间
start_time = time.time()

# DBSCAN 聚类
dbscan = DBSCAN(eps=0.003, min_samples=10)  # 这些参数可能需要根据数据调整
dbscan_labels = dbscan.fit_predict(points_normalized)

# 打印DBSCAN聚类的耗时
print(f"DBSCAN clustering took {time.time() - start_time:.3f} seconds")

# 重置开始时间
# start_time = time.time()
#
# # 谱聚类（谱聚类速度太慢，先注释掉了）
# similarity_matrix = rbf_kernel(points_normalized, points_normalized, gamma=0.5)
# spectral = SpectralClustering(n_clusters=n_clusters, affinity='precomputed', random_state=42)
# spectral.fit(similarity_matrix)
# spectral_labels = spectral.labels_
#
# # 打印谱聚类的耗时
# print(f"Spectral clustering took {time.time() - start_time:.3f} seconds")

# 绘制K-Means聚类结果
plt.figure(figsize=(5, 5))
plt.subplot(2, 2, 1)
scatter1 = plt.scatter(points_normalized[:, 0], points_normalized[:, 1], c=kmeans_labels, cmap='tab20', s=0.05, edgecolors='none')
plt.title('K-Means Clustering')
plt.xlabel('X')
plt.ylabel('Y')

# 绘制层次聚类结果
plt.subplot(2, 2, 2)
scatter2 = plt.scatter(points_normalized[:, 0], points_normalized[:, 1], c=hierarchical_labels, cmap='tab20', s=0.05, edgecolors='none')
plt.title('Hierarchical Clustering')
plt.xlabel('X')
plt.ylabel('Y')

# 绘制DBSCAN聚类结果
plt.subplot(2, 2, 3)
scatter3 = plt.scatter(points_normalized[:, 0], points_normalized[:, 1], c=dbscan_labels, cmap='tab20', s=0.05, marker='o', edgecolors='none')
plt.title('DBSCAN Clustering')
plt.xlabel('X')
plt.ylabel('Y')

# # 绘制谱聚类结果
# plt.subplot(2, 2, 4)
# plt.scatter(points_normalized[:, 0], points_normalized[:, 1], c=spectral_labels, cmap='viridis', s=1)
# plt.title('Spectral Clustering')
# plt.xlabel('X')
# plt.ylabel('Y')

# 调整子图间距
plt.tight_layout()

# 显示所有子图
plt.show()