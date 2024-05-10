from my_network import POI
from osmclasses import Way
from process_geo_information import get_polygon_from_nodes
from shapely import geometry


def get_poi_from_way(POI_way_list, net_bound):
    print("从道路中获取poi数据...")
    POI_list_from_way = []
    for way in POI_way_list:
        poly, poly_xy = get_polygon_from_nodes(way.ref_node_list)
        if poly is None: continue
        if poly.disjoint(net_bound): continue

        poi = POI()
        poi.osm_way_id = way.osm_way_id
        poi.name = way.name
        poi.building = way.building
        poi.amenity = way.amenity
        poi.leisure = way.leisure
        poi.way = way.way_poi

        poi.geometry, poi.geometry_xy = poly, poly_xy
        lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
        poi.centroid = geometry.Point((round(lon,7),round(lat,7)))
        x, y = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y
        poi.centroid_xy = geometry.Point((round(x,2),round(y,2)))
        POI_list_from_way.append(poi)
    print(f'道路中获取poi数据数量为：{POI_list_from_way.__len__()}')
    return POI_list_from_way


def get_poi_from_relation(POI_relation_list, net_bound):
    print("从关系中获取poi数据...")
    poi_list_from_relation = []
    for relation in POI_relation_list:
        poi = POI()
        poi.osm_relation_id = relation.osm_relation_id
        poi.name = relation.name
        poi.building = relation.building
        poi.amenity = relation.amenity
        poi.leisure = relation.leisure
        polygon_list = []
        polygon_list_xy = []
        number_of_members = len(relation.member_list)
        m_ref_node_list = []
        for m in range(number_of_members):
            member = relation.member_list[m]
            role = relation.member_role_list[m]
            if isinstance(member, Way):
                if role != 'outer': continue
                if m_ref_node_list:
                    combined_ref_node_list = []
                    if m_ref_node_list[-1] is member.ref_node_list[0]:
                        combined_ref_node_list = m_ref_node_list + member.ref_node_list[1:]
                    elif m_ref_node_list[-1] is member.ref_node_list[-1]:
                        combined_ref_node_list = m_ref_node_list + list(reversed(member.ref_node_list[:-1]))
                    elif m_ref_node_list[0] is member.ref_node_list[0]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + member.ref_node_list[1:]
                    elif m_ref_node_list[0] is member.ref_node_list[-1]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + list(reversed(member.ref_node_list[:-1]))

                    if combined_ref_node_list:
                        if combined_ref_node_list[0] is combined_ref_node_list[-1]:
                            poly, poly_xy = get_polygon_from_nodes(combined_ref_node_list)
                            if poly is not None:
                                polygon_list.append(poly)
                                polygon_list_xy.append(poly_xy)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = combined_ref_node_list
                    else:
                        poly, poly_xy = get_polygon_from_nodes(m_ref_node_list)
                        if poly is not None:
                            polygon_list.append(poly)
                            polygon_list_xy.append(poly_xy)
                        if member.ref_node_list[0] is member.ref_node_list[-1]:
                            poly, poly_xy = get_polygon_from_nodes(m_ref_node_list)
                            if poly is not None:
                                polygon_list.append(poly)
                                polygon_list_xy.append(poly_xy)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = member.ref_node_list
                else:
                    if member.ref_node_list[0] is member.ref_node_list[-1]:
                        poly, poly_xy = get_polygon_from_nodes(member.ref_node_list)
                        if poly is not None:
                            polygon_list.append(poly)
                            polygon_list_xy.append(poly_xy)
                    else:
                        m_ref_node_list = member.ref_node_list
            else:
                pass

        if m_ref_node_list:
            poly, poly_xy = get_polygon_from_nodes(m_ref_node_list)
            if poly is not None:
                polygon_list.append(poly)
                polygon_list_xy.append(poly_xy)

        if len(polygon_list) == 0:
            continue
        else:
            if len(polygon_list) == 1:
                poi.geometry = polygon_list[0]
                if poi.geometry.disjoint(net_bound): continue
                poi.geometry_xy = polygon_list_xy[0]
            else:
                disjoint = True
                for poly in polygon_list:
                    if not poly.disjoint(net_bound):
                        disjoint = False
                        break
                if disjoint: continue
                poi.geometry = geometry.MultiPolygon(polygon_list)
                poi.geometry_xy = geometry.MultiPolygon(polygon_list_xy)

            lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
            poi.centroid = geometry.Point((round(lon, 7), round(lat, 7)))
            x, y = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y
            poi.centroid_xy = geometry.Point((round(x, 2), round(y, 2)))

            poi_list_from_relation.append(poi)
    print(f'关系中获取poi数据数量为：{poi_list_from_relation.__len__()}')
    return poi_list_from_relation


def get_all_pois(POI_way_list, osm_relation_list, network):
    print('生成POI数据')

    POI_list1 = get_poi_from_way(POI_way_list, network.bounds)
    POI_list2 = get_poi_from_relation(osm_relation_list, network.bounds)

    POI_list = POI_list1 + POI_list2

    max_poi_id = network.max_poi_id
    for poi in POI_list:
        poi.poi_id = max_poi_id
        max_poi_id += 1
    network.max_poi_id = max_poi_id
    network.POI_list = POI_list
