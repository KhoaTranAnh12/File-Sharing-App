import tkinter as tk
import SERVER
import json
from threading import Thread, Lock
import time

stop_threads = []

def trigger(oldFrame:tk.Frame,frame:tk.Frame):
    oldFrame.place_forget()
    frame.place(x=0,y=0,height=500,width=500)

def terminalScreen(server):
    mainscreen= tk.Frame(app)
    terminal=tk.Text(mainscreen,background='black',font=('Arial',12))
    terminal.tag_configure("color",foreground="white")
    terminal.insert(tk.END,"Terminal version 1.0\nThis is the Server terminal.\n","color")
    terminal.config(state = tk.DISABLED)
    terminal.place(x=0,y=0,height=400,width=300)

    info= tk.Text(font=('Arial',12))
    info.config(state=tk.NORMAL)
    info.config(state=tk.DISABLED)
    info.place(x=300,y=0,height=400,width=200)
    
    threadServer=None
    mutex=Lock()


    commandentry =tk.Entry(font=('Arial',12))
    commandentry.place(x=0,y=400,height=100,width=300)


    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:handleTerminal(mainscreen,commandentry.get(),server,terminal,info))
    button1.place(x=300,y=400,height=100,width=200)
    # button2 = tk.Button(mainscreen,text="Đăng xuất",font=('Arial',12),command=lambda:logout(mainscreen,server))
    # button2.place(x=300,y=450,height=50,width=200)
    threadServer = Thread(target=update_output, args=[server,info])
    threadServer.start()
    return mainscreen

def update_output(server,info):
     while 1:
        time.sleep(0.5)
        print(stop_threads)
        if len(stop_threads)>0:
            break
        server.savehosts()
        server.queue_mutex.acquire()
        if not server.output_queue.empty():
            info.config(state=tk.NORMAL)
            output = server.output_queue.get()
            info.insert(tk.END, f'{output}\n',)
            info.see(tk.END)
            info.config(state=tk.DISABLED)
        server.queue_mutex.release()


def mainScreen(server):
    pass

def handleTerminal(screen,command,server:SERVER.Server,terminal:tk.Text,info:tk.Text):
    print(command)
    terminal.config(state=tk.NORMAL)
    terminal.insert(tk.END,f'{command}\n',"color")
    a,b,c=SERVER.separate(command)
    if a == 'ping':
        respond = server.ping(b)
        terminal.insert(tk.END,respond,"color")
        terminal.config(state=tk.DISABLED)
    if a == 'discover':
        respond = server.discover(b)
        if respond[0] == f'Discover {b} failure':
            terminal.insert(tk.END,respond,"color")
            terminal.config(state=tk.DISABLED)
        else:
            terminal.insert(tk.END,f'{b}:\n',"color")
            for i in respond[1].keys():
                terminal.insert(tk.END,f'{i}: {respond[1][i]}\n',"color")
            terminal.config(state=tk.DISABLED)
    else:
        terminal.insert(tk.END,'Syntax Error!\nThose Syntaxs you can use are:\n        ping hname\n        discover hname\n',"color")
        terminal.config(state=tk.DISABLED)
    pass
def start():
    mainscreen= tk.Frame(app)
    label1 = tk.Label(mainscreen,text="Nhập port máy chủ",font=('Arial',24))
    label1.place(x=0,y=0)
    label3 = tk.Label(mainscreen,text="Port",font=('Arial',12))
    label3.place(x=0,y=200)
    textbox2= tk.Entry(mainscreen,font=('Arial',12))
    textbox2.place(x=200,y=200,height=20,width=290)
    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:startFunc(mainscreen,textbox2.get()))
    button1.place(x=400,y=350)
    return mainscreen

def startFunc(screen,port):
    server=SERVER.Server(int(port))
    app.protocol('WM_DELETE_WINDOW', lambda: close(server,stop_threads))
    trigger(screen,terminalScreen(server))
def close(server,stop_threads):
    server.exit()
    stop_threads.append(1)
    app.destroy()
    return


app=tk.Tk()
app.geometry("500x500")
app.minsize(500,500)
app.maxsize(500,500)
mainscreen=start()
mainscreen.place(x=0,y=0,height=500,width=500)
app.mainloop()