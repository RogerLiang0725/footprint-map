"""
把 Natural Earth 的真实国界 / 一级行政区数据，做拓扑简化后投影成 SVG 路径。

用法:
    pip install shapely topojson
    python scripts/build_vector.py                 # 生成 data/world.js + data/admin1.js
    python scripts/build_vector.py --simplify 0.02 # 保留更多细节(文件更大)
    python scripts/build_vector.py --no-admin1

投影: Equal Earth (等积), 闭式公式, 浏览器端不需要任何投影库。
简化: 用 topojson 做拓扑简化 —— 相邻国家共享的边界会被一起简化,
所以不会像逐个多边形简化那样在国界之间裂出缝隙。
"""
import argparse
import json
import math
import os
import urllib.request

import topojson
from shapely.geometry import shape

BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = {
    "countries": "ne_50m_admin_0_countries.geojson",
    "admin1": "ne_10m_admin_1_states_provinces.geojson",
}

# ---------- Equal Earth 投影 ----------
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
_SQRT3 = math.sqrt(3)


def equal_earth(lon, lat):
    lam = math.radians(lon)
    phi = math.radians(max(-90.0, min(90.0, lat)))
    th = math.asin(_SQRT3 / 2 * math.sin(phi))
    t2 = th * th
    y = th * (A1 + A2 * t2 + A3 * t2**3 + A4 * t2**4)
    dy = A1 + 3 * A2 * t2 + 7 * A3 * t2**3 + 9 * A4 * t2**4
    x = 2 * _SQRT3 * lam * math.cos(th) / (3 * dy)
    return x, y


X_MAX = equal_earth(180, 0)[0]
Y_MAX = equal_earth(0, 90)[1]


def fetch(name):
    fn = FILES[name]
    if not os.path.exists(fn):
        print(f"下载 {fn} ...")
        urllib.request.urlretrieve(BASE + fn, fn)
    return json.load(open(fn, encoding="utf-8"))


def simplify(features, tol):
    """拓扑简化: 相邻多边形共享的边界一起简化, 不会裂缝。"""
    # 先用 shapely 粗筛掉密集顶点, 否则 4600 个 10m 精度多边形会撑爆内存
    pre = []
    for f in features:
        g = shape(f["geometry"]).simplify(tol / 4, preserve_topology=True)
        if g.is_empty:
            continue
        pre.append({"type": "Feature", "properties": f["properties"],
                    "geometry": json.loads(json.dumps(g.__geo_interface__))})
    topo = topojson.Topology(pre, prequantize=1e5, topology=True, shared_coords=False)
    return json.loads(topo.toposimplify(tol).to_geojson())["features"]


def simplify_grouped(features, tol, key):
    """按国家分组做拓扑简化 —— 同一国家内部的省界依然严丝合缝, 内存也扛得住。"""
    groups = {}
    for f in features:
        groups.setdefault(f["properties"].get(key), []).append(f)
    out = []
    for k, fs in groups.items():
        try:
            out.extend(simplify(fs, tol))
        except Exception as e:  # 个别畸形几何单独降级处理
            print(f"  ! {k} 拓扑简化失败({e.__class__.__name__}), 改用逐个简化")
            for f in fs:
                g = shape(f["geometry"]).simplify(tol, preserve_topology=True)
                if not g.is_empty:
                    out.append({"type": "Feature", "properties": f["properties"],
                                "geometry": json.loads(json.dumps(g.__geo_interface__))})
    return out


def to_path(geom, scale, ox, oy, nd):
    """shapely 几何 -> SVG path d"""
    parts = []

    def ring(coords):
        out = []
        prev = None
        for lon, lat in coords:
            x, y = equal_earth(lon, lat)
            px = round(ox + x * scale, nd)
            py = round(oy - y * scale, nd)
            if (px, py) != prev:
                out.append((px, py))
                prev = (px, py)
        if len(out) < 3:
            return
        parts.append("M" + " ".join(f"{x} {y}" for x, y in out) + "Z")

    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for poly in polys:
        if poly.is_empty:
            continue
        ring(poly.exterior.coords)
        for h in poly.interiors:
            ring(h.coords)
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=2000, help="投影后画布宽度(px)")
    ap.add_argument("--simplify", type=float, default=0.05, help="国界简化容差, 越小越精细")
    ap.add_argument("--simplify-admin1", type=float, default=0.08)
    ap.add_argument("--decimals", type=int, default=1, help="坐标小数位")
    ap.add_argument("--no-admin1", action="store_true")
    ap.add_argument("--outdir", default="data")
    a = ap.parse_args()

    scale = a.width / (2 * X_MAX)
    height = 2 * Y_MAX * scale
    ox, oy = a.width / 2, height / 2
    os.makedirs(a.outdir, exist_ok=True)

    # ---------- 国家 ----------
    src = fetch("countries")["features"]
    feats = simplify(src, a.simplify)
    a3_to_a2 = {}
    countries = []
    for f in feats:
        p = f["properties"]
        iso = p.get("ISO_A2_EH") or p.get("ISO_A2") or p.get("ADM0_ISO")
        if iso in ("-99", None):
            iso = p.get("NAME")
        a3_to_a2[p.get("ADM0_A3")] = iso
        d = to_path(shape(f["geometry"]), scale, ox, oy, a.decimals)
        if not d:
            continue
        countries.append({
            "iso": iso,
            "zh": p.get("NAME_ZH") or p.get("NAME"),
            "en": p.get("NAME_EN") or p.get("NAME"),
            "cont": p.get("CONTINENT"),
            "d": d,
        })
    countries.sort(key=lambda c: c["iso"])

    world = {"w": round(a.width), "h": round(height, 1), "countries": countries}
    path = os.path.join(a.outdir, "world.js")
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.WORLD = " + json.dumps(world, separators=(",", ":"), ensure_ascii=False) + ";")
    print(f"{path}: {len(countries)} 个国家 · {os.path.getsize(path)//1024} KB")

    if a.no_admin1:
        return

    # ---------- 一级行政区 ----------
    src = fetch("admin1")["features"]
    feats = simplify_grouped(src, a.simplify_admin1, "adm0_a3")
    regions = []
    for f in feats:
        p = f["properties"]
        d = to_path(shape(f["geometry"]), scale, ox, oy, a.decimals)
        if not d:
            continue
        regions.append({
            "id": p.get("iso_3166_2") or f"{p.get('adm0_a3')}-{p.get('name')}",
            "iso": a3_to_a2.get(p.get("adm0_a3"), p.get("adm0_a3")),
            "zh": p.get("name_zh") or p.get("name"),
            "en": p.get("name_en") or p.get("name"),
            "d": d,
        })
    regions.sort(key=lambda r: r["id"])

    path = os.path.join(a.outdir, "admin1.js")
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.ADMIN1 = " + json.dumps({"regions": regions}, separators=(",", ":"), ensure_ascii=False) + ";")
    print(f"{path}: {len(regions)} 个一级行政区 · {os.path.getsize(path)//1024} KB")


if __name__ == "__main__":
    main()
