import logging

# 是否启用日志记录
log = False
# 日志级别
log_level = logging.WARNING
# 日志名称
log_name = 'osm2gmns'

# 是否启用详细输出
verbose = True

# 经纬度坐标精度
lonlat_coord_precision = 7
# 本地坐标精度
local_coord_precision = 2

# 默认的道路缓冲区大小（单位：米）
default_int_buffer = 20.0
# 道路分辨率（单位：米）
segment_resolution = 5.0

# OpenStreetMap 中的道路类型字典，将其映射到内部表示
osm_highway_type_dict = {
    'motorway': ('motorway', False),
    'motorway_link': ('motorway', True),
    'trunk': ('trunk', False),
    'trunk_link': ('trunk', True),
    'primary': ('primary', False),
    'primary_link': ('primary', True),
    'secondary': ('secondary', False),
    'secondary_link': ('secondary', True),
    'tertiary': ('tertiary', False),
    'tertiary_link': ('tertiary', True),
    'residential': ('residential', False),
    'residential_link': ('residential', True),
    'living_street': ('living_street', False),
    'service': ('service', False),
    'services': ('service', False),
    'cycleway': ('cycleway', False),
    'footway': ('footway', False),
    'pedestrian': ('footway', False),
    'steps': ('footway', False),
    'track': ('track', False),
    'unclassified': ('unclassified', False)
}

# 链接类型编号字典
link_type_no_dict = {
    'motorway': 1, 'trunk': 2, 'primary': 3, 'secondary': 4,
    'tertiary': 5, 'residential': 6, 'living_street': 7,
    'service': 8, 'cycleway': 9, 'footway': 10, 'track': 11,
    'unclassified': 15, 'connector': 20, 'railway': 30, 'aeroway': 31
}

# 默认车道数字典
default_lanes_dict = {
    'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2,
    'tertiary': 2, 'residential': 1, 'living_street': 1, 'service': 1,
    'cycleway': 1, 'footway': 1, 'track': 1, 'unclassified': 1, 'connector': 2
}

# 默认速度限制字典（单位：km/h）
default_speed_dict = {
    'motorway': 120, 'trunk': 100, 'primary': 80, 'secondary': 60,
    'tertiary': 40, 'residential': 30, 'living_street': 30, 'service': 30,
    'cycleway': 5, 'footway': 5, 'track': 30, 'unclassified': 30, 'connector': 120
}

# 默认容量字典（车辆每小时通过数）
default_capacity_dict = {
    'motorway': 2300, 'trunk': 2200, 'primary': 1800,
    'secondary': 1600, 'tertiary': 1200, 'residential': 1000,
    'living_street': 1000, 'service': 800,
    'cycleway': 800, 'footway': 800, 'track': 800,
    'unclassified': 800, 'connector': 9999
}

# 默认单行道标志字典
default_oneway_flag_dict = {
    'motorway': False, 'trunk': False, 'primary': False,
    'secondary': False, 'tertiary': False,
    'residential': False, 'living_street': False,
    'service': False, 'cycleway': True, 'footway': True,
    'track': True, 'unclassified': False, 'connector': False,
    'railway': True, 'aeroway': True
}

# 默认边界坐标
default_bounds = {
    'minlat': -90.0,
    'minlon': -180.0,
    'maxlat': 90.0,
    'maxlon': 180.0
}
