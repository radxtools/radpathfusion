import numpy as np
import cv2

# cv2.ocl.setUseOpenCL(False)

from pprint import pprint

pprint(cv2.getBuildInformation().split("\n"))

sshape = np.array([[100,100],[200,100],[240,200],[300,250]],np.float32)
tshape = np.array([[100,180],[200,130],[240,220],[300,280]],np.float32)
sshape = sshape.reshape(1,-1,2)
tshape = tshape.reshape(1,-1,2)
matches = list()
matches.append(cv2.DMatch(0,0,0))
matches.append(cv2.DMatch(1,1,0))
matches.append(cv2.DMatch(2,2,0))
matches.append(cv2.DMatch(3,3,0))
tps = cv2.createThinPlateSplineShapeTransformer()
tps.estimateTransformation(sshape,tshape,matches)




print("done")