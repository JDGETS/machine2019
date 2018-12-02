import Tkinter
import rpyc
import os


pi_hostname = 'raspberrypi-1'
pi = rpyc.connect(pi_hostname, 18861)
# print pi.root.exposed_goto(200, 0, 200, 0, speed=50)

x = 200
y = 0
z = 300
r = 0

os.system('xset r off')


from Tkinter import *
def keydown(e):
    global x, y, z, r
    k = e.char

    if k == 'w':
        x += 5

    if k == 's':
        x -= 5

    if k == 'e':
        z += 5
    if k == 'd':
        z -= 5



    print (x, y, z, r)
    pi.root.exposed_goto(x, y, z, r, speed=50)


def keyup(e):
    print 'up', e.char

root = Tk()
frame = Frame(root, width=100, height=100)
frame.bind("<KeyPress>", keydown)
frame.bind("<KeyRelease>", keyup)
frame.pack()
frame.focus_set()
root.mainloop()
