import cv2
import time
import pyzbar.pyzbar as pyzbar

cap = cv2.VideoCapture("tcp://raspberrypi-rose:2222")


def mousecallback(event, x, y, flags, param):
    '''
    Handle le drag n drop pour définir la région où le QR code se trouve
    '''

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

        crop = frame[y:y+h, x:x+w]

        out = pyzbar.decode(crop)

        if out:
            out = out[0].data
            print(out)
        else:
            print('Unreadable QR code')

cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mousecallback)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
