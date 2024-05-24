import tkinter as tk
import CLIENT
import json
def trigger(oldFrame:tk.Frame,frame:tk.Frame):
    oldFrame.place_forget()
    frame.place(x=0,y=0,height=500,width=500)

def mainScreen(client):
    mainscreen= tk.Frame(app)
    label1 = tk.Label(mainscreen,text="Đăng nhập",font=('Arial',24))
    label1.place(x=0,y=0)
    label2 = tk.Label(mainscreen,text="Username",font=('Arial',12))
    label2.place(x=0,y=150)
    label3 = tk.Label(mainscreen,text="Password",font=('Arial',12))
    label3.place(x=0,y=250)
    textbox1= tk.Entry(mainscreen,font=('Arial',12))
    textbox1.place(x=200,y=150,height=20,width=290)
    textbox2= tk.Entry(mainscreen,font=('Arial',12))
    textbox2.place(x=200,y=250,height=20,width=290)
    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:checkLogin(textbox1.get(),textbox2.get(),client,mainscreen))
    button1.place(x=400,y=350)
    button2 = tk.Button(mainscreen,text="Đăng ký",font=('Arial',12),command=lambda:trigger(mainscreen,signUpScreen(client)))
    button2.place(x=200,y=350)
    return mainscreen

def signUpScreen(client):
    mainscreen= tk.Frame(app)
    label1 = tk.Label(mainscreen,text="Đăng ký",font=('Arial',24))
    label1.place(x=0,y=0)
    label2 = tk.Label(mainscreen,text="Username",font=('Arial',12))
    label2.place(x=0,y=150)
    label3 = tk.Label(mainscreen,text="Password",font=('Arial',12))
    label3.place(x=0,y=250)
    textbox1= tk.Entry(mainscreen,font=('Arial',12))
    textbox1.place(x=200,y=150,height=20,width=290)
    textbox2= tk.Entry(mainscreen,font=('Arial',12))
    textbox2.place(x=200,y=250,height=20,width=290)
    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:checkRegister(textbox1.get(),textbox2.get(),client,mainscreen))
    button1.place(x=400,y=350)
    button2 = tk.Button(mainscreen,text="Đăng nhập",font=('Arial',12),command=lambda:trigger(mainscreen,mainScreen(client)))
    button2.place(x=200,y=350)
    return mainscreen


def checkLogin(username,password,client:CLIENT.Client,screen:tk.Frame):
    response=client.login(username,password)
    print(response)
    if response == 'OK':
        print('ok1')
        trigger(screen,terminalScreen(client))
    elif response == 'LOGGED':
        print('ok2')
        screen.place_forget()
        newlabel = tk.Label(screen,text='Username Logged In',font=('Arial',12))
        newlabel.place(x=200,y=300)
        screen.place(x=0,y=0,height=500,width=500)
    elif response == 'FALSE1':
        print('ok3')
        screen.place_forget()
        newlabel = tk.Label(screen,text='Wrong password, try again',font=('Arial',12))
        newlabel.place(x=200,y=300)
        screen.place(x=0,y=0,height=500,width=500)
    elif response == 'FALSE2':
        print('ok4')
        screen.place_forget()
        newlabel = tk.Label(screen,text="Username hasn't been created",font=('Arial',12))
        newlabel.place(x=200,y=300)
        screen.place(x=0,y=0,height=500,width=500)    

def checkRegister(username,password,client:CLIENT.Client,screen:tk.Frame):
    response=client.register(username,password)
    if response == 'OK':
        trigger(screen,mainScreen(client))
    elif response == 'DUPLICATE':
        screen.place_forget()
        newlabel = tk.Label(screen,text='Username has been created, try another',font=('Arial',12))
        newlabel.place(x=200,y=300)
        screen.place(x=0,y=0,height=500,width=500)

def dummy():
    mainscreen= tk.Frame(app)
    label1 = tk.Label(mainscreen,text="ok nhá",font=('Arial',24))
    label1.place(x=0,y=0)
    return mainscreen

def terminalScreen(client):
    mainscreen= tk.Frame(app)
    terminal=tk.Text(mainscreen,background='black',font=('Arial',12))
    terminal.tag_configure("color",foreground="white")
    terminal.insert(tk.END,"Terminal version 1.0\nThis is the Client terminal.\n","color")
    terminal.config(state = tk.DISABLED)
    terminal.place(x=0,y=0,height=400,width=300)


    published= tk.Text(font=('Arial',12))
    published_files=client.showPublishedFiles()
    published.tag_configure("color",foreground="black")
    print(published_files)
    for i in published_files.keys():
        print(f'{i}: {published_files[i]}')
        published.insert(tk.END,f'{i}: {published_files[i]}\n',"color")
    published.config(state= tk.DISABLED)
    published.place(x=300,y=0,height=400,width=200)


    commandentry =tk.Entry(font=('Arial',12))
    commandentry.place(x=0,y=400,height=100,width=300)


    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:handlecommand(mainscreen,commandentry.get(),client,terminal,published))
    button1.place(x=300,y=400,height=50,width=200)
    button2 = tk.Button(mainscreen,text="Đăng xuất",font=('Arial',12),command=lambda:logout(mainscreen,client))
    button2.place(x=300,y=450,height=50,width=200)


    return mainscreen

def logout(screen,client):
    response=client.logout()
    if response == 'OK':
        trigger(screen,mainScreen(client))
def handlecommand(screen,command,client:CLIENT.Client,terminal:tk.Text,published:tk.Text):
    error_syntax="Syntax Error!\nThose Syntaxs you can use are:\n        publish lname fname\n        fetch fname\n        delete fname\n"
    print(command)
    terminal.config(state=tk.NORMAL)
    terminal.insert(tk.END,f'{command}\n',"color")
    a,b,c=CLIENT.separate(command)
    if a == 'publish':
        res = client.publish(b,c)
        if res == 'OK':    
            published.config(state=tk.NORMAL)
            published.delete('1.0', tk.END)
            published_files=client.showPublishedFiles()
            for i in published_files.keys():
                published.insert(tk.END,f'{i}: {published_files[i]}\n')
            terminal.insert(tk.END,f'OK\n',"color")
            terminal.config(state=tk.DISABLED)
            published.config(state=tk.DISABLED)
        else:
            terminal.insert(tk.END,res)
            terminal.config(state=tk.DISABLED)
    elif a == 'fetch' or a== 'delete':
        if c != "": b = b+ " " +c
        if a == 'fetch':
            res = client.fetch (b)
            if res == None: print('none')
            else: print (res)
            if res == '':
                terminal.insert(tk.END,f'NO FILES FOUND\n',"color")
            else:
                x="'"
                y='"'
                print(x + ' ' + y)
                res =res.replace(x,y)
                files = json.loads(res)
                print(type(files))
                for i in files.values():
                    terminal.insert(tk.END,client.retrieve(b,i),"color")
                published.config(state=tk.NORMAL)
                published.delete('1.0', tk.END)
                published_files=client.showPublishedFiles()
                for i in published_files.keys():
                    published.insert(tk.END,f'{i}: {published_files[i]}\n')
                published.config(state=tk.DISABLED)
                terminal.insert(tk.END,f'OK\n',"color")
                terminal.config(state=tk.DISABLED)
        if a == 'delete':
            res = client.dele(b)
            published.config(state=tk.NORMAL)
            published.delete('1.0', tk.END)
            published_files=client.showPublishedFiles()
            for i in published_files.keys():
                published.insert(tk.END,f'{i}: {published_files[i]}\n')
            published.config(state=tk.DISABLED)
            terminal.insert(tk.END,res,"color")
            terminal.config(state=tk.DISABLED)
    else:
        terminal.insert(tk.END,error_syntax,"color")
        terminal.config(state=tk.DISABLED)

def start():
    mainscreen= tk.Frame(app)
    label1 = tk.Label(mainscreen,text="Nhập thông tin máy chủ",font=('Arial',24))
    label1.place(x=0,y=0)
    label2 = tk.Label(mainscreen,text="Host",font=('Arial',12))
    label2.place(x=0,y=150)
    label3 = tk.Label(mainscreen,text="Port",font=('Arial',12))
    label3.place(x=0,y=250)
    textbox1= tk.Entry(mainscreen,font=('Arial',12))
    textbox1.place(x=200,y=150,height=20,width=290)
    textbox2= tk.Entry(mainscreen,font=('Arial',12))
    textbox2.place(x=200,y=250,height=20,width=290)
    button1= tk.Button(mainscreen,text="Submit",font=('Arial',12),command=lambda:startFunc(mainscreen,textbox1.get(),textbox2.get()))
    button1.place(x=400,y=350)
    return mainscreen

def startFunc(screen,host,port):
    client=CLIENT.Client(host,int(port))
    app.protocol('WM_DELETE_WINDOW', lambda: close(client))
    trigger(screen,mainScreen(client))
def close(client):
    try:
        client.logout()
    except:
        pass
    client.exit()
    app.destroy()
app=tk.Tk()
app.geometry("500x500")
app.minsize(500,500)
app.maxsize(500,500)
mainscreen=start()
mainscreen.place(x=0,y=0,height=500,width=500)
# root is your root window

app.mainloop()