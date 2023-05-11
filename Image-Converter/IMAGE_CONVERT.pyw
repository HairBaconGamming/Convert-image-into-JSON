from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox as tkshow
import cv2
import time
import json
import numpy as np
import pyperclip
import win32api, win32con
import keyboard
from pynput.mouse import Button, Controller, Listener
import pyautogui

# create the root window
root = tk.Tk()
root.title('IMAGE CONVERTER')
root.resizable(False, False)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("325x440+%d+%d" % (screen_width/2-325/2, screen_height/2-440/2))
root.iconbitmap('Assets/convert.ico')
root.lift()
root.attributes('-topmost', True)

mouse = Controller()

filename = None
my_image_label = None
choosed_image = None
negative = False
aa = None
bb = None
current_value = tk.DoubleVar()
sensitivity = 127
sv = tk.StringVar()

sv.set(sensitivity)
current_value.set(sensitivity)

def resize_image_to_smaller(image,max):
    height,width = image.shape
    if width > max[0]:
        resize_factor = width / max[0]
        image = cv2.resize(image,(int(width / resize_factor), int(height / resize_factor)), interpolation = cv2.INTER_AREA)
    if height > max[1]:
        resize_factor = height / max[1]
        image = cv2.resize(image,(int(width / resize_factor), int(height / resize_factor)), interpolation = cv2.INTER_AREA)
    width, height = image.shape
    if width > max[0]:
        image = resize_image_to_smaller(image,max)
    if height > max[1]:
        image = resize_image_to_smaller(image,max)
    return image

def image_():
    global choosed_image
    global filename
    global my_image_label
    imagea = cv2.imread(filename)
    grayImage = cv2.cvtColor(imagea, cv2.COLOR_BGR2GRAY)
    if negative == True:
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, sensitivity, 255, cv2.THRESH_BINARY_INV)
    else:
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, sensitivity, 255, cv2.THRESH_BINARY)
    imagea = resize_image_to_smaller(blackAndWhiteImage,(250,250))
    
    imagea = cv2.cvtColor(imagea, cv2.COLOR_BGR2RGB)
    imagea = Image.fromarray(imagea)
    my_image = ImageTk.PhotoImage(imagea)
    choosed_image = my_image
    if my_image_label != None:
        my_image_label.configure(image=my_image)
        my_image_label.image = my_image

def select_file():
    global filename
    global my_image_label
    global choosed_image
    global aa
    global bb
    
    filetypes = (
        ('Image files', '*.jpg *.jpeg *.png'),
    )

    oldfilename = filename
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    
    if filename == '':
        filename = oldfilename
        return
    
    if aa and bb != None:
        image = cv2.imread(filename)
        height,width,channels = image.shape
        aa.set(str(width))
        bb.set(str(height))
    # image = Image.open(filename)
    image_()

def loopCheck():
    if choosed_image == None:
        select_file()
        if choosed_image == None:
            loopCheck()

def createprocesstab(title):
    createdroot = tk.Tk()
    createdroot.title(title)
    createdroot.geometry("325x125+%d+%d" % (screen_width/2-325/2, screen_height/2-125/2))
    createdroot.iconbitmap('Assets/loading.ico')
    createdroot.resizable(False, False)
    createdroot.attributes('-topmost', True)
    pb = ttk.Progressbar(
        createdroot,
        orient='horizontal',
        mode='determinate',
        length=315
    )
    frame = tk.Frame(createdroot)
    percent = ttk.Label(frame,text="0%")
    percent2 = ttk.Label(frame,text="0/0")
    total = ttk.Label(frame,text="???")
    btn = ttk.Button(createdroot,text="End convert",command=onclick)
    pb.grid(column=0, row=0, padx=10, pady=10)
    frame.grid(column=0,row=1)
    percent.grid(column=0,row=0)
    percent2.grid(column=0,row=1)
    total.grid(column=0,row=2)
    btn.grid(column=0,row=2,padx=70)
    
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    createdroot.grid_rowconfigure(0, weight=1)
    createdroot.grid_columnconfigure(0, weight=1)

    return createdroot,pb,percent,percent2,total,btn

def file_save(content,type):
    f = fd.asksaveasfile(mode='w', defaultextension=type)
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f.write(content)
    f.close() # `()` was missing.

endconvert = False
def onclick():
    global endconvert
    result = tkshow.askquestion("Convert","If you end the procedure, it will be lost. You must be certain.")
    if result == 'yes':
        endconvert = True

def Convert():
    global negative
    global endconvert
    endconvert = False
    width_ = int(entry.get())
    height_ = int(entry2.get())
    originalImage = cv2.imread(filename)
    originalImageResized = cv2.resize(originalImage,(width_,height_), interpolation = cv2.INTER_AREA)
    grayImage = cv2.cvtColor(originalImageResized, cv2.COLOR_BGR2GRAY)
    if negative == True:
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, sensitivity, 255, cv2.THRESH_BINARY_INV)
    else:
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, sensitivity, 255, cv2.THRESH_BINARY)
    height,width = blackAndWhiteImage.shape
    if height and width > 500:
        msg_box = tkshow.askquestion("Convert","Image to JSON conversion? It will take a while to convert.")
        if msg_box == "no":
            return
    imagea = cv2.cvtColor(blackAndWhiteImage, cv2.COLOR_BGR2RGB)
    imagea = Image.fromarray(imagea)
    root.withdraw()
    createdroot,pb,percent,percent2,total,btn = createprocesstab("Converting")
    data = {}
    index = 0
    per = 0
    #per2 = 0
    totaladded = 0
    btn.configure(command=onclick)
    for x in range(width):
        for y in range(height):
            if endconvert == True:
                break
            index += 1
            per += 1
            #per2 += 1
            pixelcolor = imagea.getpixel((x,y))
            if isinstance(pixelcolor,tuple) == False:
                shade = pixelcolor
            else:
                shade = (pixelcolor[0] + pixelcolor[1] + pixelcolor[2]) / 3
            # print(shade,pixelcolor,thresh)
            if shade == 0:
                totaladded += 1
                data[totaladded]={'X':x,'Y':y,'Down':True}
            total.configure(text="Added "+str(totaladded)+" temps")
            if per > 1234:
                per = 0
                percent.configure(text=str(int(index/(width*height) * 100000)/1000)+"%")
                percent2.configure(text=str(index)+"/"+str(width*height))
                pb['value'] = index/(width*height) * 100
                createdroot.update()
    createdroot.destroy()
    root.deiconify()
    if endconvert == False:
        dataconverted = json.dumps(data)
        msg_box = tkshow.askquestion("Create","Save a file as json?")
        if msg_box == 'yes':
            file_save(dataconverted,'.json')
        else:
            pyperclip.copy(dataconverted)
            tkshow.showinfo("Clipboard","Data was copied to the clipboard!")

def switch():
    global negative
    negative = not negative
    if negative:
        on_button.config(image = on)
    else:
        on_button.config(image = off)
    image_()

def slider_changed(event):
    global sensitivity
    sensitivity = int(current_value.get())
    sv.set(str(int(current_value.get())))
    entry3.configure(textvariable=sv)
    image_()

oldsv = sv.get()
def callbacksentry3(event):
    global sv
    global sensitivity
    global oldsv
    if event.get() == "":
        sv.set(str(0))
        slider.set(0)
        entry3.configure(textvariable=sv)
        oldsv = sv.get()
        sensitivity = int(sv.get())
        return
    try:
        if int(event.get()) > 255:
            event.set(str(255))
            sv.set(str(255))
        sensitivity = int(event.get())
        current_value.set(sensitivity)
        slider.set(sensitivity)
        entry3.configure(textvariable=sv)
        oldsv = sv.get()
    except:
        sv.set(oldsv)
        entry3.configure(textvariable=sv)
        slider.set(int(oldsv))
        sensitivity = int(sv.get())
        return
    image_()

def move(x,y):
    win32api.SetCursorPos((x,y))
def clickdown(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
def clickup(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
def click(x,y):
    move(x,y)
    clickdown(x,y)
    clickup(x,y)

enddrawing = False
def onclick2():
    global enddrawing
    result = tkshow.askquestion("Draw","If you end the draw, it will be lost. You must be certain.")
    if result == 'yes':
        enddrawing = True

def Draw():
    global enddrawing
    enddrawing = False
    filetypes = (
        ('Json file', '*.json'),
    )

    jfilename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    
    if jfilename == '':
        return
    jsonfile = open(jfilename, "r")
    data = json.loads(jsonfile.read())
    createdroot,pb,percent,percent2,total,btn = createprocesstab("Drawing")
    ask = tkshow.askquestion("Draw","Insane drawing? (The drawing won't be working.)")
    root.withdraw()
    for i in range(1,15):
        total.configure(text="Find position for draw. ("+str(15-i)+"s)")
        createdroot.update()
        time.sleep(1)
    total.configure(text="DO NOT MOVE OR CLICK YOUR MOVE!")
    createdroot.update()
    ox,oy = win32api.GetCursorPos()
    btn.configure(text="End [Z]",command=onclick2)
    delay = 0
    index = 0
    for index in data:
        try:  
            if keyboard.is_pressed('z'): 
                result = tkshow.askquestion("Draw","If you end the draw, it will be lost. You must be certain.")
                if result == 'yes':
                    enddrawing = True
        except:
            continue
        if enddrawing == True:
            break
        temp = data[index]
        x = int(ox) + int(temp["X"])
        y = int(oy) + int(temp["Y"])
        mouse.move(x,y)
        pyautogui.move(x,y)
        if ask == 'no':
            time.sleep(0.0029)
        #click(x,y)
        pyautogui.leftClick(x,y)
        delay += 1
        if delay > 123:
            delay = 0
            percent.configure(text=str(int(int(index)/(len(data)) * 100000)/1000)+"%")
            percent2.configure(text=str(index)+"/"+str(len(data)))
            pb['value'] = int(index)/(len(data)) * 100
            #total.configure(text="Mouse1Down: "+str(down))
            createdroot.update()
    createdroot.destroy()
    root.deiconify()

# open button

loopCheck()

image = cv2.imread(filename)
height,width,channels = image.shape

frmMain = tk.Frame(root)
frmMain2 = tk.Frame(root)

open_button = ttk.Button(
    root,
    text='Select a file',
    command=select_file
)

my_image_label = ttk.Label(root,image=choosed_image)

convertbutton = ttk.Button(frmMain2, text = 'Convert', command = Convert)
drawbutton = ttk.Button(frmMain2,text='Draw',command=Draw)

label_negative = ttk.Label(frmMain,text="Negative:",anchor="e",justify=tk.RIGHT)

aa = tk.StringVar()
aa.set(str(width))
bb = tk.StringVar()
bb.set(str(height))

on = Image.open("Assets/on.png")
off = Image.open("Assets/off.png")
on = on.resize((65,25))
off = off.resize((65,25))
on = ImageTk.PhotoImage(on)
off = ImageTk.PhotoImage(off)
on_button = tk.Button(frmMain, image = off,bd = 0,command = switch)
closebutton = ttk.Button(frmMain2, text = 'Exit', command = root.quit)
label_width = ttk.Label(frmMain,text="Width:",anchor="e",justify=tk.RIGHT)
entry = tk.Entry(frmMain,textvariable=aa)
label_height= ttk.Label(frmMain,text="Height:",anchor="e",justify=tk.RIGHT)
entry2 = tk.Entry(frmMain,textvariable=bb)
label_sen= ttk.Label(frmMain,text="Sensitivity:",anchor="e",justify=tk.RIGHT)
sv.trace("w", lambda name, index, mode, sv=sv: callbacksentry3(sv))
entry3 = ttk.Entry(frmMain,textvariable=sv)
slider = ttk.Scale(
    frmMain,
    from_=0,
    to=255,
    variable=current_value,
    orient='horizontal',  # horizontal
    command=slider_changed
)

my_image_label.grid(row=0,column=0)
open_button.grid(column=0,row=1)
frmMain.grid(row=2, column=0, sticky="NESW",padx=25)
label_negative.grid(column=0,row=0)
on_button.grid(column=1,row=0)
label_width.grid(column=0,row=1,pady=2)
entry.grid(column=1,row=1,pady=2)
label_height.grid(column=0,row=2,pady=2)
entry2.grid(column=1,row=2,pady=2)
label_sen.grid(column=0,row=3,pady=2)
entry3.grid(column=1,row=3,pady=2)
slider.grid(column=1,row=4,pady=2)
frmMain2.grid(row=3,column=0, sticky="NESW", padx=50)
convertbutton.grid(column=0,row=0)
drawbutton.grid(column=1,row=0)
closebutton.grid(column=2,row=0)

# run the application
#frmMain.grid_rowconfigure(0, weight=1)
#frmMain.grid_columnconfigure(0, weight=1)
frmMain2.grid_rowconfigure(1, weight=1)
frmMain2.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.mainloop()