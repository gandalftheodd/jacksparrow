#    pyinstaller --onefile --noconsole -i "skullp.ico" gui.py


import glob
import os
import atexit
import time
import jacksparrow as jk
import threading
from jacksparrow import download
from jacksparrow import getLink
from tkinter import *
from tkinter import scrolledtext
import tkinter as rt
from tkinter.filedialog import askdirectory
from tkinter import font
import configparser
from multiprocessing import Process, Pipe



config = configparser.ConfigParser()
config.read('config.ini')
window = Tk()
songs = []
run = 0
log_length = 0
dl = threading.Thread()
go = 1
queue = []
running = 0
actvlog = open('log.txt','r')
filename = config['DEFAULT']['Download Location']

#makes main window
window.title("jacksparrow")
window.geometry('800x600')

#sets icon for program
img = PhotoImage(file="skl.png")
window.iconphoto(False,img)

#creates the song entry vox
titlf = Frame(window,relief=SUNKEN,borderwidth=2)
titl = Entry(master=titlf,width=20,relief=SUNKEN)
titlf.place(x=10,y=230)
titl.pack()
titll = Label(window, text = "Song Name")
titll.place(x=10,y=210)

#creates the artist entry window
artistf = Frame(window,relief=SUNKEN,borderwidth=2)
artist = Entry(master=artistf,width=20,relief=SUNKEN)
artistf.place(x=10,y=300)
artist.pack()
artistl = Label(window, text="Song Artist")
artistl.place(x=10,y=280)

#creates the box that shows where music is being downloaded to
fllc = Label(window, text = 'Music Download Location')
und = font.Font(fllc, fllc.cget("font"))
und.configure(underline = True)
fllc.configure(font=und)
fllc.place(x=10,y=3)
lctf = Frame(window,relief=SUNKEN,borderwidth=2)
lct = Entry(master=lctf,width = 36, relief=SUNKEN)
lct.insert(0,filename)
lctf.place(x=10,y=23)
lct.pack()

#creates the list of songs to be downloaded
sl = scrolledtext.ScrolledText(window,width=40,height=30)
sl.place(x=380,y=20)

lawg = scrolledtext.ScrolledText(window,width=40,height=10)
lawg.place(x=20,y=400)
lawg.configure(font='Helvetica 10')
#lawg.configure(state='disabled')

#sets what pressing the big red x on the top right of the window does
def stp():
    global actvlog
    actvlog.close()
    global go
    go = 0
    try:
        window.destroy()
    except:
        pass
window.protocol("WM_DELETE_WINDOW", stp)

#the function for the button labeled "enter"
def clenter():
    combiner = ''
    if titl.get() != '':
        if artist.get() != '':
            combiner = ' - '
        songs = sl.get(1.0,END).splitlines()
        songs.append(titl.get()+combiner+artist.get())
        titl.delete(0,END)
        sl.delete(1.0,END)
        sl.insert(INSERT,'\n'.join(songs))
        combiner = ''

#the exact same thing but for the key 'enter'
def handleReturn(event):
    combiner = ''
    if titl.get() != '':
        if artist.get() != '':
            combiner = ' - '
        songs = sl.get(1.0,END).splitlines()
        songs.append(titl.get()+combiner+artist.get())
        titl.delete(0,END)
        sl.delete(1.0,END)
        sl.insert(INSERT,'\n'.join(songs))
        combiner = ''

#the function to download the top item in the list
def dtop():
    global queue
    thing = sl.get(1.0,END).replace('-','by')
    sng = thing.splitlines()
    #print(sng)
    queue.append(sng[1])
    #print('queue1:')
    #print(queue)
    sng.pop(1)
    cum = '\n'.join(sng)
    pen = cum.replace('by', ' - ')

    sl.delete(1.0,END)
    sl.insert(INSERT, pen)
    lawg.configure(state='normal')
    lawg.insert(INSERT,'-This may take a couple seconds-\n')
    lawg.configure(state='disabled')
    #print('queue2:')
    #print(queue)

#function to change the download location
def pkfil():
    global filename
    filename = askdirectory()
    #lct["text"] = filename
    lct.delete(0,END)
    lct.insert(0,filename)
    #print(filename)
    config['DEFAULT']['Download Location'] = filename
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

#function to download all items on the list
def dall():
    global queue
    thing = sl.get(1.0,END).replace('-','by')
    sng = thing.splitlines()
    sl.delete(1.0,END)
    lawg.configure(state='normal')
    lawg.insert(INSERT,'-This may take a couple seconds-\n')
    lawg.configure(state='disabled')
    for v in range(len(sng)-1):
        queue.append(sng[v+1])

#function to initialize a thread to download all items in the que
def downl(conn):
    global queue
    #print(queue)
    global running
    global go
    while go == 1:
        if len(queue) > 0:
            if running == 0:
                running = 1
                dl = threading.Thread(target=download,args=(queue[0],filename,conn,))
                dl.start()
                queue.pop(0)
                while running == 1:
                    if not dl.is_alive():
                        running = 0


def testing(conn):
    fgh = []
    while go == 1:
        kl = conn.recv()
        print(kl)
        fgh.append(kl)
        lawg.configure(state='normal')
        lawg.insert(INSERT,str(kl))
        lawg.yview(END)
        lawg.configure(state='disabled')
    time.sleep(1)
    print(fgh)







"""
def check_log():
    #global actvlog
    global go
    global log_length
    while go == 1:
        zkv = open('log.txt','r')
        log = zkv.read()
        log_items = log.split('\n')
        lng = len(log_items)
        print(log_items)
        if lng > log_length:
            lawg.insert(INSERT, log_items[lng-1])
            log_length = lng
        zkv.close()
        time.sleep(1)
"""




#binds enter key to its function
titl.bind("<Return>", handleReturn)
artist.bind("<Return>", handleReturn)

#binds button to change download location
fil = Button(window,text='browse',command=pkfil)
fil.place(x=240,y=20)

#binds button to enter song and artist name into the list
btn = Button(window,text='Enter',command=clenter)
btn.place(x=200,y=268)

#binds button to download top item
down = Button(window,text='Download Top Item',command=dtop)
down.place(x=380,y=510)

#binds button to download all items
downall = Button(window,text='Download All',command=dall)
downall.place(x=500,y=510)

#start the thread (duh)
parent_conn, child_conn = Pipe()

tr = threading.Thread(target=downl,args=(child_conn,))
tr.start()

lg = threading.Thread(target=testing,args=(parent_conn,))
lg.setDaemon(True)
lg.start()

window.mainloop()

