import math
from typing import Tuple, Union, Sequence, List

# 常量定义
A: int = 6378_245
EE: float = 0.00669342162296594323


def transform_lon(lon: float, lat: float) -> float:
    """
    辅助函数，用于WGS84到GCJ02和GCJ02到WGS84的转换
    :param lon: 经度
    :param lat: 纬度
    :return: 经度偏移量
    """
    ret = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lon * math.pi) + 40.0 * math.sin(lon / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lon / 12.0 * math.pi) + 300.0 * math.sin(lon / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def transform_lat(lon: float, lat: float) -> float:
    """
    辅助函数，用于WGS84到GCJ02和GCJ02到WGS84的转换
    :param lon: 经度
    :param lat: 纬度
    :return: 纬度偏移量
    """
    ret = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    WGS84坐标转换为GCJ02坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    dLon = transform_lon(lon - 105.0, lat - 35.0)
    dLat = transform_lat(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = 1 - EE * math.sin(radLat) * math.sin(radLat)
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (A / sqrtMagic * math.cos(radLat) * math.pi)
    mgLon = lon + dLon
    mgLat = lat + dLat
    return round(mgLon, acc), round(mgLat, acc)


def gcj02_to_wgs84(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    GCJ02坐标转换为WGS84坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    dLat = transform_lat(lon - 105.0, lat - 35.0)
    dLon = transform_lon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = math.sin(radLat)
    magic = 1 - EE * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (A / sqrtMagic * math.cos(radLat) * math.pi)
    mglon = lon + dLon
    mglat = lat + dLat
    return round(lon * 2 - mglon, acc), round(lat * 2 - mglat, acc)


def gcj02_to_bd09(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    GCJ02坐标转换为BD09坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    x_pi = math.pi * 3000.0 / 180.0
    z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * x_pi)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return round(bd_lon, acc), round(bd_lat, acc)


def bd09_to_gcj02(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    BD09坐标转换为GCJ02坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    x_pi = math.pi * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lon = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return round(gg_lon, acc), round(gg_lat, acc)


# 常量定义
R: float = 6371_000.0


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float, acc: int = 2) -> float:
    """
    计算两个经纬度点之间的弧面距离
    :param lon1: 第一个点的经度（单位：度）
    :param lat1: 第一个点的纬度（单位：度）
    :param lon2: 第二个点的经度（单位：度）
    :param lat2: 第二个点的纬度（单位：度）
    :param acc: 精确度
    :return: 两点间的弧面距离（米）
    """
    # 将十进制度数转换为弧度
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    # Haversine公式计算
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # 计算距离
    distance = round(R * c, acc)
    return distance


def coordinate_translation(lon: float, lat: float, dx: float, dy: float, acc: int = 8) -> Tuple[float, float]:
    """
    计算从原点经纬度移动指定距离后的新坐标
    :param lon: 原点经度（单位：度）
    :param lat: 原点纬度（单位：度）
    :param dx: 东西方向移动距离(米)，东为正，西为负
    :param dy: 南北方向移动距离(米)，北为正，南为负
    :param acc: 精准度
    :return: 目标坐标 (x2, y2)
    """
    # 计算南北方向移动（纬度变化）
    dlat = dy / R
    new_lat = lat + math.degrees(dlat)
    # 计算东西方向移动（经度变化）
    avg_lat = math.radians((lat + new_lat) / 2.0)
    dlon = dx / (R * math.cos(avg_lat))
    new_lon = lon + math.degrees(dlon)
    # 处理边界情况（经度范围-180到180）
    new_lon = (new_lon + 180) % 360 - 180
    return round(new_lon, acc), round(new_lat, acc)


def lonlat_to_cartesian(lon: float, lat: float, radius=1.0) -> Tuple[float, float, float]:
    """
    将经纬度转换为三维笛卡尔坐标（单位球）
    :param lon: 经度（度）
    :param lat: 纬度（度）
    :param radius: 球半径（默认单位球）
    :return: (x, y, z) 笛卡尔坐标
    """
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)
    return x, y, z


def spherical_excess(
        a: Tuple[float, float, float],
        b: Tuple[float, float, float],
        c: Tuple[float, float, float]
) -> float:
    """
    计算球面三角形的球面角盈（面积）
    :param b: 单位球上的三个点（三维向量）
    :param a: 单位球上的三个点（三维向量）
    :param c: 单位球上的三个点（三维向量）
    :return: 球面角盈（即面积，单位：球面度）
    """

    # 计算矢量点积
    ab = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    bc = b[0] * c[0] + b[1] * c[1] + b[2] * c[2]
    ca = c[0] * a[0] + c[1] * a[1] + c[2] * a[2]

    # 计算叉积 (a × b) 并与 c 点积
    cross_ab = (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )
    dot_cross_ab_c = cross_ab[0] * c[0] + cross_ab[1] * c[1] + cross_ab[2] * c[2]
    num = abs(dot_cross_ab_c)
    den = 1 + ab + bc + ca

    # 避免分母为零（理论上不会发生）
    if den <= 0:
        return math.pi if num < 1e-10 else 2 * math.atan2(num, den)
    return 2 * math.atan2(num, den)


def spherical_polygon_area(coords: Sequence[Sequence[Union[int, float]]], acc: int = 2) -> float:
    """
    计算球面多边形面积
    :param coords: 经纬度坐标列表，格式 [(lon1, lat1), (lon2, lat2), ...]
    :return: 多边形面积（平方米）
    """
    n = len(coords)
    if n < 3:
        return 0.0

    # 转换为笛卡尔坐标（单位球）
    points = [lonlat_to_cartesian(lon, lat) for lon, lat in coords]

    # 分解多边形为三角形（以第一个顶点为公共顶点）
    total_area = 0.0
    for i in range(1, n - 1):
        a = points[0]
        b = points[i]
        c = points[i + 1]
        total_area += spherical_excess(a, b, c)

    # 球面角盈乘以半径平方
    return round(abs(total_area) * (R ** 2), acc)
