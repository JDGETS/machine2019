import cv2
import cv2 as cv
import math
import numpy as np

img = cv2.imread('./git/vision/output.jpg')

cv2.imshow('image', img)

state = 0
mx, my = 0, 0
w, h = 0, 0
crop = None
bar_region = []
points = []


def mousecallback(event, x, y, flags, param):
    global mx, my, w, h, crop

    if event == cv2.EVENT_LBUTTONDOWN:
        mx = x
        my = y

    if event == cv2.EVENT_LBUTTONUP:
        w = abs(mx - x)
        h = abs(my - y)

        x = min(mx, x)
        y = min(my, y)

        print (x, y, w, h)

        crop = img[y:y+h, x:x+w]


        crop = cv2.resize(crop, (w * 3, h * 3))

        cv2.imshow('crop', crop)


def mousecallback_crop(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        print (x, y)
        if len(points) != 3:
            points.append((x, y))
        else:
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]

            points.append((points[-1][0] - dx, points[-1][1] - dy))

            cv2.polylines(crop, np.int32([points]), False, (0, 0, 255))

            cv2.imshow('crop', crop)

            points = [(mx + x / 3.0, my + y / 3.0) for (x, y) in points]

            s = 40
            target_points = [(8 * s, 720 - s), (8 * s, 720), (10 * s, 720), (10 * s, 720 - s)]

            print len(points), len(target_points)

            h = cv2.getPerspectiveTransform(np.array([points], dtype="float32"), np.array([target_points], dtype="float32"))
            test = cv2.warpPerspective(img, h, (2280, 720))

            x = cv2.polylines(img, np.int32([points]), False, (0, 0, 255))
            cv2.polylines(x, np.int32([target_points]), False, (0, 255, 0))

            cv2.imshow('image', x)
            cv2.imshow('test', test)

a = None

def mousecallback_test(event, x, y, flags, param):
    global a

    if event == cv2.EVENT_LBUTTONDOWN:
        if a == None:
            a = (x, y)
        else:
            print (abs(x - a[0]) / 80.0, abs(y - a[1]) / 80.0)



cv2.setMouseCallback('image', mousecallback)

cv2.namedWindow('crop')
cv2.setMouseCallback('crop', mousecallback_crop)

cv2.namedWindow('test')
cv2.setMouseCallback('test', mousecallback_test)

cv2.waitKey()
