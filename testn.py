import tkinter as tk
from PIL import ImageTk, Image 
app=tk.Tk()
app.geometry("500x500")
app.minsize(500,500)
app.maxsize(500,500)
info= tk.Text(font=('Arial',12))
info.place(x=300,y=0,height=400,width=200)
# imgtk = ImageTk.PhotoImage(file="./logobk.png")
# imglabel=tk.Label(app,image=imgtk)
# imglabel.place(x=300,y=0,height=200,width=200)
app.mainloop()