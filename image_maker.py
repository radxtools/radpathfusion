from pathlib import Path
import cv2
import xml.etree.ElementTree as ET
import jmespath
import xmltodict
import numpy as np

xml_dir = Path('./data/patient87/RadPath')
source_dir = xml_dir.parent / "pathology"
mask_dir = xml_dir.parent / "pathology" / "masks"
mask_dir.mkdir(exist_ok=True)


for x in xml_dir.glob("*.xml"):
    s = source_dir / f"{x.stem}.tif"
    print("processing", s)
    print("reading xml", x)
    source = cv2.imread(str(s))
    h, w = source.shape[0:2]

    mask_path = mask_dir / f"{x.stem}.trace.tif"

    root = xmltodict.parse(x.read_text())
    query = """Annotations.Annotation[*].Regions.Region[*].Vertices.Vertex[*].["@X", "@Y"]"""

    annotations = jmespath.search(query, root)

    img = np.zeros((h, w, 3), dtype=np.int32)
    for annotation in annotations:
        for region in annotation:
            points = np.array(region, dtype=np.float32).astype(np.int32)
            points = points.reshape((-1, 1, 2))
            color = (255, 255, 0)
            # changing the thickness to 100 makes it easier to have a closed region for flood filling
            img = cv2.polylines(
                img, [points], isClosed=False, color=color, thickness=100)

    cv2.imwrite(str(mask_path), img)
    img = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    mh, mw = img.shape
    mask = np.zeros((mh+2, mw+2), np.uint8)
    _, img, mask, rect = cv2.floodFill(img, mask, (0, 0), 179)
    cv2.imwrite(str(mask_path), img)


# def colors_gen():
#     while True:
#         color = (
#             np.random.randint(0, 255),
#             np.random.randint(0, 255),
#             np.random.randint(0, 255),
#         )
#         print(color)
#         yield color


# def gen_path():
#     img=np.zeros((h, w, 3), dtype = np.int32)
#     for annotation in annotations:
#         for region in annotation:
#             points=np.array(region, dtype = np.float32).astype(np.int32)
#             points=points.reshape((-1, 1, 2))
#             # color = next(colors)
#             color=(255, 255, 0)
#             img=cv2.polylines(
#                 img, [points], isClosed = False, color = color, thickness = 100)
#     # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
#     cv2.imwrite("path_trace.tif", img)
#     img=cv2.imread("path_trace.tif", cv2.IMREAD_GRAYSCALE)
#     h, w=img.shape
#     mask=np.zeros((h+2, w+2), np.uint8)
#     _, img, mask, rect=cv2.floodFill(img, mask, (0, 0), 179)
#     cv2.imwrite("path_trace.tif", img)
#     return img


# def gen_area():
#     points_arr = []
#     mask = np.zeros((h, w, 3), dtype=np.int32)
#     for annotation in annotations:
#         for region in annotation:
#             points = np.array(region, dtype=np.float32).astype(np.int32)
#             points = points.reshape((-1, 1, 2))
#             # color = next(colors)
#             color = (255, 255, 0)
#             points_arr.append(points)
#     mask = cv2.fillPoly(mask, points_arr, (255, 255, 255))
#     cv2.imwrite("area_trace.tif", mask)
#     return mask


# # this is per region
# mask = np.zeros((h, w, 3), dtype=np.int32)
# for annotation in annotations:
#     color = next(colors)
#     for region in annotation:
#         points = np.array([region], dtype=np.float32).astype(np.int32)
#         mask = cv2.fillConvexPoly(mask,
#                                   points,
#                                   color=color)
# cv2.imwrite("region_fill.tif", mask)


# mask = np.zeros((h, w, 3), dtype=np.int32)
# for annotation in annotations:
#     region = jmespath.search("[*] | []", annotation)
#     points = np.array([region], dtype=np.float32).astype(np.int32)
#     mask = cv2.fillConvexPoly(mask, points, color=next(colors))

# cv2.imwrite("conver_poly_fill.tif", mask)
