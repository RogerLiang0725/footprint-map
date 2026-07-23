# Footprint Map · 足迹地图

在世界地图上标出去过的地方：没去过的是冷蓝色，去过的整块变橙色。
纯静态、无后端、无框架、无构建，推到 GitHub Pages 就能用。

👉 **在线体验：** https://USERNAME.github.io/footprint-map/

| 页面 | 说明 |
|---|---|
| `index.html` | **精准边界版** —— 真实国界矢量，可缩放，可细到省 / 州 / 县级 |
| `dots.html` | **点阵版** —— 用小圆点铺出世界，海报风格 |

## 功能

- **点击标记** —— 点国家（或省/州）即可点亮
- **两级粒度** —— 顶部切换「国家 / 省·州」，省级数据按需加载，4588 个一级行政区（日本 47 都道府县、中国 34 省级、瑞典 21 län、法国 101 省…）
- **缩放拖动** —— 滚轮缩放、按住拖动，最高 24×
- **照片坐标批量导入** —— 粘贴 `纬度,经度`，同时点亮国家和省。判定用浏览器原生 `isPointInFill` 对真实边界做 point-in-polygon，**不联网、不调任何地图 API**
- **分享链接** —— 状态编码进 URL：`#c=CN,JP,SE&p=JP-27,CN-GD`
- 导出 / 导入 JSON、下载 PNG、亮暗主题、刷新自动恢复

## 部署到 GitHub Pages

```bash
git init && git add . && git commit -m "footprint map"
git branch -M main
git remote add origin https://github.com/USERNAME/footprint-map.git
git push -u origin main
```

Settings → Pages → Source 选 `main` / `(root)`，一两分钟后就上线了。
想用 Actions 部署的话，仓库里已经带了 `.github/workflows/pages.yml`，把 Source 改成
`GitHub Actions` 即可。

本地预览：`python -m http.server 8000`（`index.html` 要走 HTTP，因为省级数据是按需加载的）。

## 把自己的照片变成地图

```bash
pip install osxphotos
python scripts/photos_to_coords.py > coords.txt   # 读 macOS「照片」图库的 GPS
```

或者扫任意文件夹：

```bash
brew install exiftool
python scripts/photos_to_coords.py --dir ~/Pictures/旅行
```

把 `coords.txt` 全选复制，粘进网页下方的输入框，点「解析并标记」。

## 重新生成地图数据

```bash
pip install -r requirements.txt

# 矢量版：国界 + 一级行政区
python scripts/build_vector.py                     # 默认
python scripts/build_vector.py --simplify 0.02 --simplify-admin1 0.03   # 更精细，文件更大
python scripts/build_vector.py --width 3000        # 更高的投影分辨率

# 点阵版
python scripts/build_dots.py --cols 260            # 点更密
```

当前默认输出：

| 文件 | 内容 | 体积 | gzip 后 |
|---|---|---|---|
| `data/world.js` | 242 个国家，50m 精度 | 809 KB | ~270 KB |
| `data/admin1.js` | 4588 个省/州，10m 精度，按需加载 | 3.3 MB | ~990 KB |
| `data/dots.js` | 5630 个点 | 73 KB | ~25 KB |

## 实现要点

**投影** 用 Equal Earth（等积投影，2018 年提出，闭式公式）。投影在 Python 里一次算完，
直接输出 SVG path，所以浏览器端不需要 d3-geo 或任何投影库——整个页面零依赖。

**简化** 用 `topojson` 做拓扑简化：相邻国家共享的那条边界会被当作同一条弧线一起简化，
所以不会像逐个多边形 `shapely.simplify` 那样在国界之间裂出白缝。省级数据 4588 个多边形
一次性建拓扑会吃掉几 GB 内存，脚本改成**按国家分组**建拓扑——同一国内部的省界依然严丝合缝。

**坐标反查国家** 没有用任何 geocoding API：把 `(lat, lon)` 用同一套 Equal Earth 公式投影到
SVG 坐标系，再调浏览器原生的 `SVGGeometryElement.isPointInFill()` 去测命中哪个 `<path>`。
海岸线附近拍的照片（GPS 漂到水里）会向外做几圈容差搜索，约 15 km。

**性能** 切换颜色只改 `<path>` 的 class，浏览器只重绘那一块；省级图层不进 DOM 直到你切过去。

## 关于地图数据源

边界数据来自 [Natural Earth](https://www.naturalearthdata.com/)（public domain，可商用、可再分发），
中英文国名/省名也在属性里自带。

几点值得注意的：

- **Google / 百度 / 高德的地图数据不能这样用。** 它们的边界数据不是开放数据，
  服务条款一般禁止把矢量数据抓下来离线渲染或再分发，只允许通过官方 JS API / 瓦片服务展示。
  想用它们，正确姿势是嵌入官方地图组件、在其上叠加你自己的标记图层。
- **国内坐标系。** 高德/腾讯用 GCJ-02、百度用 BD-09，跟 GPS 的 WGS-84 有几百米偏移。
  照片 EXIF 里是 WGS-84，和 Natural Earth 一致，所以本项目不需要纠偏；
  一旦混用国内地图底图就要做坐标转换。
- **更细的中国行政区划**（市级、区县级）推荐
  [阿里 DataV.GeoAtlas](https://datav.aliyun.com/portal/school/atlas/area_selector)，
  按 adcode 提供免费 GeoJSON，覆盖到区县，可以直接替换 `data/admin1.js` 的生成源。
- **全球更细的行政区划** 可以看 [geoBoundaries](https://www.geoboundaries.org/)（开放许可）
  或 [GADM](https://gadm.org/)（学术免费，商用需授权）。
- 边界呈现涉及不同国家和地区的主张差异，Natural Earth 的画法只是其中一种；
  需要特定呈现方式的话可以换用相应来源的数据。

## 结构

```
index.html                     # 精准边界版
dots.html                      # 点阵版
data/world.js                  # 国界 SVG 路径 (window.WORLD)
data/admin1.js                 # 一级行政区，按需加载 (window.ADMIN1)
data/dots.js                   # 点阵数据 (window.DOTS)
scripts/build_vector.py        # 生成矢量数据
scripts/build_dots.py          # 生成点阵数据
scripts/photos_to_coords.py    # 照片 GPS -> 坐标列表
```

## License

代码 MIT，地图数据 Natural Earth（public domain）。
