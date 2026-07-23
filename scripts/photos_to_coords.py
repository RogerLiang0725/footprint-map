"""
把 macOS 照片库(或任意文件夹)里的照片 GPS 导出成 `纬度,经度` 文本,
直接粘贴到网页的"从照片坐标批量标记"框里。

依赖(二选一):
    pip install osxphotos          # 读系统"照片"App 图库, 不用导出原图
    brew install exiftool          # 读任意文件夹里的图片

用法:
    python scripts/photos_to_coords.py                    # osxphotos 读系统图库
    python scripts/photos_to_coords.py --dir ~/Pictures   # exiftool 扫文件夹
    python scripts/photos_to_coords.py > coords.txt
"""
import argparse
import json
import subprocess
import sys


def from_osxphotos():
    out = subprocess.run(
        ["osxphotos", "query", "--only-photos", "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    for p in json.loads(out):
        lat, lon = p.get("latitude"), p.get("longitude")
        if lat is not None and lon is not None:
            yield lat, lon


def from_exiftool(folder):
    out = subprocess.run(
        ["exiftool", "-r", "-n", "-j", "-GPSLatitude", "-GPSLongitude", folder],
        capture_output=True, text=True, check=True,
    ).stdout
    for p in json.loads(out or "[]"):
        lat, lon = p.get("GPSLatitude"), p.get("GPSLongitude")
        if lat is not None and lon is not None:
            yield lat, lon


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="改用 exiftool 扫描这个文件夹")
    ap.add_argument("--round", type=int, default=2,
                    help="坐标保留几位小数(默认 2, 约 1km, 顺便去重)")
    a = ap.parse_args()

    try:
        pairs = from_exiftool(a.dir) if a.dir else from_osxphotos()
        uniq = sorted({(round(la, a.round), round(lo, a.round)) for la, lo in pairs})
    except FileNotFoundError as e:
        sys.exit(f"找不到命令: {e.filename}。先装 osxphotos 或 exiftool。")

    for la, lo in uniq:
        print(f"{la},{lo}")
    print(f"# 共 {len(uniq)} 个去重后的坐标", file=sys.stderr)


if __name__ == "__main__":
    main()
