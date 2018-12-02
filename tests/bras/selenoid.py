import pigpio
import time

pi = pigpio.pi('raspberrypi-1')

pi.set_PWM_dutycycle(22, 120)

time.sleep(0.5)


pi.set_PWM_dutycycle(22, 0)
