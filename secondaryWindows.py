import tkinter as tk
from tkinter import Scrollbar
from tkinter.messagebox import askyesno
import os
import copy
import abc
from model import RenderEngine
from utils import Colors
from utils import checkIsDigitInput,convertEnumToStr,convertStrToEnum
from tkinter import filedialog as fd
from exceptionWindows import ExceptionWindow
from dragndrop_frame import DragDropFrame

currentCopiedSettings = None

class SecondaryWindow:
    def __init__(self,master,do_pack=True):
        self.master = master
        self.window = tk.Toplevel(self.master,bg=Colors.widget)
        self.contentFrame = tk.Frame(self.window,bg=Colors.widget)
        #self.headerFrame = tk.Frame(self.window,bg=Colors.header,height=40)
        self.footerFrame  = tk.Frame(self.window,bg=Colors.header,height=40)
        
        self.footerSeperator= tk.ttk.Separator(self.footerFrame, orient=tk.HORIZONTAL)
        self.saveBtn = tk.Button(self.footerFrame,bg=Colors.background,fg=Colors.fontColor,width=7,text='Save',command=lambda: self.save(),height=1)
        
        if do_pack:
            self.pack()
        
    
    
    def pack(self):
        self.footerSeperator.pack(side=tk.TOP,fill=tk.X)
        self.saveBtn.pack(side=tk.RIGHT,anchor=tk.SE)
        #self.headerFrame.pack(side=tk.TOP,fill=tk.X)
        self.contentFrame.pack(side=tk.TOP,fill=tk.X)
        self.footerFrame.pack(side=tk.BOTTOM,fill=tk.X)
    
    @abc.abstractmethod
    def save(self):pass
    
    def closeWindowEvent(self):
        answer = askyesno(title='confirmation',
                message='Are you sure that you want to quit?\nChanges wil be discarded')
        if answer:
            self.destroy()
            return 
        self.window.focus_force()
    
    def destroy(self):
        self.window.destroy()

class ColorManagementSettings(SecondaryWindow):
    def __init__(self,settingsWindow) :
        self.settingsWindow = settingsWindow
        self.scene = settingsWindow.scene
        self.rSettings = self.scene.rSettings
        self.colorSettings = self.rSettings.colorSettings
        self.master = self.settingsWindow.window
        super().__init__(self.master)
        self.window.title(self.scene.name + ' - Color Management')
        self.window.iconbitmap(r"img\icon.ico")
        self.window.geometry('400x250')
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindowEvent)
        tk.Grid.columnconfigure(self.contentFrame,1,weight=1)

        self.view_transformVar = tk.StringVar(value=self.colorSettings.view_transform)
        self.lookVar = tk.StringVar(value=self.colorSettings.look)
        self.exposureVar = tk.DoubleVar(value=self.colorSettings.exposure)
        self.gammaVar = tk.DoubleVar(value=self.colorSettings.gamma)

        
        tk.Label(self.contentFrame,text='View Transform: ',bg=Colors.widget,fg=Colors.fontColor).grid(column=0,row=2,sticky=tk.W,padx=(2,5),pady=3)
        tk.Label(self.contentFrame,text='Look: ',bg=Colors.widget,fg=Colors.fontColor).grid(column=0,row=3,sticky=tk.W,padx=(2,5),pady=3)
        tk.Label(self.contentFrame,text='Exposure: ',bg=Colors.widget,fg=Colors.fontColor).grid(column=0,row=4,sticky=tk.W,padx=(2,5),pady=3)
        tk.Label(self.contentFrame,text='Gamma: ',bg=Colors.widget,fg=Colors.fontColor).grid(column=0,row=5,sticky=tk.W,padx=(2,5),pady=3)
        tk.Label(self.contentFrame,text='Color Settings: ',bg=Colors.widget,fg=Colors.fontColor).grid(column=0,row=0,pady=(8,4))
        tk.ttk.Separator(self.contentFrame, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=2, sticky='WE',pady=(0,5))
        self.view_tranfsformBtn = tk.OptionMenu(self.contentFrame,self.view_transformVar,*['Standard','Filmic Log','Filmic', 'Raw','False Color']) 
        self.view_tranfsformBtn.grid(column=1,row=2,sticky=tk.E,pady=3,padx=5)
        self.view_tranfsformBtn.config(bg=Colors.widget,fg=Colors.fontColor,highlightthickness=0)
        self.lookBtn = tk.OptionMenu(self.contentFrame,self.lookVar,*['None','Low Contrast','Medium Low Contrast', 'Medium Contrast','Medium High Contrast','High Contrast','Very High Contrast']) 
        self.lookBtn.grid(column=1,row=3,sticky=tk.E,pady=3,padx=5)
        self.lookBtn.config(bg=Colors.widget,fg=Colors.fontColor,highlightthickness=0)
        self.exposureScale = tk.Scale(self.contentFrame,from_=-10,to=10,variable=self.exposureVar,orient=tk.HORIZONTAL,digits=4,resolution=0.01,bg=Colors.widget,fg=Colors.fontColor,troughcolor=Colors.background,highlightthickness=0)
        self.exposureScale.grid(column=1,row=4,sticky=tk.E,pady=3,padx=5)
        self.gammaScale = tk.Scale(self.contentFrame,from_=0,to=5,orient=tk.HORIZONTAL,digits=3,resolution=0.01,bg=Colors.widget,fg=Colors.fontColor,troughcolor=Colors.background,highlightthickness=0)
        self.gammaScale.grid(column=1,row=5,sticky=tk.E,pady=3,padx=5)


    def save(self):
        self.colorSettings.view_transform = self.view_transformVar.get()
        self.colorSettings.look = self.lookVar.get()
        self.colorSettings.exposure = self.exposureVar.get()
        self.colorSettings.gamma = self.gammaVar.get()
        self.destroy()

    def destroy(self):
        self.settingsWindow.window.focus_force()
        self.window.destroy()

class RenderSettings(SecondaryWindow):
    def __init__(self,sceneWidget):
        self.sceneWidget = sceneWidget
        self.jobWindow = self.sceneWidget.parent.window
        super().__init__(self.jobWindow,False)
        self.window.title(sceneWidget.scene.name+' - Render Settings')
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindowEvent)
        self.window.iconbitmap(r"img\icon.ico")
        self.vald = self.sceneWidget.vald
        
        self.scene = sceneWidget.scene
        self.outputPath = tk.StringVar(value=self.scene.rSettings.outputPath)
        #self.outputFormat = tk.StringVar(value=self.scene.rSettings.output)
        self.sceneEngine = tk.StringVar(value=convertEnumToStr(self.scene.rSettings.engine))
        self.sceneStart = tk.IntVar(value=self.scene.rSettings.startFrame)
        self.sceneEnd = tk.IntVar(value=self.scene.rSettings.endFrame)
        self.sceneFPS = tk.IntVar(value=self.scene.rSettings.fps)
        self.sceneX = tk.IntVar(value=self.scene.rSettings.x)
        self.sceneY = tk.IntVar(value=self.scene.rSettings.y)
        self.sceneSize = tk.IntVar(value=self.scene.rSettings.size)
        
        self.sceneHeaderFrame = tk.Frame(self.window,bg=Colors.widget)
        tk.Grid.columnconfigure(self.sceneHeaderFrame,1,weight=1)
        tk.Grid.rowconfigure(self.sceneHeaderFrame,0,weight=1)
        tk.Grid.columnconfigure(self.contentFrame,4,weight=1)
        tk.Grid.rowconfigure(self.contentFrame,0,weight=1)


        tk.Label(self.sceneHeaderFrame,text='Scene Settings: ',bg=Colors.widget,fg=Colors.fontColor).grid(row=1,column=0,sticky='W',pady=5)
        tk.ttk.Separator(self.sceneHeaderFrame, orient=tk.HORIZONTAL).grid(column=0, row=2, columnspan=3, sticky='WE',pady=(0,5))

        #           ---Render Settings--
        tk.Label(self.contentFrame,text='Output Path',bg=Colors.widget,fg=Colors.fontColor).grid(row=0,column=0,sticky='W',padx=(0,1))
        tk.Label(self.contentFrame,text='Color Management',bg=Colors.widget,fg=Colors.fontColor).grid(row=1,column=0,sticky='W',padx=(0,1))
        tk.Label(self.contentFrame,text='Output Engine',bg=Colors.widget,fg=Colors.fontColor).grid(row=2,column=0,sticky='W',padx=(0,1))

        
        self.sceneOutputButton = tk.Button(self.contentFrame,text=self.outputPath.get(),command=lambda: self.browseOutPutpath(),background=Colors.widget,fg=Colors.fontColor)
        self.sceneOutputButton.grid(row=0,column=1,padx=7,sticky='W')
        self.colorManagementBtn = tk.Button(self.contentFrame,text='Open Color Settings',command=lambda: self.openColorSettings(),bg=Colors.background,fg=Colors.fontColor) 
        self.colorManagementBtn.grid(row=1,column=1,sticky='W',padx=7)
        self.sceneEngineButton = tk.OptionMenu(self.contentFrame,self.sceneEngine,*[convertEnumToStr(e) for e in RenderEngine]) 
        self.sceneEngineButton.grid(row=2,column=1, sticky='W',padx=7)
        self.sceneEngineButton.config(bg=Colors.widget,fg=Colors.fontColor,highlightthickness=0)
        
        tk.Label(self.contentFrame,text='Start Frame',bg=Colors.widget,fg=Colors.fontColor).grid(row=0,column=2,sticky='E',padx=(70,1))
        tk.Label(self.contentFrame,text='End Frame',bg=Colors.widget,fg=Colors.fontColor).grid(row=1,column=2,sticky='E',padx=(70,1))
        tk.Label(self.contentFrame,text='FPS',bg=Colors.widget,fg=Colors.fontColor).grid(row=2,column=2,sticky='E',padx=(70,1))
        self.sceneStartButton = tk.Entry(self.contentFrame,textvariable=self.sceneStart,background=Colors.widget,fg=Colors.fontColor) 
        self.sceneStartButton.grid(row=0,column=3, sticky='W',padx=7)
        self.sceneEndButton = tk.Entry(self.contentFrame,textvariable=self.sceneEnd,background=Colors.widget,fg=Colors.fontColor) 
        self.sceneEndButton.grid(row=1,column=3,padx=7)
        self.sceneFPSButton = tk.Entry(self.contentFrame,textvariable=self.sceneFPS,background=Colors.widget,fg=Colors.fontColor)
        self.sceneFPSButton.grid(row=2,column=3, sticky='E',padx=7)
        
        tk.Label(self.contentFrame,text='X Size',bg=Colors.widget,fg=Colors.fontColor).grid(row=0,column=4,sticky='E',padx=(70,1))
        tk.Label(self.contentFrame,text='Y Size',bg=Colors.widget,fg=Colors.fontColor).grid(row=1,column=4,sticky='E',padx=(70,1))
        tk.Label(self.contentFrame,text='Size',bg=Colors.widget,fg=Colors.fontColor).grid(row=2,column=4,sticky='E',padx=(70,1))
        self.sceneXButton = tk.Entry(self.contentFrame,textvariable=self.sceneX,background=Colors.widget,fg=Colors.fontColor) 
        self.sceneXButton.grid(row=0,column=5,padx=7)
        self.sceneYButton = tk.Entry(self.contentFrame,textvariable=self.sceneY,background=Colors.widget,fg=Colors.fontColor) 
        self.sceneYButton.grid(row=1,column=5,padx=7)
        self.sceneSizeButton = tk.Entry(self.contentFrame,textvariable=self.sceneSize,background=Colors.widget,fg=Colors.fontColor) 
        self.sceneSizeButton.grid(row=2,column=5,padx=7)

        self.createValidator()
        self.sceneHeaderFrame.pack(side=tk.TOP,fill=tk.X,pady=10)
        super().pack()

    def openColorSettings(self):
        a = ColorManagementSettings(self)
       
    def save(self):
        self.scene.rSettings.outputPath = self.outputPath.get()
        #self.scene.rSettings.output = self.outputFormat.get()
        self.scene.rSettings.engine = convertStrToEnum(self.sceneEngine.get())
        self.scene.rSettings.startFrame = self.sceneStart.get()
        self.scene.rSettings.endFrame = self.sceneEnd.get()
        self.scene.rSettings.fps = self.sceneFPS.get()
        self.scene.rSettings.x = self.sceneX.get()
        self.scene.rSettings.y = self.sceneY.get()
        self.scene.rSettings.size = self.sceneSize.get()

        self.destroy()
        
    def destroy(self):
        self.jobWindow.focus_force()
        self.window.destroy()

    def browseOutPutpath(self):
        self.outputPath.set(fd.askdirectory(parent=self.contentFrame, initialdir=self.outputPath.get(), title='Please select a output path'))
        self.sceneOutputButton.config(text=self.outputPath.get())

    def createValidator(self):
        self.sceneStartButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneEndButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneFPSButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneYButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneXButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneSizeButton.config(validate='key',validatecommand=(self.vald,'%P'))

class CameraWidget:
    def __init__(self,sceneWidget,cam_name):
        self.sceneWidget = sceneWidget
        self.master = self.sceneWidget.cameraSettingsFrame
        self.cam_name = cam_name
        self.root = DragDropFrame(self.master,self.sceneWidget.cameraWidgets, highlight_thickness=2, highlight_color=Colors.accent,offset=5,ispropagte=False,drag_dir='X',bg=Colors.widget2,height=30,width=30,padx=5)
        self.camVar = tk.BooleanVar()
        self.cam_btn  =tk.Checkbutton(self.root,activeforeground=Colors.fontColor ,bg=Colors.widget2,fg=Colors.fontColor,selectcolor= Colors.widget2,activebackground=Colors.widget2,
                variable=self.camVar)
        self.cam_label = tk.Label(self.root,text=self.cam_name,bg=Colors.widget2,fg=Colors.fontColor)
        self.cam_label.pack(side=tk.LEFT,padx=(0,5))
        self.cam_btn.pack(side=tk.LEFT)
        if self.cam_name in self.sceneWidget.scene.aCamera:
                self.cam_btn.select()

        self.root.bind_childs([self.cam_label]) 
    def pack(self):
        self.root.do_pack(side=tk.LEFT,padx=(10,5))

class SceneWidget:
    def __init__(self,JobAdvancedSettings,scene):
        self.parent = JobAdvancedSettings
        self.scene = scene
        self.vald = self.parent.contentFrame.register(checkIsDigitInput)
        self.renderSettingsWindow = None

        self.isActiv = tk.IntVar(value=scene.isActiv)
        self.isCamBurst = tk.IntVar(value=scene.rSettings.isCamBurst)
        self.isCamOwnFolder = tk.IntVar(value=scene.rSettings.isCamOwnFolder)
        self.activCamVarList = []
        self.cameraWidgets = [] #cam btns
        self.outputPath = tk.StringVar(value=scene.rSettings.outputPath)
        #self.outputFormat = tk.StringVar(value=scene.rSettings.output)
        self.sceneEngine = tk.StringVar(value=scene.rSettings.engine)
        self.sceneStart = tk.IntVar(value=scene.rSettings.startFrame)
        self.sceneEnd = tk.IntVar(value=scene.rSettings.endFrame)
        self.sceneFPS = tk.IntVar(value=scene.rSettings.fps)
        self.sceneX = tk.IntVar(value=scene.rSettings.x)
        self.sceneY = tk.IntVar(value=scene.rSettings.y)
        self.sceneSize = tk.IntVar(value=scene.rSettings.size)
        
        
 
        self.root = DragDropFrame(self.parent.contentFrame,self.parent.sceneWidgets,highlight_thickness=2, highlight_color=Colors.accent,offset=4,ispropagte=False,bg=Colors.widget,pady=5,padx=8)
        self.sceneHeaderFrame = tk.Frame(self.root,bg=Colors.widget)
        self.sceneContentFrame = tk.Frame(self.root,bg=Colors.widget)
        self.renderSettingsFrame = tk.Frame(self.sceneContentFrame,bg=Colors.widget)
        self.cameraSettingsFrame =tk.Frame(self.sceneContentFrame,bg=Colors.widget)



        tk.Grid.columnconfigure(self.sceneHeaderFrame,1,weight=1)
        tk.Grid.rowconfigure(self.sceneHeaderFrame,0,weight=1)
        tk.Grid.columnconfigure(self.sceneContentFrame,2,weight=1)
        tk.Grid.rowconfigure(self.sceneContentFrame,0,weight=1)
        tk.Grid.columnconfigure(self.renderSettingsFrame,4,weight=1)
        tk.Grid.rowconfigure(self.renderSettingsFrame,0,weight=1)

        self.name = tk.Label(self.sceneHeaderFrame,text=f'Scene Name: {scene.name}',bg=Colors.widget,fg=Colors.fontColor).grid(row=0,column=0,sticky='W')
        self.isActivButton = tk.Checkbutton(self.sceneHeaderFrame,text='Active Scene',variable=self.isActiv,
            selectcolor= Colors.widget,activebackground=Colors.widget,bg=Colors.widget,fg=Colors.fontColor)
        self.isActivButton.grid(row=0,column=1,sticky='E',padx=5)
        self.camBurstButton = tk.Checkbutton(self.sceneHeaderFrame,text='Render all cameras',variable=self.isCamBurst,command=self.camButtonsSwitch,
            selectcolor= Colors.widget,activebackground=Colors.widget,bg=Colors.widget,fg=Colors.fontColor)
        self.camFolderButton = tk.Checkbutton(self.sceneHeaderFrame,text='Save Camera in separate Folder',variable=self.isCamOwnFolder,selectcolor= Colors.widget,activebackground=Colors.widget,bg=Colors.widget,fg=Colors.fontColor)    
        self.camBurstButton.grid(row=0,column=2,sticky='E',padx=5)
        self.camFolderButton.grid(row=0,column=3,sticky='E',padx=5)

        
        
        self.renderSettingsBtn = tk.Button(self.renderSettingsFrame,text="Settings",command=self.openRsettings,bg=Colors.background, fg = Colors.fontColor)
        self.renderSettingsBtn.pack(side=tk.LEFT)
        self.copyPNG = tk.PhotoImage(file=r'img\copy.png')
        self.copyBtn = tk.Button(self.renderSettingsFrame,image=self.copyPNG,bg=Colors.background,command=lambda:self.copySettings())
        self.copyBtn.pack(side=tk.LEFT,padx=(4,0))
        self.pastePNG = tk.PhotoImage(file=r'img\paste.png')
        self.pasteBtn = tk.Button(self.renderSettingsFrame,image=self.pastePNG,bg=Colors.background,command=lambda:self.pasteSettings())
        self.pasteBtn.pack(side=tk.LEFT)

        self.folderPNG = tk.PhotoImage(file=r'img\folder.png')
        self.openPathBtn = tk.Button(self.renderSettingsFrame,image=self.folderPNG,bg=Colors.background,command=lambda:self.openPath())
        self.openPathBtn.pack(side=tk.LEFT,padx=4)
        
        #           ---Camera Settings---
        tk.Label(self.cameraSettingsFrame,text='Cameras: ',bg=Colors.widget,fg=Colors.fontColor).pack(side=tk.TOP,anchor='nw',pady=5)
        tk.ttk.Separator(self.cameraSettingsFrame, orient=tk.HORIZONTAL).pack(side=tk.TOP,fill=tk.X,pady=(2,7))


        for cam in self.scene.cameras:
            a = CameraWidget(self,cam)
            self.cameraWidgets.append(a)
            a.pack()
            self.activCamVarList.append(a.camVar)
        

        self.renderSettingsFrame.pack(side=tk.TOP,fill=tk.X)
        self.cameraSettingsFrame.pack(side=tk.TOP,fill=tk.X,pady=15)
        self.sceneHeaderFrame.pack(side=tk.TOP,fill=tk.X)
        self.sceneContentFrame.pack(side=tk.TOP,fill=tk.X)
        
        self.root.bind_childs([self.sceneHeaderFrame,self.renderSettingsFrame,self.sceneContentFrame,self.cameraSettingsFrame])

    def pack(self):
        self.root.do_pack(fill=tk.X,pady=20)

    def copySettings(self):
        global currentCopiedSettings
        currentCopiedSettings = copy.deepcopy(self.scene.rSettings) 

    def pasteSettings(self):
        global currentCopiedSettings
        self.scene.rSettings = currentCopiedSettings
    
    def openPath(self):
        '''ONLY FOR WINDOWS'''
        path = self.scene.rSettings.outputPath
        os.startfile(path)
    
    def camButtonsSwitch(self):
        if self.isCamBurst.get():
            for w in self.cameraWidgets:
                w.cam_btn.config(state='disabled')
        else:
            for w in self.cameraWidgets:
                w.cam_btn.config(state='active')

    def openRsettings(self):
        self.renderSettingsWindow = RenderSettings(self)

    def browseOutPutpath(self):
        self.outputPath.set(fd.askdirectory(parent=self.renderSettingsFrame, initialdir=self.outputPath.get(), title='Please select a output path'))
        self.sceneOutputButton.config(text=self.outputPath.get())

    def createValidator(self):
        self.sceneStartButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneEndButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneFPSButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneYButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneXButton.config(validate='key',validatecommand=(self.vald,'%P'))
        self.sceneSizeButton.config(validate='key',validatecommand=(self.vald,'%P'))

    def safe(self):
        print(self.scene.cameras)
        self.scene.aCamera.clear()
        self.scene.cameras.clear()
        for w in (self.cameraWidgets):
            self.scene.cameras.append(w.cam_name)
            if w.camVar.get():
                self.scene.aCamera.append(w.cam_name)
        self.scene.isActiv = self.isActiv.get()

class JobAdvancedSettings:
    def __init__(self,parent):
        self.parent = parent
        self.master = parent.root
        self.Job = parent.Job
        self.settings = parent.settings
        self.window = tk.Toplevel(self.master,bg=Colors.background)
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindowEvent)
        self.window.iconbitmap(r"img\icon.ico")
        self.window.geometry('900x500')
        self.window.title(self.Job.path)
        self.sceneWidgets = []
        self.main = tk.Frame(self.window)
        self.head = tk.Frame(self.window,bg=Colors.header,height=40)
        self.head.pack(side=tk.TOP,fill=tk.X)
        self.canvas = tk.Canvas(self.main, background=Colors.background,width=900,height=300,highlightthickness=0)
        
        self.blendVersionVar = tk.StringVar()
        if self.Job.blender:
            self.blendVersionVar.set(self.Job.blender.name)
        else:
            self.blendVersionVar.set('Selec Blender Version')
        tk.Label(self.head,text='Blender Version: ',fg=Colors.fontColor, bg=Colors.header).pack(side=tk.LEFT)
        self.blendOptionMenu=tk.OptionMenu(self.head,self.blendVersionVar,*self.settings.blenderVersions if self.settings.blenderVersions else ['Selec Blender Version'],
            command=self.setBlenderVersion)
        self.blendOptionMenu.pack(side=tk.LEFT,padx=3,pady=(5,4))
        self.blendOptionMenu.config(bg=Colors.widget,fg=Colors.fontColor)
        self.blendOptionMenu['highlightthickness'] = 0

        self.scrollbar=Scrollbar(self.main,orient="vertical",command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)

        self.contentFrame = tk.Frame(self.canvas,bg=Colors.background)
        self.canvasFrame=self.canvas.create_window((0,0), window=self.contentFrame, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.canvas.bind("<Configure>",  self.resize_frame)
        self.window.bind("<MouseWheel>", self._on_mousewheel)
        
        self.main.pack(fill=tk.BOTH, expand=True)
        for sc in self.Job.scenes:
            a=SceneWidget(self,sc)
            a.pack()
            self.sceneWidgets.append(a)
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        self.footer = tk.Frame(self.window,bg=Colors.header,height=40)
        tk.ttk.Separator(self.footer, orient=tk.HORIZONTAL).pack(side=tk.TOP,fill=tk.X)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.saveButton =tk.Button(self.footer,bg=Colors.background,fg=Colors.fontColor,width=7,text='Save',command=lambda: self.safe(),height=1)
        self.saveButton.pack(side=tk.RIGHT,anchor=tk.SE)
        self.fileStats = tk.Label(self.footer,text=self.getFileStats(),fg=Colors.fontColor,bg=Colors.header)
        self.fileStats.pack(side=tk.BOTTOM,anchor=tk.SW,pady=5,padx=3)
        
    
    def resize_frame(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvasFrame, width = canvas_width)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def setBlenderVersion(self,value):
        for blend in self.settings.blenderVersions:
            if blend.name == self.blendVersionVar.get():
                self.Job.blender = blend
                self.parent.blendVersionVar.set(blend.name)

    def getFileStats(self):
        stats = ''
        stats += 'Total number of scenes: '+str(len(self.Job.scenes))
        stats += '   |   '
        stats += 'Total number of cameras: '
        i = 0
        for s in self.Job.scenes:
            i+= len(s.cameras)
        stats += str(i)
        return stats

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        '''On Windows, you bind to <MouseWheel> and you need to divide event.delta by 120 (or some other factor depending on how fast you want the scroll)
            on OSX, you bind to <MouseWheel> and you need to use event.delta without modification
            on X11 systems you need to bind to <Button-4> and <Button-5>, and you need to divide event.delta by 120 (or some other factor depending on how fast you want to scroll)
        '''
    def safe(self):
        self.Job.scenes.clear()
        for widget in self.sceneWidgets:
            self.Job.scenes.append(widget.scene)
            widget.safe()
            self.destroy()
    def destroy(self):
        self.window.destroy()

    def closeWindowEvent(self):
        answer = askyesno(title='confirmation',
                message='Are you sure that you want to quit?\nChanges wil be discarded')
        if answer:
            self.destroy()
            return 
        self.window.focus_force()

def main():
    def testExveption():
        def addWindow(master):
            a = ExceptionWindow('Blend files below 2.8 are not supported',master)
        master = tk.Tk()
        master.geometry('150x100')
        mButton = tk.Button(master,text='test sec. Window',command=lambda: addWindow(master)).pack(pady=20)
        master.mainloop()

if __name__ == '__main__':
    main()