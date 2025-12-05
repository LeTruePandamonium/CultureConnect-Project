import customtkinter as ctk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageSequence
from tkinter import StringVar
import os
import json
from pypinyin import lazy_pinyin
import pykakasi
import time
import threading
import subprocess
import sys
import math


ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")

# Color theme system
COLOR_THEMES = {
    "Blue": {
        "primary": "#6096ba",
        "button_bg": "#8abee6",
        "button_fg": "#35495e",
        "text": "white",
        "text_dark": "black"
    },
    "Pink": {
        "primary": "#c77dba",
        "button_bg": "#e8a5d8",
        "button_fg": "#4a3d4a",
        "text": "white",
        "text_dark": "black"
    },
    "Green": {
        "primary": "#7ab89f",
        "button_bg": "#a8d5ba",
        "button_fg": "#4a5a4a",
        "text": "white",
        "text_dark": "black"
    }
}

CURRENT_THEME = "Blue"

def get_current_theme():
    global CURRENT_THEME
    return COLOR_THEMES[CURRENT_THEME]

def set_theme(theme_name):
    global CURRENT_THEME
    if theme_name in COLOR_THEMES:
        CURRENT_THEME = theme_name
        # Save theme to file
        try:
            with open("theme_settings.json", "w") as f:
                json.dump({"theme": theme_name}, f)
        except Exception as e:
            print(f"Error saving theme: {e}") 

def get_relative_size(base_size, widget):
    try:
        window_width = widget.winfo_width()
        window_height = widget.winfo_height()
        scale_factor = min(window_width / 1920, window_height / 1080)
        return max(int(base_size * scale_factor), base_size // 2)
    except:
        return base_size

def get_relative_font(base_size, widget, family="League Spartan", weight="bold"):
    size = get_relative_size(base_size, widget)
    try:
        return (family, size, weight)
    except:
        return ("Helvetica", size, weight)

def load_ctk_image(image_path, widget, height_percentage=0.25):
    """Load image as CTkImage for CustomTkinter widgets"""
    try:
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None
        original = Image.open(image_path)
        widget_height = widget.winfo_height() if widget.winfo_height() > 1 else 600
        target_height = int(widget_height * height_percentage)
        aspect_ratio = original.width / original.height
        target_width = int(target_height * aspect_ratio)
        target_width = max(target_width, 50)
        target_height = max(target_height, 50)
        resized_image = original.resize((target_width, target_height), Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(target_width, target_height))
    except Exception as e:
        print(f"Error loading CTkImage {image_path}: {e}")
        return None


root = ctk.CTk()
root.title("CultureConnect")
root.minsize(800, 600)


screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.attributes("-fullscreen", True)


resized_images = {}

class DynamicFrame(ctk.CTkFrame):
    def __init__(self, parent, bg_color="#6096ba"):
        super().__init__(parent, fg_color=bg_color)
        self.bg_color = bg_color
        self.update_scheduled = False
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, event=None):
        if not self.update_scheduled:
            self.update_scheduled = True
            self.after(100, self.update_elements)

    def update_elements(self):
        """Override this method in subclasses"""
        self.update_scheduled = False



frame_container = ctk.CTkFrame(root)
frame_container.pack(fill="both", expand=True)

def show_frame(frame_class):
    
    for key in ["1", "2", "3", "4", "5", "6"]:
        root.unbind(key)
    
    
    for widget in frame_container.winfo_children():
        widget.destroy()
    
    
    frame = frame_class(frame_container)
    frame.pack(fill="both", expand=True)
    
    
    root.update_idletasks()
    frame.pack(fill="both", expand=True)

class MainPage(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()
    
    def create_ui_elements(self):
        try:
            self.logo_image = load_ctk_image("logo.png", self, height_percentage=0.25)
            if self.logo_image:
                self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="", fg_color=get_current_theme()["primary"])
            else:
                raise FileNotFoundError("Logo not found")
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_label = ctk.CTkLabel(
                self, 
                text="CultureConnect",
                font=get_relative_font(36, self),
                text_color="white",
                fg_color=get_current_theme()["primary"]
            )
        self.logo_label.place(relx=0.5, rely=0.3, anchor="center")
        
        self.title = ctk.CTkLabel(
            self,
            text="CultureConnect",
            font=get_relative_font(50, self),
            text_color="white",
            fg_color=get_current_theme()["primary"]
        )
        self.title.place(relx=0.5, rely=0.5, anchor="center")

        theme = get_current_theme()
        self.button_bg = theme["button_bg"]
        self.button_fg = theme["button_fg"]

        self.start_btn = ctk.CTkButton(
            self,
            text="START",
            command=lambda: show_frame(ChooseModePage),
            fg_color=self.button_bg,
            text_color=self.button_fg,
            font=get_relative_font(28, self),
            corner_radius=8
        )
        
        self.about_btn = ctk.CTkButton(
            self,
            text="ABOUT US",
            command=lambda: show_frame(AboutUs),
            fg_color=self.button_bg,
            text_color=self.button_fg,
            font=get_relative_font(28, self),
            corner_radius=8
        )

        try:
            power_icon = load_ctk_image("icons/power_icon.png", self, height_percentage=0.012)
            if power_icon:
                self.shutdown_btn = ctk.CTkButton(
                    self,
                    text="",  
                    image=power_icon,
                    fg_color="red",
                    hover_color="#cc0000",  
                    text_color="white",
                    corner_radius=25,  
                    width=30,  
                    height=30,  
                    command=lambda: os.system("systemctl poweroff")
                )
            else:
                raise FileNotFoundError("Power icon not found")
        except Exception as e:
            print(f"Error loading power icon: {e}")
            self.shutdown_btn = ctk.CTkButton(
                self,
                text="⏻",  
                fg_color="red",
                hover_color="#cc0000",
                text_color="white",
                corner_radius=18,
                width=30,
                height=30,
                font=("Arial", 12),  
                command=lambda: os.system("systemctl poweroff")
            )

        # Settings button (gear icon)
        try:
            settings_icon = load_ctk_image("icons/settings_icon.png", self, height_percentage=0.012)
            if settings_icon:
                self.settings_btn = ctk.CTkButton(
                    self,
                    text="",
                    image=settings_icon,
                    fg_color=self.button_bg,
                    hover_color="#7ba6d6",
                    text_color="white",
                    corner_radius=25,
                    width=30,
                    height=30,
                    command=lambda: show_frame(SettingsPage)
                )
            else:
                raise FileNotFoundError("Settings icon not found")
        except Exception as e:
            print(f"Error loading settings icon: {e}")
            self.settings_btn = ctk.CTkButton(
                self,
                text="⚙",
                fg_color=self.button_bg,
                hover_color="#7ba6d6",
                text_color=self.button_fg,
                corner_radius=18,
                width=30,
                height=30,
                font=("Arial", 14),
                command=lambda: show_frame(SettingsPage)
            )

        self.update_button_sizes()
        
        root.bind("1", lambda event: self.start_btn.invoke())
        root.bind("2", lambda event: self.about_btn.invoke())
        root.bind("3", lambda event: self.shutdown_btn.invoke())
        root.bind("4", lambda event: self.settings_btn.invoke())
    
    def update_button_sizes(self):
        btn_width = max(int(self.winfo_width() * 0.15), 120)
        btn_height = max(int(self.winfo_height() * 0.06), 35)
        
        self.start_btn.configure(width=btn_width, height=btn_height)
        self.about_btn.configure(width=btn_width, height=btn_height)
        
        try:
            power_icon = load_ctk_image("icons/power_icon.png", self, height_percentage=0.012)
            if power_icon:
                self.shutdown_btn.configure(image=power_icon)
        except:
            pass
        
        self.start_btn.place(relx=0.5, rely=0.63, anchor="center")
        self.about_btn.place(relx=0.5, rely=0.75, anchor="center")
        
        self.shutdown_btn.place(relx=1.0, x=-10, y=10, anchor="ne")
        self.settings_btn.place(relx=0.0, x=10, y=10, anchor="nw")
    
    def update_elements(self):
        super().update_elements()
        try:
            self.logo_image = load_ctk_image("logo.png", self, height_percentage=0.25)
            if self.logo_image:
                self.logo_label.configure(image=self.logo_image)
        except:
            self.logo_label.configure(font=get_relative_font(36, self))
        
        self.title.configure(font=get_relative_font(50, self))
        self.start_btn.configure(font=get_relative_font(28, self))
        self.about_btn.configure(font=get_relative_font(28, self))
        self.update_button_sizes()

class AboutUs(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()
    
    def create_ui_elements(self):
        # Title
        theme = get_current_theme()
        self.title = ctk.CTkLabel(
            self,
            text="About Us",
            font=get_relative_font(72, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.5, rely=0.08, anchor="center")

        # Description text
        description_text = (
            "Connecting with different cultures for a better future.\n\n"
            "We believe that language should never be a barrier to understanding and connection.\n\n"
            "We are a small group of students from STI College Pasay-EDSA, driven by a shared passion for learning languages—"
            "especially Japanese, Chinese, and Korean. Inspired by our curiosity and love for culture, we created a hardware device "
            "designed to translate these languages into our native tongue, Filipino.\n\n"
            "Our goal is to make language learning more accessible, engaging, and meaningful. This device represents more than just "
            "a thesis project—it's a step toward bridging cultural gaps and empowering others to explore the world through language."
        )

        self.description = ctk.CTkLabel(
            self,
            text=description_text,
            font=get_relative_font(32, self),
            text_color="white",
            fg_color=theme["primary"],
            justify="center",
            wraplength=1000
        )
        self.description.place(relx=0.5, rely=0.5, anchor="center")

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(18, self),
            fg_color="white",
            text_color="black",
            width=100,
            height=40,
            command=lambda: show_frame(MainPage)
        )
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")
    
    def update_elements(self):
        super().update_elements()
        
        theme = get_current_theme()
        try:
            self.configure(fg_color=theme["primary"])
            if hasattr(self, 'title'):
                self.title.configure(fg_color=theme["primary"])
            if hasattr(self, 'description'):
                self.description.configure(fg_color=theme["primary"])
        except Exception:
            pass
class SettingsPage(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()
    
    def create_ui_elements(self):
        theme = get_current_theme()
        
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Settings",
            font=get_relative_font(72, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.5, rely=0.08, anchor="center")

        # Theme selection label
        self.theme_label = ctk.CTkLabel(
            self,
            text="Choose Theme Color:",
            font=get_relative_font(36, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.theme_label.place(relx=0.5, rely=0.25, anchor="center")

        
        button_width = max(int(self.winfo_width() * 0.18), 180)
        button_height = max(int(self.winfo_height() * 0.10), 80)
        
        self.blue_btn = ctk.CTkButton(
            self,
            text="Blue",
            command=lambda: self.apply_theme("Blue"),
            fg_color="#8abee6" if CURRENT_THEME != "Blue" else "#5a7fa3",
            text_color="#35495e",
            font=get_relative_font(32, self),
            width=button_width,
            height=button_height,
            corner_radius=10
        )
        self.blue_btn.place(relx=0.25, rely=0.40, anchor="center")
        
        self.pink_btn = ctk.CTkButton(
            self,
            text="Pink",
            command=lambda: self.apply_theme("Pink"),
            fg_color="#e8a5d8" if CURRENT_THEME != "Pink" else "#9b5a8a",
            text_color="#4a3d4a",
            font=get_relative_font(32, self),
            width=button_width,
            height=button_height,
            corner_radius=10
        )
        self.pink_btn.place(relx=0.5, rely=0.40, anchor="center")

        self.green_btn = ctk.CTkButton(
            self,
            text="Green",
            command=lambda: self.apply_theme("Green"),
            fg_color="#a8d5ba" if CURRENT_THEME != "Green" else "#6b9a7e",
            text_color="#4a5a4a",
            font=get_relative_font(32, self),
            width=button_width,
            height=button_height,
            corner_radius=10
        )
        self.green_btn.place(relx=0.75, rely=0.40, anchor="center")

        # Current theme display
        self.current_theme_label = ctk.CTkLabel(
            self,
            text=f"Current Theme: {CURRENT_THEME}",
            font=get_relative_font(24, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.current_theme_label.place(relx=0.5, rely=0.55, anchor="center")

        # Back button
        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            command=lambda: show_frame(MainPage),
            fg_color="white",
            text_color="black",
            font=get_relative_font(28, self),
            width=180,
            height=70
        )
        self.back_button.place(relx=0.05, rely=0.9, anchor="w")

        root.bind("1", lambda event: self.back_button.invoke())
    
    def apply_theme(self, theme_name):
        set_theme(theme_name)
        
        show_frame(SettingsPage)
    
    def update_elements(self):
        """Update all elements on resize"""
        super().update_elements()
        theme = get_current_theme()
        self.configure(fg_color=theme["primary"])
        self.title.configure(font=get_relative_font(72, self), fg_color=theme["primary"])
        self.theme_label.configure(font=get_relative_font(36, self), fg_color=theme["primary"])
        self.current_theme_label.configure(
            text=f"Current Theme: {CURRENT_THEME}",
            font=get_relative_font(24, self),
            fg_color=theme["primary"]
        )
        self.back_button.configure(font=get_relative_font(28, self))

class ChooseModePage(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()
        
    def create_ui_elements(self):
        self.header_label = ctk.CTkLabel(
            self,
            text="Mode",
            font=get_relative_font(80, self),
            text_color="white",
            fg_color="transparent"
        )
        self.header_label.place(relx=0.5, rely=0.12, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': (0.25, "Translate", JapTranslate),
            'tutoring': (0.5, "Tutoring", Tutoring),
            'drills': (0.75, "Drills", Drills)
        }
        icon_paths = {
            'translate': os.path.join("icons", "translate_icon.png"),
            'tutoring': os.path.join("icons", "tutoring_icon.png"),
            'drills': os.path.join("icons", "drills_icon.png")
        }

        for btn_name, (relx, label_text, target_class) in positions.items():
            frame = ctk.CTkFrame(
                self, fg_color="transparent", border_width=4, border_color="black",
                width=btn_width, height=btn_height
            )
            self.frames[btn_name] = frame

            icon = load_ctk_image(icon_paths[btn_name], self, height_percentage=0.15)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[btn_name] = btn
            btn.pack(fill="both", expand=True, padx=10, pady=10)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{btn_name}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=160, height=60,
            command=lambda: show_frame(MainPage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()

        root.bind("1", lambda event: self.buttons['translate'].invoke())
        root.bind("2", lambda event: self.buttons['tutoring'].invoke())
        root.bind("3", lambda event: self.buttons['drills'].invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def update_layout(self):
        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': 0.25,
            'tutoring': 0.5,
            'drills': 0.75
        }

        for btn_name, relx in positions.items():
            frame = self.frames[btn_name]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=0.48, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{btn_name}_icon.png"), self, height_percentage=0.15)
            if icon:
                self.buttons[btn_name].configure(image=icon)
                self.buttons[btn_name].image = icon

            label = self.buttons[f"{btn_name}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            label.place(relx=relx, rely=0.70, anchor="center")

        self.back_button.place(relx=0.5, rely=0.9, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()
        
        theme = get_current_theme()
        try:
            self.configure(fg_color=theme["primary"])
            if hasattr(self, 'title'):
                self.title.configure(fg_color=theme["primary"])
        except Exception:
            pass
        
        theme = get_current_theme()
        try:
            self.configure(fg_color=theme["primary"])
            if hasattr(self, 'title'):
                self.title.configure(fg_color=theme["primary"])
        except Exception:
            pass

    def update_elements(self):
        super().update_elements()
        
        theme = get_current_theme()
        try:
            self.configure(fg_color=theme["primary"])
            if hasattr(self, 'title'):
                self.title.configure(fg_color=theme["primary"])
        except Exception:
            pass

class JapModePage(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.create_ui_elements()
        
    def create_ui_elements(self):
        self.japtext1_label = ctk.CTkLabel(
            self,
            text="Mode",
            font=get_relative_font(80, self),
            text_color="white",
            fg_color="transparent"
        )
        self.japtext1_label.place(relx=0.5, rely=0.12, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': (0.25, "Translate", JapTranslate),
            'tutoring': (0.5, "Tutoring", JapTutoring),
            'drills': (0.75, "Drills", JapDrills)
        }
        icon_paths = {
            'translate': os.path.join("icons", "translate_icon.png"),
            'tutoring': os.path.join("icons", "tutoring_icon.png"),
            'drills': os.path.join("icons", "drills_icon.png")
        }

        for btn_name, (relx, label_text, target_class) in positions.items():
            frame = ctk.CTkFrame(
                self, fg_color="transparent", border_width=4, border_color="black",
                width=btn_width, height=btn_height
            )
            self.frames[btn_name] = frame

            icon = load_ctk_image(icon_paths[btn_name], self, height_percentage=0.15)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[btn_name] = btn
            btn.pack(fill="both", expand=True, padx=10, pady=10)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{btn_name}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=160, height=60,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()

        root.bind("1", lambda event: self.buttons['translate'].invoke())
        root.bind("2", lambda event: self.buttons['tutoring'].invoke())
        root.bind("3", lambda event: self.buttons['drills'].invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def update_layout(self):
        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': 0.25,
            'tutoring': 0.5,
            'drills': 0.75
        }

        for btn_name, relx in positions.items():
            frame = self.frames[btn_name]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=0.48, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{btn_name}_icon.png"), self, height_percentage=0.15)
            if icon:
                self.buttons[btn_name].configure(image=icon)
                self.buttons[btn_name].image = icon

            label = self.buttons[f"{btn_name}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            label.place(relx=relx, rely=0.70, anchor="center")

        self.back_button.place(relx=0.5, rely=0.9, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()

class JapTranslate(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Translate", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)


        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(self.bubble_frame, 
                                              text="Press START to begin", 
                                              font=get_relative_font(22, self),
                                              text_color="black", fg_color="transparent",
                                              wraplength=380, justify="center")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.tagalog_label = ctk.CTkLabel(self, text="TAGALOG", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color=theme["primary"])
        self.tagalog_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(self, image=self.swap_img, text="", 
                                         fg_color="transparent", hover_color="#d9d9d9",
                                         width=50, height=50,
                                         command=lambda: show_frame(JapTranslateJaptoEnglish))
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.language_option = ctk.CTkOptionMenu(self, values=["Japanese", "Korean", "Chinese"], 
                                                 command=self.on_language_select, width=120, height=40)
        self.language_option.set("Japanese")
        self.language_option.place(relx=0.86, rely=0.30, anchor="center")

        self.tagalog_label.lift()
        self.language_option.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(self, text="START", 
                                          font=get_relative_font(22, self), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.toggle_listening)
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: self.swap_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        status_file = os.path.join("Modes", "Translation", "status.json")
        if self.is_listening:
            with open(status_file, "w") as f:
                json.dump({"status": "LOADING"}, f)
            self.start_translator()
        else:
            self.stop_translator()
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(ChooseModePage)

    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapTranslate)
        elif value == "Korean":
            show_frame(KorTranslate)
        elif value == "Chinese":
            show_frame(ChiTranslate)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "JapTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            stop_path = os.path.join("Modes", "Translation", "stop.json")
            with open(stop_path, "w") as f:
                json.dump({"stop": True}, f)


        self.panda_label.configure(image=self.pandaA_img)
        self.placeholder_label.configure(text="Press START to begin")
        self.panda_toggle = False

        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")
                    if state == "SPEAKING":
                        if getattr(self, "panda_toggle", False):
                            self.set_panda("pandaB")
                        else:
                            self.set_panda("pandaC")
                        self.panda_toggle = not getattr(self, "panda_toggle", False)

                    elif state == "IDLE":
                        self.set_panda("pandaA")
                        self.panda_toggle = False
                        
                    elif state == "LOADING":
                        self.placeholder_label.configure(text="Loading Model...")
                        self.set_panda("pandaA")
                        
                    elif state == "LOADED":
                        self.placeholder_label.configure(text="Listening speak now")
                        self.set_panda("pandaA")
                        
            if os.path.exists(translation_file):
                with open (translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()
                romanized = trans_data.get("romanized_text", "").strip()

                if translated or romanized:
                    display_text = f"{romanized}\n{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading status.json", e)

        self.after(250, self.check_translator_output)

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.japanese_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)
        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)
        

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)


class JapTranslateJaptoEnglish(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Translate", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(self.bubble_frame, 
                                              text="Press START to begin", 
                                              font=get_relative_font(22, self),
                                              text_color="black", fg_color="transparent",
                                              wraplength=380, justify="center")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.tagalog_label = ctk.CTkLabel(self, text="JAPANESE", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color="#6096ba")
        self.tagalog_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(self, image=self.swap_img, text="", 
                                         fg_color="transparent", hover_color="#d9d9d9",
                                         width=50, height=50,
                                         command=lambda: show_frame(JapTranslate))
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.japanese_label = ctk.CTkLabel(self, text="TAGALOG", 
                                           font=get_relative_font(28, self, weight="bold"), 
                                           text_color="black", fg_color="#6096ba")
        self.japanese_label.place(relx=0.86, rely=0.30, anchor="center")

        self.tagalog_label.lift()
        self.japanese_label.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(self, text="START", 
                                          font=get_relative_font(22, self), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.toggle_listening)
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: show_frame(JapTranslate))
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.placeholder_label.configure(text="Listening... Speak now")
            self.start_button.configure(text="STOP")
            self.start_translator()
        else:
            self.placeholder_label.configure(text="Press START to begin")
            self.start_button.configure(text="START")
            self.stop_translator()
            self.set_panda("pandaA")
            self.panda_toggle = False

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(ChooseModePage)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "JapToFilTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            try:
                self.translator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.translator_process.kill()
            print("Translator Process Terminated")

        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False

        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")
                    if state == "SPEAKING":
                        if getattr(self, "panda_toggle", False):
                            self.set_panda("pandaB")
                        else:
                            self.set_panda("pandaC")
                        self.panda_toggle = not getattr(self, "panda_toggle", False)

                    elif state == "IDLE":
                        self.set_panda("pandaA")
                        self.panda_toggle = False
                        
            if os.path.exists(translation_file):
                with open (translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()

                if translated:
                    display_text = f"{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading statsu.json", e)

        self.after(250, self.check_translator_output)

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.japanese_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)
        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)
        

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)

class JapTutoring(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        # Language selector dropdown
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_select,
            width=160,
            height=44
        )
        self.language_option.set("Japanese")
        self.language_option.place(relx=0.82, rely=0.08, anchor="e")

        self.title = ctk.CTkLabel(
            self,
            text="Tutoring",
            font=get_relative_font(64, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.5, rely=0.08, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35, "Colors", JapColors, "colors_icon.png"),
            "animals": (0.4, 0.35, "Animals", JapAnimals, "animals_icon.png"),
            "shapes": (0.6, 0.35, "Shapes", JapShapes, "shapes_icon.png"),
            "numbers": (0.8, 0.35, "Numbers", JapNumbers, "numbers_icon.png"),
            "alphabet": (0.35, 0.65, "Japanese Alphabet", JapAlphabet, "japalphabet_icon.png"),
            "conversation": (0.65, 0.65, "Conversation", JapConversation, "conversation_icon.png"),
        }

        for key, (relx, rely, label_text, target_class, icon_file) in positions.items():
            frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
                border_width=2,
                border_color="black",
                width=btn_width,
                height=btn_height
            )
            self.frames[key] = frame

            icon = load_ctk_image(os.path.join("icons", icon_file), self, height_percentage=0.08)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[key] = btn
            btn.pack(fill="both", expand=True, padx=3, pady=3)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{key}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=100,
            height=35,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()
        
        root.bind("1", lambda event: show_frame(JapColors))
        root.bind("2", lambda event: show_frame(JapAnimals))
        root.bind("3", lambda event: show_frame(JapShapes))
        root.bind("4", lambda event: show_frame(JapNumbers))
        root.bind("5", lambda event: show_frame(JapAlphabet))
        root.bind("6", lambda event: show_frame(JapConversation))
        root.bind("0", lambda event: show_frame(ChooseModePage))

    def on_language_select(self, value):
        """Handle language dropdown selection."""
        if value == "Japanese":
            show_frame(JapTutoring)
        elif value == "Korean":
            show_frame(KorTutoring)
        elif value == "Chinese":
            show_frame(ChiTutoring)

    def update_layout(self):
        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35),
            "animals": (0.4, 0.35),
            "shapes": (0.6, 0.35),
            "numbers": (0.8, 0.35),
            "alphabet": (0.35, 0.65),
            "conversation": (0.65, 0.65),
        }

        for key, (relx, rely) in positions.items():
            frame = self.frames[key]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=rely, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{key}_icon.png"), self, height_percentage=0.08)
            if icon:
                self.buttons[key].configure(image=icon)
                self.buttons[key].image = icon

            label = self.buttons[f"{key}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            
            if key in ["alphabet", "conversation"]:
                label.place(relx=relx, rely=rely + 0.12, anchor="center")
            else:
                label.place(relx=relx, rely=rely + 0.10, anchor="center")

        self.back_button.place(relx=0.5, rely=0.92, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()

class JapColors(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Colors", 
                                  font=get_relative_font(60, self),  
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg=theme["primary"], highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self),  
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Japanese + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self),  
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)  
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, 
                                         fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, 
                                         fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(28, self),
                                         width=100, height=45,
                                         fg_color="white", text_color="black",
                                         command=lambda: show_frame(JapTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_JAPANESE = {
            "Colors": {
                "Filipino": ["Pula", "Berde", "Asul", "Dilaw", "Itim", "Kahel", "Lila", "Puti", "Ginto"],
                "Japanese": ["赤", "緑", "青", "黄色", "黒", "オレンジ", "紫", "白", "金"],
                "Romanized": ["Aka", "Midori", "Ao", "Kiiro", "Kuro", "Orenji", "Murasaki", "Shiro", "Kin"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Japanese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_JAPANESE["Colors"]["Filipino"][self.current_index]
        japanese = self.CATEGORIES_JAPANESE["Colors"]["Japanese"][self.current_index]
        romaji = self.CATEGORIES_JAPANESE["Colors"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇯🇵 {japanese}\n({romaji})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Japanese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_JAPANESE["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_JAPANESE["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
        
class JapAnimals(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Animals", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg=theme["primary"], highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Japanese + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, 
                                         fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, 
                                         fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(28, self),
                                         width=100, height=45,
                                         fg_color="white", text_color="black",
                                         command=lambda: show_frame(JapTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_JAPANESE = {
            "Animals": {
                "Filipino": [
                    "Aso", "Pusa", "Ibon", "Isda", "Kabayo", "Pato", "Tigre", 
                    "Leopardo", "Elepante", "Kangaroo", "Zebra", "Unggoy", 
                    "Leon", "Pating"
                ],
                "Japanese": [
                    "犬", "猫", "鸟", "鱼", "马", "鸭", "虎", 
                    "豹", "象", "カンガルー", "シマウマ", "猿", 
                    "ライオン", "サメ"
                ]
            }
        }

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("J", "a")
        self.converter = kakasi.getConverter()

        self.is_flipped = False  # False = Filipino, True = Japanese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_JAPANESE["Animals"]["Filipino"][self.current_index]
        japanese = self.CATEGORIES_JAPANESE["Animals"]["Japanese"][self.current_index]
        romanized = self.converter.do(japanese)
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇯🇵 {japanese}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Japanese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_JAPANESE["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_JAPANESE["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class JapShapes(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Shapes", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg=theme["primary"], highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Japanese + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, 
                                         fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", 
                                         font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, 
                                         fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(28, self),
                                         width=100, height=45,
                                         fg_color="white", text_color="black",
                                         command=lambda: show_frame(JapTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_JAPANESE = {
            "Shapes": {
                "Filipino": [
                    "Bilog", "Parihaba", "Tatsulok", "Obalo", "Puso", 
                    "Heksagono", "Octagon", "Pentagon", "Bituin", "Trapezoid"
                ],
                "Japanese": [
                    "丸", "矩形", "三角形", "楕円形", "心臓", 
                    "六角形", "八角形", "五角形", "星", "台形"
                ]
            }
        }

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("J", "a")
        self.converter = kakasi.getConverter()

        self.is_flipped = False  # False = Filipino, True = Japanese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_JAPANESE["Shapes"]["Filipino"][self.current_index]
        japanese = self.CATEGORIES_JAPANESE["Shapes"]["Japanese"][self.current_index]
        romanized = self.converter.do(japanese)
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇯🇵 {japanese}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Japanese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_JAPANESE["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_JAPANESE["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
        
class JapNumbers(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Numbers", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg=theme["primary"], highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Japanese + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(JapTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_JAPANESE = {
            "Numbers": {
                "Filipino": ["Isa", "Dalawa", "Tatlo", "Apat", "Lima", "Anim", "Pito", "Walo", "Siyam", "Sampu"],
                "Japanese": ["いち", "に", "さん", "し", "ご", "ろく", "しち", "はち", "きゅう", "じゅう"]
            }
        }

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("J", "a")
        self.converter = kakasi.getConverter()

        self.is_flipped = False  # False = Filipino, True = Japanese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_JAPANESE["Numbers"]["Filipino"][self.current_index]
        japanese = self.CATEGORIES_JAPANESE["Numbers"]["Japanese"][self.current_index]
        romanized = self.converter.do(japanese)
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇯🇵 {japanese}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Japanese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_JAPANESE["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_JAPANESE["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class JapAlphabet(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Japanese Alphabet", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg=theme["primary"], highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.65, relheight=0.4)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.65, relheight=0.4)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Hiragana)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black", justify="center")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Katakana + Romaji)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black", justify="center")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.85, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.85, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(JapTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_JAPANESE = {
            "Alphabet": {
                "Hiragana": ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と",
                             "な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も",
                             "や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん"],
                "Katakana": ["ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","チ","ツ","テ","ト",
                             "ナ","ニ","ヌ","ネ","ノ","ハ","ヒ","フ","ヘ","ホ","マ","ミ","ム","メ","モ",
                             "ヤ","ユ","ヨ","ラ","リ","ル","レ","ロ","ワ","ヲ","ン"],
                "Romaji":   ["a","i","u","e","o","ka","ki","ku","ke","ko","sa","shi","su","se","so","ta","chi","tsu","te","to",
                             "na","ni","nu","ne","no","ha","hi","fu","he","ho","ma","mi","mu","me","mo",
                             "ya","yu","yo","ra","ri","ru","re","ro","wa","(w)o","n"]
            }
        }

        self.is_flipped = False  # False = Hiragana, True = Katakana
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        hiragana = self.CATEGORIES_JAPANESE["Alphabet"]["Hiragana"][self.current_index]
        katakana = self.CATEGORIES_JAPANESE["Alphabet"]["Katakana"][self.current_index]
        romaji = self.CATEGORIES_JAPANESE["Alphabet"]["Romaji"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇯🇵 Hiragana: {hiragana}")
        self.back_label.configure(text=f"🇯🇵 {katakana}\n({romaji})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Katakana (Hiragana → Katakana)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Hiragana (Katakana → Hiragana)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_JAPANESE["Alphabet"]["Hiragana"])
        # Always show Hiragana side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_JAPANESE["Alphabet"]["Hiragana"])
        # Always show Hiragana side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
     
class JapDrills(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.drill_process = None
        self.running = True
        self.is_listening = False
        self.score = 0
        self.current_word = ""
        self.current_translation = ""
        self.current_romanized = ""
        self.user_input = ""
        self.create_ui_elements()
        self.clear_drill_json()
        self.update_drill_results()

    def create_ui_elements(self):
        # Title
        self.title = ctk.CTkLabel(self, text="Drills", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        # Language dropdown
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_changed,
            width=160,
            height=44
        )
        self.language_option.set("Japanese")
        self.language_option.place(relx=0.95, rely=0.08, anchor="ne")

        # Panda image
        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        
        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        
        self.bubble_content = ctk.CTkLabel(self.bubble_frame, 
                                           text="Choose WORDS or PHRASES to begin", 
                                           font=get_relative_font(22, self),
                                           text_color="black", fg_color="transparent",
                                           wraplength=380, justify="center")
        self.bubble_content.place(relx=0.5, rely=0.5, anchor="center")

        
        self.words_button = ctk.CTkButton(self, text="WORDS", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.start_word_drill)
        self.words_button.place(relx=0.70, rely=0.30, anchor="center")

        self.phrases_button = ctk.CTkButton(self, text="PHRASES", 
                                            font=get_relative_font(28, self, weight="bold"), 
                                            fg_color="white", text_color="black",
                                            width=140, height=50,
                                            command=self.start_phrase_drill)
        self.phrases_button.place(relx=0.86, rely=0.30, anchor="center")

        
        self.score_label = ctk.CTkLabel(self, text="Score: 0/5", 
                                        font=get_relative_font(22, self), 
                                        text_color="white", fg_color="#6096ba")
        self.score_label.place(relx=0.78, rely=0.65, anchor="n")

        
        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        # Key bindings
        root.bind("1", lambda event: self.words_button.invoke())
        root.bind("2", lambda event: self.phrases_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

    def start_word_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "JapDrill.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Word drill started! Listen and speak your answers.")

    def start_phrase_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "JapDrillPhrase.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Phrase drill started! Listen and speak your answers.")

    def on_language_changed(self, choice):
        # Only navigate if a different language is selected
        if choice == "Korean":
            self.running = False
            self.stop_drill()
            show_frame(KorDrills)
        elif choice == "Chinese":
            self.running = False
            self.stop_drill()
            show_frame(ChiDrills)
        # If "Japanese" is selected, do nothing (already on this page)

    def on_back(self):
        self.running = False
        self.stop_drill()
        show_frame(ChooseModePage)

    def stop_drill(self):
        if self.drill_process and self.drill_process.poll() is None:
            self.drill_process.terminate()
            try:
                self.drill_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.drill_process.kill()
            print("[✓] Drill process terminated.")

        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False            

    def update_score(self):
        self.score_label.configure(text=f"Score: {self.score}/5")
    
    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def update_drill_results(self):
        if not self.running:
            return
        try:
            json_path = os.path.join("Modes", "Drill", "drill_results.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                    
                    if "current_word" in data:
                        self.current_word = data["current_word"]
                    
                    if "user_input" in data:
                        self.user_input = data["user_input"]
                        # Show current question and user's answer in bubble
                        display_text = f"Filipino: {self.current_word}\n\nYour answer: {self.user_input}"
                        self.bubble_content.configure(text=display_text)
            
                    if "status" in data:
                        if data["status"] == "QUESTION":
                           self.bubble_content.configure(
                               text=f"Filipino: {data['current_word']}"
                           )
                           if getattr(self, "panda_toggle", False):
                               self.set_panda("pandaB")
                           else:
                               self.set_panda("pandaC")
                           self.panda_toggle = not getattr(self, "panda_toggle", False)
                        elif data["status"] == "ANSWER":
                            self.bubble_content.configure(
                                text=f"Your answer: {data['user_input']} ({data['user_romanized']})"
                            )
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "RESULT":
                            if data["is_correct"]:
                                result_text = (f"Correct!\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Japanese: {data['translation']} ({data['romanized']})")
                            else:
                                result_text = (f"Incorrect\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Correct answer:\nJapanese: {data['translation']} ({data['romanized']})")
                            self.bubble_content.configure(text=result_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "COMPLETE":
                            final_text = f"Drill Complete!"
                            if data['final_score'] >= 4:
                                final_text += "\n\nExcellent work!"
                            elif data['final_score'] >= 3:
                                final_text += "\n\nGood Job! Keep Practicing!"
                            else:
                                final_text += "\n\nKeep studying! You'll improve!"
                            self.bubble_content.configure(text=final_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        
        except Exception as e:
            print(f"[!] Failed to update drill results: {e}")
        
        if self.running:
            self.after(1000, self.update_drill_results)

    def clear_drill_json(self):
        results_file = os.path.join("Modes", "Drill", "drill_results.json")
        try:
            with open(results_file, "w") as f:
                json.dump({}, f)
            print("Results cleared")
        except Exception as e:
            print("Failed to clear")

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.bubble_content.configure(font=get_relative_font(22, self))
        self.words_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.phrases_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.score_label.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        
        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        
        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

# Korean Classes
class KorModePage(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.create_ui_elements()

    def create_ui_elements(self):
        self.kortext1_label = ctk.CTkLabel(
            self,
            text="Mode",
            font=get_relative_font(80, self),
            text_color="white",
            fg_color="transparent"
        )
        self.kortext1_label.place(relx=0.5, rely=0.12, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': (0.25, "Translate", KorTranslate),
            'tutoring': (0.5, "Tutoring", KorTutoring),
            'drills': (0.75, "Drills", KorDrills)
        }
        icon_paths = {
            'translate': os.path.join("icons", "translate_icon.png"),
            'tutoring': os.path.join("icons", "tutoring_icon.png"),
            'drills': os.path.join("icons", "drills_icon.png")
        }

        for btn_name, (relx, label_text, target_class) in positions.items():
            frame = ctk.CTkFrame(
                self, fg_color="transparent", border_width=4, border_color="black",
                width=btn_width, height=btn_height
            )
            self.frames[btn_name] = frame

            icon = load_ctk_image(icon_paths[btn_name], self, height_percentage=0.15)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[btn_name] = btn
            btn.pack(fill="both", expand=True, padx=10, pady=10)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{btn_name}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=160, height=60,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()

        root.bind("1", lambda event: self.buttons['translate'].invoke())
        root.bind("2", lambda event: self.buttons['tutoring'].invoke())
        root.bind("3", lambda event: self.buttons['drills'].invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def update_layout(self):
        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': 0.25,
            'tutoring': 0.5,
            'drills': 0.75
        }

        for btn_name, relx in positions.items():
            frame = self.frames[btn_name]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=0.48, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{btn_name}_icon.png"), self, height_percentage=0.15)
            if icon:
                self.buttons[btn_name].configure(image=icon)
                self.buttons[btn_name].image = icon

            label = self.buttons[f"{btn_name}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            label.place(relx=relx, rely=0.70, anchor="center")

        self.back_button.place(relx=0.5, rely=0.9, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()

class KorTranslate(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Translate", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)


        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(self.bubble_frame, 
                                              text="Press START to begin", 
                                              font=get_relative_font(22, self),
                                              text_color="black", fg_color="transparent",
                                              wraplength=380, justify="center")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.tagalog_label = ctk.CTkLabel(self, text="TAGALOG", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color=theme["primary"])
        self.tagalog_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(self, image=self.swap_img, text="", 
                                         fg_color="transparent", hover_color="#d9d9d9",
                                         width=50, height=50,
                                         command=lambda: show_frame(KorTranslateJaptoEnglish))
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.korean_label = ctk.CTkLabel(self, text="KOREAN", 
                                         font=get_relative_font(28, self, weight="bold"), 
                                         text_color="black", fg_color=theme["primary"])
        self.korean_label.place(relx=0.86, rely=0.30, anchor="center")

        self.language_option = ctk.CTkOptionMenu(self, values=["Japanese", "Korean", "Chinese"], 
                                                 command=self.on_language_select, width=120, height=40)
        self.language_option.set("Korean")
        self.language_option.place(relx=0.86, rely=0.30, anchor="center")

        self.tagalog_label.lift()
        self.language_option.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(self, text="START", 
                                          font=get_relative_font(22, self), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.toggle_listening)
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: self.swap_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(ChooseModePage)

    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapTranslate)
        elif value == "Korean":
            show_frame(KorTranslate)
        elif value == "Chinese":
            show_frame(ChiTranslate)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        status_file = os.path.join("Modes", "Translation", "status.json")
        if self.is_listening:
            with open(status_file, "w") as f:
                json.dump({"status": "LOADING"}, f)
            self.start_translator()
        else:
            self.stop_translator()
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "KorTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            stop_path = os.path.join("Modes", "Translation", "stop.json")
            with open(stop_path, "w") as f:
                json.dump({"stop": True}, f)


        self.panda_label.configure(image=self.pandaA_img)
        self.placeholder_label.configure(text="Press START to begin")
        self.panda_toggle = False

        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")
                    if state == "SPEAKING":
                        if getattr(self, "panda_toggle", False):
                            self.set_panda("pandaB")
                        else:
                            self.set_panda("pandaC")
                        self.panda_toggle = not getattr(self, "panda_toggle", False)

                    elif state == "IDLE":
                        self.set_panda("pandaA")
                        self.panda_toggle = False
                        
                    elif state == "LOADING":
                        self.placeholder_label.configure(text="Loading Model...")
                        self.set_panda("pandaA")
                        
                    elif state == "LOADED":
                        self.placeholder_label.configure(text="Listening speak now")
                        self.set_panda("pandaA")
                        
            if os.path.exists(translation_file):
                with open (translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()
                romanized = trans_data.get("romanized_text", "").strip()

                if translated or romanized:
                    display_text = f"{romanized}\n{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading statsu.json", e)

        self.after(250, self.check_translator_output)


    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.korean_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)

class KorTranslateJaptoEnglish(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Translate", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(self.bubble_frame, 
                                              text="Press START to begin", 
                                              font=get_relative_font(22, self),
                                              text_color="black", fg_color="transparent",
                                              wraplength=380, justify="center")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.korean_label = ctk.CTkLabel(self, text="KOREAN", 
                                         font=get_relative_font(28, self, weight="bold"), 
                                         text_color="black", fg_color=theme["primary"])
        self.korean_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(self, image=self.swap_img, text="", 
                                         fg_color="transparent", hover_color="#d9d9d9",
                                         width=50, height=50,
                                         command=lambda: show_frame(KorTranslate))
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.tagalog_label = ctk.CTkLabel(self, text="TAGALOG", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color=theme["primary"])
        self.tagalog_label.place(relx=0.86, rely=0.30, anchor="center")

        self.korean_label.lift()
        self.tagalog_label.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(self, text="START", 
                                          font=get_relative_font(22, self), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.toggle_listening)
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: show_frame(KorTranslate))
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.placeholder_label.configure(text="Listening... Speak now")
            self.start_button.configure(text="STOP")
            self.start_translator()
        else:
            self.placeholder_label.configure(text="Press START to begin")
            self.start_button.configure(text="START")
            self.stop_translator()
            self.set_panda("pandaA")
            self.panda_toggle = False

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(KorModePage)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "KorToFilTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            try:
                self.translator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.translator_process.kill()
            print("Translator Process Terminated")

        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False

        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")
                    if state == "SPEAKING":
                        if getattr(self, "panda_toggle", False):
                            self.set_panda("pandaB")
                        else:
                            self.set_panda("pandaC")
                        self.panda_toggle = not getattr(self, "panda_toggle", False)

                    elif state == "IDLE":
                        self.set_panda("pandaA")
                        self.panda_toggle = False
                        
            if os.path.exists(translation_file):
                with open (translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()

                if translated:
                    display_text = f"{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading statsu.json", e)

        self.after(250, self.check_translator_output)

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.korean_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)
        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)

class KorTutoring(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()

    def create_ui_elements(self):
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_select,
            width=160,
            height=44
        )
        self.language_option.set("Korean")
        self.language_option.place(relx=0.82, rely=0.08, anchor="e")

        theme = get_current_theme()
        self.title = ctk.CTkLabel(
            self,
            text="Tutoring",
            font=get_relative_font(64, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.5, rely=0.08, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35, "Colors", KorColors, "colors_icon.png"),
            "animals": (0.4, 0.35, "Animals", KorAnimals, "animals_icon.png"),
            "shapes": (0.6, 0.35, "Shapes", KorShapes, "shapes_icon.png"),
            "numbers": (0.8, 0.35, "Numbers", KorNumbers, "numbers_icon.png"),
            "alphabet": (0.35, 0.65, "Korean Alphabet", KorAlphabet, "koralphabet_icon.png"),
            "conversation": (0.65, 0.65, "Conversation", KorConversation, "conversation_icon.png"),
        }

        for key, (relx, rely, label_text, target_class, icon_file) in positions.items():
            frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
                border_width=2,
                border_color="black",
                width=btn_width,
                height=btn_height
            )
            self.frames[key] = frame

            icon = load_ctk_image(os.path.join("icons", icon_file), self, height_percentage=0.08)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[key] = btn
            btn.pack(fill="both", expand=True, padx=3, pady=3)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{key}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=100,
            height=35,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()
        
        root.bind("1", lambda event: show_frame(KorColors))
        root.bind("2", lambda event: show_frame(KorAnimals))
        root.bind("3", lambda event: show_frame(KorShapes))
        root.bind("4", lambda event: show_frame(KorNumbers))
        root.bind("5", lambda event: show_frame(KorAlphabet))
        root.bind("6", lambda event: show_frame(ChooseModePage))

    def on_language_select(self, value):
        """Handle language dropdown selection."""
        if value == "Japanese":
            show_frame(JapTutoring)
        elif value == "Korean":
            show_frame(KorTutoring)
        elif value == "Chinese":
            show_frame(ChiTutoring)

    def update_layout(self):
        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35),
            "animals": (0.4, 0.35),
            "shapes": (0.6, 0.35),
            "numbers": (0.8, 0.35),
            "alphabet": (0.35, 0.65),
            "conversation": (0.65, 0.65),
        }

        for key, (relx, rely) in positions.items():
            frame = self.frames[key]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=rely, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{key}_icon.png"), self, height_percentage=0.08)
            if icon:
                self.buttons[key].configure(image=icon)
                self.buttons[key].image = icon

            label = self.buttons[f"{key}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            
            if key in ["alphabet", "conversation"]:
                label.place(relx=relx, rely=rely + 0.12, anchor="center")
            else:
                label.place(relx=relx, rely=rely + 0.10, anchor="center")

        self.back_button.place(relx=0.5, rely=0.92, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()


# Korean tutoring subpages

class KorColors(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Colors (색깔)", 
                                  font=get_relative_font(60, self),  
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Korean + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(KorTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_KOREAN = {
            "Colors": {
                "Filipino": ["Pula", "Berde", "Asul", "Dilaw", "Itim", "Kahel", "Lila", "Puti"],
                "Korean":   ["빨강", "초록", "파랑", "노랑", "검정", "주황", "보라", "하얀"],
                "Romanized": ["Ppalgang", "Chorok", "Parang", "Norang", "Geomjeong", "Juhwang", "Bora", "Hayan"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Korean
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_KOREAN["Colors"]["Filipino"][self.current_index]
        korean = self.CATEGORIES_KOREAN["Colors"]["Korean"][self.current_index]
        romanized = self.CATEGORIES_KOREAN["Colors"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇰🇷 {korean}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Korean (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_KOREAN["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_KOREAN["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class KorAnimals(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Animals (동물)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Korean + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(KorTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_KOREAN = {
            "Animals": {
                "Filipino": ["Aso", "Pusa", "Ibon", "Isda", "Kabayo", "Pato", "Unggoy", "Elepante"],
                "Korean":   ["개", "고양이", "새", "물고기", "말", "오리", "원숭이", "코끼리"],
                "Romanized": ["Gae", "Goyangi", "Sae", "Mulgogi", "Mal", "Ori", "Wonsungi", "Kokkiri"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Korean
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_KOREAN["Animals"]["Filipino"][self.current_index]
        korean = self.CATEGORIES_KOREAN["Animals"]["Korean"][self.current_index]
        romanized = self.CATEGORIES_KOREAN["Animals"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇰🇷 {korean}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Korean (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_KOREAN["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_KOREAN["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class KorNumbers(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Numbers (숫자)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Korean + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(KorTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_KOREAN = {
            "Numbers": {
                "Filipino": ["Isa", "Dalawa", "Tatlo", "Apat", "Lima", "Anim", "Pito", "Walo", "Siyam", "Sampu"],
                "Korean":   ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열"],
                "Romanized": ["Hana", "Dul", "Set", "Net", "Daseot", "Yeoseot", "Ilgop", "Yeodeol", "Ahop", "Yeol"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Korean
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_KOREAN["Numbers"]["Filipino"][self.current_index]
        korean = self.CATEGORIES_KOREAN["Numbers"]["Korean"][self.current_index]
        romanized = self.CATEGORIES_KOREAN["Numbers"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇰🇷 {korean}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    # COPY ALL THESE METHODS FROM KorAnimals CLASS - THEY ARE IDENTICAL
    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Korean (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_KOREAN["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_KOREAN["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class KorShapes(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Shapes (모양)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Korean + Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(KorTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_KOREAN = {
            "Shapes": {
                "Filipino": ["Bilog", "Parihaba", "Tatsulok", "Obalo", "Puso", "Heksagono", "Octagon", "Pentagon", "Bituin", "Trapezoid"],
                "Korean":   ["원", "직사각형", "삼각형", "타원", "하트", "육각형", "팔각형", "오각형", "별", "사다리꼴"],
                "Romanized": ["Won", "Jiksa-gakhyeong", "Samgakhyeong", "Tawon", "Hateu", "Yukgakhyeong", "Pal-gakhyeong", "Ogakhyeong", "Byeol", "Sadari-kkol"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Korean
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_KOREAN["Shapes"]["Filipino"][self.current_index]
        korean = self.CATEGORIES_KOREAN["Shapes"]["Korean"][self.current_index]
        romanized = self.CATEGORIES_KOREAN["Shapes"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇰🇷 {korean}\n({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Korean (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_KOREAN["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_KOREAN["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
        
class KorAlphabet(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Korean Alphabet (한글)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.65, relheight=0.4)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.65, relheight=0.4)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Hangul)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black", justify="center")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Romanized)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black", justify="center")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.85, anchor="center")

        # REMOVED the flip button - the flashcard itself is now the flip button

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.85, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(KorTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_KOREAN = {
            "Alphabet": {
                "Hangul":    ["ㄱ","ㄴ","ㄷ","ㄹ","ㅁ","ㅂ","ㅅ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ",
                              "ㅏ","ㅑ","ㅓ","ㅕ","ㅗ","ㅛ","ㅜ","ㅠ","ㅡ","ㅣ"],
                "Romanized": ["g/k","n","d/t","r/l","m","b/p","s","ng","j","ch","k","t","p","h",
                              "a","ya","eo","yeo","o","yo","u","yu","eu","i"]
            }
        }

        self.is_flipped = False  # False = Hangul, True = Romanized
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        hangul = self.CATEGORIES_KOREAN["Alphabet"]["Hangul"][self.current_index]
        romanized = self.CATEGORIES_KOREAN["Alphabet"]["Romanized"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇰🇷 {hangul}")
        self.back_label.configure(text=f"({romanized})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Romanized (Hangul → Romanized)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Hangul (Romanized → Hangul)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_KOREAN["Alphabet"]["Hangul"])
        # Always show Hangul side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_KOREAN["Alphabet"]["Hangul"])
        # Always show Hangul side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
        
class KorDrills(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.drill_process = None
        self.running = True
        self.is_listening = False
        self.score = 0
        self.current_word = ""
        self.current_translation = ""
        self.current_romanized = ""
        self.user_input = ""
        self.create_ui_elements()
        self.clear_drill_json()
        self.update_drill_results()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Drills", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        # Language dropdown
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_changed,
            width=160,
            height=44
        )
        self.language_option.set("Korean")
        self.language_option.place(relx=0.95, rely=0.08, anchor="ne")

        # Panda image
        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.bubble_content = ctk.CTkLabel(self.bubble_frame, 
                                           text="Choose WORDS or PHRASES to begin", 
                                           font=get_relative_font(22, self),
                                           text_color="black", fg_color="transparent",
                                           wraplength=380, justify="center")
        self.bubble_content.place(relx=0.5, rely=0.5, anchor="center")

        self.words_button = ctk.CTkButton(self, text="WORDS", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.start_word_drill)
        self.words_button.place(relx=0.70, rely=0.30, anchor="center")

        self.phrases_button = ctk.CTkButton(self, text="PHRASES", 
                                            font=get_relative_font(28, self, weight="bold"), 
                                            fg_color="white", text_color="black",
                                            width=140, height=50,
                                            command=self.start_phrase_drill)
        self.phrases_button.place(relx=0.86, rely=0.30, anchor="center")

        self.score_label = ctk.CTkLabel(self, text="Score: 0/5", 
                                        font=get_relative_font(22, self), 
                                        text_color="white", fg_color="#6096ba")
        self.score_label.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.words_button.invoke())
        root.bind("2", lambda event: self.phrases_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

    def start_word_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "KorDrill.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Word drill started! Listen and speak your answers.")

    def start_phrase_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "KorDrillPhrase.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Phrase drill started! Listen and speak your answers.")

    def on_language_changed(self, choice):
        # Only navigate if a different language is selected
        if choice == "Japanese":
            self.running = False
            self.stop_drill()
            show_frame(JapDrills)
        elif choice == "Chinese":
            self.running = False
            self.stop_drill()
            show_frame(ChiDrills)
        # If "Korean" is selected, do nothing (already on this page)

    def on_back(self):
        self.running = False
        self.stop_drill()
        show_frame(KorModePage)

    def stop_drill(self):
        if self.drill_process and self.drill_process.poll() is None:
            self.drill_process.terminate()
            try:
                self.drill_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.drill_process.kill()
            print("[✓] Drill process terminated.")
        
        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False

    def update_score(self):
        self.score_label.configure(text=f"Score: {self.score}/5")

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def update_drill_results(self):
        if not self.running:
            return
        try:
            json_path = os.path.join("Modes", "Drill", "drill_results.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                    
                    if "current_word" in data:
                        self.current_word = data["current_word"]
                    
                    if "user_input" in data:
                        self.user_input = data["user_input"]
                        # Show current question and user's answer in bubble
                        display_text = f"Filipino: {self.current_word}\n\nYour answer: {self.user_input}"
                        self.bubble_content.configure(text=display_text)
            
                    if "status" in data:
                        if data["status"] == "QUESTION":
                           self.bubble_content.configure(
                               text=f"Filipino: {data['current_word']}"
                           )
                           if getattr(self, "panda_toggle", False):
                               self.set_panda("pandaB")
                           else:
                               self.set_panda("pandaC")
                           self.panda_toggle = not getattr(self, "panda_toggle", False)
                        elif data["status"] == "ANSWER":
                            self.bubble_content.configure(
                                text=f"Your answer: {data['user_input']} ({data['user_romanized']})"
                            )
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "RESULT":
                            if data["is_correct"]:
                                result_text = (f"Correct!\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Korean: {data['translation']} ({data['romanized']})")
                            else:
                                result_text = (f"Incorrect\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Correct answer:\nKorean: {data['translation']} ({data['romanized']})")
                            self.bubble_content.configure(text=result_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "COMPLETE":
                            final_text = f"Drill Complete!"
                            if data['final_score'] >= 4:
                                final_text += "\n\nExcellent work!"
                            elif data['final_score'] >= 3:
                                final_text += "\n\nGood Job! Keep Practicing!"
                            else:
                                final_text += "\n\nKeep studying! You'll improve!"
                            self.bubble_content.configure(text=final_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        
        except Exception as e:
            print(f"[!] Failed to update drill results: {e}")

        if self.running:
            self.after(1000, self.update_drill_results)

    def clear_drill_json(self):
        results_file = os.path.join("Modes", "Drill", "drill_results.json")
        try:
            with open(results_file, "w") as f:
                json.dump({}, f)
            print("Results cleared")
        except Exception as e:
            print("Failed to clear")


    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.bubble_content.configure(font=get_relative_font(22, self))
        self.words_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.phrases_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.score_label.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

# Chinese Classes 
class ChiModePage(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.create_ui_elements()

    def create_ui_elements(self):
        self.chitext1_label = ctk.CTkLabel(
            self,
            text="Mode",
            font=get_relative_font(80, self),
            text_color="white",
            fg_color="transparent"
        )
        self.chitext1_label.place(relx=0.5, rely=0.12, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': (0.25, "Translate", ChiTranslate),
            'tutoring': (0.5, "Tutoring", ChiTutoring),
            'drills': (0.75, "Drills", ChiDrills)
        }
        icon_paths = {
            'translate': os.path.join("icons", "translate_icon.png"),
            'tutoring': os.path.join("icons", "tutoring_icon.png"),
            'drills': os.path.join("icons", "drills_icon.png")
        }

        for btn_name, (relx, label_text, target_class) in positions.items():
            frame = ctk.CTkFrame(
                self, fg_color="transparent", border_width=4, border_color="black",
                width=btn_width, height=btn_height
            )
            self.frames[btn_name] = frame

            icon = load_ctk_image(icon_paths[btn_name], self, height_percentage=0.15)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[btn_name] = btn
            btn.pack(fill="both", expand=True, padx=10, pady=10)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{btn_name}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=160, height=60,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()

        root.bind("1", lambda event: self.buttons['translate'].invoke())
        root.bind("2", lambda event: self.buttons['tutoring'].invoke())
        root.bind("3", lambda event: self.buttons['drills'].invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def update_layout(self):
        btn_width = max(int(self.winfo_width() * 0.18), 200)
        btn_height = max(int(self.winfo_height() * 0.20), 180)
        label_font_size = 42

        positions = {
            'translate': 0.25,
            'tutoring': 0.5,
            'drills': 0.75
        }

        for btn_name, relx in positions.items():
            frame = self.frames[btn_name]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=0.48, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{btn_name}_icon.png"), self, height_percentage=0.15)
            if icon:
                self.buttons[btn_name].configure(image=icon)
                self.buttons[btn_name].image = icon

            label = self.buttons[f"{btn_name}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            label.place(relx=relx, rely=0.70, anchor="center")

        self.back_button.place(relx=0.5, rely=0.9, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()

class ChiTranslate(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(
            self,
            text="Translate",
            font=get_relative_font(48, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")

        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(
                self,
                image=self.pandaA_img,
                text="",
                fg_color="transparent"
            )
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            border_color="black",
            border_width=3,
            corner_radius=20,
            width=420,
            height=180
        )
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(
            self.bubble_frame,
            text="Press START to begin",
            font=get_relative_font(22, self),
            text_color="black",
            fg_color="transparent",
            wraplength=380,
            justify="center"
        )
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.tagalog_label = ctk.CTkLabel(
            self,
            text="TAGALOG",
            font=get_relative_font(28, self, weight="bold"),
            text_color="black",
            fg_color=theme["primary"]
        )
        self.tagalog_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(
            self,
            image=self.swap_img,
            text="",
            fg_color="transparent",
            hover_color="#d9d9d9",
            width=50,
            height=50,
            command=lambda: show_frame(ChiTranslateJaptoEnglish)
        )
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.chinese_label = ctk.CTkLabel(
            self,
            text="CHINESE",
            font=get_relative_font(28, self, weight="bold"),
            text_color="black",
            fg_color=theme["primary"]
        )
        self.chinese_label.place(relx=0.86, rely=0.30, anchor="center")

        self.language_option = ctk.CTkOptionMenu(
            self,
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_select,
            width=120,
            height=40
        )
        self.language_option.set("Chinese")
        self.language_option.place(relx=0.86, rely=0.30, anchor="center")

        self.tagalog_label.lift()
        self.language_option.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(
            self,
            text="START",
            font=get_relative_font(22, self),
            fg_color="white",
            text_color="black",
            width=140,
            height=50,
            command=self.toggle_listening
        )
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(18, self),
            fg_color="white",
            text_color="black",
            width=100,
            height=40,
            command=self.on_back
        )
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: self.swap_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(ChooseModePage)

    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapTranslate)
        elif value == "Korean":
            show_frame(KorTranslate)
        elif value == "Chinese":
            show_frame(ChiTranslate)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        status_file = os.path.join("Modes", "Translation", "status.json")

        if self.is_listening:
            with open(status_file, "w") as f:
                json.dump({"status": "LOADING"}, f)
            self.start_translator()
        else:
            self.stop_translator()
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "ChineseTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            stop_path = os.path.join("Modes", "Translation", "stop.json")
            with open(stop_path, "w") as f:
                json.dump({"stop": True}, f)

        # Reset visual
        self.panda_label.configure(image=self.pandaA_img)
        self.placeholder_label.configure(text="Press START to begin")
        self.panda_toggle = False

        # Clear translation file
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        # Reset status file
        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")

        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")

                if state == "SPEAKING":
                    if getattr(self, "panda_toggle", False):
                        self.set_panda("pandaB")
                    else:
                        self.set_panda("pandaC")
                    self.panda_toggle = not getattr(self, "panda_toggle", False)

                elif state == "IDLE":
                    self.set_panda("pandaA")
                    self.panda_toggle = False

                elif state == "LOADING":
                    self.placeholder_label.configure(text="Loading Model...")
                    self.set_panda("pandaA")

                elif state == "LOADED":
                    self.placeholder_label.configure(text="Listening speak now")
                    self.set_panda("pandaA")

            if os.path.exists(translation_file):
                with open(translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()
                romanized = trans_data.get("romanized_text", "").strip()

                if translated or romanized:
                    display_text = f"{romanized}\n{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading status.json", e)

        self.after(250, self.check_translator_output)

    def update_elements(self):
        super().update_elements()

        self.title.configure(font=get_relative_font(48, self))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.chinese_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")

        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)

class ChiTranslateJaptoEnglish(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.translator_process = None
        self.running = True
        self.is_listening = False
        self.create_ui_elements()

    def create_ui_elements(self):
        theme = get_current_theme()
        self.title = ctk.CTkLabel(self, text="Translate", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.placeholder_label = ctk.CTkLabel(self.bubble_frame, 
                                              text="Press START to begin", 
                                              font=get_relative_font(22, self),
                                              text_color="black", fg_color="transparent",
                                              wraplength=380, justify="center")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.chinese_label = ctk.CTkLabel(self, text="CHINESE", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color=theme["primary"])
        self.chinese_label.place(relx=0.70, rely=0.30, anchor="center")

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        self.swap_button = ctk.CTkButton(self, image=self.swap_img, text="", 
                                         fg_color="transparent", hover_color="#d9d9d9",
                                         width=50, height=50,
                                         command=lambda: show_frame(ChiTranslate))
        self.swap_button.place(relx=0.78, rely=0.30, anchor="center")

        self.tagalog_label = ctk.CTkLabel(self, text="TAGALOG", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          text_color="black", fg_color=theme["primary"])
        self.tagalog_label.place(relx=0.86, rely=0.30, anchor="center")

        self.chinese_label.lift()
        self.tagalog_label.lift()
        self.swap_button.lift()

        self.start_button = ctk.CTkButton(self, text="START", 
                                          font=get_relative_font(22, self), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.toggle_listening)
        self.start_button.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.start_button.invoke())
        root.bind("2", lambda event: show_frame(ChiTranslate))
        root.bind("3", lambda event: self.back_button.invoke())

        self.after(250, self.check_translator_output)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.placeholder_label.configure(text="Listening... Speak now")
            self.start_button.configure(text="STOP")
            self.start_translator()
        else:
            self.placeholder_label.configure(text="Press START to begin")
            self.start_button.configure(text="START")
            self.stop_translator()
            self.set_panda("pandaA")
            self.panda_toggle = False

    def on_back(self):
        self.running = False
        self.stop_translator()
        show_frame(ChiModePage)

    def start_translator(self):
        if self.translator_process is None or self.translator_process.poll() is not None:
            script_path = os.path.join("Modes", "Translation", "ChiToFilTranslator.py")
            self.translator_process = subprocess.Popen(["python3", script_path])

    def stop_translator(self):
        if self.translator_process and self.translator_process.poll() is None:
            self.translator_process.terminate()
            try:
                self.translator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.translator_process.kill()
            print("Translator Process Terminated")

        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False

        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            with open(translation_file, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
        except Exception as e:
            print("Error clearing translation file:", e)

        status_file = os.path.join("Modes", "Translation", "status.json")
        try:
            with open(status_file, "w") as f:
                json.dump({"status": "IDLE"}, f)
        except Exception as e:
            print("Failed to reset status:", e)

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)

    def check_translator_output(self):
        status_file = os.path.join("Modes", "Translation", "status.json")
        translation_file = os.path.join("Modes", "Translation", "translation_data.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    data = json.load(f)
                    state = data.get("status", "")
                    if state == "SPEAKING":
                        if getattr(self, "panda_toggle", False):
                            self.set_panda("pandaB")
                        else:
                            self.set_panda("pandaC")
                        self.panda_toggle = not getattr(self, "panda_toggle", False)

                    elif state == "IDLE":
                        self.set_panda("pandaA")
                        self.panda_toggle = False
                        
            if os.path.exists(translation_file):
                with open (translation_file, "r") as f:
                    trans_data = json.load(f)

                translated = trans_data.get("translated_text", "").strip()

                if translated:
                    display_text = f"{translated}"
                    self.placeholder_label.configure(text=display_text, justify="center")

        except Exception as e:
            print("error reading statsu.json", e)

        self.after(250, self.check_translator_output)

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.chinese_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.tagalog_label.configure(font=get_relative_font(28, self, weight="bold"))
        self.placeholder_label.configure(font=get_relative_font(22, self))
        self.start_button.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)

        swap_path = os.path.join("assets", "swap.png")
        self.swap_img = load_ctk_image(swap_path, self, height_percentage=0.06)
        if self.swap_img:
            self.swap_button.configure(image=self.swap_img)

class ChiTutoring(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.create_ui_elements()

    def create_ui_elements(self):
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_select,
            width=160,
            height=44
        )
        self.language_option.set("Chinese")
        self.language_option.place(relx=0.82, rely=0.08, anchor="e")

        theme = get_current_theme()
        self.title = ctk.CTkLabel(
            self,
            text="Tutoring",
            font=get_relative_font(64, self),
            text_color="white",
            fg_color=theme["primary"]
        )
        self.title.place(relx=0.5, rely=0.08, anchor="center")

        self.buttons = {}
        self.frames = {}

        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35, "Colors", ChiColors, "colors_icon.png"),
            "animals": (0.4, 0.35, "Animals", ChiAnimals, "animals_icon.png"),
            "shapes": (0.6, 0.35, "Shapes", ChiShapes, "shapes_icon.png"),
            "numbers": (0.8, 0.35, "Numbers", ChiNumbers, "numbers_icon.png"),
            "alphabet": (0.35, 0.65, "Chinese Alphabet", ChiAlphabet, "chialphabet_icon.png"),
            "conversation": (0.65, 0.65, "Conversation", ChiConversation, "conversation_icon.png"),
        }

        for key, (relx, rely, label_text, target_class, icon_file) in positions.items():
            frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
                border_width=2,
                border_color="black",
                width=btn_width,
                height=btn_height
            )
            self.frames[key] = frame

            icon = load_ctk_image(os.path.join("icons", icon_file), self, height_percentage=0.08)

            btn = ctk.CTkButton(
                frame,
                image=icon if icon else None,
                text="",
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                command=lambda cls=target_class: show_frame(cls)
            )
            btn.image = icon
            self.buttons[key] = btn
            btn.pack(fill="both", expand=True, padx=3, pady=3)

            label = ctk.CTkLabel(
                self,
                text=label_text,
                font=get_relative_font(label_font_size, self),
                text_color="black",
                fg_color="transparent"
            )
            self.buttons[f"{key}_label"] = label

        self.back_button = ctk.CTkButton(
            self,
            text="BACK",
            font=get_relative_font(28, self),
            width=100,
            height=35,
            command=lambda: show_frame(ChooseModePage),
            fg_color="white",
            text_color="black"
        )

        self.update_layout()
        
        root.bind("1", lambda event: show_frame(ChiColors))
        root.bind("2", lambda event: show_frame(ChiAnimals))
        root.bind("3", lambda event: show_frame(ChiShapes))
        root.bind("4", lambda event: show_frame(ChiNumbers))
        root.bind("5", lambda event: show_frame(ChiAlphabet))
        root.bind("6", lambda event: show_frame(ChooseModePage))

    def on_language_select(self, value):
        """Handle language dropdown selection."""
        if value == "Japanese":
            show_frame(JapTutoring)
        elif value == "Korean":
            show_frame(KorTutoring)
        elif value == "Chinese":
            show_frame(ChiTutoring)

    def update_layout(self):
        btn_width = 110
        btn_height = 100
        label_font_size = 30

        positions = {
            "colors": (0.2, 0.35),
            "animals": (0.4, 0.35),
            "shapes": (0.6, 0.35),
            "numbers": (0.8, 0.35),
            "alphabet": (0.35, 0.65),
            "conversation": (0.65, 0.65),
        }

        for key, (relx, rely) in positions.items():
            frame = self.frames[key]
            frame.configure(width=btn_width, height=btn_height)
            frame.place(relx=relx, rely=rely, anchor="center")

            icon = load_ctk_image(os.path.join("icons", f"{key}_icon.png"), self, height_percentage=0.08)
            if icon:
                self.buttons[key].configure(image=icon)
                self.buttons[key].image = icon

            label = self.buttons[f"{key}_label"]
            label.configure(font=get_relative_font(label_font_size, self))
            
            if key in ["alphabet", "conversation"]:
                label.place(relx=relx, rely=rely + 0.12, anchor="center")
            else:
                label.place(relx=relx, rely=rely + 0.10, anchor="center")

        self.back_button.place(relx=0.5, rely=0.92, anchor="center")

    def update_elements(self):
        super().update_elements()
        self.update_layout()

# Chinese tutoring subpages

class ChiColors(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Colors (颜色)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Chinese + Pinyin)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(ChiTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_CHINESE = {
            "Colors": {
                "Filipino": ["Pula", "Berde", "Asul", "Dilaw", "Itim", "Kahel", "Lila", "Puti", "Ginto"],
                "Chinese":  ["红色", "绿色", "蓝色", "黄色", "黑色", "橙色", "紫色", "白色", "金色"],
                "Pinyin":   ["hóng sè", "lǜ sè", "lán sè", "huáng sè", "hēi sè", "chéng sè", "zǐ sè", "bái sè", "jīn sè"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Chinese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_CHINESE["Colors"]["Filipino"][self.current_index]
        chinese = self.CATEGORIES_CHINESE["Colors"]["Chinese"][self.current_index]
        pinyin = self.CATEGORIES_CHINESE["Colors"]["Pinyin"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇨🇳 {chinese}\n({pinyin})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Chinese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_CHINESE["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_CHINESE["Colors"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class ChiAnimals(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Animals (动物)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Chinese + Pinyin)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(ChiTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_CHINESE = {
            "Animals": {
                "Filipino": ["Aso", "Pusa", "Ibon", "Isda", "Kabayo", "Pato", "Elepante", "Unggoy", "Leon", "Tigre"],
                "Chinese":  ["狗", "猫", "鸟", "鱼", "马", "鸭", "大象", "猴子", "狮子", "老虎"],
                "Pinyin":   ["gǒu", "māo", "niǎo", "yú", "mǎ", "yā", "dà xiàng", "hóu zi", "shī zi", "lǎo hǔ"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Chinese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_CHINESE["Animals"]["Filipino"][self.current_index]
        chinese = self.CATEGORIES_CHINESE["Animals"]["Chinese"][self.current_index]
        pinyin = self.CATEGORIES_CHINESE["Animals"]["Pinyin"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇨🇳 {chinese}\n({pinyin})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Chinese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_CHINESE["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_CHINESE["Animals"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class ChiNumbers(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Numbers (数字)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Chinese + Pinyin)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(ChiTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_CHINESE = {
            "Numbers": {
                "Filipino": ["Isa", "Dalawa", "Tatlo", "Apat", "Lima", "Anim", "Pito", "Walo", "Siyam", "Sampu"],
                "Chinese":  ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"],
                "Pinyin":   ["yī", "èr", "sān", "sì", "wǔ", "liù", "qī", "bā", "jiǔ", "shí"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Chinese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_CHINESE["Numbers"]["Filipino"][self.current_index]
        chinese = self.CATEGORIES_CHINESE["Numbers"]["Chinese"][self.current_index]
        pinyin = self.CATEGORIES_CHINESE["Numbers"]["Pinyin"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇨🇳 {chinese}\n({pinyin})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Chinese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_CHINESE["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_CHINESE["Numbers"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()

class ChiShapes(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Shapes (形状)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.55, relheight=0.35)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.55, relheight=0.35)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Filipino)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Chinese + Pinyin)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.82, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.82, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(ChiTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_CHINESE = {
            "Shapes": {
                "Filipino": ["Bilog", "Parihaba", "Tatsulok", "Obalo", "Puso", "Heksagono", "Octagon", "Pentagon", "Bituin", "Trapezoid"],
                "Chinese":  ["圆形", "矩形", "三角形", "椭圆", "心形", "六边形", "八边形", "五边形", "星形", "梯形"],
                "Pinyin":   ["yuán xíng", "jǔ xíng", "sān jiǎo xíng", "tuǒ yuán", "xīn xíng", "liù biān xíng", "bā biān xíng", "wǔ biān xíng", "xīng xíng", "tī xíng"]
            }
        }

        self.is_flipped = False  # False = Filipino, True = Chinese
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        filipino = self.CATEGORIES_CHINESE["Shapes"]["Filipino"][self.current_index]
        chinese = self.CATEGORIES_CHINESE["Shapes"]["Chinese"][self.current_index]
        pinyin = self.CATEGORIES_CHINESE["Shapes"]["Pinyin"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇵🇭 {filipino}")
        self.back_label.configure(text=f"🇨🇳 {chinese}\n({pinyin})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    # COPY ALL THESE METHODS FROM ChiAnimals CLASS - THEY ARE IDENTICAL
    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Chinese (front → back)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Filipino (back → front)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_CHINESE["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_CHINESE["Shapes"]["Filipino"])
        # Always show Filipino side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
             
class ChiAlphabet(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.current_index = 0
        self.create_ui_elements()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Chinese Alphabet (拼音)", 
                                  font=get_relative_font(60, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        # Create canvas for flip animation
        self.canvas = ctk.CTkCanvas(self, bg="#6096ba", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", 
                         relwidth=0.65, relheight=0.4)

        # Create the actual flashcard frames (will be drawn on canvas)
        self.flashcard_frame = ctk.CTkFrame(self, fg_color="white", 
                                           corner_radius=20, 
                                           border_width=4, 
                                           border_color="black")
        self.flashcard_frame.place(relx=0.5, rely=0.5, anchor="center", 
                                  relwidth=0.65, relheight=0.4)
        self.flashcard_frame.lower()  # Keep it hidden, we'll use canvas for animation

        # Front side label (Character)
        self.front_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                       font=get_relative_font(52, self), 
                                       text_color="black", justify="center")
        self.front_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Back side label (Pinyin)
        self.back_label = ctk.CTkLabel(self.flashcard_frame, text="", 
                                      font=get_relative_font(52, self), 
                                      text_color="black", justify="center")
        self.back_label.place(relx=0.5, rely=0.5, anchor="center")
        self.back_label.lower()

        # Make canvas clickable
        self.canvas.bind("<Button-1>", lambda e: self.flip_card())
        self.canvas.configure(cursor="hand2")

        btn_font = get_relative_font(30, self)
        btn_w, btn_h = 120, 50

        self.prev_button = ctk.CTkButton(self, text="← Prev", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_prev, fg_color="white", text_color="black")
        self.prev_button.place(relx=0.3, rely=0.85, anchor="center")

        self.next_button = ctk.CTkButton(self, text="Next →", font=btn_font, width=btn_w, height=btn_h,
                                         command=self.show_next, fg_color="white", text_color="black")
        self.next_button.place(relx=0.7, rely=0.85, anchor="center")

        self.back_button = ctk.CTkButton(self, text="BACK", font=get_relative_font(28, self),
                                         width=100, height=45, fg_color="white", text_color="black",
                                         command=lambda: show_frame(ChiTutoring))
        self.back_button.place(relx=0.08, rely=0.92, anchor="w")

        self.CATEGORIES_CHINESE = {
            "Alphabet": {
                "Character": ["ㄅ", "ㄆ", "ㄇ", "ㄈ", "ㄉ", "ㄊ", "ㄋ", "ㄌ", "ㄍ", "ㄎ", "ㄏ"],
                "Pinyin":    ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h"]
            }
        }

        self.is_flipped = False  # False = Character, True = Pinyin
        self.is_animating = False
        self.show_card()

        # Bind keyboard shortcuts
        root.bind("1", lambda event: self.flip_card())
        root.bind("2", lambda event: self.prev_button.invoke())
        root.bind("3", lambda event: self.next_button.invoke())
        root.bind("4", lambda event: self.back_button.invoke())

    def show_card(self):
        char = self.CATEGORIES_CHINESE["Alphabet"]["Character"][self.current_index]
        pinyin = self.CATEGORIES_CHINESE["Alphabet"]["Pinyin"][self.current_index]
        
        # Update both labels
        self.front_label.configure(text=f"🇨🇳 {char}")
        self.back_label.configure(text=f"({pinyin})")

        # Show the correct label based on current flip state
        if self.is_flipped:
            self.back_label.lift()
            self.front_label.lower()
        else:
            self.front_label.lift()
            self.back_label.lower()

        # Draw current state on canvas
        self.draw_card()

    def draw_card(self):
        """Draw the current card state on canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Prevent drawing if canvas is too small
            return
            
        # Draw card background
        self.canvas.create_rectangle(2, 2, width-2, height-2, 
                                   fill="white", outline="black", width=4)
        
        # Draw card content based on current flip state
        if self.is_flipped:
            text = self.back_label.cget("text")
        else:
            text = self.front_label.cget("text")
        
        # Split text into lines if it contains newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            y_pos = height // 2 - (len(lines) - 1) * 20 + i * 40
            self.canvas.create_text(width // 2, y_pos, text=line, 
                                  font=("Arial", 32), fill="black")

    def flip_card(self):
        """Flip the card to the opposite side and stay there"""
        if not self.is_animating:
            self.is_animating = True
            # Determine the target flip state (opposite of current)
            target_flipped = not self.is_flipped
            self.animate_flip(target_flipped)

    def animate_flip(self, target_flipped):
        def animation():
            steps = 20
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10 or height < 10:  # Skip animation if canvas is too small
                self.is_flipped = target_flipped
                self.show_card()
                self.is_animating = False
                return
            
            # Determine animation direction
            if target_flipped:
                # Flip to Pinyin (Character → Pinyin)
                start_angle = 0
                end_angle = 180
            else:
                # Flip back to Character (Pinyin → Character)
                start_angle = 180
                end_angle = 360
            
            # Animate the flip
            for i in range(steps + 1):
                self.canvas.delete("all")
                progress = i / steps
                current_angle = start_angle + progress * (end_angle - start_angle)
                
                # Draw rotating card
                self.draw_rotating_card(width, height, current_angle, target_flipped)
                time.sleep(0.6 / steps)
            
            # Update the final flip state and redraw
            self.is_flipped = target_flipped
            self.show_card()  # This will redraw the final state
            self.is_animating = False
        
        threading.Thread(target=animation, daemon=True).start()

    def draw_rotating_card(self, width, height, angle, target_flipped):
        """Draw a card at the given rotation angle"""
        center_x, center_y = width // 2, height // 2
        
        # Normalize angle to 0-180 range for perspective calculation
        normalized_angle = angle % 180
        if normalized_angle > 90:
            normalized_angle = 180 - normalized_angle
        
        # Calculate card width based on rotation (perspective)
        card_width = int(width * abs(math.cos(math.radians(normalized_angle))))
        card_height = height - 10
        
        # Calculate card position
        card_x1 = center_x - card_width // 2
        card_y1 = center_y - card_height // 2
        card_x2 = center_x + card_width // 2
        card_y2 = center_y + card_height // 2
        
        # Draw card
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, 
                                   fill="white", outline="black", width=2)
        
        # Only show text when card is mostly facing viewer
        if abs(math.cos(math.radians(normalized_angle))) > 0.3:
            # Use target text (what we're flipping to/from)
            if target_flipped:
                text = self.back_label.cget("text")
            else:
                text = self.front_label.cget("text")
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                y_pos = center_y - (len(lines) - 1) * 15 + i * 30
                self.canvas.create_text(center_x, y_pos, text=line, 
                                      font=("Arial", 24), fill="black")

    def show_next(self):
        self.current_index = (self.current_index + 1) % len(self.CATEGORIES_CHINESE["Alphabet"]["Character"])
        # Always show Character side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def show_prev(self):
        self.current_index = (self.current_index - 1) % len(self.CATEGORIES_CHINESE["Alphabet"]["Character"])
        # Always show Character side when changing cards
        if self.is_flipped:
            self.is_flipped = False
        self.show_card()

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(60, self))
        self.front_label.configure(font=get_relative_font(52, self))
        self.back_label.configure(font=get_relative_font(52, self))
        self.back_button.configure(font=get_relative_font(28, self))
        # Redraw card after font size changes
        self.draw_card()
        
class ChiDrills(DynamicFrame):
    def __init__(self, parent):
        super().__init__(parent, "#6096ba")
        self.drill_process = None
        self.running = True
        self.is_listening = False
        self.score = 0
        self.current_word = ""
        self.current_translation = ""
        self.current_romanized = ""
        self.user_input = ""
        self.create_ui_elements()
        self.clear_drill_json()
        self.update_drill_results()

    def create_ui_elements(self):
        self.title = ctk.CTkLabel(self, text="Drills", 
                                  font=get_relative_font(48, self), 
                                  text_color="white", fg_color="#6096ba")
        self.title.place(relx=0.05, rely=0.08, anchor="w")

        # Language dropdown
        self.language_option = ctk.CTkOptionMenu(
            self, 
            values=["Japanese", "Korean", "Chinese"],
            command=self.on_language_changed,
            width=160,
            height=44
        )
        self.language_option.set("Chinese")
        self.language_option.place(relx=0.95, rely=0.08, anchor="ne")

        pandaA_path = os.path.join("assets", "pandaA.png")
        pandaB_path = os.path.join("assets", "pandaB.png")
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)

        if self.pandaA_img:
            self.panda_label = ctk.CTkLabel(self, image=self.pandaA_img, text="", fg_color="transparent")
            self.panda_label.place(relx=0.20, rely=1.0, anchor="sw")

        self.bubble_frame = ctk.CTkFrame(self, 
                                         fg_color="white",
                                         border_color="black",
                                         border_width=3,
                                         corner_radius=20,
                                         width=420,
                                         height=180)
        self.bubble_frame.place(relx=0.78, rely=0.48, anchor="center")

        self.bubble_content = ctk.CTkLabel(self.bubble_frame, 
                                           text="Choose WORDS or PHRASES to begin", 
                                           font=get_relative_font(22, self),
                                           text_color="black", fg_color="transparent",
                                           wraplength=380, justify="center")
        self.bubble_content.place(relx=0.5, rely=0.5, anchor="center")

        self.words_button = ctk.CTkButton(self, text="WORDS", 
                                          font=get_relative_font(28, self, weight="bold"), 
                                          fg_color="white", text_color="black",
                                          width=140, height=50,
                                          command=self.start_word_drill)
        self.words_button.place(relx=0.70, rely=0.30, anchor="center")

        self.phrases_button = ctk.CTkButton(self, text="PHRASES", 
                                            font=get_relative_font(28, self, weight="bold"), 
                                            fg_color="white", text_color="black",
                                            width=140, height=50,
                                            command=self.start_phrase_drill)
        self.phrases_button.place(relx=0.86, rely=0.30, anchor="center")

        self.score_label = ctk.CTkLabel(self, text="Score: 0/5", 
                                        font=get_relative_font(22, self), 
                                        text_color="white", fg_color="#6096ba")
        self.score_label.place(relx=0.78, rely=0.65, anchor="n")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                         font=get_relative_font(18, self),
                                         fg_color="white", text_color="black",
                                         width=100, height=40,
                                         command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.words_button.invoke())
        root.bind("2", lambda event: self.phrases_button.invoke())
        root.bind("3", lambda event: self.back_button.invoke())

    def start_word_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "ChinDrill.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Word drill started! Listen and speak your answers.")

    def start_phrase_drill(self):
        self.clear_drill_json()
        self.set_panda("pandaA")
        if self.drill_process is None or self.drill_process.poll() is not None:
            script_path = os.path.join("Modes", "Drill", "ChinDrillPhrase.py")
            self.drill_process = subprocess.Popen(["python3", script_path])
            self.score = 0
            self.update_score()
            self.bubble_content.configure(text="Phrase drill started! Listen and speak your answers.")

    def on_language_changed(self, choice):
        # Only navigate if a different language is selected
        if choice == "Japanese":
            self.running = False
            self.stop_drill()
            show_frame(JapDrills)
        elif choice == "Korean":
            self.running = False
            self.stop_drill()
            show_frame(KorDrills)
        # If "Chinese" is selected, do nothing (already on this page)

    def on_back(self):
        self.running = False
        self.stop_drill()
        show_frame(ChiModePage)

    def stop_drill(self):
        if self.drill_process and self.drill_process.poll() is None:
            self.drill_process.terminate()
            try:
                self.drill_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.drill_process.kill()
            print("[✓] Drill process terminated.")

        self.panda_label.configure(image=self.pandaA_img)
        self.panda_toggle = False

    def update_score(self):
        self.score_label.configure(text=f"Score: {self.score}/5")

    def set_panda(self, state):
        if state == "pandaA":
            self.panda_label.configure(image=self.pandaA_img)
        elif state == "pandaB":
            self.panda_label.configure(image=self.pandaB_img)
        elif state == "pandaC":
            self.panda_label.configure(image=self.pandaC_img)


    def update_drill_results(self):
        if not self.running:
            return
        try:
            json_path = os.path.join("Modes", "Drill", "drill_results.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                    
                    if "current_word" in data:
                        self.current_word = data["current_word"]
                    
                    if "user_input" in data:
                        self.user_input = data["user_input"]
                        # Show current question and user's answer in bubble
                        display_text = f"Filipino: {self.current_word}\n\nYour answer: {self.user_input}"
                        self.bubble_content.configure(text=display_text)
            
                    if "status" in data:
                        if data["status"] == "QUESTION":
                           self.bubble_content.configure(
                               text=f"Filipino: {data['current_word']}"
                           )
                           if getattr(self, "panda_toggle", False):
                               self.set_panda("pandaB")
                           else:
                               self.set_panda("pandaC")
                           self.panda_toggle = not getattr(self, "panda_toggle", False)
                        elif data["status"] == "ANSWER":
                            self.bubble_content.configure(
                                text=f"Your answer: {data['user_input']} ({data['user_romanized']})"
                            )
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "RESULT":
                            if data["is_correct"]:
                                result_text = (f"Correct!\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Chinese: {data['translation']} ({data['romanized']})")
                            else:
                                result_text = (f"Incorrect\n\n"
                                               f"Filipino: {data['current_word']}\n"
                                               f"Your answer: {data['user_input']} ({data['user_romanized']})\n\n"
                                               f"Correct answer:\nChinese: {data['translation']} ({data['romanized']})")
                            self.bubble_content.configure(text=result_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        elif data["status"] == "COMPLETE":
                            final_text = f"Drill Complete!"
                            if data['final_score'] >= 4:
                                final_text += "\n\nExcellent work!"
                            elif data['final_score'] >= 3:
                                final_text += "\n\nGood Job! Keep Practicing!"
                            else:
                                final_text += "\n\nKeep studying! You'll improve!"
                            self.bubble_content.configure(text=final_text)
                            self.set_panda("pandaA")
                            self.panda_toggle = False
                        
        except Exception as e:
            print(f"[!] Failed to update drill results: {e}")
        
        if self.running:
            self.after(1000, self.update_drill_results)

    def clear_drill_json(self):
        results_file = os.path.join("Modes", "Drill", "drill_results.json")
        try:
            with open(results_file, "w") as f:
                json.dump({}, f)
            print("Results cleared")
        except Exception as e:
            print("Failed to clear")

    def update_elements(self):
        super().update_elements()
        self.title.configure(font=get_relative_font(48, self))
        self.bubble_content.configure(font=get_relative_font(22, self))
        self.words_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.phrases_button.configure(font=get_relative_font(28, self, weight="bold"))
        self.score_label.configure(font=get_relative_font(22, self))
        self.back_button.configure(font=get_relative_font(18, self))

        pandaA_path = os.path.join("assets", "pandaA.png")
        self.pandaA_img = load_ctk_image(pandaA_path, self, height_percentage=0.72)
        pandaB_path = os.path.join("assets", "pandaB.png")
        self.pandaB_img = load_ctk_image(pandaB_path, self, height_percentage=0.72)
        pandaC_path = os.path.join("assets", "pandaC.png")
        self.pandaC_img = load_ctk_image(pandaC_path, self, height_percentage=0.72)
        if self.pandaA_img:
            self.panda_label.configure(image=self.pandaA_img)
        elif self.pandaB_img:
            self.panda_label.configure(image=self.pandaB_img)
        elif self.pandaC_img:
            self.panda_label.configure(image=self.pandaC_img)

        bubble_width = max(int(self.winfo_width() * 0.28), 400)
        bubble_height = max(int(self.winfo_height() * 0.20), 150)
        self.bubble_frame.configure(width=bubble_width, height=bubble_height)


CONVERSATION_DATA = {
    "Japanese": {
        "Scenario 1": {
            "title": "Asking for directions",
            "lines": [
                ("A", "すみません、えきは どこですか。", "(Sumimasen, eki wa doko desu ka.)", "\"Excuse me, where is the train station?\""),
                ("B", "あそこです。あの たかい ビルの となりです。", "(Asoko desu. Ano takai biru no tonari desu.)", "\"It's over there. It's next to that tall building.\""),
                ("A", "どうも ありがとうございます。", "(Dōmo arigatō gozaimasu.)", "\"Thank you very much.\""),
            ]
        },
        "Scenario 2": {
            "title": "Asking the price and paying",
            "lines": [
                ("A", "すみません、これは いくらですか。", "(Sumimasen, kore wa ikura desu ka.)", "\"Excuse me, how much is this?\""),
                ("B", "130円です。", "(Hyaku-san-jū en desu.)", "\"It's 130 yen.\""),
                ("A", "これを ください。", "(Kore o kudasai.)", "\"I'll take this, please.\""),
                ("B", "はい、130円です。", "(Hai, hyaku-san-jū en desu.)", "\"Okay, that's 130 yen.\""),
                ("A", "はい。", "(Hai.)", "\"Here you go.\""),
            ]
        },
        "Scenario 3": {
            "title": "Asking a Local About Specialties",
            "lines": [
                ("A", "すみません、この まちの めいぶつは なんですか。", "(Sumimasen, kono machi no meibutsu wa nan desu ka.)", "\"Excuse me, what is the specialty of this town?\""),
                ("B", "この まちの めいぶつは ラーメンです。とても おいしいですよ。", "(Kono machi no meibutsu wa rāmen desu. Totemo oishii desu yo.)", "\"This town's specialty is ramen. It's very delicious.\""),
                ("A", "そうですか。どこで たべられますか。", "(Sō desu ka. Doko de taberaremasu ka.)", "\"I see. Where can I eat it?\""),
                ("B", "えきの まえの おみせが おすすめです。", "(Eki no mae no omise ga osusume desu.)", "\"I recommend the shop in front of the station.\""),
            ]
        },
        "Scenario 4": {
            "title": "Ordering Food at a Restaurant",
            "lines": [
                ("B", "ごちゅうもんは？", "(Gochūmon wa?)", "\"What would you like to order?\""),
                ("A", "てんぷらそばと おちゃを おねがいします。", "(Tempura soba to ocha o onegaishimasu.)", "\"Tempura soba and green tea, please.\""),
                ("B", "かしこまりました。", "(Kashikomarimashita.)", "\"Certainly.\""),
                ("A", "すみません！おかいけい、おねがいします。", "(Sumimasen! Okaikei, onegaishimasu.)", "\"Excuse me! The check, please.\""),
            ]
        },
        "Scenario 5": {
            "title": "Simple Small Talk / Asking for a Photo",
            "lines": [
                ("A", "すみません、しゃしんを とって いただけませんか。", "(Sumimasen, shashin o totte itadakemasen ka.)", "\"Excuse me, could you please take a photo?\""),
                ("B", "はい、いいですよ。", "(Hai, ii desu yo.)", "\"Yes, sure.\""),
                ("A", "どうも。", "(Dōmo.)", "\"Thanks.\""),
                ("B", "はい、どうぞ。", "(Hai, dōzo.)", "\"Here you go.\""),
                ("A", "ありがとうございました！", "(Arigatō gozaimashita!)", "\"Thank you very much!\""),
            ]
        }
    },
    "Korean": {
        "Scenario 1": {
            "title": "Asking Where a Specific Place Is",
            "lines": [
                ("A", "실례합니다, 지하철역이 어디에요?", "(Sillyehamnida, jihacheollyeogi eodieyo?)", "\"Excuse me, where is the subway station?\""),
                ("B", "저기요. 그 빨간 건물 옆이에요.", "(Jeogiyo. Geu ppalgan geonmul yeobieyo.)", "\"It's over there. It's next to that red building.\""),
                ("A", "아, 감사합니다!", "(Ah, gamsahamnida!)", "\"Ah, thank you!\""),
            ]
        },
        "Scenario 2": {
            "title": "Asking the Price and Paying",
            "lines": [
                ("A", "이거 얼마예요?", "(Igeo eolmayeyo?)", "\"How much is this?\""),
                ("B", "1,500원이요.", "(Cheonobaek-woniyo.)", "\"It's 1,500 won.\""),
                ("A", "이거 주세요.", "(Igeo juseyo.)", "\"Please give me this.\""),
                ("B", "네, 1,500원이에요.", "(Ne, cheonobaek-wonieyo.)", "\"Okay, that's 1,500 won.\""),
                ("A", "여기요.", "(Yeogiyo.)", "\"Here you go.\""),
            ]
        },
        "Scenario 3": {
            "title": "Asking a Local About Specialties",
            "lines": [
                ("A", "실례합니다, 이 곳의 특산물이 뭐예요?", "(Sillyehamnida, i gosui teuksanmuri mwoyeyo?)", "\"Excuse me, what is the local specialty of this place?\""),
                ("B", "이 동네는 비빔밥이 유명해요. 정말 맛있어요.", "(I dongneneun bibimbabi yumyeonghaeyo. Jeongmal masisseoyo.)", "\"This town is famous for bibimbap. It's really delicious.\""),
                ("A", "그래요? 어디에서 먹을 수 있어요?", "(Geuraeyo? Eodieseo meogeul su isseoyo?)", "\"Really? Where can I eat it?\""),
                ("B", "역 앞에 있는 식당이 좋아요.", "(Yeok ape inneun sikdangi joayo.)", "\"The restaurant in front of the station is good.\""),
            ]
        },
        "Scenario 4": {
            "title": "Ordering Food at a Restaurant",
            "lines": [
                ("B", "주문하시겠어요?", "(Jumunhasigesseoyo?)", "\"Are you ready to order?\""),
                ("A", "김치찌개 하나랑 공기밥 주세요.", "(Gimchijjigae hanarang gonggibap juseyo.)", "\"One kimchi jjigae and a bowl of rice, please.\""),
                ("B", "네, 알겠습니다.", "(Ne, algesseumnida.)", "\"Yes, certainly.\""),
                ("A", "저기요! 계산서 주세요.", "(Jeogiyo! Gyesanseo juseyo.)", "\"Excuse me! The bill, please.\""),
            ]
        },
        "Scenario 5": {
            "title": "Simple Small Talk / Asking for a Photo",
            "lines": [
                ("A", "실례합니다, 사진 좀 찍어 주실래요?", "(Sillyehamnida, sajin jom jjigeo jusillaeyo?)", "\"Excuse me, could you take a photo for me?\""),
                ("B", "네, 좋아요.", "(Ne, joayo.)", "\"Yes, sure.\""),
                ("A", "감사합니다.", "(Gamsahamnida.)", "\"Thank you.\""),
                ("B", "여기요, 다 찍었어요.", "(Yeogiyo, da jjigeosseoyo.)", "\"Here you go, I've taken it.\""),
                ("A", "정말 감사합니다!", "(Jeongmal gamsahamnida!)", "\"Thank you so much!\""),
            ]
        }
    },
    "Chinese": {
        "Scenario 1": {
            "title": "Asking Where a Specific Place Is",
            "lines": [
                ("A", "不好意思，地铁站在哪里？", "(Bù hǎoyìsi, dìtiě zhàn zài nǎlǐ?)", "\"Excuse me, where is the subway station?\""),
                ("B", "在那边。那个高楼的旁边。", "(Zài nàbiān. Nàgè gāo lóu de pángbiān.)", "\"It's over there. Next to that tall building.\""),
                ("A", "好的，谢谢你！", "(Hǎo de, xièxiè nǐ!)", "\"Okay, thank you!\""),
            ]
        },
        "Scenario 2": {
            "title": "Asking the Price and Paying",
            "lines": [
                ("A", "这个多少钱？", "(Zhège duōshǎo qián?)", "\"How much is this?\""),
                ("B", "三块。", "(Sān kuài.)", "\"Three kuai (RMB).\""),
                ("A", "我要这个。", "(Wǒ yào zhège.)", "\"I want this one.\""),
                ("B", "好，三块钱。", "(Hǎo, sān kuài qián.)", "\"Okay, three kuai.\""),
                ("A", "给你。", "(Gěi nǐ.)", "\"Here you go.\""),
            ]
        },
        "Scenario 3": {
            "title": "Asking a Local About Specialties",
            "lines": [
                ("A", "请问，这里有什么特产？", "(Qǐngwèn, zhèlǐ yǒu shéme tèchǎn?)", "\"Excuse me, what are the local specialties here?\""),
                ("B", "北京烤鸭很有名。很好吃。", "(Běijīng kǎoyā hěn yǒumíng. Hěn hǎochī.)", "\"Beijing Roast Duck is very famous. It's very delicious.\""),
                ("A", "是吗？在哪里可以吃到？", "(Shì ma? Zài nǎlǐ kěyǐ chī dào?)", "\"Really? Where can I eat it?\""),
                ("B", "我推荐王府井的餐厅。", "(Wǒ tuījiàn Wángfǔjǐng de cāntīng.)", "\"I recommend the restaurants in Wangfujing.\""),
            ]
        },
        "Scenario 4": {
            "title": "Ordering Food at a Restaurant",
            "lines": [
                ("B", "可以点菜了吗？", "(Kěyǐ diǎncài le ma?)", "\"Are you ready to order?\""),
                ("A", "我要宫保鸡丁和一碗米饭。", "(Wǒ yào gōngbǎo jīdīng hé yī wǎn mǐfàn.)", "\"I want Kung Pao Chicken and a bowl of rice.\""),
                ("B", "好的。", "(Hǎo de.)", "\"Okay.\""),
                ("A", "服务员，买单！", "(Fúwùyuán, mǎidān!)", "\"Waiter, check please!\""),
            ]
        },
        "Scenario 5": {
            "title": "Simple Small Talk / Asking for a Photo",
            "lines": [
                ("A", "不好意思，可以帮我拍一张照片吗？", "(Bù hǎoyìsi, kěyǐ bāng wǒ pāi yì zhāng zhàopiàn ma?)", "\"Excuse me, could you help me take a photo?\""),
                ("B", "可以。", "(Kěyǐ.)", "\"Yes, sure.\""),
                ("A", "谢谢。", "(Xièxiè.)", "\"Thanks.\""),
                ("B", "好了。", "(Hǎo le.)", "\"All done.\""),
                ("A", "太感谢了！", "(Tài gǎnxiè le!)", "\"Thank you so much!\""),
            ]
        }
    }
}

SCENARIO_CHOICES = {
    "Japanese": {
        "Scenario 1": {
            "context": "You are walking through a busy Japanese town. You need to catch a train but cannot find the station. You approach someone standing near a tall building.",
            "choices": [
                {"native": "コンビニは どこですか。", "english": "Where is the convenience store?"},
                {"native": "すみません、タクシーは どこですか。", "english": "Excuse me, where is the taxi?"},
                {"native": "あなたは どこに いきますか。", "english": "Where are you going?"},
                {"native": "すみません、えきは どこですか。", "english": "Excuse me, where is the train station?"}
            ],
            "correct": 3,
            "followup": {
                "npc_response": "The person points and says: 「あそこです。あの たかい ビルの となりです。」 – \"It's over there. It's next to that tall building.\"",
                "choices": [
                    {"native": "はい。", "english": "Okay."},
                    {"native": "どうも ありがとうございます。", "english": "Thank you very much."},
                    {"native": "わかりません。", "english": "I don't understand."},
                    {"native": "そこはどこですか？", "english": "Where is that?"}
                ],
                "correct": 1
            }
        },
        "Scenario 2": {
            "context": "You enter a convenience store and pick up a bottle of water. You are unsure of the price, so you go to the cashier.",
            "choices": [
                {"native": "これは どこですか。", "english": "Where is this?"},
                {"native": "これは なんじですか。", "english": "What time is this?"},
                {"native": "すみません、これは いくらですか。", "english": "Excuse me, how much is this?"},
                {"native": "これは おおきいですか。", "english": "Is this big?"}
            ],
            "correct": 2,
            "followup": {
                "npc_response": "The cashier replies: 「130円です。」 – \"It's 130 yen.\"",
                "choices": [
                    {"native": "いりません。", "english": "I don't want it."},
                    {"native": "これを ください。", "english": "I'll take this, please."},
                    {"native": "もっと安くしてください。", "english": "Please make it cheaper."},
                    {"native": "わかりません。", "english": "I don't know."}
                ],
                "correct": 1
            }
        },
        "Scenario 3": {
            "context": "You are exploring a new Japanese town and want to try something local and delicious. You approach a friendly resident.",
            "choices": [
                {"native": "すみません、どこで ねますか。", "english": "Excuse me, where do I sleep?"},
                {"native": "すみません、この まちの めいぶつは なんですか。", "english": "Excuse me, what is the specialty of this town?"},
                {"native": "この まちの いぬは どこですか。", "english": "Where are the town’s dogs?"},
                {"native": "あなたの たべものは なんですか。", "english": "What food do you eat?"}
            ],
            "correct": 1,
            "followup": {
                "npc_response": "The resident smiles and says: 「この まちの めいぶつは ラーメンです。とても おいしいですよ。」 – \"The specialty of this town is ramen. It's very delicious.\"",
                "choices": [
                    {"native": "そうですか。どこで たべられますか。", "english": "I see. Where can I eat it?"},
                    {"native": "ラーメンは きらいです。", "english": "I don't like ramen."},
                    {"native": "それは いくらですか。", "english": "How much is that?"},
                    {"native": "どこに ねますか。", "english": "Where do I sleep?"}
                ],
                "correct": 0
            }
        },
        "Scenario 4": {
            "context": "You sit down at a peaceful restaurant. A server approaches your table and asks: 「ごちゅうもんは？」 – 'What would you like to order?'",
            "choices": [
                {"native": "なにも いりません。", "english": "I don't need anything."},
                {"native": "みずだけで けっこうです。", "english": "Just water is fine."},
                {"native": "てんぷらそばと おちゃを おねがいします。", "english": "Tempura soba and green tea, please."},
                {"native": "ちゅうもんは あとで します。", "english": "I'll order later."}
            ],
            "correct": 2,
            "followup": {
                "npc_response": "The server replies: 「かしこまりました。」 – \"Certainly.\"",
                "choices": [
                    {"native": "すみません！おかいけい、おねがいします。", "english": "Excuse me! The check, please."},
                    {"native": "ありがとう。", "english": "Thank you."},
                    {"native": "ごちそうさまでした。", "english": "Thanks for the meal."},
                    {"native": "さようなら。", "english": "Goodbye."}
                ],
                "correct": 0
            }
        },
        "Scenario 5": {
            "context": "You are sightseeing and want someone to take a photo of you. You approach a person holding a camera.",
            "choices": [
                {"native": "しゃしんは どこですか。", "english": "Where is the photo?"},
                {"native": "カメラを ください。", "english": "Give me the camera."},
                {"native": "あなたは しゃしんが すきですか。", "english": "Do you like photos?"},
                {"native": "すみません、しゃしんを とって いただけませんか。", "english": "Excuse me, could you please take a photo?"}
            ],
            "correct": 3,
            "followup": {
                "npc_response": "The person nods and says: 「はい、いいですよ。」 – \"Yes, sure.\"",
                "choices": [
                    {"native": "おねがいします。", "english": "Please."},
                    {"native": "はやく！", "english": "Hurry!"},
                    {"native": "だめです。", "english": "No."},
                    {"native": "たくさん とって！", "english": "Take many photos!"}
                ],
                "correct": 0
            }
        }
    },
    "Korean": {
        "Scenario 1": {
            "context": "You are walking through a busy street in Seoul. You need to find the subway station. You decide to ask a nearby person.",
            "choices": [
                {"native": "지하철역 있어요？", "english": "Is there a subway station?"},
                {"native": "어이요! 지하철 어디야？", "english": "Hey! Where’s the subway?"},
                {"native": "실례합니다, 지하철역이 어디예요？", "english": "Excuse me, where is the subway station?"},
                {"native": "지하철은 필요 없어요. 그냥 물어봐요。", "english": "I don't need the subway. I'm just asking."}
            ],
            "correct": 2,
            "followup": {
                "choices": [
                    {"native": "아… 그래요.", "english": "Oh… okay."},
                    {"native": "네? 다시 말해요.", "english": "What? Say it again."},
                    {"native": "아, 감사합니다!", "english": "Ah, thank you!"},
                    {"native": "맞아요? 아닌 것 같은데요.", "english": "Are you sure? I don't think so."}
                ],
                "correct": 2
            }
        },
        "Scenario 2": {
            "context": "You pick up a bottle of water inside a convenience store. You want to ask the cashier for the price.",
            "choices": [
                {"native": "이거 뭐예요？", "english": "What is this?"},
                {"native": "이거 주세요？", "english": "Give me this?"},
                {"native": "돈 없어요. 무료예요？", "english": "I have no money. Is this free?"},
                {"native": "이거 얼마예요？", "english": "How much is this?"}
            ],
            "correct": 3,
            "followup": {
                "choices": [
                    {"native": "이거 주세요。", "english": "I'll take this."},
                    {"native": "비싸요. 안 사요。", "english": "Too expensive. I won't buy it."},
                    {"native": "공짜로 주세요。", "english": "Give it for free."},
                    {"native": "몰라요。", "english": "I don't know."}
                ],
                "correct": 0
            }
        },
        "Scenario 3": {
            "context": "You are traveling in a new Korean town and want to try its specialty food. You ask a friendly local.",
            "choices": [
                {"native": "여기 맛있는 거 없어요？", "english": "There's nothing delicious here, right?"},
                {"native": "특산물? 관심 없어요。", "english": "Specialties? I'm not interested."},
                {"native": "실례합니다, 이 곳의 특산물이 뭐예요？", "english": "Excuse me, what is the local specialty here?"},
                {"native": "인터넷 보면 돼요？", "english": "Should I just check online?"}
            ],
            "correct": 2,
            "followup": {
                "choices": [
                    {"native": "그래요? 어디에서 먹을 수 있어요？", "english": "Really? Where can I eat it?"},
                    {"native": "비빔밥 싫어요。", "english": "I don't like bibimbap."},
                    {"native": "그냥 편의점 갈게요。", "english": "I'll just go to a convenience store."},
                    {"native": "뭐라고요？", "english": "What did you say?"}
                ],
                "correct": 0
            }
        },
        "Scenario 4": {
            "context": "You sit down and the server approaches. The server asks: '주문하시겠어요?' – 'Are you ready to order?'",
            "choices": [
                {"native": "물만 주세요。", "english": "Just water, please."},
                {"native": "아직이요。", "english": "Not yet."},
                {"native": "김치찌개 하나랑 공기밥 주세요。", "english": "One kimchi jjigae and a bowl of rice, please."},
                {"native": "추천 메뉴 없어요？", "english": "Don't you have recommendations?"}
            ],
            "correct": 2
        },
        "Scenario 5": {
            "context": "You're sightseeing and want someone to take your picture. You approach a passerby.",
            "choices": [
                {"native": "사진 찍어요。", "english": "Take a photo."},
                {"native": "저 사람 사진 찍어주세요。", "english": "Take that person’s photo."},
                {"native": "사진? 필요 없어요。", "english": "No need for a picture."},
                {"native": "실례합니다, 사진 좀 찍어 주실래요？", "english": "Excuse me, could you take a photo for me?"}
            ],
            "correct": 3
        }
    },
    "Chinese": {
        "Scenario 1": {
            "context": "You are walking through a busy street in a Chinese city. You need to find the subway station. You see a person standing near a tall glass building, so you walk up and ask:",
            "choices": [
                {"native": "你知道吗？", "english": "Do you know?"},
                {"native": "你去地铁站吗？", "english": "Are you going to the subway station?"},
                {"native": "不好意思，请问地铁站在哪里？", "english": "Excuse me, where is the subway station?"},
                {"native": "那个大楼是谁的？", "english": "Whose tall building is that?"}
            ],
            "correct": 2,
            "followup": {
                "choices": [
                    {"native": "啊，好吧。", "english": "Ah, okay."},
                    {"native": "好的，谢谢你！", "english": "Okay, thank you!"},
                    {"native": "我不相信你。", "english": "I don't believe you."},
                    {"native": "你去不去？", "english": "Are you going or not?"}
                ],
                "correct": 1
            }
        },
        "Scenario 2": {
            "context": "You enter a small convenience store. You pick up a bottle of water and walk to the counter.",
            "choices": [
                {"native": "你喜欢水吗？", "english": "Do you like water?"},
                {"native": "我要喝水。", "english": "I want to drink water."},
                {"native": "多少钱？", "english": "How much?"},
                {"native": "这个多少钱？", "english": "How much is this?"}
            ],
            "correct": 3,
            "followup": {
                "choices": [
                    {"native": "太贵了！", "english": "Too expensive!"},
                    {"native": "我不要了。", "english": "I don't want it anymore."},
                    {"native": "我要这个。", "english": "I'll take this one."},
                    {"native": "你有免费的？", "english": "Do you have something free?"}
                ],
                "correct": 2
            }
        },
        "Scenario 3": {
            "context": "You're exploring a new city and want to try a famous dish. You see a friendly local and approach them.",
            "choices": [
                {"native": "你吃饱了吗？", "english": "Are you full?"},
                {"native": "哪里好玩？", "english": "What's fun here?"},
                {"native": "你为什么在这里？", "english": "Why are you here?"},
                {"native": "请问，这里有什么特产？", "english": "Excuse me, what are the local specialties here?"}
            ],
            "correct": 3,
            "followup": {
                "choices": [
                    {"native": "我不喜欢鸭。", "english": "I don't like duck."},
                    {"native": "那是什么？", "english": "What's that?"},
                    {"native": "是吗？在哪里可以吃到？", "english": "Really? Where can I eat it?"},
                    {"native": "我不要吃。", "english": "I don't want to eat."}
                ],
                "correct": 2
            }
        },
        "Scenario 4": {
            "context": "You sit down in a restaurant. The server comes over and asks: 「可以点菜了吗？」 – 'Are you ready to order?'",
            "choices": [
                {"native": "不要吃东西。", "english": "I don't want to eat."},
                {"native": "我要宫保鸡丁和一碗米饭。", "english": "I want Kung Pao Chicken and a bowl of rice."},
                {"native": "给我电脑。", "english": "Give me a computer."},
                {"native": "请给我地图。", "english": "Please give me a map."}
            ],
            "correct": 1,
            "followup": {
                "choices": [
                    {"native": "我走了。", "english": "I'm leaving."},
                    {"native": "你好。", "english": "Hello."},
                    {"native": "谢谢。", "english": "Thanks."},
                    {"native": "服务员，买单！", "english": "Waiter, check please!"}
                ],
                "correct": 3
            }
        },
        "Scenario 5": {
            "context": "You're at a busy tourist spot and want a photo of yourself. You approach someone and ask:",
            "choices": [
                {"native": "你知道我是谁吗？", "english": "Do you know who I am?"},
                {"native": "你拍什么？", "english": "What are you taking pictures of?"},
                {"native": "这个地方漂亮吗？", "english": "Is this place pretty?"},
                {"native": "不好意思，可以帮我拍一张照片吗？", "english": "Excuse me, could you help me take a photo?"}
            ],
            "correct": 3,
            "followup": {
                "choices": [
                    {"native": "快一点！", "english": "Hurry up!"},
                    {"native": "小心点。", "english": "Be careful."},
                    {"native": "谢谢。", "english": "Thank you."},
                    {"native": "拍十张！", "english": "Take ten photos!"}
                ],
                "correct": 2
            }
        }
    }
}

class JapConversation(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_scenario = "Scenario 1"
        self.create_ui_elements()
    
    def create_ui_elements(self):
        theme = get_current_theme()
        # Title (large)
        self.title = ctk.CTkLabel(self, text="Conversations",
                                  font=get_relative_font(120, self),
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.06, anchor="w")

        # Language & Scenario dropdowns (top-right)
        self.language_option = ctk.CTkOptionMenu(self, values=["Japanese", "Korean", "Chinese"],
                                                 command=self.on_language_select, width=140, height=36)
        self.language_option.set("Japanese")
        self.language_option.place(relx=0.88, rely=0.08, anchor="e")

        self.scenario_option = ctk.CTkOptionMenu(self, values=["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"],
                                                 command=self.on_scenario_select, width=140, height=36)
        self.scenario_option.set("Scenario 1")
        self.scenario_option.place(relx=0.88, rely=0.14, anchor="e")

        # Large centered conversation box (rounded, thinner border to save space)
        self.conv_frame = ctk.CTkFrame(self,
                                       fg_color=theme["primary"],
                                       border_color="black",
                                       border_width=8,
                                       corner_radius=30)
        # move slightly higher and make the box a bit taller/wider to reduce empty margins
        self.conv_frame.place(relx=0.5, rely=0.50, anchor="center", relwidth=0.88, relheight=0.62)

        # Conversation text area inside the big box (top portion)
        self.conv_text = ctk.CTkTextbox(self.conv_frame, wrap="word",
                                        font=get_relative_font(28, self),
                                        text_color="white", fg_color=theme["primary"],
                                        border_width=0)
        # reduce the vertical gap to choices by reducing text area height
        self.conv_text.place(relx=0.03, rely=0.08, relwidth=0.94, relheight=0.50)
        self.conv_text.configure(state="disabled")

        # Choice radio buttons area (below conv_text inside conv_frame)
        self.choice_var = StringVar(value="")
        # track whether we're showing a follow-up question for the current scenario
        self.in_followup = False
        choices = SCENARIO_CHOICES["Japanese"][self.current_scenario]["choices"]
        self.radio_buttons = []
        for i, choice in enumerate(choices):
            label = f"{chr(65+i)}. {choice['native']} ({choice['english']})"
            rb = ctk.CTkRadioButton(self.conv_frame, text=label, variable=self.choice_var, value=chr(65+i),
                                    font=get_relative_font(20, self))
            # start choices closer to the text and reduce spacing between them
            rb.place(relx=0.03, rely=0.61 + i*0.06, anchor="nw")
            self.radio_buttons.append(rb)

        # Submit button and feedback label
        self.submit_btn = ctk.CTkButton(self.conv_frame, text="Submit", command=self.submit_answer, width=120, height=38)
        self.submit_btn.place(relx=0.86, rely=0.82, anchor="center")

        self.feedback_label = ctk.CTkLabel(self.conv_frame, text="", text_color="white", fg_color=theme["primary"]) 
        self.feedback_label.place(relx=0.03, rely=0.82, anchor="nw")

        # Large right-side feedback label (hidden until needed)
        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="", text_color="#ff3333",
                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
        self.large_feedback.place(relx=0.78, rely=0.62, anchor="center")

        # Back button
        self.back_button = ctk.CTkButton(self, text="BACK", 
                                        font=get_relative_font(18, self),
                                        fg_color="white", text_color="black",
                                        width=100, height=40,
                                        command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.back_button.invoke())
        
        # Display initial scenario (story prompt + choices)
        self.update_story()

    def update_story(self):
        """Show scenario context and question prompt."""
        language = "Japanese"
        scenario = SCENARIO_CHOICES[language][self.current_scenario]
        # Show context (scenario description)
        context_text = scenario.get("context", "")
        text_content = f"{context_text}\n\n"
        # Add question prompt
        if not self.in_followup:
            text_content += "What will YOU say? (Choose A–D)\n"
        else:
            follow = scenario.get("followup", {})
            if self.in_followup and follow:
                # For follow-up, show the NPC response or context
                text_content += "What will YOU reply? (Choose A–D)\n"

        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")

        # refresh choices for current scenario (show native + English) and re-enable inputs
        choices = SCENARIO_CHOICES[language][self.current_scenario]["choices"]
        for i, rb in enumerate(self.radio_buttons):
            rb.configure(text=f"{chr(65+i)}. {choices[i]['native']} ({choices[i]['english']})", state="normal")
        self.choice_var.set("")
        self.feedback_label.configure(text="")
        if getattr(self, "large_feedback", None):
            try:
                self.large_feedback.destroy()
            except Exception:
                try:
                    self.large_feedback.configure(text="")
                except Exception:
                    pass
            self.large_feedback = None
        try:
            self.submit_btn.configure(state="normal")
        except Exception:
            pass
        # reset followup state when showing a new scenario
        self.in_followup = False

    def submit_answer(self):
        selected = self.choice_var.get()
        if not selected:
            return
        scenario = SCENARIO_CHOICES["Japanese"][self.current_scenario]
        if not self.in_followup:
            correct_index = scenario["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            # correct initial answer
            self.feedback_label.configure(text="Correct!")
            if getattr(self, "large_feedback", None):
                try:
                    self.large_feedback.destroy()
                except Exception:
                    try:
                        self.large_feedback.configure(text="")
                    except Exception:
                        pass
                self.large_feedback = None
            if getattr(self, "large_feedback", None):
                try:
                    self.large_feedback.destroy()
                except Exception:
                    try:
                        self.large_feedback.configure(text="")
                    except Exception:
                        pass
                self.large_feedback = None
            # if there's a follow-up, show NPC response and follow-up question
            follow = scenario.get("followup")
            if follow:
                self.in_followup = True
                # Show NPC response and follow-up prompt
                language = "Japanese"
                npc_response = follow.get("npc_response", "")
                text_content = f"{npc_response}\n\n"
                text_content += "What will YOU reply? (Choose A–D)\n"
                self.conv_text.configure(state="normal")
                self.conv_text.delete("1.0", "end")
                self.conv_text.insert("1.0", text_content)
                self.conv_text.configure(state="disabled")
                # Load follow-up choices
                for i, rb in enumerate(self.radio_buttons):
                    try:
                        fchoice = follow["choices"][i]
                        rb.configure(text=f"{chr(65+i)}. {fchoice['native']} ({fchoice['english']})", state="normal")
                    except Exception:
                        rb.configure(state="disabled")
                self.choice_var.set("")
                self.feedback_label.configure(text="")
                if getattr(self, "large_feedback", None):
                    try:
                        self.large_feedback.destroy()
                    except Exception:
                        try:
                            self.large_feedback.configure(text="")
                        except Exception:
                            pass
                    self.large_feedback = None
                return
            # no follow-up: show full conversation
            if getattr(self, "large_feedback", None):
                try:
                    self.large_feedback.destroy()
                except Exception:
                    try:
                        self.large_feedback.configure(text="")
                    except Exception:
                        pass
                self.large_feedback = None
            self.update_conversation()
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return
        # if we're in follow-up mode, check follow-up answer
        follow = scenario.get("followup", None)
        if follow:
            correct_index = follow["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            # follow-up correct: show full conversation and disable inputs
            self.feedback_label.configure(text="Correct!")
            if getattr(self, "large_feedback", None):
                try:
                    self.large_feedback.destroy()
                except Exception:
                    try:
                        self.large_feedback.configure(text="")
                    except Exception:
                        pass
                self.large_feedback = None
            if getattr(self, "large_feedback", None):
                try:
                    self.large_feedback.destroy()
                except Exception:
                    try:
                        self.large_feedback.configure(text="")
                    except Exception:
                        pass
                self.large_feedback = None
            self.update_conversation()
            self.in_followup = False
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return

    def next_scenario(self):
        # advance to next scenario (wrap around)
        scenarios = list(SCENARIO_CHOICES["Japanese"].keys())
        idx = scenarios.index(self.current_scenario)
        next_idx = (idx + 1) % len(scenarios)
        self.current_scenario = scenarios[next_idx]
        try:
            self.scenario_option.set(self.current_scenario)
        except Exception:
            pass
        self.update_story()
    
    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapConversation)
        elif value == "Korean":
            show_frame(KorConversation)
        elif value == "Chinese":
            show_frame(ChiConversation)
    
    def on_scenario_select(self, value):
        self.current_scenario = value
        self.update_story()
    
    def update_conversation(self):
        language = "Japanese"
        scenario_data = CONVERSATION_DATA[language][self.current_scenario]
        
        text_content = f"{scenario_data['title']}\n\n"
        for speaker, native, romanized, english in scenario_data['lines']:
            text_content += f"{speaker}: {native}\n{romanized}\n{english}\n\n"
        
        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")
    
    def on_back(self):
        show_frame(ChooseModePage)
    
    def update_elements(self):
        super().update_elements()
        theme = get_current_theme()
        self.title.configure(font=get_relative_font(120, self), fg_color=theme["primary"])
        # update conv_frame/conv_text colors and font
        self.conv_frame.configure(fg_color=theme["primary"], border_color="black")
        self.conv_text.configure(font=get_relative_font(28, self), fg_color=theme["primary"], text_color="white")
        try:
            self.large_feedback.configure(font=get_relative_font(48, self))
        except Exception:
            pass
        for rb in self.radio_buttons:
            rb.configure(font=get_relative_font(20, self))
        self.back_button.configure(font=get_relative_font(18, self))

class KorConversation(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_scenario = "Scenario 1"
        self.create_ui_elements()
    
    def create_ui_elements(self):
        theme = get_current_theme()
        # Title (large)
        self.title = ctk.CTkLabel(self, text="Conversations",
                                  font=get_relative_font(120, self),
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.06, anchor="w")

        # Language & Scenario dropdowns (top-right)
        self.language_option = ctk.CTkOptionMenu(self, values=["Japanese", "Korean", "Chinese"],
                                                 command=self.on_language_select, width=140, height=36)
        self.language_option.set("Korean")
        self.language_option.place(relx=0.88, rely=0.08, anchor="e")

        self.scenario_option = ctk.CTkOptionMenu(self, values=["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"],
                                                 command=self.on_scenario_select, width=140, height=36)
        self.scenario_option.set("Scenario 1")
        self.scenario_option.place(relx=0.88, rely=0.14, anchor="e")

        # Large centered conversation box (rounded, thinner border to save space)
        self.conv_frame = ctk.CTkFrame(self,
                                       fg_color=theme["primary"],
                                       border_color="black",
                                       border_width=8,
                                       corner_radius=30)
        # move slightly higher and make the box a bit taller/wider to reduce empty margins
        self.conv_frame.place(relx=0.5, rely=0.50, anchor="center", relwidth=0.88, relheight=0.62)

        self.conv_text = ctk.CTkTextbox(self.conv_frame, wrap="word",
                                        font=get_relative_font(28, self),
                                        text_color="white", fg_color=theme["primary"], border_width=0)
        self.conv_text.place(relx=0.03, rely=0.08, relwidth=0.94, relheight=0.50)
        self.conv_text.configure(state="disabled")

        # Choice radio buttons area
        self.choice_var = StringVar(value="")
        # track follow-up state for this scenario
        self.in_followup = False
        choices = SCENARIO_CHOICES["Korean"][self.current_scenario]["choices"]
        self.radio_buttons = []
        for i, choice in enumerate(choices):
            label = f"{chr(65+i)}. {choice['native']} ({choice['english']})"
            rb = ctk.CTkRadioButton(self.conv_frame, text=label, variable=self.choice_var, value=chr(65+i),
                                    font=get_relative_font(20, self))
            # start choices closer to the text and reduce spacing between them
            rb.place(relx=0.03, rely=0.61 + i*0.06, anchor="nw")
            self.radio_buttons.append(rb)

        self.submit_btn = ctk.CTkButton(self.conv_frame, text="Submit", command=self.submit_answer, width=120, height=38)
        self.submit_btn.place(relx=0.86, rely=0.82, anchor="center")

        self.feedback_label = ctk.CTkLabel(self.conv_frame, text="", text_color="white", fg_color=theme["primary"]) 
        self.feedback_label.place(relx=0.03, rely=0.82, anchor="nw")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                        font=get_relative_font(18, self),
                                        fg_color="white", text_color="black",
                                        width=100, height=40,
                                        command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.back_button.invoke())

        self.update_story()
    
    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapConversation)
        elif value == "Korean":
            show_frame(KorConversation)
        elif value == "Chinese":
            show_frame(ChiConversation)
    
    def on_scenario_select(self, value):
        self.current_scenario = value
        self.update_story()
    
    def update_conversation(self):
        language = "Korean"
        scenario_data = CONVERSATION_DATA[language][self.current_scenario]
        
        text_content = f"{scenario_data['title']}\n\n"
        for speaker, native, romanized, english in scenario_data['lines']:
            text_content += f"{speaker}: {native}\n{romanized}\n{english}\n\n"
        
        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")

    def update_story(self):
        language = "Korean"
        scenario = SCENARIO_CHOICES[language][self.current_scenario]
        # Show context (scenario description)
        context_text = scenario.get("context", "")
        text_content = f"{context_text}\n\n"
        # Add question prompt
        if not self.in_followup:
            text_content += "What will you say? Choose A–D.\n"
        else:
            follow = scenario.get("followup", {})
            if self.in_followup and follow:
                text_content += "What will you reply? Choose A–D.\n"

        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")

        choices = SCENARIO_CHOICES[language][self.current_scenario]["choices"]
        for i, rb in enumerate(self.radio_buttons):
            rb.configure(text=f"{chr(65+i)}. {choices[i]['native']} ({choices[i]['english']})", state="normal")
        self.choice_var.set("")
        self.feedback_label.configure(text="")
        try:
            self.submit_btn.configure(state="normal")
        except Exception:
            pass
        self.in_followup = False

    def submit_answer(self):
        selected = self.choice_var.get()
        if not selected:
            return
        language = "Korean"
        scenario = SCENARIO_CHOICES[language][self.current_scenario]
        if not self.in_followup:
            correct_index = scenario["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            self.feedback_label.configure(text="Correct!")
            follow = scenario.get("followup")
            if follow:
                self.in_followup = True
                npc_response = follow.get("npc_response", "")
                text_content = f"{npc_response}\n\n"
                text_content += "What will you reply? Choose A–D.\n"
                self.conv_text.configure(state="normal")
                self.conv_text.delete("1.0", "end")
                self.conv_text.insert("1.0", text_content)
                self.conv_text.configure(state="disabled")
                for i, rb in enumerate(self.radio_buttons):
                    try:
                        fchoice = follow["choices"][i]
                        rb.configure(text=f"{chr(65+i)}. {fchoice['native']} ({fchoice['english']})", state="normal")
                    except Exception:
                        rb.configure(state="disabled")
                self.choice_var.set("")
                self.feedback_label.configure(text="")
                return
            self.update_conversation()
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return
        follow = scenario.get("followup", None)
        if follow:
            correct_index = follow["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            self.feedback_label.configure(text="Correct!")
            self.update_conversation()
            self.in_followup = False
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return

    def next_scenario(self):
        language = "Korean"
        scenarios = list(SCENARIO_CHOICES[language].keys())
        idx = scenarios.index(self.current_scenario)
        next_idx = (idx + 1) % len(scenarios)
        self.current_scenario = scenarios[next_idx]
        try:
            self.scenario_option.set(self.current_scenario)
        except Exception:
            pass
        self.update_story()
    
    def on_back(self):
        show_frame(ChooseModePage)
    
    def update_elements(self):
        super().update_elements()
        theme = get_current_theme()
        # Keep title large and apply theme to conv box and text
        self.title.configure(font=get_relative_font(120, self), fg_color=theme["primary"])
        try:
            self.conv_frame.configure(fg_color=theme["primary"], border_color="black")
            self.conv_text.configure(font=get_relative_font(28, self), fg_color=theme["primary"], text_color="white")
            for rb in self.radio_buttons:
                rb.configure(font=get_relative_font(20, self))
        except Exception:
            pass
        self.back_button.configure(font=get_relative_font(18, self))

class ChiConversation(DynamicFrame):
    def __init__(self, parent):
        theme = get_current_theme()
        super().__init__(parent, theme["primary"])
        self.current_scenario = "Scenario 1"
        self.create_ui_elements()
    
    def create_ui_elements(self):
        theme = get_current_theme()
        # Title (large)
        self.title = ctk.CTkLabel(self, text="Conversations",
                                  font=get_relative_font(120, self),
                                  text_color="white", fg_color=theme["primary"])
        self.title.place(relx=0.05, rely=0.06, anchor="w")

        # Language & Scenario dropdowns (top-right)
        self.language_option = ctk.CTkOptionMenu(self, values=["Japanese", "Korean", "Chinese"],
                                                 command=self.on_language_select, width=140, height=36)
        self.language_option.set("Chinese")
        self.language_option.place(relx=0.88, rely=0.08, anchor="e")

        self.scenario_option = ctk.CTkOptionMenu(self, values=["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"],
                                                 command=self.on_scenario_select, width=140, height=36)
        self.scenario_option.set("Scenario 1")
        self.scenario_option.place(relx=0.88, rely=0.14, anchor="e")

        # Large centered conversation box (rounded, thinner border to save space)
        self.conv_frame = ctk.CTkFrame(self,
                                       fg_color=theme["primary"],
                                       border_color="black",
                                       border_width=8,
                                       corner_radius=30)
        # move slightly higher and make the box a bit taller/wider to reduce empty margins
        self.conv_frame.place(relx=0.5, rely=0.50, anchor="center", relwidth=0.88, relheight=0.62)

        self.conv_text = ctk.CTkTextbox(self.conv_frame, wrap="word",
                                        font=get_relative_font(28, self),
                                        text_color="white", fg_color=theme["primary"], border_width=0)
        self.conv_text.place(relx=0.03, rely=0.08, relwidth=0.94, relheight=0.50)
        self.conv_text.configure(state="disabled")

        # Choice radio buttons area
        self.choice_var = StringVar(value="")
        # track follow-up state for this scenario
        self.in_followup = False
        choices = SCENARIO_CHOICES["Chinese"][self.current_scenario]["choices"]
        self.radio_buttons = []
        for i, choice in enumerate(choices):
            label = f"{chr(65+i)}. {choice['native']} ({choice['english']})"
            rb = ctk.CTkRadioButton(self.conv_frame, text=label, variable=self.choice_var, value=chr(65+i),
                                    font=get_relative_font(20, self))
            # start choices closer to the text and reduce spacing between them
            rb.place(relx=0.03, rely=0.61 + i*0.06, anchor="nw")
            self.radio_buttons.append(rb)

        self.submit_btn = ctk.CTkButton(self.conv_frame, text="Submit", command=self.submit_answer, width=120, height=38)
        self.submit_btn.place(relx=0.86, rely=0.82, anchor="center")

        self.feedback_label = ctk.CTkLabel(self.conv_frame, text="", text_color="white", fg_color=theme["primary"]) 
        self.feedback_label.place(relx=0.03, rely=0.82, anchor="nw")

        self.back_button = ctk.CTkButton(self, text="BACK", 
                                        font=get_relative_font(18, self),
                                        fg_color="white", text_color="black",
                                        width=100, height=40,
                                        command=self.on_back)
        self.back_button.place(relx=0.07, rely=0.92, anchor="w")

        root.bind("1", lambda event: self.back_button.invoke())

        self.update_story()
    
    def on_language_select(self, value):
        if value == "Japanese":
            show_frame(JapConversation)
        elif value == "Korean":
            show_frame(KorConversation)
        elif value == "Chinese":
            show_frame(ChiConversation)
    
    def on_scenario_select(self, value):
        self.current_scenario = value
        self.update_story()
    
    def update_conversation(self):
        language = "Chinese"
        scenario_data = CONVERSATION_DATA[language][self.current_scenario]
        
        text_content = f"{scenario_data['title']}\n\n"
        for speaker, native, romanized, english in scenario_data['lines']:
            text_content += f"{speaker}: {native}\n{romanized}\n{english}\n\n"
        
        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")

    def update_story(self):
        language = "Chinese"
        scenario = SCENARIO_CHOICES[language][self.current_scenario]
        # Show context (scenario description)
        context_text = scenario.get("context", "")
        text_content = f"{context_text}\n\n"
        # Add question prompt
        if not self.in_followup:
            text_content += "What will YOU say? (Choose A–D)\n"
        else:
            follow = scenario.get("followup", {})
            if self.in_followup and follow:
                text_content += "What will YOU reply? (Choose A–D)\n"

        self.conv_text.configure(state="normal")
        self.conv_text.delete("1.0", "end")
        self.conv_text.insert("1.0", text_content)
        self.conv_text.configure(state="disabled")

        choices = SCENARIO_CHOICES[language][self.current_scenario]["choices"]
        for i, rb in enumerate(self.radio_buttons):
            rb.configure(text=f"{chr(65+i)}. {choices[i]['native']} ({choices[i]['english']})", state="normal")
        self.choice_var.set("")
        self.feedback_label.configure(text="")
        try:
            self.submit_btn.configure(state="normal")
        except Exception:
            pass
        self.in_followup = False

    def submit_answer(self):
        selected = self.choice_var.get()
        if not selected:
            return
        language = "Chinese"
        scenario = SCENARIO_CHOICES[language][self.current_scenario]
        if not self.in_followup:
            correct_index = scenario["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            self.feedback_label.configure(text="Correct!")
            follow = scenario.get("followup")
            if follow:
                self.in_followup = True
                npc_response = follow.get("npc_response", "")
                text_content = f"{npc_response}\n\n"
                text_content += "What will YOU reply? (Choose A–D)\n"
                self.conv_text.configure(state="normal")
                self.conv_text.delete("1.0", "end")
                self.conv_text.insert("1.0", text_content)
                self.conv_text.configure(state="disabled")
                for i, rb in enumerate(self.radio_buttons):
                    try:
                        fchoice = follow["choices"][i]
                        rb.configure(text=f"{chr(65+i)}. {fchoice['native']} ({fchoice['english']})", state="normal")
                    except Exception:
                        rb.configure(state="disabled")
                self.choice_var.set("")
                self.feedback_label.configure(text="")
                return
            self.update_conversation()
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return
        follow = scenario.get("followup", None)
        if follow:
            correct_index = follow["correct"]
            correct_letter = chr(65 + correct_index)
            if selected != correct_letter:
                self.feedback_label.configure(text="Incorrect — try again.")
                theme = get_current_theme()
                if getattr(self, "large_feedback", None) is None:
                    try:
                        self.large_feedback = ctk.CTkLabel(self.conv_frame, text="INCORRECT", text_color="#ff3333",
                                                           font=get_relative_font(48, self), fg_color=theme["primary"]) 
                        self.large_feedback.place(relx=0.78, rely=0.72, anchor="center")
                    except Exception:
                        pass
                else:
                    try:
                        self.large_feedback.configure(text="INCORRECT")
                    except Exception:
                        pass
                self.choice_var.set("")
                return
            self.feedback_label.configure(text="Correct!")
            self.update_conversation()
            self.in_followup = False
            try:
                self.submit_btn.configure(state="disabled")
            except Exception:
                pass
            for rb in self.radio_buttons:
                try:
                    rb.configure(state="disabled")
                except Exception:
                    pass
            return

    def next_scenario(self):
        language = "Chinese"
        scenarios = list(SCENARIO_CHOICES[language].keys())
        idx = scenarios.index(self.current_scenario)
        next_idx = (idx + 1) % len(scenarios)
        self.current_scenario = scenarios[next_idx]
        try:
            self.scenario_option.set(self.current_scenario)
        except Exception:
            pass
        self.update_story()
    
    def on_back(self):
        show_frame(ChooseModePage)
    
    def update_elements(self):
        super().update_elements()
        theme = get_current_theme()
        # Keep title large and apply theme to conv box and text
        self.title.configure(font=get_relative_font(120, self), fg_color=theme["primary"])
        try:
            self.conv_frame.configure(fg_color=theme["primary"], border_color="black")
            self.conv_text.configure(font=get_relative_font(28, self), fg_color=theme["primary"], text_color="white")
            for rb in self.radio_buttons:
                rb.configure(font=get_relative_font(20, self))
        except Exception:
            pass
        self.back_button.configure(font=get_relative_font(18, self))

# Start the application
if __name__ == "__main__":
    # --- Unified tutor/drill and tutor-topic aliases (defined after originals) ---
    class TutorColors(JapColors):
        def __init__(self, parent):
            super().__init__(parent)
            try:
                self.back_button.configure(command=lambda: show_frame(Tutoring))
            except Exception:
                pass
            root.bind("4", lambda e: show_frame(Tutoring))

    class TutorAnimals(JapAnimals):
        def __init__(self, parent):
            super().__init__(parent)
            try:
                self.back_button.configure(command=lambda: show_frame(Tutoring))
            except Exception:
                pass
            root.bind("4", lambda e: show_frame(Tutoring))

    class TutorShapes(JapShapes):
        def __init__(self, parent):
            super().__init__(parent)
            try:
                self.back_button.configure(command=lambda: show_frame(Tutoring))
            except Exception:
                pass
            root.bind("4", lambda e: show_frame(Tutoring))

    class TutorNumbers(JapNumbers):
        def __init__(self, parent):
            super().__init__(parent)
            try:
                self.back_button.configure(command=lambda: show_frame(Tutoring))
            except Exception:
                pass
            root.bind("4", lambda e: show_frame(Tutoring))

    class Alphabets(JapAlphabet):
        def __init__(self, parent):
            super().__init__(parent)
            try:
                self.back_button.configure(command=lambda: show_frame(Tutoring))
            except Exception:
                pass
            root.bind("4", lambda e: show_frame(Tutoring))

    class TutorAlphabet(Alphabets):
        pass

    class Tutoring(JapTutoring):
        def __init__(self, parent):
            super().__init__(parent)
            # Remap button commands to tutor-specific pages
            mapping = {
                'colors': TutorColors,
                'animals': TutorAnimals,
                'shapes': TutorShapes,
                'numbers': TutorNumbers,
                'alphabet': Alphabets,
                'conversation': JapConversation
            }
            for key, target in mapping.items():
                btn = self.buttons.get(key)
                if btn:
                    btn.configure(command=lambda cls=target: show_frame(cls))

            # Rebind hotkeys to tutor pages
            root.bind("0", lambda e: show_frame(JapTranslate))
            root.bind("1", lambda e: show_frame(TutorColors))
            root.bind("2", lambda e: show_frame(TutorAnimals))
            root.bind("3", lambda e: show_frame(TutorShapes))
            root.bind("4", lambda e: show_frame(TutorNumbers))
            root.bind("5", lambda e: show_frame(Alphabets))
            root.bind("6", lambda e: show_frame(JapConversation))

            try:
                self.back_button.configure(command=lambda: show_frame(ChooseModePage))
            except Exception:
                pass

    class Drills(JapDrills):
        def __init__(self, parent):
            super().__init__(parent)
            # Ensure back returns to unified ChooseModePage
            try:
                self.back_button.configure(command=lambda: show_frame(ChooseModePage))
            except Exception:
                pass

    show_frame(MainPage)
    
    # Load saved theme if it exists
    try:
        with open("theme_settings.json", "r") as f:
            theme_data = json.load(f)
            saved_theme = theme_data.get("theme", "Blue")
            if saved_theme in COLOR_THEMES:
                set_theme(saved_theme)
                # Refresh the current frame with new theme
                show_frame(MainPage)
    except Exception as e:
        print(f"No saved theme found or error loading theme: {e}")
    
    root.mainloop()