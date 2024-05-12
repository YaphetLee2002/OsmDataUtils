# osm数据类的定义

class NodeInOsm:
    def __init__(self, osm_node_name, osm_node_id, geometry, in_region, osm_highway, ctrl_type):
        self.name = osm_node_name
        self.osm_node_id = osm_node_id
        self.geometry = geometry
        self.geometry_xy = None
        self.osm_highway = osm_highway
        self.ctrl_type = ctrl_type
        self.in_region = in_region
        self.is_crossing = False
        self.node = None
        self.usage_count = 0


class WayInOsm:
    def __init__(self):
        self.osm_way_id = None
        self.highway = None
        self.railway = None
        self.aeroway = None
        self.link_class = ''
        self.link_type_name = ''
        self.link_type = 0
        self.is_link = False
        self.name = None
        self.lanes = None
        self.forward_lanes = None
        self.backward_lanes = None
        self.turn_lanes = None
        self.turn_lanes_forward = None
        self.turn_lanes_backward = None
        self.maxspeed = None
        self.oneway = None
        self.junction = None
        self.area = None
        self.motor_vehicle = None
        self.motorcar = None
        self.service = None
        self.access = None
        self.foot = None
        self.bicycle = None
        self.building = None
        self.amenity = None
        self.leisure = None
        self.way_poi = None
        self.allowable_agent_type_list = []
        self.allowed_uses = []
        self.is_reversed = False
        self.is_cycle = False
        self.is_pure_cycle = False
        self.ref_node_id_list = []
        self.ref_node_list = []
        self.number_of_segments = 0
        self.segment_node_list = []

    def getNodeListForSegments(self):
        number_of_ref_nodes = len(self.ref_node_list)
        last_idx = 0
        idx = 0

        while True:
            m_segment_node_list = [self.ref_node_list[last_idx]]
            for idx in range(last_idx+1,number_of_ref_nodes):
                ref_node = self.ref_node_list[idx]
                m_segment_node_list.append(ref_node)
                if ref_node.is_crossing:
                    last_idx = idx
                    break
            self.segment_node_list.append(m_segment_node_list)
            self.number_of_segments += 1
            if idx == number_of_ref_nodes-1: break


class RelationInOsm:
    def __init__(self):
        self.osm_relation_id = None
        self.member_id_list = []
        self.member_type_list = []
        self.member_list = []
        self.member_role_list = []
        self.name = ''
        self.building = None
        self.amenity = None
        self.leisure = None


class NetworkInOsm:
    def __init__(self):
        self.osm_node_dict = {}
        self.osm_way_dict = {}
        self.osm_relation_list = []
        self.link_way_list = []
        self.POI_way_list = []
        self.bounds = None
        self.GT = None

