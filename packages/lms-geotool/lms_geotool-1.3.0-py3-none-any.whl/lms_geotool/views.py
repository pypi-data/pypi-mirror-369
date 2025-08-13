import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .tools.projected import lonlat_to_mercator, mercator_to_lonlat
from .tools.geographic import wgs84_to_gcj02, gcj02_to_wgs84, gcj02_to_bd09, bd09_to_gcj02, haversine_distance, spherical_polygon_area, coordinate_translation
from .tools.matrix import apply_affine_transform, calc_scale, calc_shear
from .models import AffineMatrix, LinearRegression
from .apps import GeotoolConfig

# Create your views here.
TRANSFORMATION_MAP = {
    '1-2': lambda point: lonlat_to_mercator(point[0], point[1]),
    '2-1': lambda point: mercator_to_lonlat(point[0], point[1]),

    '3-4': lambda point: lonlat_to_mercator(point[0], point[1]),
    '4-3': lambda point: mercator_to_lonlat(point[0], point[1]),

    '5-6': lambda point: lonlat_to_mercator(point[0], point[1]),
    '6-5': lambda point: mercator_to_lonlat(point[0], point[1]),

    '1-3': lambda point: wgs84_to_gcj02(point[0], point[1]),
    '3-1': lambda point: gcj02_to_wgs84(point[0], point[1]),

    '3-5': lambda point: gcj02_to_bd09(point[0], point[1]),
    '5-3': lambda point: bd09_to_gcj02(point[0], point[1]),
}


@login_required(login_url="/admin/")
def convert_html(request):
    if request.method == "GET":
        context = {}
        return render(request, f"{GeotoolConfig.name}/convert.html", context=context)

    elif request.method == "POST":
        input_choose = request.POST.get("input_choose")
        output_choose = request.POST.get("output_choose")
        transformation_key = f"{input_choose}-{output_choose}"

        input_area = request.POST.get("input_area")
        input_list = input_area.split("\r\n")
        context = {
            "input_choose": input_choose,
            "output_choose": output_choose,
            "input_area": json.dumps(input_area)
        }
        try:
            transform_function = TRANSFORMATION_MAP[transformation_key]
            result = []
            for each in input_list:
                positions = each.split(",")
                temp = transform_function([float(positions[0]), float(positions[1])])
                result.append(f"{temp[0]},{temp[1]}")
            res = "\r\n".join(result)
        except KeyError as e:
            res = f"{e}\r\n暂不支持跨步骤转换，请逐步操作"
        except IndexError as e:
            res = f"{e}\r\n缺少部分数据，请检查数据格式"
        except ValueError as e:
            res = f"{e}\r\n存在非法字符，请检查数据格式"

        context["output_area"] = json.dumps(res)
        return render(request, f"{GeotoolConfig.name}/convert.html", context=context)


@login_required(login_url="/admin/")
def matrix_html(request):
    mapid = request.GET.get("mapid")
    context = {}
    try:
        map = AffineMatrix.objects.get(mapid=mapid)
        anchor = map.anchor.all()
        anchor_list = [{
            "origin_x": each.origin_x,
            "origin_y": each.origin_y,
            "target_x": each.target_x,
            "target_y": each.target_y,
        } for each in anchor]

        source_data = [[each.origin_x, each.origin_y] for each in anchor]
        target_data = [[each.target_x, each.target_y] for each in anchor]
        scale_rate = calc_scale(source_data, target_data)
        shear_rate = calc_shear(json.loads(map.matrix))
        context.update({
            "mapid": map.mapid,
            "name": map.name,
            "floor": map.floor,
            "matrix": map.matrix,
            "anchor": json.dumps(anchor_list),
            "scale_rate": scale_rate,
            "shear_rate": shear_rate
        })
    except AffineMatrix.DoesNotExist as e:
        print(e)
    except Exception as e:
        print(e)

    if request.method == "POST":
        input_area = request.POST.get("input_area")
        input_list = input_area.split("\r\n")

        try:
            result = []
            for each in input_list:
                positions = each.split(",")
                # print(positions)
                temp = apply_affine_transform(float(positions[0]), float(positions[1]), context.get("matrix"))
                result.append(f"{temp[0]},{temp[1]}")
            res = "\r\n".join(result)
        except KeyError as e:
            res = f"{e}\r\n暂不支持跨步骤转换，请逐步操作"
        except IndexError as e:
            res = f"{e}\r\n缺少部分数据，请检查数据格式"
        except ValueError as e:
            res = f"{e}\r\n存在非法字符，请检查数据格式"
        context.update({
            "input_area": json.dumps(input_area),
            "output_area": json.dumps(res)
        })
    return render(request, f"{GeotoolConfig.name}/matrix.html", context=context)


@login_required(login_url="/admin/")
def dimsum_html(request):
    if request.method == "GET":
        context = {}
        return render(request, f"{GeotoolConfig.name}/dimsum.html", context=context)
    elif request.method == "POST":
        input_choose = request.POST.get("input_choose")
        input_area = request.POST.get("input_area")
        input_list = input_area.split("\r\n")
        context = {
            "input_choose": input_choose,
            "input_area": json.dumps(input_area)
        }
        try:
            if input_choose == "1":
                res = 0
                for each in range(len(input_list) - 1):
                    print(each)
                    temp1 = input_list[each].split(",")
                    temp2 = input_list[each + 1].split(",")
                    s = haversine_distance(float(temp1[0]), float(temp1[1]), float(temp2[0]), float(temp2[1]))
                    res += s
                result = f"{round(res, 2)} 米"
            elif input_choose == "2":
                res = spherical_polygon_area([(float(each.split(",")[0]), float(each.split(",")[1])) for each in input_list])
                result = f"{res} 平方米"
            else:
                result = 0
        except ValueError as e:
            result = f"{e}\r\n存在非法字符，请检查数据格式"
        except IndexError as e:
            result = f"{e}\r\n缺少部分数据，请检查数据格式"
        except Exception as e:
            result = f"{e}"
        context["output_area"] = json.dumps(result)
        return render(request, f"{GeotoolConfig.name}/dimsum.html", context=context)


@login_required(login_url="/admin/")
def translation_html(request):
    if request.method == "GET":
        context = {
            "lon": 0,
            "lat": 0,
            "x": 0,
            "y": 0
        }
        return render(request, f"{GeotoolConfig.name}/translation.html", context=context)
    elif request.method == "POST":
        lon = request.POST.get("lon")
        lat = request.POST.get("lat")
        x = request.POST.get("x")
        y = request.POST.get("y")
        context = {
            "lon": lon,
            "lat": lat,
            "x": x,
            "y": y
        }
        try:

            res = coordinate_translation(float(lon), float(lat), float(x), float(y))
            result = f"经度：{res[0]}；纬度：{res[1]}"
            context["result"] = result
        except Exception as e:
            print(e)
            raise
        return render(request, f"{GeotoolConfig.name}/translation.html", context=context)


@login_required(login_url="/admin/")
def regression_html(request):
    lrid = request.GET.get("lrid")
    context = {}
    try:
        lr = LinearRegression.objects.get(lrid=lrid)
        samplepoint = lr.samplepoint.filter(is_valid=True).all()
        samplepoint_list = [{
            "x": each.x,
            "y": each.y,
        } for each in samplepoint]

        x_values = [item["x"] for item in samplepoint_list]
        y_values = [item["y"] for item in samplepoint_list]

        max_x, min_x = max(x_values), min(x_values)
        max_y, min_y = max(y_values), min(y_values)

        context.update({
            "lrid": lr.lrid,
            "name": lr.name,
            "k": lr.k,
            "b": lr.b,
            "max_x": max_x,
            "min_x": min_x,
            "max_y": max_y,
            "min_y": min_y,
            "samplepoint": json.dumps(samplepoint_list),
        })
    except Exception as e:
        print(e)

    if request.method == "POST":
        input_value = request.POST.get("input_value")
        output_value = float(input_value) * context.get("k") + context.get("b")
        context.update({
            "output_value": output_value
        })
    return render(request, f"{GeotoolConfig.name}/regression.html", context=context)
