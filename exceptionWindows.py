import tkinter as tk


class ExceptionWindow:
    def __init__(self,message,master):
        self.message = message
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.geometry('300x100')
        self.window.title('An error occurred')
        self.label = tk.Label(self.window,text=message).pack(side=tk.TOP,pady=2)
        self.okButton = tk.Button(self.window,text='Ok', command=self.okButtonAction, width=10).pack(side=tk.BOTTOM,pady=2)
        self.window.focus_force()
        
    def destroy(self):
        self.window.destroy()

    def okButtonAction(self):
        self.destroy()

class CriticalWindow(ExceptionWindow):
    def __init__(self,message,master):
        super().__init__(message,master)
    def destroy(self):
        self.master.destroy()