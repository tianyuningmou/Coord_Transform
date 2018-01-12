# 坐标转换模块
此模块用于百度坐标系(bd-09)、火星坐标系(国测局坐标系、gcj02)、WGS84坐标系的相互转换，并提供中文地址到坐标的转换功能，使用了requests第三方库。中文地址到坐标转换使用百度地图API，需要[申请](http://lbsyun.baidu.com/)API KEY。

# 使用说明
```
    lng = 116.4889647
    lat = 39.9854645
    result1 = gcj02_to_bd09(lng, lat)#火星坐标系->百度坐标系
    result2 = bd09_to_gcj02(lng, lat)#百度坐标系->火星坐标系
    result3 = wgs84_to_gcj02(lng, lat)#WGS84坐标系->火星坐标系
    result4 = gcj02_to_wgs84(lng, lat)#火星坐标系->WGS84坐标系
    result5 = bd09_to_wgs84(lng, lat)#百度坐标系->WGS84坐标系
    result6 = wgs84_to_bd09(lng, lat)#WGS84坐标系->百度坐标系

	# 填写在百度生成应用事的ak和sk
    bd_geo = BD_Geocoding('ak', 'sk')
    result7 = bd_geo.baidu_geocode('北京市朝阳区宏源大厦')
    print(result1, result2, result3, result4, result5, result6, result7)
```


