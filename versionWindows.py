import tkinter as tk
import os
from utils import Colors
from tkinter import filedialog as fd
from tkinterdnd2 import DND_FILES, TkinterDnD
from model import Blender
from tkinter.messagebox import askyesno
from utils import writeToVersionJSON,writeToSettingsJSON
#Exception wenn Entrys leer sind
class AddBlenderVersionWindow:
    def __init__(self,master,parent,settings,path=''):
        self.parent = parent
        self.master = master
        self.settings = settings
        self.window = tk.Toplevel(self.master,bg=Colors.background)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.iconbitmap(r"img\icon.ico")
        self.blendPath = path if path else''
        self.nameVar = tk.StringVar()
        self.versionVar = tk.StringVar()

        

        self.contentFrame = tk.Frame(self.window,bg=Colors.background)
        self.contentFrame.grid_columnconfigure(0, weight=1)
        self.contentFrame.grid_columnconfigure(1, weight=1)
        self.contentFrame.grid_columnconfigure(2, weight=1)
        self.contentFrame.grid_columnconfigure(3, weight=1)
        self.contentFrame.grid_rowconfigure(1, weight=1)
        self.nameLabel = tk.Label(self.contentFrame,text='Name: ',bg=Colors.background, fg = Colors.fontColor)
        self.nameEntry = tk.Entry(self.contentFrame,textvariable=self.nameVar,bg=Colors.background, fg = Colors.fontColor,insertbackground=Colors.fontColor)
        self.versionLabel = tk.Label(self.contentFrame,text='Version: ',bg=Colors.background, fg = Colors.fontColor)
        self.versionEntry = tk.Entry(self.contentFrame,textvariable=self.versionVar,bg=Colors.background, fg = Colors.fontColor,insertbackground=Colors.fontColor)
        self.pathButton = tk.Button(self.contentFrame,text=self.blendPath if self.blendPath else 'Select Blender path', command=lambda : self.browseBlenderPath(),
            bg=Colors.background, fg = Colors.fontColor )
        self.saveButton = tk.Button(self.window,text='Save',command=lambda : self.save(),
            bg=Colors.background, fg = Colors.fontColor )

        self.nameLabel.grid(row=0, column=0,sticky='E')
        self.nameEntry.grid(row=0, column=1,padx=(0,5),sticky='WE')
        self.versionLabel.grid(row=0, column=2,sticky='E')
        self.versionEntry.grid(row=0, column=3,sticky='WE')
        self.pathButton.grid(row=1,column=0,columnspan=4,pady=10,sticky='NWE')
        #self.saveButton.grid(row=2, column=1,columnspan=2,sticky='NWE')
        self.contentFrame.pack(side=tk.TOP, fill=tk.BOTH,padx=5,pady=(17,5))
        self.saveButton.pack(side=tk.TOP,pady=(0,15))

    def confirm(self):
        answer = askyesno(title='confirmation',
                    message='Are you sure that you want to quit?\nChanges wil be discarded')
        if answer:
            self.window.destroy()
            return 
        self.window.focus_force()

    def on_closing(self):
        self.confirm()

    def formatPathString(self):
        if len(self.blendPath) > 20:
            return self.blendPath[:20] + '...'
        else:
            return self.blendPath

    def browseBlenderPath(self):
        self.blendPath = fd.askopenfilename(filetypes=(("Blender.exe", "blender.exe"),("all","*")))
        self.master.focus_force()
        self.window.focus_force()
        if self.blendPath:
            self.pathButton.configure(text=self.blendPath)     

    def save(self):
        if self.nameVar.get() and self.versionVar.get() and self.blendPath:
            blender = Blender(self.nameVar.get(),self.versionVar.get(),self.blendPath)
            self.settings.blenderVersions.append(blender)
            self.parent.addBlenderVersion(blender)
            self.window.destroy()

#Exception wenn Entrys leer sind
class UpdateBlenderVersionWindow(AddBlenderVersionWindow):
    def __init__(self, master ,parent, settings):
        #parent = BlenderVersionSettings Class
        super().__init__(master,parent, settings)
        self.oldName = self.parent.blendVersion.name
        self.nameVar.set(self.oldName)
        self.versionVar.set(self.parent.blendVersion.version)
        self.blendPath = self.parent.blendVersion.path
        self.pathButton.config(text=self.parent.blendVersion.path)

    def save(self):
        if self.nameVar.get() and self.versionVar.get() and self.blendPath:
            self.parent.blendVersion.name = self.nameVar.get()
            self.parent.blendVersion.version = self.versionVar.get()
            self.parent.blendVersion.path = self.blendPath
            self.updateMainBlenderList()
            self.parent.name.config(text=f'Name: {self.parent.blendVersion.name}')
            self.parent.version.config(text=f'Version: {self.parent.blendVersion.version}')
            self.parent.path.config(text=f'Path: {self.parent.formatPathString()}')
            self.window.destroy()

    def updateMainBlenderList(self):
        main = self.parent.parent.parent
        for e in main.entries:
            if e.blendVersionVar.get() == self.oldName:
                e.blendVersionVar.set(self.nameVar.get())

class BlendVersionWidget:
    #parent: BlenderVersionSettings
    def __init__(self,parent,blendVersion):
        self.parent = parent
        self.master = self.parent.contentFrame
        self.blendVersion = blendVersion
        self.isDefault = tk.IntVar(value=self.checkForDefaultVersion())
        self.frame = tk.Frame(self.master,bg=Colors.widget,highlightthickness=1)
        self.deltePNG = tk.PhotoImage(file=r'img\delete-x.png')
        self.delteButton = tk.Button(self.frame,image=self.deltePNG,bg=Colors.background, fg = Colors.fontColor,command=lambda: self.parent.deleteWidgets(self))
        self.delteButton.pack(side=tk.RIGHT,anchor=tk.NE,padx=2,pady=(3,0))
        self.settingsPNG = tk.PhotoImage(file=r'img\gear0.5x.png')
        self.updateButton = tk.Button(self.frame,bg=Colors.background,image=self.settingsPNG,command= lambda: self.update())
        
        self.updateButton.pack(side=tk.RIGHT,anchor=tk.NE,padx=(5,2),pady=(3,0))
        self.name = tk.Label(self.frame,fg=Colors.fontColor,bg=Colors.widget,text=f'Name: {blendVersion.name}')
        self.name.pack(side=tk.TOP,anchor=tk.SW)
        
        self.version = tk.Label(self.frame,fg=Colors.fontColor,bg=Colors.widget,text=f'Version: {blendVersion.version}')
        self.version.pack(side=tk.TOP,anchor=tk.SW)
        self.path = tk.Label(self.frame,fg=Colors.fontColor,bg=Colors.widget,text=f'Path: {self.formatPathString()}')
        self.path.pack(side=tk.TOP,anchor=tk.SW)
        tk.Label(self.frame,text='Default Version',bg=Colors.widget,fg=Colors.fontColor).pack(side=tk.LEFT,anchor=tk.SW)
        self.isDefaultButton = tk.Checkbutton(self.frame,bg=Colors.widget,fg=Colors.fontColor,selectcolor= Colors.widget,activebackground=Colors.widget,
            command=self.makeDefault,variable=self.isDefault)
        self.isDefaultButton.pack(side=tk.TOP,anchor=tk.SW)
        
    def update(self):
        UpdateBlenderVersionWindow(self.master,self,self.parent.settings)

    def checkForDefaultVersion(self):
        return self.parent.settings.defaultBlenderVersion == self.blendVersion
        


    def makeDefault(self):
        if not self.parent.settings.defaultBlenderVersion:
            self.parent.settings.defaultBlenderVersion = self.blendVersion
        else:
            for w in self.parent.blendWidgets:
                if w is not self:
                    w.isDefault.set(False)
                    w.isDefaultButton.config()
            self.parent.settings.defaultBlenderVersion = self.blendVersion
        

    def formatPathString(self):
        if len(self.blendVersion.path) > 20:
            return self.blendVersion.path[:20] + '...'
        else:
            return self.blendVersion.path


    def packWidget(self,i):
        self.frame.grid(row=i//3,column=i%3,padx=5,pady=5,sticky=tk.SW)

class BlenderVersionSettings:
    #parent: maingui
    def __init__(self,parent,settings):
        self.parent = parent
        self.master = self.parent.root
        self.settings = settings
        self.blendVersions = self.settings.blenderVersions
        self.blendWidgets = []
        # #Test
        # if len(self.blendVersions) == 0:
        #     self.test()
        # #End Test
        self.window = tk.Toplevel(self.master,bg=Colors.background)
        self.window.iconbitmap(r"img\icon.ico")
        self.window.geometry('400x400')
        self.window.protocol("WM_DELETE_WINDOW", self.closeEvent)
        self.head = tk.Frame(self.window,bg=Colors.header,height=40)
        self.head.pack(side=tk.TOP,fill=tk.X)
        self.AddVersionButton = tk.Button(self.head,text='Add new Blender',height=1,bg=Colors.background, fg = Colors.fontColor,command=lambda: AddBlenderVersionWindow(self.window,self,settings))
        self.AddVersionButton.pack(side=tk.LEFT,pady=5,padx=5)
        self.contentFrame = tk.Frame(self.window,bg=Colors.background)
        self.contentFrame.pack(side=tk.TOP,fill=tk.BOTH)
        self.footerFrame = tk.Frame(self.window,bg=Colors.background)
        self.footerFrame.pack(side=tk.BOTTOM,fill=tk.BOTH)
        self.saveButton = tk.Button(self.footerFrame,text='Ok',height=1,width=7,command=lambda: self.closeEvent(),bg=Colors.background, fg = Colors.fontColor)
        self.saveButton.pack(side=tk.RIGHT,pady=5,padx=5)
        self.window.drop_target_register(DND_FILES)  
        self.window.dnd_bind("<<Drop>>",self.dropEvent) 
        self.drawWidgets()
    
    def dropEvent(self,event):
        AddBlenderVersionWindow(self.window,self,self.settings,path=event.data)
    
    def drawWidgets(self):
        for i, b in enumerate(self.blendVersions):
            a=BlendVersionWidget(self,b)
            a.packWidget(i)
            self.blendWidgets.append(a)
    
    def deleteWidgets(self,widget):
        self.deleteAllWidgets()

        self.blendVersions.remove(widget.blendVersion)
        self.drawWidgets()
        

    def deleteAllWidgets(self):
        for elm in self.blendWidgets:
            elm.frame.destroy()
    

    
    def addBlenderVersion2(self,name,version,path):
        blend = Blender(name,version,path)
        self.settings.blenderVersions.append(blend)
    
    def addBlenderVersion(self,blenderVersion):
        a=BlendVersionWidget(self,blenderVersion)
        a.packWidget(len(self.blendVersions)-1)
        self.blendWidgets.append(a)

    def closeEvent(self,):
        self.parent.updateBlenderVersions()
        writeToVersionJSON(self.settings.blenderVersions)
        writeToSettingsJSON(self.settings)
        self.window.destroy()

    def browseOutPutpath(self):
        self.outputPath.set(fd.askdirectory(parent=self.renderSettingsFrame, initialdir=self.outputPath.get(), title='Please select a output path'))   