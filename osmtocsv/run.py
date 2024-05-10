from build_net import get_network
from shapely import wkt
import csv
import os


def output_node(network, output_folder, node_filename):
    node_filepath = os.path.join(output_folder, node_filename)
    outfile = open(node_filepath, 'w', newline='', errors='ignore')
    writer = csv.writer(outfile)
    writer.writerow(
        ['name', 'node_id', 'osm_node_id', 'osm_highway', 'zone_id', 'ctrl_type', 'node_type', 'activity_type',
         'is_boundary', 'x_coord', 'y_coord', 'intersection_id', 'poi_id'])

    for _, node in network.node_dict.items():
        x_coord = round(node.geometry.x, 7)
        y_coord = round(node.geometry.y, 7)
        line = [node.name, node.node_id, node.osm_node_id, node.osm_highway, node.zone_id, node.ctrl_type, '',
                node.activity_type,
                node.is_boundary, x_coord, y_coord, node.intersection_id, node.poi_id]
        writer.writerow(line)
    outfile.close()

    # 获取文件大小（仅用于检查数据是否正常输出）
    file_size = os.path.getsize(node_filepath)
    print(f"node文件大小：{file_size} bytes")


def output_link(network, output_folder, link_filename):
    link_filepath = os.path.join(output_folder, link_filename)
    outfile = open(link_filepath, 'w', newline='', errors='ignore')
    writer = csv.writer(outfile)
    writer.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes',
                     'free_speed', 'capacity', 'link_type_name', 'link_type', 'geometry', 'allowed_uses', 'from_biway',
                     'is_link'])
    for link_id, link in network.link_dict.items():
        from_biway = 1 if link.from_bidirectional_way else 0
        is_link = 1 if link.is_link else 0
        geometry_ = wkt.dumps(link.geometry, rounding_precision=7)
        line = [link.name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id, link.dir_flag,
                link.length,
                link.lanes, link.free_speed, link.capacity, link.link_type_name, link.link_type, geometry_,
                ';'.join(link.allowed_uses),
                from_biway, is_link]
        writer.writerow(line)
    outfile.close()

    # 获取文件大小的代码
    file_size = os.path.getsize(link_filepath)
    print(f"link文件大小：{file_size} bytes")


def output_poi(network, output_folder, poi_filename):
    poi_filepath = os.path.join(output_folder, poi_filename)
    if network.POI_list:
        outfile = open(poi_filepath, 'w', newline='', errors='ignore')
        writer = csv.writer(outfile)
        writer.writerow(
            ['name', 'poi_id', 'osm_way_id', 'osm_relation_id', 'building', 'amenity', 'leisure', 'way', 'geometry',
             'centroid',
             'area'])
        for poi in network.POI_list:
            geometry_ = poi.geometry
            centroid = poi.centroid
            area = poi.geometry_xy.area
            line = [poi.name, poi.poi_id, poi.osm_way_id, poi.osm_relation_id, poi.building, poi.amenity, poi.leisure,
                    poi.way, geometry_,
                    centroid, round(area, 1)]
            writer.writerow(line)

        outfile.close()
        # 获取poi文件大小
        file_size = os.path.getsize(poi_filepath)
        print(f"POI文件大小：{file_size} bytes")


if __name__ == '__main__':
    net = get_network("osm_data/Beijing.osm")

    print('输出数据集的csv文件')

    if not os.path.isdir('output'): os.mkdir('output')
    output_node(net, 'output', 'node.csv')
    output_link(net, 'output', 'link.csv')
    output_poi(net, 'output', 'poi.csv')

    print("数据集已输出到output文件夹中")

"""
示例输出：
生成节点89611个，生成路径193603条，生成poi105224个
输出数据集的csv文件
node文件大小：4710564 bytes
link文件大小：32772946 bytes
POI文件大小：26636485 bytes
"""