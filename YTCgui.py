from tkinter import *
from tkinter import ttk
import tkinter
import tkinter.messagebox
import YTC


def init():
    def getFromFile():
        try:
            result = YTC.getPlayersFromFile(role.get())
        except Exception as e:
            tkinter.messagebox.askokcancel(title='错误', message=e.args)
            return
        for j in range(4):
            redName[j]['text'] = result[0][j].name
            blueName[j]['text'] = result[1][j].name
            redScore[j]['text'] = result[0][j].score
            blueScore[j]['text'] = result[1][j].score
            redTotalScore['text'] = str(result[2])
            blueTotalScore['text'] = str(result[3])
            redHighScore['text'] = str(result[4])
            blueHighScore['text'] = str(result[5])

    def getFromMplink():
        try:
            mplink = getData2.get()
            result = YTC.getPlayersFromMplink(mplink, role.get())
        except Exception as e:
            tkinter.messagebox.askokcancel(title='错误', message=e.args)
            return
        for j in range(4):
            redName[j]['text'] = result[0][j].name
            blueName[j]['text'] = result[1][j].name
            redScore[j]['text'] = result[0][j].score
            blueScore[j]['text'] = result[1][j].score
            redTotalScore['text'] = str(result[2])
            blueTotalScore['text'] = str(result[3])
            redHighScore['text'] = str(result[4])
            blueHighScore['text'] = str(result[5])

    root = Tk()

    getDate = Button(root, text='读取数据', command=getFromFile)
    getDate.grid(row=0, column=0)

    getData2 = Entry(root, width=10)
    getData2.grid(row=0, column=1)
    getData3 = Button(root, text='mplink读取', command=getFromMplink)
    getData3.grid(row=0, column=2)

    Label(root, text='选择计分方式：').grid(row=1, column=0)
    role = ttk.Combobox(root, width=6)
    role['values'] = ['v1', 'acc']
    role.current(0)
    role.grid(row=1, column=1)

    redName = []
    blueName = []
    redScore = []
    blueScore = []
    for i in range(4):
        redName.append(Label(root))
        blueName.append(Label(root))
        redScore.append(Label(root))
        blueScore.append(Label(root))
        redName[i].grid(row=2 + i, column=0)
        blueName[i].grid(row=2 + i, column=3)
        redScore[i].grid(row=2 + i, column=1)
        blueScore[i].grid(row=2 + i, column=4)
    Label(root, text='高分奖励：').grid(row=6, column=0)
    Label(root, text='高分奖励：').grid(row=6, column=3)
    redHighScore = Label(root)
    blueHighScore = Label(root)
    redHighScore.grid(row=6, column=1)
    blueHighScore.grid(row=6, column=4)
    redTotalScore = Label(root)
    blueTotalScore = Label(root)
    redTotalScore.grid(row=7, column=1)
    blueTotalScore.grid(row=7, column=4)
    Label(root, text='总分：').grid(row=7, column=0)
    Label(root, text='总分：').grid(row=7, column=3)

    root.mainloop()
