from Tkinter import *

def main():

    dyn_infos = {
        'motor1': {'temp': 1, 'voltage': 20, 'position': [12, 12, 34]},
        'motor2': {'temp': 2, 'voltage': 20, 'position': [12, 12, 34]},
        'motor3': {'temp': 3, 'voltage': 20, 'position': [12, 12, 34]},
        'motor4': {'temp': 4, 'voltage': 20, 'position': [12, 12, 34]},
        'motor5': {'temp': 5, 'voltage': 20, 'position': [12, 12, 34]}
    }

    master = Tk()

    Label(master, text="MOUVEMENTS", bg="BLACK", fg="white").grid(row=1, column=0)

    Button(master, text="STOP").grid(row=2, column=0)
    Button(master, text="Apporter a tyrolienne").grid(row=2, column=1)
    Button(master, text="Lacher").grid(row=2, column=2)
    Button(master, text="Home").grid(row=2, column=3)

    Label(master, text="CROCHETS", bg="BLACK", fg="white").grid(row=3, column=0)
    for i in range(4):
        Button(master, width=10, text=str(1 + i)).grid(row=4 + i, column=0)
        Button(master, width=10, text=str(i + 4 + 1)).grid(row=4 + i, column=1)

    Label(master, width=13, text="", bg="BLACK", fg="white").grid(row=8, column=0)
    Label(master, width=20, text="dyn1", bg="BLACK", fg="white").grid(row=8, column=1)
    Label(master, width=13, text="dyn2", bg="BLACK", fg="white").grid(row=8, column=2)
    Label(master, width=13, text="dyn3", bg="BLACK", fg="white").grid(row=8, column=3)
    Label(master, width=13, text="dyn4", bg="BLACK", fg="white").grid(row=8, column=4)
    Label(master, width=13, text="dyn5", bg="BLACK", fg="white").grid(row=8, column=5)
    Label(master, width=13, text="Temperatures", bg="BLACK", fg="white").grid(row=9, column=0)
    Label(master, width=13, text="Voltages", bg="BLACK", fg="white").grid(row=10, column=0)
    Label(master, width=13, text="Positions", bg="BLACK", fg="white").grid(row=11, column=0)

    for i in range(5):
        Label(master, width=13, text=dyn_infos['motor' + str(i + 1)]['temp'], fg="BLACK").grid(row=9, column=i + 1)
        Label(master, width=13, text=dyn_infos['motor' + str(i + 1)]['voltage'], fg="BLACK").grid(row=10, column=i + 1)
        Label(master, width=13, text=dyn_infos['motor' + str(i + 1)]['position'], fg="BLACK").grid(row=11, column=i + 1)

    mainloop()


if __name__ == '__main__':
    main()
