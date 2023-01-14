import tkinter as tk

class DragDropFrame(tk.Frame):
    def __init__(self, parent, frame_list, highlight_thickness=10, highlight_color='YELLOW',offset=0, ispropagte=True, drag_dir='Y' ,*args, **kwargs):
        self.parent = parent
        self.frame_list = frame_list
        self.offset = offset
        self.ispropagte = ispropagte
        self.drag_dir = drag_dir
        self.pack_args = []
        self.pack_kwargs = []
        
        super().__init__(parent, *args, **kwargs)
        c ='hand1' if self.drag_dir =='Y' else 'watch'
        self.config(cursor=c)
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<B1-Motion>', self.on_motion)

        
        self.highlight_thickness = highlight_thickness
        self.highlight_color = highlight_color
        if 'Y'==self.drag_dir:
            self.drag_highlight = tk.Frame(self,bg=self.highlight_color,height=self.highlight_thickness)
        else: 
            self.drag_highlight = tk.Frame(self,bg=self.highlight_color,width=self.highlight_thickness)
        self.startDragingPos = 0
       


    def on_press(self, e):
        print('DEBUG')
        if self.drag_dir =='Y':
            self.startDragingPos = e.y+ self.winfo_y()
        else: 
            self.startDragingPos = e.x+ self.winfo_x()


    def on_release(self, e):
        if self.drag_dir == 'Y':
            y = e.y + self.winfo_y()
            self.pos_y = y
        else:
            x = e.x + self.winfo_x()
            self.pos_x = x

        
        self.refresh_frames()

    def on_motion(self, e):
        current_lower = None
        current_upper = None
        if self.drag_dir == 'Y':
            y = e.y + self.winfo_y()
            for f in self.frame_list:    
                if f.root.drag_highlight.winfo_ismapped():
                    f.root.drag_highlight.place_forget()
            
            
            #Movement Down
            if y > self.startDragingPos:
                for f in self.frame_list:
                    if f.root is self:
                        continue
                    if self.startDragingPos > f.root.pos_y:
                        continue
                    if y > f.root.pos_y:
                        current_lower = f.root
                        
                if current_lower:
                    current_lower.drag_highlight.place(rely=1.0,relx=0.0,relwidth=1.0,anchor=tk.SW,y=self.offset)
                    current_lower.drag_highlight.lift()

            #Movement Up
            if y < self.startDragingPos:
                for f in self.frame_list:
                    
                    if f.root is self:
                        continue
                    if self.startDragingPos < f.root.pos_y:
                        continue
                    if y < f.root.pos_y:
                        current_upper = f.root
                        break
                if current_upper:
                    current_upper.drag_highlight.place(rely=0.0,relx=0.0,relwidth=1.0,anchor=tk.NW,y=-1*self.offset)
                    current_upper.drag_highlight.lift()
        
        
        else:
            x = e.x + self.winfo_x()
            for f in self.frame_list:    
                if f.root.drag_highlight.winfo_ismapped():
                    f.root.drag_highlight.place_forget()
            
            
            #Movement Right
            if x > self.startDragingPos:
                for f in self.frame_list:
                    if f.root is self:
                        continue
                    if self.startDragingPos > f.root.pos_x:
                        continue
                    if x > f.root.pos_x:
                        current_lower = f.root
                        
                if current_lower:
                    current_lower.drag_highlight.place(rely=0.0,relx=1.0,relheight=1.0,anchor=tk.NE,x=self.offset)
                    current_lower.drag_highlight.lift()

            #Movement Left
            if x < self.startDragingPos:
                for f in self.frame_list:
                    if f.root is self:
                        continue
                    if self.startDragingPos < f.root.pos_x:
                        continue
                    if x < f.root.pos_x:
                        current_upper = f.root
                        break
                if current_upper:
                    current_upper.drag_highlight.place(rely=0.0,relx=0.0,relheight=1.0,anchor=tk.NW,x=-self.offset)
                    current_upper.drag_highlight.lift()   


    def do_pack(self,*args, **kwargs):
        if not self.pack_args:
            self.pack_args = args
        if not self.pack_kwargs:
            self.pack_kwargs = kwargs
        if self.ispropagte:
            self.pack_propagate(0) 
        self.pack(*args, **kwargs)
        self.parent.update()
        self.update()
        if self.drag_dir == 'Y':
            self.pos_y = self.winfo_y()
        else:
            self.pos_x = self.winfo_x()
        

    def refresh_frames(self):
        for f in self.frame_list:
            if f.root.drag_highlight.winfo_ismapped():
                f.root.drag_highlight.place_forget()
            f.root.pack_forget()
        if self.drag_dir == 'Y':
            self.frame_list.sort(key=lambda x: x.root.pos_y)
        else:
            self.frame_list.sort(key=lambda x: x.root.pos_x)
        for f in self.frame_list:
            f.root.do_pack(*self.pack_args,**self.pack_kwargs)


    def bind_childs(self,childs):
        for c in childs:
            c.bind('<Button-1>', self.on_press)
            c.bind('<ButtonRelease-1>', self.on_release)
            c.bind('<B1-Motion>', self.on_motion)


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
    print(':)')
    root.mainloop()
