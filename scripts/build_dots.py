"""
生成点阵世界地图数据。

用法:
    python scripts/build_dots.py                # 默认 190 列
    python scripts/build_dots.py --cols 260     # 更密的点
    python scripts/build_dots.py --cols 120

原理: 在 Miller 投影后的规则网格上取点, 逐点做 point-in-polygon 判定,
落在陆地上的格子才输出一个点, 并记下它属于哪个国家。
"""
import argparse
import json
import math
import os
import urllib.request

from shapely.geometry import shape, Point
from shapely.prepared import prep
from shapely.strtree import STRtree

GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_110m_admin_0_countries.geojson"
)
CACHE = "world.geojson"


def load_world():
    if not os.path.exists(CACHE):
        print("下载国界数据 ...")
        urllib.request.urlretrieve(GEOJSON_URL, CACHE)
    return json.load(open(CACHE, encoding="utf-8"))


# Miller 圆柱投影
def miller_y(lat_deg):
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat_deg)))


def miller_inv(y):
    return math.degrees(2.5 * (math.atan(math.exp(0.8 * y)) - math.pi / 4))


def build(cols, lat_top, lat_bot):
    world = load_world()
    feats = []
    for f in world["features"]:
        p = f["properties"]
        iso = p.get("ISO_A2_EH") or p.get("ISO_A2") or p.get("ADM0_ISO")
        if iso in ("-99", None):
            iso = p.get("NAME")
        feats.append({
            "iso": iso,
            "en": p.get("NAME_EN") or p.get("NAME"),
            "zh": p.get("NAME_ZH") or p.get("NAME"),
            "cont": p.get("CONTINENT"),
            "geom": shape(f["geometry"]),
        })

    geoms = [f["geom"] for f in feats]
    tree = STRtree(geoms)
    prepped = [prep(g) for g in geoms]

    step = 2 * math.pi / cols
    y_top, y_bot = miller_y(lat_top), miller_y(lat_bot)
    rows = int((y_top - y_bot) / step) + 1

    dots, used = [], set()
    for r in range(rows):
        lat = miller_inv(y_top - r * step)
        for c in range(cols):
            lon = math.degrees(-math.pi + (c + 0.5) * step)
            pt = Point(lon, lat)
            for idx in tree.query(pt):
                if prepped[idx].contains(pt):
                    dots.append((c, r, int(idx)))
                    used.add(int(idx))
                    break

    order = sorted(used)
    remap = {old: i for i, old in enumerate(order)}
    countries = [
        {"iso": feats[i]["iso"], "en": feats[i]["en"],
         "zh": feats[i]["zh"], "cont": feats[i]["cont"]}
        for i in order
    ]
    return {
        "cols": cols,
        "rows": rows,
        "dots": [[c, r, remap[k]] for c, r, k in dots],
        "countries": countries,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cols", type=int, default=190, help="横向点数, 越大越密")
    ap.add_argument("--lat-top", type=float, default=84.0)
    ap.add_argument("--lat-bot", type=float, default=-58.0)
    ap.add_argument("--out", default="data/dots.js")
    a = ap.parse_args()

    data = build(a.cols, a.lat_top, a.lat_bot)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    body = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("window.DOTS = " + body + ";" if a.out.endswith(".js") else body)

    print(f"{a.out}: {len(data['dots'])} 个点 · {len(data['countries'])} 个国家 · "
          f"{data['cols']}×{data['rows']} 网格 · {os.path.getsize(a.out) // 1024} KB")


if __name__ == "__main__":
    main()
