#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.colorchooser
import math
import os

working_directory = os.path.dirname(__file__)
file_types = [("Canvas datoteke", "*.can"), ("Sve datoteke", "*.*")]


class Point(object):

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
        return


class Stack(object):

    def __init__(self):
        self.queue = []
        return

    def __str__(self):
        output = "Stack object:\n"
        for level in self.queue:
            output += str(level) + '\n'
        return output

    def push(self, obj):
        self.queue.append(obj)
        return

    def pop(self):
        if self.is_empty():
            return None
        return self.queue.pop()

    def empty(self):
        self.queue = []
        return

    def is_empty(self):
        if len(self.queue):
            return False
        return True


class EditLineWidthDialog(tk.simpledialog.Dialog):

    def body(self, parent):
        self.root = parent
        self.title("Debljina linije")
        self.user_input = None

        self.msg_label = tk.Label(master=self.root, text="Unesite debljinu linije")
        self.msg_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.width_var = tk.StringVar()
        entry = tk.Entry(master=self.root, textvariable=self.width_var, width=5)
        entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        entry.focus_set()

    def apply(self):
        self.user_input = self.width_var.get()


class Menubar(tk.Menu):

    def __init__(self, root):
        self.root = root
        super().__init__(master=self.root)
        # self.menubar = tk.Menu(master=self.root)
        self.create_gui()

    def create_gui(self):
        self.file_menu = tk.Menu(master=self, tearoff=0)
        self.file_menu.add_command(label="Nova", command=self.root.on_new, accelerator="Ctrl+N")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Spremi", command=self.root.on_save, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Otvori", command=self.root.on_open, accelerator="Ctrl+O")
        self.add_cascade(menu=self.file_menu, label="Datoteka")
        self.edit_menu = tk.Menu(master=self, tearoff=0)
        self.edit_menu.add_command(label="Promijeni boju linije", command=lambda: self.root.edit_color(key="outline"))
        self.edit_menu.add_command(label="Promijeni boju ispune", command=lambda: self.root.edit_color(key="inline"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Debljina linije", command=self.root.edit_line_width)
        # self.edit_menu.add_command(label="Duljina radijusa", command=self.root.edit_radius_length)
        self.add_cascade(menu=self.edit_menu, label="Uredi")
        return


class Canvas(tk.Canvas):

    def __init__(self, root):
        self.root = root
        super().__init__(master=self.root, width=800, height=600, bg="#ffffff")

    # def _mouse_move(self, event):   # curved line - good, but leaks when user moves mouse very rapidly - try and see
    #     self.root.draw_with_radius(event=event, key="circle", radius=50.0)
    #     return


class Toolbar(tk.Frame):

    def __init__(self, root):
        self.root = root
        self.bg = "#bebebe"
        super().__init__(master=self.root, background=self.bg)
        self.create_gui()

    def create_gui(self):
        for object_key in enumerate(self.root.all_objects_keywords):
            key = object_key[1]
            image = tk.PhotoImage(file=f"{working_directory}\\toolbar_icons\\{key}_small.png")
            button = tk.Button(master=self, image=image, command=lambda k=key: self.root.on_select_object(key=k))
            button.grid(row=1, column=object_key[0] + 1, padx=2, pady=2)
            button.image = image

        self.selected_label = tk.Label(master=self, font=("Calibri", 10, "italic"), bg=self.bg)
        self.selected_label.grid(row=2, column=1, columnspan=3, sticky=tk.W)

        # for object_param in enumerate([("Debljina linije", "nw"), ("Duljina radijusa", "sw")]):
        #     tk.Label(master=self, text=object_param[1][0], bg=self.bg).grid(
        #         row=1, column=5, pady=4, sticky=object_param[1][1])
        #
        # self.spinboxes = list()
        # for spinbox in []:
        #     spinbox = ttk.Spinbox(master=self, values=[x for x in range(5, 101)], width=5, wrap=True, command=lambda x=2: x)
        #     spinbox.grid(row=1, column=6, padx=5, pady=4, sticky={0: "nw", 1: "sw"}[i])
        #     spinbox.set(self.root)
        #     self.spinboxes.append(spinbox)

    def update_label(self, label):
        self.selected_label.config(text=f"Odabran oblik: {label}")


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title_ = "Bez imena - Platno za crtanje"
        icon = tk.PhotoImage(file="icon.png")
        self.iconphoto(True, icon)

        self._translation = ["Linija", "Elipsa", "Četverokut"]
        self.all_objects_keywords = ["line", "oval", "rectangle"]

        self.menubar = Menubar(root=self)
        self.toolbar = Toolbar(root=self)
        self.canvas = Canvas(root=self)
        self.toolbar.grid(row=1, column=1, sticky="ew")
        self.canvas.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.config(menu=self.menubar)

        self.grid_columnconfigure(weight=1, index=1)
        self.grid_rowconfigure(weight=1, index=2)

        self.selected_object_key = "line"
        self.outline_color = "#000000"  # black
        self.inline_color = "#ffffff"  # white
        self.line_width = 10
        self.radius_length = 10
        self.displayed_objects = Stack()
        self.deleted_objects = Stack()
        self.loaded_objects = Stack()
        self.object_drawing_cache = Stack()  # used while user moves mouse with pressed B1
        self.start_point = None
        self.end_point = None

        self._bind_all()
        return

    def _bind_all(self):
        self.bind("<Button-2>", self._test)
        self.canvas.bind("<Button-3>", self.draw_with_radius)
        self.canvas.bind("<Button-1>", lambda e: self.mouse_press(event=e))
        self.canvas.bind("<B1-Motion>", lambda e: self.mouse_pressed_motion(event=e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.mouse_release(event=e))
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<Control-n>", self.on_new)
        self.bind("<Control-s>", self.on_save)
        self.bind("<Control-o>", self.on_open)
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-y>", self.redo)
        self.bind("<Escape>", self.on_escape)
        return

    def _test(self, event):
        print(self.object_drawing_cache)

    @property
    def title_(self):
        return self._title

    @title_.setter
    def title_(self, value):
        if '*' in value and '*' in self.title_:
            pass
        else:
            self._title = value
            self.title(self._title)

    @property
    def objects_string(self):
        """
        Creates dictionary which contains string values for drawing an object using built-in function eval.
        This is needed, mainly because we store displayed objects as string in *.can file.
        Example:
        self.create_oval(185, 125, 185, 125, width=20, fill="#ffffff", outline="#000000")
        :return:    dict()
        """
        dict_ = dict()
        args_points = f"{self.start_point.x}, {self.start_point.y}, {self.end_point.x}, {self.end_point.y}"
        for key in self.all_objects_keywords:
            value = f"self.canvas.create_{key}({args_points}, width={self.line_width}, "
            if key == "line":
                value += f"fill=\"{self.outline_color}\")"
            else:
                value += f"fill=\"{self.inline_color}\", outline=\"{self.outline_color}\")"
            dict_[key] = value
            # print(value)
        return dict_

    def on_new(self, event=None):
        self.canvas.delete(tk.ALL)
        self.displayed_objects.empty()
        self.deleted_objects.empty()
        self.title_ = "Bez imena - Platno za crtanje"
        return

    def on_save(self, event=None):
        file_path = tk.filedialog.asksaveasfilename(title="Spremi",
                                                    initialdir=f"{working_directory}\\save",
                                                    initialfile="canvas",
                                                    defaultextension=".can",
                                                    filetypes=file_types)

        try:
            with open(file_path, "wb") as file:
                for _, obj_str in self.loaded_objects.queue + self.displayed_objects.queue:
                    file.write((obj_str + '\n').encode("ascii"))
        except FileNotFoundError:
            return
        else:
            self.displayed_objects.empty()  # important, check why!
            self.title_ = file_path.split("/")[-1] + " - Platno za crtanje"
            return

    def on_open(self, event=None):
        self.on_new()
        file_path = tk.filedialog.askopenfilename(title="Otvori", initialdir=working_directory, filetypes=file_types)

        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                for line in file.readlines():
                    obj_str = line.strip().decode("ascii")
                    obj_id = eval(obj_str)
                    self.loaded_objects.push(obj=(obj_id, obj_str))

            self.title_ = file_path.split("/")[-1] + " - Platno za crtanje"
        return

    def on_escape(self, event=None):
        self.start_point = self.end_point = None
        while not self.object_drawing_cache.is_empty():
            # This should always be looping only once, as mentioned stack contains 0 or 1 elements,
            # but this is for safety reasons as it is very important to clear the all cache
            self.canvas.delete(self.object_drawing_cache.pop())

    def on_mouse_wheel(self, event):
        operator = {True: '+', False: '-'}[event.delta > 0]
        self.radius_length = eval(f"self.radius_length {operator} 5")
        print(self.radius_length)
        return

    def edit_color(self, key):
        rgb_value = tk.colorchooser.askcolor()[1]
        if key == "outline":
            self.outline_color = rgb_value
        else:
            self.inline_color = rgb_value
        return

    def edit_line_width(self):
        dialog = EditLineWidthDialog(parent=self)
        width = dialog.user_input

        try:
            width = int(width)
        except ValueError:
            is_valid = False
        except TypeError:
            is_valid = False
        else:
            is_valid = width in range(5, 101)

        if is_valid:
            self.line_width = int(width)
        elif width is None:
            pass
        else:
            tk.messagebox.showwarning(title="Upozorenje", message="Neispravan unos.")
        return

    def edit_radius_length(self):
        return

    @property
    def selected_object_key(self):
        return self._selected_object_key

    @selected_object_key.setter
    def selected_object_key(self, value):
        self._selected_object_key = value
        self.toolbar.update_label(label=self._translation[self.all_objects_keywords.index(value)])

    def on_select_object(self, key):
        self.selected_object_key = key
        return

    def mouse_press(self, event):
        if self.start_point is None:
            self.start_point = Point(x=event.x, y=event.y)
            self.object_drawing_cache.empty()  # secures the clear drawing!
        return

    def mouse_pressed_motion(self, event):
        # expression explanied:
        #   if user press the Escape button, we want to forget the starting point, which will then cancel drawing
        # TODO: Noticed weird shadovs being drawn while moving the end point closer and closer to the starting point - NBG
        if self.start_point:
            old_obj_id = self.object_drawing_cache.pop()
            if old_obj_id:
                self.canvas.delete(old_obj_id)
            self.end_point = Point(x=event.x, y=event.y)
            new_obj_id, _ = self.draw()
            self.object_drawing_cache.push(obj=new_obj_id)
        return

    def mouse_release(self, event):
        self.end_point = Point(x=event.x, y=event.y)
        if self.start_point:
            self.draw(final=True)
            self.start_point = self.end_point = None
            self.object_drawing_cache.empty()
        return

    def draw(self, script=None, final=False):
        """
        Description:
        Function draws the canvas object from pure string.
        Depending on parameters script and final;
            - function takes (script=<some string value>) object string or
              gets new script for new object (script=None)
            - function pushes the final sketch to te displayed objects stack
              (otherwise, every object that has been drawn during the pressed
              left mouse button (<B1-Motion>) would be pushed on the stack,
              causing some unwanted results later on (invalid undo/redo etc.))
        TODO (DONE!): This will be implemented for all objects:
        Object types for now: line, oval and rectangle
        :param script: string   (if None -> selects script based on current selected object type)
        :param final: boolean   (if True -> pushes drawn object on displayed objects stack)
        :return: tuple (int, string)
        """
        obj_str = script
        if obj_str is None:
            obj_str = self.objects_string[self.selected_object_key]
        obj_id = eval(obj_str)
        if final:
            self.displayed_objects.push(obj=(obj_id, obj_str))
            self.title_ = '*' + self.title_
        return obj_id, obj_str

    def draw_with_radius(self, event):
        """
        Description:
        Function for circles or squares, depends on current selected style (oval or rectangle)
        Right click generated the point S (see picture below) which is the center of the object.
        Function then calculates points T1 and T2, and sends them to the drawing function draw.
        :param event: tkinter event object
        :return: None
        """
        """T1   a

            a   S   a

                a   T2"""
        # selected object cannot be line and we can start with normal drawing, and then press right click, so second expression is must
        if self.selected_object_key != "line" and self.start_point is None:
            a = round(math.sqrt(math.pow(self.radius_length, 2) / 2), 2)
            self.start_point = Point(x=event.x - a, y=event.y + a)  # T1
            self.end_point = Point(x=event.x + a, y=event.y - a)  # T2
            self.draw(final=True)
            self.start_point = None
        return

    def update_canvas(self):
        """
        Refreshes screen after every undo event.
        TODO: Try to find a better solution:
        TODO: instead of deleting all objects and then drawing them back (except the last on the stack)
        TODO: try to delete only the last one
        NOTE: Previous version had that solution, but after new update that algoritam doesn't work anymore, dunno why
        :return: None
        """
        for object_ in self.loaded_objects.queue + self.displayed_objects.queue:
            obj_id, obj_str = object_
            self.draw(script=obj_str)
        return

    def undo(self, event):
        # print("Undo")
        try:
            obj_id, obj_str = self.displayed_objects.pop()
        except TypeError:
            """Stack is empty, returns None, which cannot be interpreted as tuple object (a, b <= None)
            TypeError: cannot unpack non-iterable NoneType object"""
            return
        else:
            # self.canvas.delete(obj_id)     # we need object id to delete it   TODO: implement this method!!
            self.canvas.delete(tk.ALL)
            self.deleted_objects.push(obj=obj_str)  # here we send object string, needed because of option redo
            self.update_canvas()
            return

    def redo(self, event):
        # print("Redo")
        obj_str = self.deleted_objects.pop()
        if obj_str:
            self.draw(script=obj_str, final=True)
        return


def main():
    App()
    tk.mainloop()


if __name__ == '__main__':
    main()
