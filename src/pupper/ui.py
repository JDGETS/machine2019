import config
import pigpio
import inputs
from inputs import get_gamepad
import time
from Tkinter import *
from threading import Thread
from utils import sign
import numpy as np
import pyzbar.pyzbar as pyzbar
import cv2
import os

WINDOW_NAME_HD_PIC = "hd picture"

PIXEL_BY_INCHE = 80.0

SIZE_BUTTON = 40

BUTTON_QR = (25,75,SIZE_BUTTON,SIZE_BUTTON)
BUTTON_2D_FIGUR = (25,125,SIZE_BUTTON,SIZE_BUTTON)

FONT = cv2.FONT_HERSHEY_SIMPLEX

gpio = None
w = None

running = True
label_vars = {}
keys = {}
pad_keys = {}
states = {}
grip_state = True
rotated_servo = False
master = None
light_state = True
light_value = 0

JOYSTICK_IGNORE_THRESHOLD = 32000

# Robot Moving speed
forward_mov_speed = config.get_param('for_speed')
backwards_mov_speed = config.get_param('back_speed')
rotation_speed = config.get_param('rotation_speed')

servo_camera_front = config.get_param('servo_camera_front')
servo_camera_back = config.get_param('servo_camera_back')


luminosity_step = 255/5
luminosity = luminosity_step

start_stream_cmd = "mplayer -fps 200 -demuxer h264es ffmpeg://tcp://%s:9999 > /dev/null &"
capture_hd_image_cmd = "nc %s 9000 > img.jpg"


def servo_180(state):

    servo_channel = config.get_param('servo_camera_channel')

    if state:
        gpio.set_servo_pulsewidth(servo_channel, servo_camera_front )
    else:
        gpio.set_servo_pulsewidth(servo_channel, servo_camera_back )

    master.after(500, lambda: gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0))


def keydown(e):
    global x, y, z, r, light_state, light_value, rotated_servo
    k = e.char

    keys[e.char] = 1

    if e.char == 'l':
        if(light_state == True):
            light_value = 50
            light_state = False
        else:
            light_value = 0
            light_state = True
    elif e.char == 'm' and light_value <= 100:
        light_value += 5
    elif e.char == 'n' and light_value > 5:
        light_value -= 5

    gpio.set_PWM_dutycycle(5, light_value)

    if e.char == 'k':

        if rotated_servo:
            print "low"
            gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), servo_camera_front)
            #gpio.hardware_PWM(19, 50, 100000) # 800Hz 25% dutycycle
        else:
            print "high"
            gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), servo_camera_back)
            #gpio.hardware_PWM(19, 50, 900000) # 800Hz 25% dutycycle

        rotated_servo = not rotated_servo

        master.after(500, lambda: gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0))
        

    if e.char == 'j':
        gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0)


def write_pwm(pins, value):
    for pin in pins:
        if pin not in states or states[pin] != value:
            states[pin] = value

            #print ('write', pin, value)
            gpio.set_PWM_dutycycle(pin, value)


def keyup(e):
    if e.char in keys:
        del keys[e.char]


def start_vision():
    os.system('killall mplayer')
    time.sleep(1)    
    print "start caputre"
    os.system(capture_hd_image_cmd % config.get_param('ip'))
    print "finish capture"
    img_hd = cv2.imread("img.jpg")
    print "get picture"

    analyse_picture(config.get_param('matrix_calibration_camera'), config.get_param('coefficient_distortion'), img_hd) 
    pass


def start_stream():
    if not os.getenv('NO_CAMERA'):

        os.system(start_stream_cmd % config.get_param('ip'))

        time.sleep(1)

        os.system('''i3-msg '[class="MPlayer"] floating enable' ''')


def main():
    global luminosity, gpio, w, running, master


    ip = config.get_param('ip') 
    gpio = pigpio.pi(ip)

    master = Tk()
    master.title('Pupper control')
    master.geometry('500x500')

    Button(master, text="START VISION", command=start_vision).grid(row=2, column=0)

    master.bind("<KeyPress>", keydown)
    master.bind("<KeyRelease>", keyup)

    start_stream()

    t = gpioloop()
    t.start()

    t1 = gamepadloop()
    t1.start()

    mainloop()

    running = False

    t.join()
    t1.join()


class gamepadloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.right_trigger = False
        self.left_trigger = False

    def run(self):

        while running:

            events =[]

            try:
                events = get_gamepad()
            except inputs.UnpluggedError:
                break

            # #print("Pas de manette connectee")
            # for event in events:
            #
            #     # Controle d'evenements et actions avec les boutons
            #     if event.ev_type == "Key":
            #
            #         # Bouton A : rotation camera
            #         if event.code == 'BTN_SOUTH' and event.state == 1:
            #             global rotated_servo
            #             rotated_servo = not rotated_servo
            #             servo_180(rotated_servo)
            #             print "hello"
            #
            #         elif event.code == "BTN_TR":
            #             global luminosity
            #             luminosity += luminosity_step
            #             write_pwm(config.get_param('light_channel'), luminosity)
            #
            #         elif event.code == "BTN_TL":
            #             global luminosity
            #             luminosity -= luminosity_step
            #             write_pwm(config.get_param('light_channel'), luminosity)
            #
            #     # Controle du mouvement avec joysticks et trigger
            #     if event.ev_type == "Absolute":
            #
            #         # Si le right trigger est enfonce : controle du robot
            #         if event.code == "ABS_RZ" and event.state == 255:
            #             self.right_trigger = True
            #
            #         # Si le right trigger est relache
            #         elif event.code == "ABS_RZ" and event.state < 200:
            #             self.right_trigger = False
            #             if 'forward' in pad_keys:
            #                 del pad_keys['forward']
            #             if 'backward' in pad_keys:
            #                 del pad_keys['backward']
            #             if 'left' in pad_keys:
            #                 del pad_keys['left']
            #             if 'right' in pad_keys:
            #                 del pad_keys['right']
            #
            #         # left joystick Y
            #         elif event.code == "ABS_Y":
            #             if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'forward' in pad_keys:
            #                     del pad_keys['forward']
            #
            #                 pad_keys['backward'] = 1
            #
            #             elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'backward' in pad_keys:
            #                     del pad_keys['backward']
            #
            #                 pad_keys['forward'] = 1
            #
            #             else:
            #                 if 'forward' in pad_keys:
            #                     del pad_keys['forward']
            #                 if 'backward' in pad_keys:
            #                     del pad_keys['backward']
            #
            #         # right joystick X
            #         elif event.code == "ABS_RX":
            #             if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'left' in pad_keys:
            #                     del pad_keys['left']
            #
            #                 pad_keys['right'] = 1
            #
            #             elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'right' in pad_keys:
            #                     del pad_keys['right']
            #
            #                 pad_keys['left'] = 1
            #
            #             else:
            #                 if 'left' in pad_keys:
            #                     del pad_keys['left']
            #                 if 'right' in pad_keys:
            #                     del pad_keys['right']


class gpioloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.speed = 0
        self.state = 'stop'
        self.target_x = 0
        self.actual_x = 0

        self.acceleration_ratio = config.get_param('acceleration_ratio')

        self.motor_left_actual_speed = 0
        self.motor_left_target_speed = 0

        self.motor_right_actual_speed = 0
        self.motor_right_target_speed = 0

        self.states = {}

    def run(self):
        while running:
            if 'w' in keys or 'forward' in pad_keys:
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = forward_mov_speed

            elif 'e' in keys:
                self.motor_right_target_speed = forward_mov_speed
                self.motor_left_target_speed = 0
            elif 'q' in keys:
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = 0

            elif 's' in keys or 'backward' in pad_keys:
                self.motor_left_target_speed = -backwards_mov_speed
                self.motor_right_target_speed = -backwards_mov_speed

            elif 'd' in keys or 'right' in pad_keys:
                self.motor_left_target_speed = rotation_speed
                self.motor_right_target_speed = -rotation_speed

            elif 'a' in keys or 'left' in pad_keys:
                self.motor_left_target_speed = -rotation_speed
                self.motor_right_target_speed = rotation_speed

            elif 'z' in keys:
                self.motor_left_target_speed = -2*backwards_mov_speed
                self.motor_right_target_speed = -2*backwards_mov_speed

            else:
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0

            dx_left = sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
            dx_right = sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

            self.motor_left_actual_speed += dx_left * self.acceleration_ratio
            self.motor_right_actual_speed += dx_right * self.acceleration_ratio

            # self.motor_left_actual_speed = self.motor_left_target_speed
            # self.motor_right_actual_speed = self.motor_right_target_speed

            self.motor_left_actual_speed =  int(self.motor_left_actual_speed * config.get_param('speed_motor_left')/100.0)
            self.motor_right_actual_speed = int(self.motor_right_actual_speed * config.get_param('speed_motor_right')/100.0)

            if self.motor_left_actual_speed < 0:
                write_pwm([config.get_param('motor_left_back_channel')], abs(self.motor_left_actual_speed))
                write_pwm([config.get_param('motor_left_for_channel')], 0)
            else:
                write_pwm([config.get_param('motor_left_for_channel')], self.motor_left_actual_speed)
                write_pwm([config.get_param('motor_left_back_channel')], 0)

            if self.motor_right_actual_speed < 0:
                write_pwm([config.get_param('motor_right_back_channel')], abs(self.motor_right_actual_speed))
                write_pwm([config.get_param('motor_right_for_channel')], 0)
            else:
                write_pwm([config.get_param('motor_right_for_channel')], self.motor_right_actual_speed)
                write_pwm([config.get_param('motor_right_back_channel')], 0)

            time.sleep(1/60.0)


if __name__ == '__main__':
    main()

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


app_state = state_machine()

class take_hd_image_state:
    def __init__(self, matrix_calibration_camera, coefficient_distortion, img_hd):
        self.mode = "take_hd_image"
        print("init take hd image")
        self.matrix_calibration = matrix_calibration_camera
        self.coefficient_distortion = coefficient_distortion
        self.img_hd = img_hd
        pass

    def init(self):

        (h, w) = self.img_hd.shape[:2]

        center = (w / 2, h / 2) 
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        img_rotated = cv2.warpAffine(self.img_hd, M, (w, h)) 

        k = np.array(self.matrix_calibration)

        #Define distortion coefficients d
        d = np.array(self.coefficient_distortion)

        #Generate new camera matrix from parameters
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(k, d, (w,h), 0)

        #Generate look-up tables for remapping the camera image
        map_x, map_y = cv2.initUndistortRectifyMap(k, d, None, new_camera_matrix, (w, h), 5)
        
        #Remap the original image to a new image
        self.img_hd = cv2.remap(img_rotated, map_x, map_y, cv2.INTER_LINEAR)

        self.img_show = self.img_hd

        app_state.push_state(crop_image_state(self.img_hd))


    def exit(self):
        #this can be remove if needed
        i = 2
        #self.cap.release()




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
            app_state.push_state(crop_image_state(self.full_img_hd))


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


def analyse_picture(matrix_calibration_camera, coefficient_distortion, img_hd):
    cv2.namedWindow(WINDOW_NAME_HD_PIC,0)

    app_state.push_state(take_hd_image_state(matrix_calibration_camera, coefficient_distortion, img_hd))

    key_val = 0

    #key_val == 27 is ESC
    while(key_val != 27):

        cv2.imshow(WINDOW_NAME_HD_PIC , app_state.state.img_show)
        
        key_val = cv2.waitKey(1)

    print("leave analyse picture")
    cv2.destroyAllWindows()

    start_stream()
