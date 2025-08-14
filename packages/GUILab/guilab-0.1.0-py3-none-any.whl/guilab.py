import ttkbootstrap as tkb
from tkinter import *
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame  # for audio playback
import os
from tkvideo import tkvideo
def Window(theme, title, width, height, x=0, y=0,resizeable=(True,True)):
    if theme.lower() == "dark":
        root = tkb.Window(themename="darkly",resizable=resizeable)
    elif theme.lower() == "light":
        root = tkb.Window(themename="litera")
    else:
        root = tkb.Window(themename="litera")
    root.title(title)
    root.geometry(f"{width}x{height}+{x}+{y}")
    return root  

def showError(title=None, message=None):
    return messagebox.showerror(title or "", message or "")

def showInfo(title=None, message=None):
    return messagebox.showinfo(title or "", message or "")

def showWarning(title=None, message=None):
    return messagebox.showwarning(title or "", message or "")

def systemError(time, title=None, message=None):
    try:
        toast = ToastNotification(
            title=title or "",
            message=message or "",
            duration=time * 1000
        )
        toast.show_toast()
    except Exception as e:
        messagebox.showerror(title="An error has occurred",message=f"Error : {e}")
def Button(link=None,function=None,value=None,text=None,textVar=None,width=None,mode=None,style="primary"):
    try:
        Button=tkb.Button(master=link,textvariable=textVar,width=width,state=mode,name=value,text=text,command=function,style=f"{style}.TButton")
        return Button
    except Exception as e:
        messagebox.showerror(title="An error has occurred",message=f"Error : {e}")
def Label(link=None,variable=None,bg_color=None,fg_color=None,border=None,font=None,width=None,text=None,mode=None,border_style=None,border_size=None,pad=None,style="primary"):
    try:
        Label=tkb.Label(master=link,background=bg_color,textvariable=variable,foreground=fg_color,border=border,font=font,width=width,text=text,state=mode,relief=border_style,borderwidth=border_size,padding=pad,style=f"{style}.TLabel")
        return Label
    except Exception as e:
        messagebox.showerror(title="An error has occurred",message=f"Error : {e}")
        tkb.Entry()
def TextBox(link=None,bg_color=None,variable=None,fg_color=None,name=None,replace_with="",mode="normal",width=100,font=None,justify=None,style="primary"):
    Entry=tkb.Entry(master=link,background=bg_color,textvariable=variable,foreground=fg_color,show=replace_with,name=name,state=mode,width=width,font=font,justify=justify,style=f"{style}.TEntry")
    return Entry
def CheckBox(link=None,function=None,offvalue=None,onvalue=None,mode=None,style="primary",text=None,width=10,variable=None,pad=None):
    CheckBox=tkb.Checkbutton(master=link,command=function,offvalue=offvalue,onvalue=onvalue,state=mode,style=f"{style}.TCheckbutton",variable=variable,padding=pad)
    return CheckBox
def RadioButton(link=None,function=None,name=None,pad=None,mode="normal",style="primary",text=None,value=None,variable=None,width=10):
    Radio=tkb.Radiobutton(master=link,command=function,name=name,padding=pad,state=mode,style=f"{style}.TRadiobutton",text=text,value=value,variable=variable,width=width)
    return Radio
def slider(link=None,function=None,min=0,max=100,length=100,name=None,orientation="horizontal",mode="normal",style="primary",value=None,variable=None):
    slider=tkb.Scale(master=link,command=function,from_=min,to=max,length=length,name=name,style=f"{style}.TScale",orient=orientation,state=mode,value=value,variable=variable)
    return slider
def Progressbar(link=None,length=200,max=100,mode="determinate",name=None,orientation="horizontal",style="primary",value=None,variable=None):
    bar=tkb.Progressbar(master=link,length=length,maximum=max,mode=mode,name=name,orient=orientation,style=f"{style}.TProgressbar",value=value,variable=variable)
    return bar
def Meter(link=None,style="primary",total=100,used=0,meter_thickness=10,size=500,type=FULL,strip_thickness=5,showtext=True,interaction=False,left_text=None,right_text=None,font=None,step=None):
    meter=tkb.Meter(master=link,bootstyle=style,meterthickness=meter_thickness,amounttotal=total,amountused=used,metersize=size,metertype=type,stripethickness=strip_thickness,showtext=showtext,interactive=interaction,textleft=left_text,textright=right_text,textfont=font,stepsize=step)
    return meter
def Frame(link=None,border=None,border_width=None,height=200,name=None,pad=None,border_style=None,style="primary",width=200):
    frame=tkb.Frame(master=link,border=border,borderwidth=border_width,height=height,name=name,padding=pad,relief=border_style,width=width,style=f"{style}.TFrame")
    return frame
def Tab(link=None,height=200,width=200,style="primary",name=None,pad=None,tabs=[]):
    tab=tkb.Notebook(master=link,height=height,width=width,style=f"{style}.TNotebook",name=name,padding=pad)
    try:
        if tabs:    
            for tabitem in tabs:
                tab_frame=tkb.Frame(master=tab)
                tab.add(tab_frame,text=tabitem)
    except Exception as e:
        messagebox.showerror(title="Error",message=f"Something went wrong.\nerror: {e}")
    return tab
def Dropdown(link=None, values=None, variable=None, width=None, function=None, style="primary"):
    try:
        combo = tkb.Combobox(master=link, values=values, textvariable=variable, width=width, style=f"{style}.TCombobox")
        if function:
            combo.bind("<<ComboboxSelected>>", lambda e: function())
        return combo
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")
def Datepicker(link=None, variable=None, date_format="%d-%m-%Y", width=None, style="primary"):
    try:
        date_entry = tkb.DateEntry(master=link, dateformat=date_format, width=width, style=f"{style}.TEntry")
        return date_entry
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")
def SpinBox(link=None, from_=0, to=10, increment=1, variable=None, width=None, style="primary"):
    try:
        spin = tkb.Spinbox(master=link, from_=from_, to=to, increment=increment, textvariable=variable, width=width, style=f"{style}.TSpinbox")
        return spin
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")
def MenuBar(link=None, menus=None, font=None,fg_color=None,bg_color=None):
    """
    Create a menubar.
    menus: dict of { "Menu Name": [("Item Name", command_function), ...] }
    """
    try:
        menu_bar = tkb.Menu(master=link,font=font,background=bg_color,foreground=fg_color)
        if menus:
            for menu_name, commands in menus.items():
                menu = tkb.Menu(menu_bar, tearoff=0)
                for label, cmd in commands:
                    menu.add_command(label=label, command=cmd)
                menu_bar.add_cascade(label=menu_name, menu=menu)
        return menu_bar
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")


def Toolbar(link=None, buttons=None, style="primary"):
    """
    Create a toolbar frame with buttons.
    buttons: list of dicts [{"text": "Btn1", "command": func1}, ...]
    """
    try:
        toolbar = tkb.Frame(master=link, style=f"{style}.TFrame")
        if buttons:
            for btn in buttons:
                b = tkb.Button(master=toolbar, text=btn.get("text"), command=btn.get("command"), style=f"{style}.TButton")
                b.pack(side=LEFT, padx=2, pady=2)
        return toolbar
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")


def Table(link=None, columns=None, show="headings", style="primary", height=None):
    """
    Create a Treeview table.
    columns: list of column names
    """
    try:
        tree = tkb.Treeview(master=link, columns=columns, show=show, height=height, style=f"{style}.Treeview")
        if columns:
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor=W)
        return tree
    except Exception as e:
        messagebox.showerror(title="An error has occurred", message=f"Error : {e}")
#Media support: Image/video/audio embedding and controls.
def Canvas(
    link=None,
    width=400,
    height=300,
    bg_color=None,
    shapes=None,  # list of shape definitions
):
    """
    Create a canvas and optionally draw multiple shapes on it.

    Parameters:
    - parent: parent container
    - width, height: canvas dimensions
    - bg_color: background color
    - shapes: list of dicts, each dict defines a shape:
        {
            "type": "circle" | "rectangle" | "line" | "oval" | "polygon" | "image",
            "coords": tuple or list of coordinates,
            "fill": color,
            "outline": color,
            "width": number,
            "tags": str,
            "anchor": anchor (for image)
        }
    """
    try:
        canvas = tkb.Canvas(master=link, width=width, height=height, background=bg_color)

        # Draw each shape
        if shapes:
            for shape_def in shapes:
                shape_type = shape_def.get("type").lower()
                coords = shape_def.get("coords")
                fill = shape_def.get("fill")
                outline = shape_def.get("outline", "black")
                line_width = shape_def.get("width", 1)
                tags = shape_def.get("tags")
                anchor = shape_def.get("anchor", NW)

                if shape_type == "circle":
                    x, y, r = coords
                    canvas.create_oval(
                        x - r, y - r, x + r, y + r,
                        fill=fill, outline=outline, width=line_width, tags=tags
                    )
                elif shape_type == "rectangle":
                    x1, y1, x2, y2 = coords
                    canvas.create_rectangle(
                        x1, y1, x2, y2, fill=fill, outline=outline, width=line_width, tags=tags
                    )
                elif shape_type == "line":
                    x1, y1, x2, y2 = coords
                    canvas.create_line(
                        x1, y1, x2, y2, fill=fill or "black", width=line_width, tags=tags
                    )
                elif shape_type == "oval":
                    x1, y1, x2, y2 = coords
                    canvas.create_oval(
                        x1, y1, x2, y2, fill=fill, outline=outline, width=line_width, tags=tags
                    )
                elif shape_type == "polygon":
                    canvas.create_polygon(
                        coords, fill=fill, outline=outline, width=line_width, tags=tags
                    )
                elif shape_type == "image":
                    x, y, image_path = coords
                    img = tkb.PhotoImage(file=image_path)
                    canvas.create_image(x, y, image=img, anchor=anchor)
                    shape_def["_image_ref"] = img  # store reference to prevent GC
                else:
                    messagebox.showerror("Canvas Error", f"Unknown shape type: {shape_type}")

        return canvas
    except Exception as e:
        messagebox.showerror("Canvas Error", f"Error: {e}")
        return None


def Media(link=None, media_type="image", path=None, width=None, height=None, controls=True):
    """
    Embed media into the GUI.
    
    Parameters:
    - parent: parent widget
    - media_type: "image", "video", "audio"
    - path: file path
    - width, height: optional resizing for images/videos
    - controls: if True, show basic playback controls for audio/video
    """
    pygame.mixer.init()
    try:
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        if media_type.lower() == "image":
            img = Image.open(path)
            if width and height:
                img = img.resize((width, height), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(link, image=img_tk)
            label.image = img_tk  # keep reference
            label.pack()
            return label
        
        elif media_type.lower() == "audio":
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            
            frame = tk.Frame(link)
            
            def play():
                pygame.mixer.music.play()
            def pause():
                pygame.mixer.music.pause()
            def unpause():
                pygame.mixer.music.unpause()
            def stop():
                pygame.mixer.music.stop()
            
            if controls:
                tk.Button(frame, text="Play", command=play).pack(side="left")
                tk.Button(frame, text="Pause", command=pause).pack(side="left")
                tk.Button(frame, text="Unpause", command=unpause).pack(side="left")
                tk.Button(frame, text="Stop", command=stop).pack(side="left")
            
            frame.pack()
            return frame
        
        elif media_type.lower() == "video":
            # Simple video playback using tkvideo (install tkvideo library)
            
            label = tk.Label(link)
            label.pack()
            player = tkvideo(path, label, loop=1, size=(width, height) if width and height else None)
            player.play()
            return label
        
        else:
            messagebox.showerror("Media Error", f"Unknown media type: {media_type}")
            return None
    
    except Exception as e:
        messagebox.showerror("Media Error", f"Error: {e}")
        return None
