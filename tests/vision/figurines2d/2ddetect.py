import cv2
#import cv2.cv as cv
import numpy as np

## Read
img = cv2.imread("demo.JPG")
imgblur = cv2.blur(img,(10,10))
cv2.imwrite("img_blur.png", imgblur)

## convert to hsv
hsv = cv2.cvtColor(imgblur, cv2.COLOR_BGR2HSV)

## mask of green (36,0,0) ~ (70, 255,255)
mask1 = cv2.inRange(hsv, (0, 0, 0), (255,255,50))#(180, 255,30))
cv2.imwrite("target_mask_black.png", mask1)


## mask o yellow (15,0,0) ~ (36, 255, 255)
mask2 = cv2.inRange(hsv, (15,150,0), (36, 255, 255))

## final mask and masked
mask = cv2.bitwise_or(mask1, mask2)
cv2.imwrite("target_mask.png", mask)
maskblur = cv2.blur(mask,(10,10))
cv2.imwrite("target_mask_blur.png", maskblur)

#contours = cv2.findContours(maskblur,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
circles = cv2.HoughCircles(maskblur,cv2.HOUGH_GRADIENT,1,200,param1=30,param2=45,minRadius=0,maxRadius=0)


#print(contours)
if circles is not None:
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")
    
    # loop over the (x, y) coordinates and radius of the circles
    for (x, y, r) in circles:
        # draw the circle in the output image, then draw a rectangle in the image
        # corresponding to the center of the circle
        cv2.circle(img, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
cv2.imwrite("output.png", img)

#if(contours is not None):
#    for idx,contour in enumerate(contours):
#        if(idx<1):
#            continue
#        #cv2.boundingRect(contour)
#        print(contour)
#        minrect = cv2.minAreaRect(list(contour)
#        box = cv2.boxPoints(minrect)
#        box = np.int0(box)
#        cv2.drawContours(img,[box],0,(0,255,0),2)
        #cv2.drawContours(img,contours,idx,(0,255,0))
        #vertices = minrect
        #for i in range(0,4):
        #    cv2.line(img,minrect[i],minrect[(i+1)%4],(0,255,0),2,cv2.LINE_AA)


#maskEdge = cv2.Canny(maskblur,4,4)
#circles = cv2.HoughCircles(maskEdge,cv2.HOUGH_GRADIENT,1.2,75)
#print(circles)

#if circles is not None:
#    circles = np.round(circles[0,:]).astype("int")
#    for (x,y,r) in circles:
#        cv2.circle(img, (x,y), r,(0,255,0),4)
#    cv2.imwrite("output",img)
#target = cv2.bitwise_and(img,img, mask=mask)

#cv2.imwrite("target.png", target)