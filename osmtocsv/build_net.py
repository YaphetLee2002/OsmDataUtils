from my_network import Network
import settings
from poi_methods import get_all_pois
from read_from_osm import readOSMFile
from shapely import geometry
from osmclasses import OSMNode
from my_network import Node, Link

_filter_in = {'auto': {'motor_vehicle': {'yes'},
                       'motorcar': {'yes'}},
              'bike': {'bicycle': {'yes'}},
              'walk': {'foot': {'yes'}}}

_filters_ex = {
    'auto': {
        'highway': {'cycleway', 'footway', 'pedestrian', 'steps', 'track', 'corridor', 'elevator', 'escalator',
                    'service', 'living_street'},
        'motor_vehicle': {'no'},
        'motorcar': {'no'},
        'access': {'private'},
        'service': {'parking', 'parking_aisle', 'driveway', 'private', 'emergency_access'}
    },
    'bike': {
        'highway': {'footway', 'steps', 'corridor', 'elevator', 'escalator', 'motor', 'motorway',
                    'motorway_link'},
        'bicycle': {'no'},
        'service': {'private'},
        'access': {'private'}
    },
    'walk': {
        'highway': {'cycleway', 'motor', 'motorway', 'motorway_link'},
        'foot': {'no'},
        'service': {'private'},
        'access': {'private'}
    }
}


def _checkIn(way, agent_type):
    m_filter_in = _filter_in[agent_type]
    for tag, include_list in m_filter_in.items():
        if getattr(way, tag) in include_list:
            return True
    return None


def _checkEx(way, agent_type):
    m_filter_ex = _filters_ex[agent_type]
    for tag, exclude_list in m_filter_ex.items():
        if getattr(way, tag) in exclude_list:
            return False
    return True


def _createNodeOnBoundary(node_in, node_outside, network):
    """
    创建一个在边界上的节点。这个函数主要用于处理在区域边界上的节点，这些节点可能部分在区域内部分在区域外。
    """
    line = network.bounds.intersection(geometry.LineString([node_in.geometry, node_outside.geometry]))
    lon, lat = line.coords[1]
    geometry_lonlat = geometry.Point(
        (round(lon, settings.lonlat_coord_precision), round(lat, settings.lonlat_coord_precision)))
    boundary_osm_node = OSMNode('', '', geometry_lonlat, True, '', '')
    boundary_osm_node.geometry_xy = network.GT.geo_from_latlon(geometry_lonlat)
    boundary_osm_node.is_crossing = True
    return boundary_osm_node


def _getSegmentNodeList(way, segment_no, network):
    """
    获取路段的节点列表。这个函数主要用于获取一个路段上的所有节点，包括在区域内和区域外的节点。
    """
    m_segment_node_list = way.segment_node_list[segment_no]
    if way.is_reversed: m_segment_node_list = list(reversed(m_segment_node_list))
    number_of_nodes = len(m_segment_node_list)

    m_segment_node_list_group = []

    if m_segment_node_list[0].in_region:
        idx_first_outside = -1
        for idx, node in enumerate(m_segment_node_list):
            if not node.in_region:
                idx_first_outside = idx
                break

        if idx_first_outside == -1:
            m_segment_node_list_group.append(m_segment_node_list)
            return m_segment_node_list_group
        else:
            new_node = _createNodeOnBoundary(m_segment_node_list[idx_first_outside - 1],
                                             m_segment_node_list[idx_first_outside], network)
            m_segment_node_list_group.append(m_segment_node_list[:idx_first_outside] + [new_node])

    if m_segment_node_list[-1].in_region:
        idx_last_outside = -1
        for idx in range(number_of_nodes - 2, -1, -1):
            if not m_segment_node_list[idx].in_region:
                idx_last_outside = idx
                break
        new_node = _createNodeOnBoundary(m_segment_node_list[idx_last_outside + 1],
                                         m_segment_node_list[idx_last_outside], network)
        m_segment_node_list_group.append([new_node] + m_segment_node_list[idx_last_outside + 1:])

    return m_segment_node_list_group


def _createNodeFromOSMNode(network, osmnode):
    """
    从OSM节点创建一个新的节点。这个函数主要用于从OSM节点信息中创建一个新的节点对象。
    """
    if osmnode.node is None:
        node = Node(network.max_node_id)
        node.buildFromOSMNode(osmnode)
        osmnode.node = node
        network.node_dict[node.node_id] = node
        network.max_node_id += 1


def _createNodesAndLinks(network, link_way_list):
    """
    创建网络中的节点和链接。这个函数主要用于从OSM的way列表中创建网络中的节点和链接。
    """
    if settings.verbose:
        print('生成节点和道路数据')

    link_dict = {}
    max_link_id = network.max_link_id
    for way in link_way_list:
        if way.is_pure_cycle: continue
        way.getNodeListForSegments()
        for segment_no in range(way.number_of_segments):
            m_segment_node_list_group = _getSegmentNodeList(way, segment_no, network)
            for m_segment_node_list in m_segment_node_list_group:
                if len(m_segment_node_list) < 2: continue
                _createNodeFromOSMNode(network, m_segment_node_list[0])
                _createNodeFromOSMNode(network, m_segment_node_list[-1])

                link = Link(max_link_id)
                link.buildFromOSMWay(way, 1, m_segment_node_list, network.default_lanes, network.default_speed,
                                     network.default_capacity)
                link_dict[link.link_id] = link
                max_link_id += 1
                if not way.oneway:
                    linkb = Link(max_link_id)
                    linkb.buildFromOSMWay(way, -1, list(reversed(m_segment_node_list)), network.default_lanes,
                                          network.default_speed, network.default_capacity)
                    link_dict[linkb.link_id] = linkb
                    max_link_id += 1
    network.link_dict = link_dict
    network.max_link_id = max_link_id


def preprocess_way(osmnetwork, network_types):
    """
    预处理OSM的way。这个函数主要用于处理OSM的way，包括识别路段类型、确定路段是否在区域内等。
    """
    link_way_list = []
    POI_way_list = []
    network_types_set = set(network_types)
    for _, way in osmnetwork.osm_way_dict.items():

        # 对于building、amenity、leisure，是poi中的属性
        if way.building or way.amenity or way.leisure:
            POI_way_list.append(way)

        elif way.highway:
            if way.highway in {'bus_stop', 'platform'}:
                way.way_poi = way.highway
                POI_way_list.append(way)
                continue
            if way.area and way.area != 'no':
                continue
            if way.highway in {'path', 'construction', 'proposed', 'raceway', 'bridleway', 'rest_area', 'su',
                               'road', 'abandoned', 'planned', 'trailhead', 'stairs', 'dismantled', 'disused', 'razed',
                               'access',
                               'corridor', 'stop'}:
                continue
            if len(way.ref_node_list) < 2:
                continue

            try:
                way.link_type_name, way.is_link = settings.osm_highway_type_dict[way.highway]
                way.link_type = settings.link_type_no_dict[way.link_type_name]
            except KeyError:
                continue

            # 获取一条道路允许的通行方式:
            allowable_agent_type_list = []

            for agent_type in ['auto', 'bike', 'walk']:

                allowed_in = None
                allowed_ex = True
                m_filter_in = _filter_in[agent_type]
                for tag, include_list in m_filter_in.items():
                    if getattr(way, tag) in include_list:
                        allowed_in = True
                        break
                m_filter_ex = _filters_ex[agent_type]
                for tag, exclude_list in m_filter_ex.items():
                    if getattr(way, tag) in exclude_list:
                        allowed_ex = False

                if allowed_in:
                    allowable_agent_type_list.append(agent_type)
                    continue
                if allowed_ex:
                    allowable_agent_type_list.append(agent_type)
            way.allowable_agent_type_list = list(set(allowable_agent_type_list).intersection(network_types_set))
            if len(way.allowable_agent_type_list) == 0:
                continue
            way.allowed_uses = way.allowable_agent_type_list

            way.ref_node_list[0].is_crossing = True
            way.ref_node_list[-1].is_crossing = True
            for node in way.ref_node_list:
                node.usage_count += 1

            if way.ref_node_list[0] is way.ref_node_list[-1]:
                way.is_cycle = True
            if way.oneway is None:
                if way.junction in ['circular', 'roundabout']:
                    way.oneway = True
                else:
                    way.oneway = settings.default_oneway_flag_dict[way.link_type_name]
            way.link_class = 'highway'
            link_way_list.append(way)

        else:
            pass

    osmnetwork.link_way_list = link_way_list
    osmnetwork.POI_way_list = POI_way_list


def create_network_data_from_osmnet(osmnetwork, network):
    # 预处理OSM的way。这个函数主要用于处理OSM的way，包括识别路段类型、确定路段是否在区域内等。
    preprocess_way(osmnetwork, ['auto'])

    # 类型为signal和出现多于一次的点是交叉的OSM节点
    for _, osmnode in osmnetwork.osm_node_dict.items():
        if osmnode.usage_count >= 2 or osmnode.ctrl_type == 'signal':
            osmnode.is_crossing = True

    # 标注循环路段
    for way in osmnetwork.link_way_list:
        if way.is_cycle:
            way.is_pure_cycle = True
            for node in way.ref_node_list[1:-1]:
                if node.is_crossing:
                    way.is_pure_cycle = False
                    break

    # 创建网络中的节点和链接。这个函数主要用于从OSM的way列表中创建网络中的节点和链接。
    _createNodesAndLinks(network, osmnetwork.link_way_list)

    # 生成POI数据
    get_all_pois(osmnetwork.POI_way_list, osmnetwork.osm_relation_list, network)


def build_network(osmnetwork):
    """
    构建网络。这个函数主要用于从OSM数据中构建网络，包括创建节点、链接和兴趣点，以及处理网络中的一些特殊情况，如孤立节点、重叠链接等。
    """
    print('构建从osm解析的网络')

    network = Network()
    network.bounds = osmnetwork.bounds
    create_network_data_from_osmnet(osmnetwork, network)

    return network


def get_network(filename):
    osmnetwork = readOSMFile(filename)
    network = build_network(osmnetwork)
    print(f'生成节点{len(network.node_dict)}个，生成路径{len(network.link_dict)}条，生成poi{len(network.POI_list)}个')
    return network
