import pigpio
import time

pi = pigpio.pi('doggo-control')


pi.set_servo_pulsewidth(22, 1500)

time.sleep(1)

pi.set_servo_pulsewidth(22, 1200)

time.sleep(1)

pi.set_servo_pulsewidth(22, 1500)

time.sleep(1)


pi.set_servo_pulsewidth(22, 0)
