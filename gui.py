import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.ttk import Progressbar,Style
from tkinter import filedialog as fd
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import signal
import subprocess
import threading
from utils import Colors, checkOS, exportJob,createJob
from tkinter import Scrollbar
from dragndrop_frame import DragDropFrame

class Entry:
    from secondaryWindows import JobAdvancedSettings

    def __init__(self,mainGUI,job):
        self.parent = mainGUI
        self.Job = job
        self.path = job.path
        self.settings = mainGUI.settings
        self.isChecked = tk.BooleanVar()
        self.settingsWindow = None
        self.blendVersionVar = tk.StringVar()
        if self.Job.blender:
            self.blendVersionVar.set(self.Job.blender.name)
        else:
            self.blendVersionVar.set('Selec Blender Version')
        self.master = mainGUI.contentFrame
        self.root = DragDropFrame(self.master,self.parent.entries,highlight_thickness=2, highlight_color=Colors.accent,offset=4,highlightbackground='ORANGE',bg=Colors.widget,pady=5,padx=10)#Colors.accent
        
        
        tk.Grid.columnconfigure(self.root,4,weight=1)
        tk.Grid.rowconfigure(self.root,1,weight=1)
        tk.Label(self.root,text=self.path[:25], borderwidth=1,bg=Colors.widget,fg=Colors.fontColor).grid(row=0,column=0,sticky='W')
        
        
        self.control_frame = tk.Frame(self.root,bg=Colors.widget)
        self.control_frame.grid(row=0,column=5,padx=10,sticky='E')

        self.settingsPNG = tk.PhotoImage(file=r'img\gear0.5x.png')
        self.settingsButton = tk.Button(self.control_frame,image=self.settingsPNG,command=lambda:self.openSettings(),bg=Colors.background)
        self.settingsButton.pack(side=tk.LEFT)
        self.settingsButton.image = self.settingsPNG

        self.moveFrame = tk.Frame(self.control_frame,bg=Colors.widget)
        self.moveFrame.pack(side=tk.LEFT)
        self.downPNG = tk.PhotoImage(file=r'img\down.png')
        self.upPNG = tk.PhotoImage(file=r'img\up.png')
        self.upButton=tk.Button(self.moveFrame,image=self.upPNG,bg=Colors.background,command=lambda:self.moveUp())
        self.upButton.pack(side=tk.LEFT)
        self.upButton.image= self.upPNG
        self.downButton=tk.Button(self.moveFrame,image=self.downPNG,bg=Colors.background,command=lambda:self.moveDown())
        self.downButton.pack(side=tk.LEFT,padx=3)
        self.downButton.image= self.downPNG

        

        self.deltePNG = tk.PhotoImage(file=r'img\delete-x.png')
        tk.Button(self.control_frame,image=self.deltePNG,command=lambda: self.destroyEntry(),bg=Colors.background, fg = Colors.fontColor).pack(side=tk.LEFT,padx=(8,0))
        self.isActiveBtn = tk.Checkbutton(self.control_frame,variable=self.isChecked,activeforeground=Colors.fontColor ,bg=Colors.widget,fg=Colors.fontColor,selectcolor= Colors.widget,activebackground=Colors.widget)
        self.isActiveBtn.pack(side=tk.LEFT)
        self.isChecked.set(True)
        self.blendOptionMenu=tk.OptionMenu(self.root,self.blendVersionVar,*self.settings.blenderVersions if self.settings.blenderVersions else ['Selec Blender Version'],
            command=self.setBlenderVersion)
        self.blendOptionMenu.grid(row=1,column=0,columnspan=2,sticky='W',pady=5)
        self.blendOptionMenu.config(bg=Colors.widget,fg=Colors.fontColor)

        
        s = Style()
        s.theme_use('clam')
        s.configure("red.Horizontal.TProgressbar", foreground=Colors.accent, background=Colors.accent,lightcolor=Colors.widget,bordercolor=Colors.widget,troughcolor=Colors.widget2)
        self.progress = Progressbar(self.root,style="red.Horizontal.TProgressbar",mode='indeterminate',orient='horizontal')
        self.stopPNG = tk.PhotoImage(file=r'img\stop.png')
        self.cancleRendering = tk.Button(self.root,image=self.stopPNG,command=lambda: self.stopRendering(),bg=Colors.background, fg = Colors.fontColor)
        
        self.blendOptionMenu['highlightthickness'] = 0
        self.checkRenderAllFiles()

    
    def stopRendering(self):
        answer = askyesno(title='confirmation',
                    message='Are you sure that you want to stop rendering?')
        if answer:
            self.parent.stopCurrentJob()
    

    def setRendering(self,isRendering):
        if isRendering:
            self.progress.grid(row=1,column=5,columnspan=4)
            self.cancleRendering.grid(row=1,column=6)
            self.progress.start([5])
            self.root.config(highlightthickness=2)
        else:
            self.progress.stop()
            self.root.config(highlightthickness=0)
            self.progress.grid_forget()
            self.cancleRendering.grid_forget()
    

    def checkRenderAllFiles(self):
        if self.parent.isAllFiles.get():
            self.isActiveBtn.config(state='disabled')
    
    def openSettings(self):
        self.settingsWindow=self.JobAdvancedSettings(self)   
           

    def pack(self):
        self.root.do_pack(side=tk.TOP,pady=4,padx=15)#fill=tk.BOTH

    def destroyEntry(self):
        self.root.destroy()
        self.parent.removeEntry(self)


    def setBlenderVersion(self,value):
        for blend in self.settings.blenderVersions:
            if blend.name == self.blendVersionVar.get():
                self.Job.blender = blend

    def moveUp(self):
        self.parent.moveEntryUp(self)

    def moveDown(self):
        self.parent.moveEntryDown(self)

class MainGUI:
    from versionWindows import BlenderVersionSettings
    from model import ProgramSettings
    from utils import exportJob,readVersionJSON,readSettingsJSON,mouseWheelEvent
    
    def __init__(self):        
        path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(path)

        self.settings = None

        if not os.path.exists('versions.json'):
            with open('versions.json', 'w'): pass

        if not os.path.exists('settings.json'):
            with open('settings.json', 'w'): pass
            self.settings = self.ProgramSettings([])
        else:
            try:
                self.settings = MainGUI.readSettingsJSON()
            except Exception:
                self.settings = self.ProgramSettings([])
        self.settings.blenderVersions = []

        self.cmd = None
        self.stopRenderFlag = False
        self.root = TkinterDnD.Tk()
        self.root.geometry('700x500')
        self.root.title("A cool render manager")
        self.root.protocol("WM_DELETE_WINDOW", self.closeWindowEvent)
        self.root.configure(background=Colors.background)
        self.root.iconbitmap(r"img\icon.ico")
        self.jobs = []
        self.entries = []
        self.entries_frame = []

        self.isAllFiles = tk.IntVar(value=0)

        self.canvas = tk.Canvas(self.root, background=Colors.background,highlightthickness=0)
        self.scrollbar=Scrollbar(self.root,orient="vertical",command=lambda:self.canvas.yview())
        self.contentFrame = tk.Frame(self.canvas,bg=Colors.background)
    
        
        try:
            MainGUI.readVersionJSON(self.settings)
            
        except Exception as e:
            print(e)
    #Einstellung Tab
        navFrame = tk.Frame(self.root,bg=Colors.header,height=40)
        navFrame.pack(side=tk.TOP,fill=tk.X)
        self.settingsButton = tk.Button(navFrame, text="Settings",command=self.openSettings,bg=Colors.background, fg = Colors.fontColor)
        self.settingsButton.pack(side=tk.LEFT, anchor=tk.NW,pady=5)
        self.renderAllFilesBtn = tk.Checkbutton(navFrame, text="Render all Files",variable=self.isAllFiles,command=self.fileSwitch,selectcolor= Colors.widget,activebackground=Colors.widget,bg=Colors.widget,fg=Colors.fontColor)
        self.renderAllFilesBtn.pack(side=tk.LEFT,padx=10,pady=5)
    #Bottom
        footerFrame = tk.Frame(self.root,bg=Colors.header,height=80)
        footerFrame.pack(side=tk.BOTTOM,fill=tk.BOTH)
        self.versionLabel = tk.Label(footerFrame, text='Version: 0.01')
        self.versionLabel.pack(side=tk.LEFT,anchor=tk.S)
        self.renderButton = tk.Button(footerFrame, text="Start Render",command=lambda: self.start_blender_thread(None),height=2,bg='GREEN') 
        self.renderButton.pack(side=tk.RIGHT)
        self.cancleRender = tk.Button(footerFrame, text="Stop Render",command=self.stopRender,height=2,bg=Colors.red)
        self.cancleRender.pack(side=tk.RIGHT)
        
        self.statusLabel = tk.Label(footerFrame, text='Status: Ready')
        self.statusLabel.pack(side=tk.RIGHT,padx=(4,10))
        
        self.currentJobLabel = tk.Label(footerFrame, text='Current File: ')
        self.currentJobLabel.pack(side=tk.RIGHT)

        

        


    #Content Grid        padx = 10 pady= 20
        addButton = tk.Button(self.root,text='Add',command=self.newJob,bg=Colors.background, fg = Colors.fontColor)
        addButton.pack(side=tk.BOTTOM,fill=tk.X)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)  
        self.scrollbar.config(orient=tk.VERTICAL, command=self.canvas.yview)      
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvasFrame=self.canvas.create_window((0,0), window=self.contentFrame, anchor=tk.E)
        self.canvas.pack(fill=tk.Y, side=tk.TOP, expand=tk.TRUE)
        
        
        

        self.root.bind("<MouseWheel>", self._on_mousewheel)
        



        self.root.drop_target_register(DND_FILES)  
        self.root.dnd_bind("<<Drop>>",self.dropEvent) 

        checkOS(self.root)
    
    def stopCurrentJob(self):
        #os.killpg(os.getpgid(self.cmd.pid), signal.SIGTERM)
        #os.kill(self.cmd.pid, signal.CTRL_C_EVENT)
        subprocess.call(['taskkill', '/F', '/T', '/PID',  str(self.cmd.pid)])
    
    def stopRender(self):
        answer = askyesno(title='confirmation',
                    message='Are you sure that you want to stop all rendering jobs?')
        if answer:
            self.stopCurrentJob()
            self.stopRenderFlag = True
        
    
    def fileSwitch(self):
        if self.isAllFiles.get():
            for e in self.entries:
                e.isActiveBtn.config(state='disabled')
        else:
            for e in self.entries:
                e.isActiveBtn.config(state='active')
                #e.isActiveBtn.config(fg=Colors.fontColor)
    
    def updateCanvas(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def dropEvent(self,event):
        self.addJob(event.data)

    def addJob(self,path):
        job = createJob(path,self.root)
        if not job:
            return
        job.scenes[0].isActiv = True
        if self.settings.defaultBlenderVersion:
            job.blender = self.settings.defaultBlenderVersion
        self.jobs.append(job)
        entryWidget = Entry(self,job)
        entryWidget.pack()
        
        self.entries.append(entryWidget)
        self.contentFrame.update()

        self.updateCanvas()
        print(self.contentFrame.winfo_y())

    def export(self):
        exportJob(self.jobs)
        exportPath = os.path.abspath("export.json")
        scriptPath = os.path.abspath("bpyScript.py")
        for e in self.entries:
            job = e.Job
            if self.isAllFiles.get() or e.isChecked.get():
                e.setRendering(True)
                self.openBlender(job,exportPath,scriptPath)
            e.setRendering(False)
            if self.stopRenderFlag:
                break
        self.stopRenderFlag = False
        self.currentJobLabel.config(text=f'Current Job:')
        self.statusLabel.config(text='Status: Ready')

    def openBlender(self,job,exportPath,scriptPath):
        self.currentJobLabel.config(text=f'Current Job: {job.path}')
        self.statusLabel.config(text='Status: Rendering')
        '''https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true'''
        self.cmd = subprocess.Popen(f'blender.exe {job.path} --background --python {scriptPath} {exportPath}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=job.blender.path.replace('blender.exe',''), shell=True)
        out, err = self.cmd.communicate()
        #print (out)

    def closeWindowEvent(self):
        if self.entries:
            answer = askyesno(title='confirmation',
                    message='Are you sure that you want to quit?\nChanges wil be discarded, current render jobs will be cancelled')
            if answer:
                self.root.destroy()
                return 
            self.root.focus_force()
        else:
            self.root.destroy()

    def start_blender_thread(self,event):
        global blender_thread
        blender_thread = threading.Thread(target=self.export)
        blender_thread.daemon = True
        blender_thread.start()

    def check_blender_thread(self):
        if self.blender_thread.is_alive():
            pass
 
    def newJob(self):
        filename = fd.askopenfilename(filetypes=(("blend files", "*.blend"),("all","*")))
        self.addJob(filename)

    def updateBlenderVersions(self):
        for e in self.entries:
            e.blendOptionMenu.children['menu'].delete(0,'end')
            for blend in self.settings.blenderVersions:
                e.blendOptionMenu.children['menu'].add_command(label=blend,command=tk._setit(e.blendVersionVar, blend))
        
    def openSettings(self):
        a=self.BlenderVersionSettings(self,self.settings)

    def resize_frame(self, event):
        canvas_width = event.width
        #self.canvas.itemconfig(self.canvasFrame, width = canvas_width)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def moveEntryUp(self,entry):
        index = self.entries.index(entry)
        if index == 0:
            return
        self.entries[index],self.entries[index-1] = self.entries[index-1], self.entries[index]
        self.refreshEntries()
        
    def moveEntryDown(self,entry):
        index = self.entries.index(entry)
        if index == len(self.entries)-1:
            return
        self.entries[index],self.entries[index+1] = self.entries[index+1], self.entries[index]
        self.refreshEntries()

    def refreshEntries(self):
        for e in self.entries:
            e.root.forget()
            e.pack()
        
    def removeEntry(self,entry):
        print(type(entry))
        self.entries.pop(self.entries.index(entry))
        self.jobs.pop(self.jobs.index(entry.Job))

    def _on_mousewheel(self, event):
        MainGUI.mouseWheelEvent(self.canvas,event)
    
    def mainloop(self):
        self.root.mainloop()
        

#./blender --background --python test.py

if __name__ == '__main__':
    g = MainGUI()
    g.mainloop()