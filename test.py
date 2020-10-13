import numpy as np
import cv2
from pprint import pprint
from PIL import Image

pprint(cv2.getBuildInformation())

fixed = np.array([
    [1074,  906],
    [1074, 1236],
    [1275, 1116],
    [ 888, 1825],
    [2234, 1985]]
).reshape(1, -1, 2)

moved = np.array([
    [ 780, 1186],
    [ 842, 1386],
    [1028, 1076],
    [1229, 2065],
    [2389, 1575]]
).reshape(1, -1, 2)


matches = []
for i in range(5):
    matches.append(cv2.DMatch(i,i,0.0))

tps : cv2.ThinPlateSplineShapeTransformer = cv2.createThinPlateSplineShapeTransformer()
tps.estimateTransformation(fixed,moved,matches)


src = Image.open('data/dario1.jpg')
si_ = np.array(src)
wi_ = np.ones_like(si_)

tps.warpImage(si_, wi_)


print("finished")