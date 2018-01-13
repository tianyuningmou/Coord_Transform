# -*- coding: utf-8 -*-

"""
Copyright () 2018

All rights reserved by tianyuningmou

FILE:  coord_transform.py
AUTHOR:  tianyuningmou
DATE CREATED:  @Time : 2018/1/12 上午10:29

DESCRIPTION:  .

VERSION: : #1 $
CHANGED By: : tianyuningmou $
CHANGE:  :  $
MODIFIED: : @Time : 2018/1/12 上午10:29
"""

import hashlib
from urllib import parse
import math
import requests

x_pi = 3.14159265358979324 * 3000.0 / 180.0
# 圆周率π
pi = 3.1415926535897932384626
# 长半轴长度
a = 6378245.0
# 地球的角离心率
ee = 0.00669342162296594323
# 矫正参数
interval = 0.000001


class BD_Geocoding:
    # 基于百度地理编码的sn验证方式，IP白名单验证方式在个人管理页面添加IP即可
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk

    def baidu_geocode(self, address):
        """
        利用百度geocoding服务解析地址获取位置坐标
        :param address:需要解析的地址
        :return:
        """

        url = 'http://api.map.baidu.com'
        queryStr = '/geocoder/v2/?address={address}&output=json&ak={ak}'.format(address=address, ak=self.ak)
        encodeStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
        rawStr = encodeStr + self.sk
        sn = hashlib.md5(parse.quote_plus(rawStr).encode(encoding='utf-8')).hexdigest()
        try:
            response = requests.get(url + queryStr + '&sn={sn}'.format(sn=sn)).json()
            location = response['result']['location']
            lng = location['lng']
            lat = location['lat']
            return [lng, lat]
        except:
            result = ['0', '0']
            return result


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)：谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:列表返回
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)：百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:列表返回
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gc_lng = z * math.cos(theta)
    gc_lat = z * math.sin(theta)
    return [gc_lng, gc_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:列表返回
    """
    # 判断是否在国内
    if out_of_china(lng, lat):
        return lng, lat
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    gclng = lng + dlng
    gclat = lat + dlat
    return [gclng, gclat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:列表返回
    """
    # 判断是否在国内
    if out_of_china(lng, lat):
        return lng, lat
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    wgslng = lng + dlng
    wgslat = lat + dlat

    #新加误差矫正部分
    corrent_list = wgs84_to_gcj02(wgslng, wgslat)
    clng = corrent_list[0]-lng
    clat = corrent_list[1]-lat
    dis = math.sqrt(clng*clng + clat*clat)

    while dis > interval:
        clng = clng/2
        clat = clat/2
        wgslng = wgslng - clng
        wgslat = wgslat - clat
        corrent_list = wgs84_to_gcj02(wgslng, wgslat)
        cclng = corrent_list[0] - lng
        cclat = corrent_list[1] - lat
        dis = math.sqrt(cclng*cclng + cclat*cclat)
        clng = clng if math.fabs(clng) > math.fabs(cclng) else cclng
        clat = clat if math.fabs(clat) > math.fabs(cclat) else cclat

    return [wgslng, wgslat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


if __name__ == '__main__':
    lng = 116.4889647
    lat = 39.9854645
    result1 = gcj02_to_bd09(lng, lat)
    result2 = bd09_to_gcj02(lng, lat)
    result3 = wgs84_to_gcj02(lng, lat)
    result4 = gcj02_to_wgs84(lng, lat)
    result5 = bd09_to_wgs84(lng, lat)
    result6 = wgs84_to_bd09(lng, lat)

    # 填写在百度生成应用时的ak和sk
    bd_geo = BD_Geocoding('ak', 'sk')
    result7 = bd_geo.baidu_geocode('北京市朝阳区宏源大厦')
    print(result1, result2, result3, result4, result5, result6, result7)
