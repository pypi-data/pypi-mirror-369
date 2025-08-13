import tkinter
import customtkinter as ctk


class HelpBox(ctk.CTkToplevel):
    # window to display help
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title('Help')
        self.geometry("400x300")

        if "text" in kwargs :
            text = kwargs["text"]
        else:
            text = ''

        if "image" in kwargs :
            image = kwargs["image"]
        else:
            image = None

        if "font" in kwargs and kwargs['font'] is not None:
            font = kwargs["font"]
        else:
            font = ctk.CTkFont(size=15)

        # create a frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        # self.main_frame.pack(fill=tkinter.BOTH, expand=True)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # create textbox
        self.textbox = ctk.CTkTextbox(self.main_frame, wrap="word", font=font)
        # self.textbox.pack(fill=tkinter.BOTH, expand=True)
        self.textbox.grid(row=0, rowspan=2, column=0, sticky="nsew")

        # add text
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")  # configure textbox to be read-only

        # create image
        if image is not None:
            self.label_image = ctk.CTkLabel(self.main_frame, text="", image=image)
            self.label_image.grid(row=0, column=1)
            # self.label_image.grid_remove()
        else:
            self.label_image=None

    def text(self, text, image=None, font=None):
        # change the text
        self.textbox.configure(state="normal")  # configure textbox to be modifiable
        self.textbox.delete("0.0", "end")  # delete all text
        self.textbox.insert("0.0", text)  # add text
        self.textbox.configure(state="disabled")  # configure textbox to be read-only

        # change image
        if self.label_image is not None:
            self.label_image.destroy()
            self.label_image = None
        if image is not None:
            self.label_image = ctk.CTkLabel(self.main_frame, text="", image=image)
            self.label_image.grid(row=0, column=1)

        self.focus()  # focus on the windows


def create_help_box(obj, text, image=None, font=None):
    if (not hasattr(obj, 'help_box')) or (obj.help_box is None) or (not obj.help_box.winfo_exists()):
        obj.help_box = HelpBox(text=text, image=image, font=font)  # create window if its None or destroyed
        obj.help_box.after(100, obj.help_box.focus)  # Workaround for bug where main window takes focus
    else:
        obj.help_box.text(text, image)  # change the text and image


class HelpWindowMain :
    # class that can create a HelpBox (a windows of help)
    def __init__(self, font=None):
        self.help_box = None
        self.font = font

    def create_help_box(self, text, image=None, font=None):
        if (not hasattr(self, 'help_box')) or (self.help_box is None) or (not self.help_box.winfo_exists()):
            if font is None and self.font is not None :
                font = self.font

            self.help_box = HelpBox(text=text, image=image, font=font)  # create window if its None or destroyed
            self.help_box.after(100, self.help_box.focus)  # Workaround for bug where main window takes focus
        else:
            self.help_box.text(text, image)  # change the text
