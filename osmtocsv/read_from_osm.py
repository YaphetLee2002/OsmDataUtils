from osmclasses import OSMNode, Way, Relation, OSMNetwork
from process_geo_information import from_latlon
from process_geo_information import GeoTransformer
from shapely import geometry
import numpy as np
import osmium
import re


class NWRHandler(osmium.SimpleHandler):
    """
    从osmium.SimpleHandler派生的类
    处理OSM文件中的节点（Node）、道路（Way）和关系（Relation）数据
    是解析OSM文件，并将解析的结果存储在类的属性中
    """
    """
    关于SimpleHandler：
    最通用的OSM数据处理程序。从此类派生您的数据处理器，并为您感兴趣的每个对象类型实现回调。可识别以下数据类型：
    节点、方式、关系、区域和变更集
    回调只接受一个参数，即对象。请注意，交给处理程序的所有对象都只能读取，并且只有在回调结束时才有效。任何应该保留的数据都必须复制到其他数据结构中。
    """

    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        # self.bounds = None

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}
        self.relation_list = []

    def node(self, n):
        osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node_geometry = geometry.Point(lon, lat)
        in_region = True

        osm_node_name = n.tags.get('name')
        osm_highway = n.tags.get('highway')
        ctrl_type = 'signal' if (osm_highway is not None) and 'signal' in osm_highway else None

        node = OSMNode(osm_node_name, osm_node_id, node_geometry, in_region, osm_highway, ctrl_type)
        self.osm_node_dict[node.osm_node_id] = node

        self.osm_node_id_list.append(osm_node_id)
        self.osm_node_coord_list.append((lon, lat))
        del n

    def way(self, w):
        way = Way()
        way.osm_way_id = str(w.id)
        way.ref_node_id_list = [str(node.ref) for node in w.nodes]

        way.highway = w.tags.get('highway')
        way.railway = w.tags.get('railway')
        way.aeroway = w.tags.get('aeroway')

        lane_info = w.tags.get('lanes')
        if lane_info is not None:
            lanes = re.findall(r'\d+\.?\d*', lane_info)
            if len(lanes) > 0:
                way.lanes = int(float(lanes[0]))

        lane_info = w.tags.get('lanes:forward')
        if lane_info is not None:
            try:
                way.forward_lanes = int(lane_info)
            except:
                pass

        lane_info = w.tags.get('lanes:backward')
        if lane_info is not None:
            try:
                way.backward_lanes = int(lane_info)
            except:
                pass

        way.turn_lanes = w.tags.get('turn:lanes')
        way.turn_lanes_forward = w.tags.get('turn:lanes:forward')
        way.turn_lanes_backward = w.tags.get('turn:lanes:backward')

        way.name = w.tags.get('name')

        maxspeed_info = w.tags.get('maxspeed')
        if maxspeed_info is not None:
            way.maxspeed = int(float(maxspeed_info))

        oneway_info = w.tags.get('oneway')
        if oneway_info is not None:
            if oneway_info == 'yes' or oneway_info == '1':
                way.oneway = True
            elif oneway_info == 'no' or oneway_info == '0':
                way.oneway = False
            elif oneway_info == '-1':
                way.oneway = True
                way.is_reversed = True
            elif oneway_info in ['reversible', 'alternating']:
                way.oneway = False
            else:
                pass

        way.junction = w.tags.get('junction')
        way.area = w.tags.get('area')
        way.motor_vehicle = w.tags.get('motor_vehicle')
        way.motorcar = w.tags.get('motorcar')
        way.service = w.tags.get('service')
        way.foot = w.tags.get('foot')
        way.bicycle = w.tags.get('bicycle')
        way.building = w.tags.get('building')
        way.amenity = w.tags.get('amenity')
        way.leisure = w.tags.get('leisure')

        self.osm_way_dict[way.osm_way_id] = way
        del w

    def relation(self, r):
        relation = Relation()
        relation.osm_relation_id = str(r.id)

        relation.building = r.tags.get('building')
        relation.amenity = r.tags.get('amenity')
        relation.leisure = r.tags.get('leisure')
        if (relation.building is None) and (relation.amenity is None):
            return
        relation.name = r.tags.get('name')

        for member in r.members:
            member_id, member_type, member_role = member.ref, member.type, member.role
            member_id_str = str(member_id)
            member_type_lc = member_type.lower()
            if member_type_lc == 'n':
                relation.member_id_list.append(member_id_str)
            elif member_type_lc == 'w':
                relation.member_id_list.append(member_id_str)
            else:
                pass
            relation.member_type_list.append(member_type_lc)
            relation.member_role_list.append(member_role)

        self.relation_list.append(relation)
        del r


def _processNodes(net, h):
    coord_array = np.array(h.osm_node_coord_list)
    central_lon, central_lat = np.mean(coord_array, axis=0)
    central_lon, central_lat = float(central_lon), float(central_lat)
    northern = True if central_lat >= 0 else False

    xs, ys = from_latlon(coord_array[:, 0], coord_array[:, 1], central_lon)
    for node_no, node_id in enumerate(h.osm_node_id_list):
        node = h.osm_node_dict[node_id]
        node.geometry_xy = geometry.Point((xs[node_no], ys[node_no]))

    net.osm_node_dict = h.osm_node_dict
    net.GT = GeoTransformer(central_lon, central_lat, northern)


def _processWays(net, h):
    for osm_way_id, osm_way in h.osm_way_dict.items():
        osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
        net.osm_way_dict[osm_way_id] = osm_way


def _processRelations(net, h):
    for relation in h.relation_list:
        valid = True
        for member_no, member_id in enumerate(relation.member_id_list):
            member_type = relation.member_type_list[member_no]
            if member_type == 'n':
                relation.member_list.append(net.osm_node_dict[member_id])
            elif member_type == 'w':
                relation.member_list.append(net.osm_way_dict[member_id])
            else:
                pass

        if valid:
            net.osm_relation_list.append(relation)


# used by getNetFromFile
def readOSMFile(filename):
    print('读取OSM文件信息')
    osmnet = OSMNetwork()
    f = osmium.io.Reader(filename)
    header = f.header()
    box = header.box()
    bottom_left = box.bottom_left
    top_right = box.top_right
    minlat, minlon = bottom_left.lat, bottom_left.lon
    maxlat, maxlon = top_right.lat, top_right.lon
    osmnet.bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])
    h = NWRHandler()
    h.bounds = osmnet.bounds
    h.apply_file(filename)

    _processNodes(osmnet, h)
    _processWays(osmnet, h)
    _processRelations(osmnet, h)
    return osmnet
