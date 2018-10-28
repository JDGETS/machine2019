import cv2
import time

cap = cv2.VideoCapture("tcp://raspberrypi-new:2222")

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()


    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame

    pattern_size = (9, 6)
    found = False

    if cv2.waitKey(1) & 0xFF == ord('c'):
        found, corners = cv2.findChessboardCorners(frame, pattern_size)

        if found:
            cv2.drawChessboardCorners(frame, pattern_size, corners, found)
            cv2.imshow('frame2', frame)


    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
