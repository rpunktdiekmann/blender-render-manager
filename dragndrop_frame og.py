import tkinter as tk

class DragDropFrame(tk.Frame):
    def __init__(self, parent, frame_list, highlight_thickness=10, highlight_color='YELLOW', *args, **kwargs):
        self.parent = parent
        self.frame_list = frame_list

        self.pack_args = []
        self.pack_kwargs = []
        
        super().__init__(parent, *args, **kwargs)
        self.config(cursor='hand1')
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<B1-Motion>', self.on_motion)

        
        self.highlight_thickness = highlight_thickness
        self.highlight_color = highlight_color
        self.drag_highlight = tk.Frame(self,bg=self.highlight_color,height=self.highlight_thickness)
        self.startDragingPos_y = 0
       


    def on_press(self, e):
        self.startDragingPos_y = e.y+ self.winfo_y()


    def on_release(self, e):
        y = e.y + self.winfo_y()
        self.pos_y = y

        
        self.refresh_frames()

    def on_motion(self, e):
        current_lower = None
        current_upper = None
        y = e.y + self.winfo_y()
        for f in self.frame_list:    
            if f.drag_highlight.winfo_ismapped():
                f.drag_highlight.place_forget()
        
        
        #Movement Down
        if y > self.startDragingPos_y:
            for f in self.frame_list:
                if f is self:
                    continue
                if self.startDragingPos_y > f.pos_y:
                    continue
                if y > f.pos_y:
                    current_lower = f
                    
            if current_lower:
                current_lower.drag_highlight.place(rely=1.0,relx=0.0,relwidth=1.0,anchor=tk.SW,y=0)

       #Movement Up
        if y < self.startDragingPos_y:
            for f in self.frame_list:
                if f is self:
                    continue
                if self.startDragingPos_y < f.pos_y:
                    continue
                if y < f.pos_y:
                    current_upper = f
                    break
            if current_upper:
                current_upper.drag_highlight.place(rely=0.0,relx=0.0,relwidth=1.0,anchor=tk.NW)



    def do_pack(self,*args, **kwargs):
        if not self.pack_args:
            self.pack_args = args
        if not self.pack_kwargs:
            self.pack_kwargs = kwargs
        self.pack_propagate(0) 
        self.pack(*args, **kwargs)
        self.parent.update()
        self.update()
        self.pos_y = self.winfo_y()
        

    def refresh_frames(self):
        for f in self.frame_list:
            if f.drag_highlight.winfo_ismapped():
                f.drag_highlight.place_forget()
            f.pack_forget()
        self.frame_list.sort(key=lambda x: x.pos_y)
        for f in self.frame_list:
            f.do_pack(*self.pack_args,**self.pack_kwargs)





if __name__ == '__main__':
    def debug(e):
        x = e.x 
        y = e.y 
        print(f'DEBUG {e.x+e.widget.winfo_x()} / {e.y+e.widget.winfo_y()}')


    root = tk.Tk()
    root.geometry('500x500')
    #root.bind('<ButtonRelease-1>', debug)
    frames = []
    #              parent | framelist | ~~           highlight options          ~~  | ~~  tk.Frame args  ~~
    f1 = DragDropFrame(root, frames , highlight_thickness=2, highlight_color='YELLOW',bg='GREEN', height=50)
    f1.do_pack(fill=tk.X, pady=50)
    frames.append(f1)
    f2 = DragDropFrame(root, frames , highlight_thickness=2, highlight_color='YELLOW',bg='RED', height=90)
    f2.do_pack(fill=tk.X, pady=50)
    frames.append(f2)
    f3 = DragDropFrame(root, frames , highlight_thickness=2, highlight_color='YELLOW',bg='BLUE', height=50)
    f3.do_pack(fill=tk.X, pady=50)
    frames.append(f3)
    btn = tk.Button(f1,text='Test')
    btn.pack()
    print(f1.winfo_screenmmwidth())
    print(f1.winfo_height())
    root.mainloop()
