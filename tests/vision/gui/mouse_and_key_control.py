import cv2
import time
import socket
import os
import numpy as np
import pyzbar.pyzbar as pyzbar

WINDOW_NAME_STREAM = "stream"
WINDOW_NAME_HD_PIC = "hd picture"
IP_ADDRESS = "192.168.1.172"
PORT_HD = 9000
PORT_STREAM = 9999

PIXEL_BY_INCHE = 80.0

SIZE_BUTTON = 80

BUTTON_QR = (100,100,SIZE_BUTTON,SIZE_BUTTON)
BUTTON_2D_FIGUR = (100,200,SIZE_BUTTON,SIZE_BUTTON)
BUTTON_NEXT = (100,100,175,175)


FONT = cv2.FONT_HERSHEY_SIMPLEX

class state_machine: 
    def __init__(self):
            self.state = None
    def push_state(self, new_state):
        if(new_state is None):
            return
       
        if(self.state is not None):
            self.state.exit()
        new_state.init()
        self.state = new_state

    def pop_state():
        print("francis dit n'importe quoi")


class default_state:
    def __init__(self):
        self.cap = cv2.VideoCapture("tcp://"+IP_ADDRESS+":"+str(PORT_STREAM))
        self.mode = "default"
        print("init default")
        pass

    def init(self):
        cv2.setMouseCallback(WINDOW_NAME_STREAM, self.on_click)

    def on_click(self, event, x, y, flag, param):
        if(event == cv2.EVENT_LBUTTONDOWN):
            if(contains(BUTTON_NEXT, x,y)):
                app_state.push_state(take_hd_image_state())

    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_STREAM, lambda *args : None)
        self.cap.release()

class take_hd_image_state:
    def __init__(self):
        self.mode = "take_hd_image"
        print("init take hd image")
        self.list_position = []
        pass

    def init(self):

        time.sleep(1)
        self.cap = cv2.VideoCapture("tcp://"+IP_ADDRESS+":"+str(PORT_HD))
        work, img = self.cap.read()

        K = np.array([[2.589484213596329482e+03, 0, 1.698729966864577591e+03],
                      [0., 2.598980566720857951e+03, 1.228227272486119546e+03],
                      [0., 0., 1.]])

        #Define distortion coefficients d
        d = np.array([1.808684126195871100e-01,-4.092267392141504811e-01,7.927461711566604480e-03,1.114186232525689975e-03,2.145718416518574423e-01])

        (h, w) = img.shape[:2]

        center = (w / 2, h / 2) 
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        img_rotated = cv2.warpAffine(img, M, (w, h)) 


        #Generate new camera matrix from parameters
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(K, d, (w,h), 0)

        #Generate look-up tables for remapping the camera image
        map_x, map_y = cv2.initUndistortRectifyMap(K, d, None, new_camera_matrix, (w, h), 5)
        
        #Remap the original image to a new image
        self.img_hd = cv2.remap(img_rotated, map_x, map_y, cv2.INTER_LINEAR)

        self.img_show = self.img_hd

        cv2.setMouseCallback(WINDOW_NAME_STREAM, self.on_click)


    def on_click(self, event, x, y, flags, nb_click):
        app_state.push_state(crop_image_state(self.img_hd))


    def exit(self):
        self.cap.release()




class crop_image_state:
    def __init__(self, hd_image):
        self.mode = "crop_image"
        print("init crop image")
        self.img_hd = hd_image
        pass

    def init(self):
        
        self.img_show = self.img_hd.copy()
        cv2.putText(self.img_show, "CROP", (200,200), FONT, 4, (0,0,0),5)

        #Should save the picture for after analyse
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, self.on_click)



    def on_click(self, event, x, y, flags, nb_click):

        if(event == cv2.EVENT_LBUTTONDOWN):
            self.mx = x
            self.my = y

        elif(event == cv2.EVENT_LBUTTONUP):
            w = abs(self.mx - x)
            h = abs(self.my - y)

            x = min(self.mx, x)
            y = min(self.my, y)

            print (x, y, w, h)

            self.img_crop = self.img_show[y:y+h, x:x+w]

            self.img_crop = cv2.resize(self.img_crop, (w * 3, h * 3))

            app_state.push_state(choice_strategy_state(self.img_hd, self.img_crop, self.mx, self.my))

        elif(event == cv2.EVENT_RBUTTONDOWN):
            app_state.push_state(default_state())

    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, lambda *args : None)


class choice_strategy_state:
    def __init__(self, hd_image, crop_image, mx, my):
        self.mode = "choice_strategy"
        print("init choice strategy")
        self.img_hd = hd_image
        self.img_crop = crop_image
        self.mx = mx
        self.my = my
        pass

    def init(self):
        img_tmp = self.img_crop.copy()
        print img_tmp.shape[:2]
        img_tmp = draw_rect_text(BUTTON_QR,img_tmp,0,255,0,"qr");
        img_tmp = draw_rect_text(BUTTON_2D_FIGUR,img_tmp,255,0,0,"dist");
        cv2.putText(img_tmp, "CHOISI!", (300, 150), FONT, 4, (0,0,0),5)

        self.img_show = img_tmp
         
        #Should save the picture for after analyse
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, self.on_click)

    def on_click(self, event, x, y, flags, nb_click):
        if(event == cv2.EVENT_LBUTTONDOWN):
            if(contains(BUTTON_QR, x,y)):
                app_state.push_state(qr_state(self.img_hd, self.img_crop))
            elif(contains(BUTTON_2D_FIGUR, x,y)):
                app_state.push_state(transform_correction_image_state(self.img_hd, self.img_crop, self.mx, self.my))

    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, lambda *args : None)

class qr_state:
    def __init__(self, img_hd, img_crop):
        self.mode = "qr"
        print("init qr_state")
        self.img_crop = img_crop
        self.img_hd = img_hd

    def init(self):

        self.img_show = self.img_crop
        cv2.putText(self.img_show, "QR!", (300,150), FONT, 4, (0,0,0),5)

        print pyzbar.decode(self.img_crop)
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, self.on_click)


    def on_click(self, event, x, y, flags, param):
        if(event == cv2.EVENT_LBUTTONDOWN):
            print x,y

        elif(event == cv2.EVENT_RBUTTONDOWN):
            app_state.push_state(crop_image_state(self.img_hd))


    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, lambda *args : None)

class transform_correction_image_state:
    def __init__(self, full_picture, crop_picture, mx, my):
        self.mode = "transform_correction_image"
        print("init transform correction")
        self.list_position = []
        self.full_img_hd = full_picture
        self.img_crop = crop_picture
        self.mx = mx
        self.my = my
        pass

    def init(self):

        self.img_show = self.img_crop
        cv2.putText(self.img_show, "Click on corner!", (300,150), FONT, 4, (0,0,0),5)

        #Should save the picture for after analyse
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, self.on_click)



    def on_click(self, event, x, y, flags, nb_click):
        if(event == cv2.EVENT_LBUTTONDOWN):
            print (x, y)
            if len(self.list_position) != 3:
                self.list_position.append((x, y))
            else:

                dx = self.list_position[1][0] - self.list_position[0][0]
                dy = self.list_position[1][1] - self.list_position[0][1]

                print "etape 1"
                print self.list_position

                self.list_position.append((self.list_position[-1][0] - dx, self.list_position[-1][1] - dy))

                print "etape 2"
                print self.list_position

                self.list_position = [(self.mx + x / 3.0, self.my + y / 3.0) for (x, y) in self.list_position]

                print "etape 3"
                print self.list_position

                target_position = [(8 * PIXEL_BY_INCHE, 2464 - PIXEL_BY_INCHE), (8 * PIXEL_BY_INCHE, 2464), 
                        (10 * PIXEL_BY_INCHE, 2464), (10 * PIXEL_BY_INCHE, 2464 - PIXEL_BY_INCHE)]

                print "etape 1"
                print target_position

                print len(self.list_position), len(target_position)

                h = cv2.getPerspectiveTransform(np.array([self.list_position], dtype="float32"), np.array([target_position], dtype="float32"))
                self.img_warp = cv2.warpPerspective(self.full_img_hd, h, (3280, 2464))


                app_state.push_state(deuxD_figur_state(self.full_img_hd, self.img_warp))

        elif(event == cv2.EVENT_RBUTTONDOWN):
            app_state.push_state(crop_image_state(self.img_hd))


    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, lambda *args : None)



class deuxD_figur_state:
    def __init__(self, hd_img, transform_img):
        self.mode = "2d_figur"
        print("init 2d_figur_state")
        self.list_position = []
        self.img_hd = hd_img
        self.img_show = transform_img
        pass

    def init(self):
        
        cv2.putText(self.img_show, "Calcul distance!", (300,150), FONT, 4, (0,0,0),5)
        #Should save the picture for after analyse
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, self.on_click)


    def on_click(self, event, x, y, flags, nb_click):
        if(event == cv2.EVENT_LBUTTONDOWN):
            if(contains(BUTTON_NEXT, x,y)):
                app_state.push_state(crop_image_state(self.img_hd))

            self.list_position.append([x,y])
            print(self.list_position)

            if(len(self.list_position) >= 2):
                vert_dist = float(abs(self.list_position[1][0] - self.list_position[0][0]))
                hori_dist = float(abs(self.list_position[1][1] - self.list_position[0][1]))

                #Divide distance by 2 because it's work like that
                vert_dist = vert_dist/2
                hori_dist = hori_dist/2

                print("Pixel dist| vert: " + str(vert_dist) + "  hori: " + str(hori_dist))
                print("Inches dist| vert: " + str(vert_dist / PIXEL_BY_INCHE) + "  hori: " + str(hori_dist/ PIXEL_BY_INCHE))
                    
                self.list_position[:] = []


        elif(event == cv2.EVENT_RBUTTONDOWN):
            app_state.push_state(crop_image_state(self.img_hd))




    def exit(self):
        cv2.setMouseCallback(WINDOW_NAME_HD_PIC, lambda *args : None)



#square 0:x 1:y 2:w 3:l
def contains(rectangle, point_x, point_y):
    if((point_x > rectangle[0] and point_x < rectangle[0] + rectangle[2]) 
    and (point_y > rectangle[1] and point_y < rectangle[1] + rectangle[3])):
	return True
    else:
	return False

def draw_rect_text(rectangle, image, r, g, b, text):

    cv2.rectangle(image,(rectangle[0],rectangle[1]),(rectangle[0]+rectangle[2],rectangle[1]+rectangle[3]),(r,g,b),4)
    cv2.putText(image, text, (rectangle[0]+5,rectangle[1]+125), FONT, 4, (r,g,b),5)

    return image


app_state = state_machine()


if __name__ == "__main__":

    cv2.namedWindow(WINDOW_NAME_STREAM,0)
    cv2.namedWindow(WINDOW_NAME_HD_PIC,0)


    instance_default_state = default_state()
    app_state.push_state(instance_default_state)

    key_val = 0

    #key_val == 27 is ESC
    while(key_val != 27):

        if(app_state.state.mode == "default"):
            #get the new frame 
            ret, image = app_state.state.cap.read()
            image = draw_rect_text(BUTTON_NEXT,image,0,255,0,"HD");
            cv2.imshow(WINDOW_NAME_STREAM, image)

        else:
            cv2.imshow(WINDOW_NAME_HD_PIC , app_state.state.img_show)
        
        key_val = cv2.waitKey(1)

    print("leave this place")
    cv2.destroyAllWindows()
