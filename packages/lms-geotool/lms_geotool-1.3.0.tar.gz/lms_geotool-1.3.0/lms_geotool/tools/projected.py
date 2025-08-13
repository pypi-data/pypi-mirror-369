import math
from typing import Tuple, Union, Sequence, List

# 常量定义
R: float = 20037508.34


def lonlat_to_mercator(lon: float, lat: float, acc: int = 2) -> tuple[float, float]:
    """
    将经纬度转换为墨卡托投影坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 横纵坐标
    """
    x = lon * R / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180) * R / 180
    return round(x, acc), round(y, acc)


def mercator_to_lonlat(x: float, y: float, acc: int = 8) -> tuple[float, float]:
    """
    将墨卡托投影坐标转换为经纬度
    :param x: 横坐标
    :param y: 纵坐标
    :param acc: 精确度
    :return: 经纬度
    """
    lon = x * 180 / R
    lat = 180 / math.pi * (2 * math.atan(math.exp(y * 180 / R * math.pi / 180)) - math.pi / 2)
    return round(lon, acc), round(lat, acc)


def polygon_area(points: Sequence[Sequence[Union[int, float]]], acc: int = 2) -> float:
    """
    计算由一系列坐标点首尾相连形成的多边形的面积
    :param points: [(x1, y1), (x2, y2), ..., (xn, yn)]
    :param acc: 精准度
    :return: 多边形的面积
    """
    n = len(points)
    area = 0.0
    # 判断多边形顶点数量，若小于3个点，不构成多边形，返回0
    if n >= 3:
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - y1 * x2
        return round(abs(area) / 2, acc)
    return 0.0
