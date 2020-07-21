import re
import sys
import time
import tkinter
import tkinter.messagebox
import threading
import network

class Main():
    def __init__(self):
        self.CLIENT = network.Client(self.handle_message, "192.168.100.8", 5555, (4096 ** 2))
        self.window = tkinter.Tk()
        self.window.geometry("600x600")
        self.window.resizable(0,0)
        self.window.title("Rock Paper Scissors")
        self.window.protocol('WM_DELETE_WINDOW', self.endAll)
        self.window.config(bg="Black")

        self.otherPlayerMove = None

        self.MainMenu()

        self.window.mainloop()

    def endAll(self):
        self.window.destroy()
        self.CLIENT.close()
        sys.exit()

    def RPS_Winner(self, p1, p2):
        p1, p2 = p1.upper()[0], p2.upper()[0]
        win = {("S", "R"):1, ("R", "S"):0, ("S", "P"):0, ("P", "S"):1, ("R", "P"):1, ("P", "R"):0}
        if p1 == p2:
            return -1
        return win[(p1, p2)]

    def handle_message(self, message):
        if message.startswith("[MOVE]"):
            self.otherPlayerMove = message.replace("[MOVE]", "").strip()
            self.opponentMoved()

        elif message.strip() == "[JOIN WITH CODE FAILED]":
            tkinter.messagebox.showerror("Failed To Join", "Invalid Code")
            self.joinGameWithCode()

        elif message.strip() == "[JOIN WILL CODE FULL]":
            tkinter.messagebox.showerror("Failed To Join", "Game Full")
            self.joinGameWithCode()

        elif message.startswith("[WAITING]"):
            self.waitingScreen(message.replace("[WAITING]", "").strip())

        elif message.strip() == "[STARTED]":
            tkinter.messagebox.showinfo("Get Ready", "Game Started!")
            self.startedGame()

        elif message.strip() == "[OPPONENT LEFT]":
            if self.Score1.get() > self.Score2.get():
                a = "You Won!"
            elif self.Score1.get() == self.Score2.get():
                a = "It Was A Tie!"
            else:
                a = "Your Opponent Won. Better Luck Next Game!"

            tkinter.messagebox.showinfo("Opponent Left", f"Your Opponent Just Left! From The Scores before he left, {a}")
            self.MainMenu()

    def joinRandomGame(self):
        self.CLIENT.send("[JOIN RANDOM]")

    def joinGameWithCode(self):
        self.resetWindow()
        tkinter.Label(text="JOIN CODE", font=('Copperplate Gothic Bold', 65, 'bold', 'underline'), fg="Gold", bg="Black").pack(side=tkinter.TOP, fill=tkinter.X)
        self.codeEntry = tkinter.Entry(font=('Hevaltica', 35), width=23)
        self.codeEntry.pack(side=tkinter.LEFT)

        self.codeEntry.bind("<Return>", self.postData)

    def resetWindow(self):
        for child in self.window.winfo_children():
            child.destroy()

    def postData(self, event):
        code = self.codeEntry.get()
        self.CLIENT.send(f"[JOIN] {code}")

        if code in self.CODES:
            self.CLIENT.send(f"[JOIN] {code}")

    def opponentMoved(self):
        self.p2.set("Locked In")
        if self.p1.get().strip() != "Choosing...":
            self.bothWent()

    def exitWaiting(self):
        self.CLIENT.send("[LEAVING WAIT]")
        self.MainMenu()

    def youMoved(self, move):
        if self.p1.get() == "Choosing...":
            self.p1.set(move)
            self.CLIENT.send(f"[MOVE] {self.p1.get()}")
            if self.otherPlayerMove != None:
                self.bothWent()
        else:
            tkinter.messagebox.showerror("Invalid Request", "You Can't Go Again, Your Move is already Locked In!")

    def bothWent(self):
        a = self.p1.get()
        b = self.otherPlayerMove
        self.otherPlayerMove = None
        self.p2.set(b)
        c = self.RPS_Winner(a, b)

        self.p1.set("Choosing...")
        self.p2.set("Choosing...")

        if c == -1:
            self.TotalScore.set(str(self.Score1.get()) + "/" + str(self.Score2.get()))
            tkinter.messagebox.showinfo("Tie", f"Your Move: {a}\nYour Opponent's Move: {b}\nIt Is a Tie!")
        elif c == 0:
            self.Score1.set(self.Score1.get() + 1)
            self.TotalScore.set(str(self.Score1.get()) + "/" + str(self.Score2.get()))
            tkinter.messagebox.showinfo("You Won", f"Your Move: {a}\nYour Opponent's Move: {b}\nYou Won!")
        elif c == 1:
            self.Score2.set(self.Score2.get() + 1)
            self.TotalScore.set(str(self.Score1.get()) + "/" + str(self.Score2.get()))
            tkinter.messagebox.showinfo("Your Opponent Won!", f"Your Move: {a}\nYour Opponent's Move: {b}\nYour Opponent Won!")

    def startedGame(self):
        self.resetWindow()

        self.p1 = tkinter.StringVar()
        self.p1.set("Choosing...")
        self.p2 = tkinter.StringVar()
        self.p2.set("Choosing...")
        self.Score1 = tkinter.IntVar()
        self.Score1.set(0)
        self.Score2 = tkinter.IntVar()
        self.Score2.set(0)
        self.TotalScore = tkinter.StringVar()
        self.TotalScore.set(str(self.Score1.get()) + "/" + str(self.Score2.get()))

        tkinter.Label(text="Player 1 (You)", font=('Copperplate Gothic Bold', 20, 'bold', "underline"), bg="Black", fg="White").place(x=0, y=0)
        tkinter.Label(text="Player 2", font=('Copperplate Gothic Bold', 20, 'bold', "underline"), bg="Black", fg="White").place(x=440, y=0)
        tkinter.Label(textvariable=self.TotalScore, font=('Copperplate Gothic Bold', 100, 'bold'), fg="Gold", bg="Grey", borderwidth=10).pack(side=tkinter.LEFT)
        tkinter.Label(textvariable=self.p1, font=('Copperplate Gothic Bold', 20, 'bold'), fg="Black", bg="Grey", borderwidth=10).place(x=0, y=400)
        tkinter.Label(textvariable=self.p2, font=('Copperplate Gothic Bold', 20, 'bold'), fg="Black", bg="Grey", borderwidth=10).place(x=405, y=400)
        tkinter.Button(text="Rock", font=('Copperplate Gothic Bold', 20, 'bold'), fg="Black", bg="Brown", borderwidth=10, command=lambda: self.youMoved("Rock")).place(x=0, y=535)
        tkinter.Button(text="Paper", font=('Copperplate Gothic Bold', 20, 'bold'), borderwidth=10, command=lambda: self.youMoved("Paper")).place(x=200, y=535)
        tkinter.Button(text="Scissors", font=('Copperplate Gothic Bold', 20, 'bold'), fg="Blue", bg="Green", borderwidth=10, command=lambda: self.youMoved("Scissors")).place(x=415, y=535)

    def MainMenu(self):
        self.resetWindow()
        tkinter.Label(text="Rock Paper Scissors\nMain Menu", font=('Copperplate Gothic Bold', 35, 'bold', "underline"), bg="Black", fg="Gold").pack(fill=tkinter.X, side=tkinter.TOP)
        tkinter.Button(text="Join Game With Code", font=('Copperplate Gothic Bold', 35, 'bold'), fg="Red", bg="Black", borderwidth=10, command=self.joinGameWithCode).pack(fill=tkinter.X, side=tkinter.BOTTOM)
        tkinter.Button(text="Join Random Game", font=('Copperplate Gothic Bold', 35, 'bold'), fg="Blue", bg="Black", borderwidth=10, command=self.joinRandomGame).pack(fill=tkinter.X, side=tkinter.BOTTOM)

    def waitingScreen(self, code):
        self.resetWindow()
        tkinter.Label(text="Rock Paper Scissors", font=('Copperplate Gothic Bold', 35, 'bold', "underline"), bg="Black", fg="Gold").pack(fill=tkinter.X, side=tkinter.TOP)
        tkinter.Label(text="\n\n\nWaiting For Players...\nJoin Code:", font=('Copperplate Gothic Bold', 34, 'bold'), bg="Black", fg="Blue").pack(fill=tkinter.X, side=tkinter.TOP)
        codeArea = tkinter.Text(font=('Copperplate Gothic Bold', 34, 'bold'), bg="Black", fg="Lime", height=1)
        codeArea.insert("insert linestart", code)
        codeArea.pack(fill=tkinter.X, side=tkinter.TOP)
        tkinter.Button(text="Exit", font=('Copperplate Gothic Bold', 70, 'bold'), fg="Red", bg="Black", borderwidth=10, command=self.exitWaiting).pack(fill=tkinter.X, side=tkinter.BOTTOM)

Main()
