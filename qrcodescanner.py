# %%
import cv2
import numpy as np
import mysql.connector
from tkinter import *
from pyzbar.pyzbar import decode
from PIL import Image as Img
from imutils.video import VideoStream
from PIL import ImageTk, ImageFont, ImageDraw
from datetime import datetime
from tkinter import ttk


# %%
class APP:
    def __init__(self,window):
        self.window = window
        self.Search = self.search(self)
        self.Detect = self.detect(self)

        self.btn1 = Button(self.window, text = '入場掃描', font = ('Arial Unicode MS', 15), width=20, height=2, highlightbackground='#3E4149',command=self.Detect.detect_func)
        self.btn2 = Button(self.window, text = '查看資料', font = ('Arial Unicode MS', 15), width=20, height=2, highlightbackground='#3E4149',command=self.Search.search_interface)
        self.btn3 = Button(self.window, text = '離開系統', font = ('Arial Unicode MS', 15), width=20, height=2, highlightbackground='#3E4149',command=self.window.destroy)

        self.btn1.pack(pady=10)
        self.btn2.pack(pady=10)
        self.btn3.pack(pady=10)

    def hide_button(self):
        self.btn1.pack_forget()
        self.btn2.pack_forget()
        self.btn3.pack_forget()
    
    def hide_btn_inner(self):
        self.B1.pack_forget()
        self.B2.pack_forget()
        self.B3.pack_forget()
        self.B4.pack_forget()
    
    def secface(self):
        self.hide_button()
 
        self.B1 = Button(self.window, text = '1月7號', font = ('Arial Unicode MS', 15), width=10, height=2, highlightbackground='#3E4149')
        self.B2 = Button(self.window, text = '1月8號 - 1', font = ('Arial Unicode MS', 15), width=10, height=2, highlightbackground='#3E4149')
        self.B3 = Button(self.window, text = '1月8號 - 2', font = ('Arial Unicode MS', 15), width=10, height=2, highlightbackground='#3E4149')
        self.B4 = Button(self.window, text = '1月9號', font = ('Arial Unicode MS', 15), width=10, height=2, highlightbackground='#3E4149')

        self.B1.pack(pady=3)
        self.B2.pack(pady=3)
        self.B3.pack(pady=3)
        self.B4.pack(pady=3)

    class detect:
        def __init__(self,outerwin):
            self.outerwin = outerwin
        
        def detect_func(self):
            self.outerwin.secface()

            self.outerwin.B1.bind("<Button-1>", lambda e: self.hiddenanresize('test'))
            self.outerwin.B2.bind("<Button-1>", lambda e: self.hiddenanresize('test'))
            self.outerwin.B3.bind("<Button-1>", lambda e: self.hiddenanresize('test'))
            self.outerwin.B4.bind("<Button-1>", lambda e: self.hiddenanresize('test'))  

        def hiddenanresize(self, srhtb):
            self.outerwin.hide_btn_inner()
            self.outerwin.window.geometry("1000x800")
            self.dtfunc(self.outerwin.window, srhtb)

        class dtfunc:
            def __init__(self,dtouterwin, srhtable):
                self.window = dtouterwin
                self.srhtable = srhtable
                self.findframe = self.detectsql(self)

                self.panel = Label(self.window)
                self.panel.pack(pady=10)

                frame1 = Frame(self.window,bg='#3E4149')
                self.db_input = Entry(frame1,font=('Arial Unicode MS', 15),bg='#3E4149',fg = 'white')
                self.db_input.pack(side=LEFT, fill=BOTH, expand=1)

                Button(frame1, text='輸入', highlightbackground='#3E4149',command=self.keyindb).pack(side=RIGHT,padx=7)

                self.my_string_var = StringVar()
                self.my_string_var.set('')
                Label(frame1, textvariable=self.my_string_var, font = ('Arial Unicode MS', 15),bg='#3E4149',fg = 'white').pack(padx=5,pady=5)
                frame1.pack(side='left',padx=15,pady=5)

                self.button = Button(self.window, text='關閉視窗', command=self.on_close, highlightbackground='#3E4149')
                self.button.pack(side='right',padx=5,pady=5)

                self.stream = VideoStream(0)
                self.stream.start()
                
                self.stop = False
                self.window.after(100, self.video_loop)

                self.window.wm_protocol("WM_DELETE_WINDOW", self.on_close)
            
            def keyindb(self):
                inputwd = self.db_input.get()
                
                if inputwd.isnumeric():
                    dbdata = self.findframe.finddata(inputwd)

                    if not dbdata:
                        self.my_string_var.set('無該訂單資料')
                    else:
                        if dbdata[1]:
                            self.my_string_var.set('已入場')
                        else:
                            self.findframe.addtime(inputwd)
                            self.my_string_var.set('已成功登記入場')
                else:
                    self.my_string_var.set('輸入值非數字')

                self.db_input.delete(0, END)

            def video_loop(self):
                frame = self.stream.read()

                img = cv2.flip(frame,1)
                imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                for barcode in decode(imggray):
                    mydata = barcode.data.decode('utf-8')
                    getdata = self.findframe.finddata(mydata)
                    noticetext = ''
                    
                    if getdata:
                        nowtime = datetime.now().timestamp()

                        if getdata[1] != 0  and (nowtime - getdata[1]) > 10:
                            noticetext = '已入場'
                            noticecolor = (0,200,255)
                            
                        else:
                            noticetext = '歡迎入場'
                            noticecolor = (17,255,0)
                            self.findframe.addtime(mydata)
                    else:
                        noticetext = '查無此人'
                        noticecolor = (0,0,255)

                    pts = np.array([barcode.polygon],np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv2.polylines(img,[pts],True,noticecolor,5)
                    pts2 = barcode.rect

                    fontpath = 'JenHe.ttf'
                    font = ImageFont.truetype(fontpath, 32)
                    img_pil = Img.fromarray(img)
                    draw = ImageDraw.Draw(img_pil)
                    draw.text((pts2[0],pts2[1]-50),  noticetext, font = font, fill = noticecolor)
                    img = np.array(img_pil)

                    
                fontpath = 'JenHe.ttf'
                amountfont = ImageFont.truetype(fontpath, 25)
                img_am = Img.fromarray(img)
                draw_am = ImageDraw.Draw(img_am)
                nwam, dbam = self.findframe.fetchamount()
                nowamount = f'目前進場人數 {nwam[0]}/{dbam[0]}'
                draw_am.text((10,10),  nowamount, font = amountfont, fill = (0,0,255))
                img = np.array(img_am)

                image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                self.image = Img.fromarray(image)
                self.photo = ImageTk.PhotoImage(self.image)
                self.panel.configure(image=self.photo)  
                if not self.stop:
                    self.window.after(10, self.video_loop)   

            def on_close(self):
                self.stop = True
                self.stream.stop()
                self.window.destroy()

            class detectsql:
                def __init__(self,findouterwin):
                    self.hostname = 'localhost'
                    self.username = ''
                    self.password = ''
                    self.database = 'test'
                    self.srhtable = findouterwin.srhtable

                def finddata(self, srhnumber):
                    conn = mysql.connector.connect( host=self.hostname, user=self.username, passwd=self.password, db=self.database)
                    cur = conn.cursor()
                    cur.execute(f"SELECT * FROM {self.srhtable} where Ordernum ={srhnumber}" )
                    returndata = cur.fetchone()
                    conn.close()

                    return returndata
                
                def addtime(self, srhnumber):
                    addtm = datetime.now().timestamp()
                    conn = mysql.connector.connect( host=self.hostname, user=self.username, passwd=self.password, db=self.database)
                    cur = conn.cursor()
                    cur.execute(f"UPDATE {self.srhtable} SET timestamp = '{addtm}' WHERE Ordernum = {srhnumber}" )

                    conn.commit()
                
                def fetchamount(self):
                    conn = mysql.connector.connect( host=self.hostname, user=self.username, passwd=self.password, db=self.database)
                    cur = conn.cursor()
                    cur.execute(f"SELECT COUNT(timestamp) FROM {self.srhtable}" )
                    dbamount = cur.fetchone()
                    cur.execute(f"SELECT COUNT(timestamp) FROM {self.srhtable} WHERE timestamp!=0" )
                    inamount = cur.fetchone()
                    conn.close()

                    return inamount,dbamount
    class search:
        def __init__(self,outerwin):
            self.outerwin = outerwin

        def search_interface(self):
            self.outerwin.secface()

            self.outerwin.B1.bind("<Button-1>", lambda e: self.show_all(self.dbfunc().search_data('test')))
            self.outerwin.B2.bind("<Button-1>", lambda e: self.show_all(self.dbfunc().search_data('test')))
            self.outerwin.B3.bind("<Button-1>", lambda e: self.show_all(self.dbfunc().search_data('test')))
            self.outerwin.B4.bind("<Button-1>", lambda e: self.show_all(self.dbfunc().search_data('test')))

        def show_all(self,data):
            self.outerwin.hide_btn_inner()

            column = ['訂單編號','進場時間']

            table = ttk.Treeview(
                master=self.outerwin.window,  
                height=10,  
                columns=column,  
                show='headings'
                )
            
            table.heading('訂單編號', text='訂單編號', )  
            table.heading('進場時間', text='進場時間', ) 
            table.column('訂單編號', width=100, anchor=CENTER)  
            table.column('進場時間', width=150, anchor=CENTER)

            table.pack(pady=20)

            self.button = Button(self.outerwin.window, text='關閉視窗', command=self.outerwin.window.destroy, highlightbackground='#3E4149')
            self.button.pack(side='right',padx=5,pady=5)
                    
            for index, dta in enumerate(data):
                dta = list(dta)
                
                if dta[1] == None or dta[1] == 0:
                    dta[1] = '尚未入場'
                else:
                    dta[1] = datetime.fromtimestamp(dta[1]).strftime('%Y-%m-%d %H:%M:%S')

                table.insert('', END, values=dta) 
        

        class dbfunc:
            def __init__(self):
                self.hostname = 'localhost'
                self.username = ''
                self.password = ''
                self.database = 'test'

            def search_data(self, datatable):
                conn = mysql.connector.connect( host=self.hostname, user=self.username, passwd=self.password, db=self.database)
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {datatable}" )
                returndata = cur.fetchall()
                conn.close()
                
                return returndata


        

# %%
if __name__ == "__main__":
    root  = Tk()
    root.title('Scanner')
    root.geometry('350x300')

    APP(root)
    root.configure(bg='#3E4149')
    mainloop()


