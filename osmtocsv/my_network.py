from process_geo_information import get_line_from_nodes
import math


class Node:
    def __init__(self, node_id):
        # 基础属性
        self.name = None
        self.node_id = node_id
        self.geometry = None
        self.geometry_xy = None

        self.other_attrs = {}

        self.incoming_link_list = []
        self.outgoing_link_list = []

        # osm节点属性（可添加）
        self.zone_id = None
        self.osm_node_id = None  # str
        self.intersection_id = None
        self.osm_highway = None
        self.node_type = ''
        self.ctrl_type = ''
        self.activity_type = ''
        self.controller_id = None
        self.is_boundary = None  # -1:in, 1:out, 2:in&out, 0:no
        self.poi_id = None

        self.movement_list = []

    def generate_from_osmnode(self, osmnode):
        self.name = osmnode.name
        self.osm_node_id = osmnode.osm_node_id
        self.osm_highway = osmnode.osm_highway
        self.ctrl_type = osmnode.ctrl_type
        self.geometry = osmnode.geometry
        self.geometry_xy = osmnode.geometry_xy


class Link:
    def __init__(self, link_id):
        # 基础属性
        self.name = None
        self.link_id = link_id
        self.from_node = None
        self.to_node = None
        self.lanes = None
        self.dir_flag = 1
        self.geometry = None
        self.geometry_xy = None

        self.other_attrs = {}

        # 添加osm中的属性
        self.osm_way_id = None  # str
        self.free_speed = None
        self.capacity = None
        self.link_class = ''  # highway, railway, aeroway
        self.link_type_name = ''
        self.link_type = 0
        self.allowed_uses = None
        self.is_link = False
        self.is_connector = False

        self.from_bidirectional_way = False
        self.ctrl_type = None  # signal node in the middle

        self.segment_list = []

    def generate_from_osmway(self, way, direction, ref_node_list, default_lanes, default_speed, default_capacity):
        self.osm_way_id = way.osm_way_id
        self.name = way.name
        self.link_class = way.link_class
        self.link_type_name = way.link_type_name
        self.link_type = way.link_type
        self.is_link = way.is_link

        if way.maxspeed:
            self.free_speed = way.maxspeed
        elif default_speed:
            self.free_speed = default_speed[self.link_type_name]

        if default_capacity:
            self.capacity = default_capacity[self.link_type_name]

        self.allowed_uses = way.allowed_uses
        if not way.oneway: self.from_bidirectional_way = True

        if way.oneway:
            self.lanes = way.lanes
        else:
            if direction == 1:
                if way.forward_lanes is not None:
                    self.lanes = way.forward_lanes
                elif way.lanes is not None:
                    self.lanes = math.ceil(way.lanes / 2)
                else:
                    self.lanes = way.lanes
            else:
                if way.backward_lanes is not None:
                    self.lanes = way.backward_lanes
                elif way.lanes is not None:
                    self.lanes = math.ceil(way.lanes / 2)
                else:
                    self.lanes = way.lanes

        if (self.lanes is None) and default_lanes:
            self.lanes = default_lanes[self.link_type_name]

        for ref_node in ref_node_list[1:-1]:
            if ref_node.ctrl_type == 'signal':
                self.ctrl_type = 'signal'

        self.from_node = ref_node_list[0].node
        self.to_node = ref_node_list[-1].node
        self.geometry, self.geometry_xy = get_line_from_nodes(ref_node_list)
        self.from_node.outgoing_link_list.append(self)
        self.to_node.incoming_link_list.append(self)

    @property
    def length(self):
        return round(self.geometry_xy.length, 2)


# POI类，读取osm中的poi信息（绑定到node?）
class POI:
    def __init__(self):
        self.poi_id = 0
        self.osm_way_id = None  # str
        self.osm_relation_id = None
        self.name = None
        self.geometry = None
        self.geometry_xy = None
        self.centroid = None
        self.centroid_xy = None
        self.nearest_node = None
        self.building = None
        self.amenity = None
        self.leisure = None
        self.way = None  # highway,railway,aeroway poi


class Network:
    def __init__(self):
        # 基础属性
        self.node_dict = {}
        self.link_dict = {}

        self.max_node_id = 0
        self.max_link_id = 0

        self.GT = None
        self.bounds = None

        self.node_other_attrs = []
        self.link_other_attrs = []

        # 添加osm中的属性
        self.default_lanes = False
        self.default_speed = False
        self.default_capacity = False

        self.max_intersection_id = 0
        self.max_segment_id = 0
        self.max_poi_id = 0
        self.max_movement_id = 0

        self.POI_list = []
