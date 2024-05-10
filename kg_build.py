import json
import csv

# Parse point osm_data
point = []
with open("osmtocsv/output/node_cleaned.csv", "r", encoding="utf-8") as node:
    node_reader = csv.DictReader(node)

    for row in node_reader:
        name = row['name']
        id = row['node_id']
        osm_id = row['osm_node_id']
        osm_highway = row['osm_highway']
        ctrl_type = row['ctrl_type']
        poi = [row['x_coord'], row['y_coord']]

        point_data = {"name": name,
                      "id": id,
                      "osm_node_id": osm_id,
                      "osm_highway": osm_highway,
                      "ctrl_type": ctrl_type,
                      "poi": poi,
                      "label": "pos"
                      }
        point.append(point_data)

# Save point osm_data to JSON
with open('osmtocsv/output/point_data.json', 'w', encoding="utf-8") as outfile:
    json.dump(point, outfile, ensure_ascii=False)

# Parse edge osm_data
edge = []
with open("../../DataspellProjects/BeijingData/data/link.csv", "r", encoding="utf-8") as link:
    link_reader = csv.DictReader(link)

    for row in link_reader:
        name = row['name']
        id = row['link_id']
        osm_id = row['osm_way_id']
        start_node_id = row['from_node_id']
        end_node_id = row['to_node_id']
        length = row['length']
        lanes = row['lanes']
        free_speed = row['free_speed']
        link_type = row['link_type_name']
        geometry = row['geometry']
        is_biway = bool(row['from_biway'])

        edge_data = {
            "id": id,
            "properties": {"edge_name": name,
                           "osm_edge_id": osm_id,
                           "length": length,
                           "lanes": lanes,
                           "free_speed": free_speed,
                           "link_type": link_type,
                           "geometry": geometry,
                           "is_biway": is_biway
                           },
            "src_node_id": start_node_id,
            "target_node_id": end_node_id,
            "edgelabel": "pos_pos",
            "src_label": "pos",
            "target_label": "pos"
        }
        edge.append(edge_data)

# Save edge osm_data to JSON
with open('osmtocsv/output/edge_data.json', 'w', encoding="utf-8") as outfile:
    json.dump(edge, outfile, ensure_ascii=False)

# Parse poi osm_data
poi = []
with open('osmtocsv/output/poi_cleaned.csv', 'r', encoding="utf-8") as poi_file:
    poi_reader = csv.DictReader(poi_file)

    for row in poi_reader:
        name = row['name']
        poi_id = row['poi_id']
        osm_way_id = row['osm_way_id']
        osm_relation_id = row['osm_relation_id']
        building = row['building']
        amenity = row['amenity']
        leisure = row['leisure']
        way = row['way']
        geometry = row['geometry']
        centroid = row['centroid']
        area = row['area']
        area_ft2 = row['area_ft2']

        poi_data = {
            "name": name,
            "poi_id": poi_id,
            "osm_way_id": osm_way_id,
            "osm_relation_id": osm_relation_id,
            "building": building,
            "amenity": amenity,
            "leisure": leisure,
            "way": way,
            "geometry": geometry,
            "centroid": centroid,
            "area": area,
            "area_ft2": area_ft2
        }
        poi.append(poi_data)

# Save poi osm_data to JSON
with open('osmtocsv/output/poi_data.json', 'w', encoding="utf-8") as outfile:
    json.dump(poi, outfile, ensure_ascii=False)
