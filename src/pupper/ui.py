from Tkinter import *
import rpyc
from threading import Thread
from config import get_param


def main():
    w = Canvas(master, width=500, height=500)
    w.pack()

    print get_param('ip')
