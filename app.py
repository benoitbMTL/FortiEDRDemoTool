import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import socket
import threading
from dotenv import load_dotenv

from gui.mitre_gui import MitreView
from gui.malware_gui import MalwareBazaarView
from gui.api_gui import FortiEDRAPIView
from backend.diagnostics import run_all_diagnostics
from backend.FortiEDRAvScanner import run_av_scan
from utils import resource_path


# Debug .env path
env_path = resource_path('.env')
print(f"[DEBUG] Looking for .env at: {env_path}")

if os.path.exists(env_path):
    print("[DEBUG] .env file exists.")
else:
    print("[DEBUG] .env file NOT found.")

# Now load it
load_result = load_dotenv(env_path)
print(f"[DEBUG] .env loaded: {load_result}")

# Check a key
print(f"[DEBUG] API_URL = {os.getenv('API_URL')}")


# Always start in dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Load environment variables from .env file
load_dotenv(resource_path('.env'))

class FortiEDRDemoTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FortiEDR Demo Tool")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        self.iconbitmap(resource_path(os.path.join("assets", "fortinet.ico")))

        # Configure main grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Options + Results

        # Left Navigation Menu
        self.nav_frame = ctk.CTkFrame(self, width=120, fg_color="#2a2a2a")
        self.nav_frame.grid(row=0, column=0, sticky="ns")

        # Load logo
        logo_path = resource_path(os.path.join("assets", "fortinet-logo-white.png"))
        logo = Image.open(logo_path)
        w_percent = 130 / float(logo.size[0])
        h_size = int(float(logo.size[1]) * w_percent)
        logo_img = logo.resize((130, h_size), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(logo_img)
        self.logo_label = tk.Label(self.nav_frame, image=self.logo, bg="#2a2a2a")
        self.logo_label.grid(row=0, column=0, pady=(15, 5))

        def create_nav_button(parent, text, command):
            btn = ctk.CTkButton(parent, text=text, command=command, fg_color="#2e2e2e", hover_color="#444444", text_color="white", corner_radius=6, font=("Arial", 12, "bold"))
            return btn

        self.active_nav = None

        def set_active_nav(btn):
            if self.active_nav:
                self.active_nav.configure(fg_color="#2e2e2e", hover_color="#444444")
            btn.configure(fg_color="#FFA500", hover_color="#FFA500")
            self.active_nav = btn

        # Top buttons
        self.btn_mitre = create_nav_button(self.nav_frame, "MITRE", lambda: [self.show_mitre(), set_active_nav(self.btn_mitre)])
        self.btn_mitre.grid(row=1, column=0, pady=(10, 5), padx=10, sticky="ew")

        self.btn_malwarebazaar = create_nav_button(self.nav_frame, "Malware Bazaar", lambda: [self.show_malwarebazaar(), set_active_nav(self.btn_malwarebazaar)])
        self.btn_malwarebazaar.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        self.btn_api = create_nav_button(self.nav_frame, "FortiEDR API", lambda: [self.show_api(), set_active_nav(self.btn_api)])
        self.btn_api.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

        self.nav_frame.grid_rowconfigure(4, weight=1)

        # Bottom buttons

        # Host Info Frame (row 5)
        host_info_frame = ctk.CTkFrame(
            self.nav_frame,
            fg_color="transparent",  # plus de fond coloré
            border_color="white",    # contour blanc
            border_width=1,
            corner_radius=0          # coins droits
        )
        host_info_frame.grid(row=5, column=0, padx=10, pady=(5, 5), sticky="ew")

        local_hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(local_hostname)
        except Exception:
            ip_address = "Unavailable"

        host_info_text = f"Host: {local_hostname}\nIP: {ip_address}"
        self.hostinfo_label = ctk.CTkLabel(
            host_info_frame,
            text=host_info_text,
            text_color="white",
            font=("Courier New", 12, "bold"),
            justify="center"
        )
        self.hostinfo_label.pack(pady=5)

        # AV Scanner Button
        self.av_btn = create_nav_button(self.nav_frame, "AV Scanner", lambda: self.show_av_scanner())
        self.av_btn.configure(fg_color="#006400", hover_color="#228B22")
        self.av_btn.grid(row=6, column=0, pady=5, padx=10, sticky="ew")

        # Health Check Button
        self.diagnostic_btn = create_nav_button(self.nav_frame, "Health Check", lambda: self.show_diagnostics())
        self.diagnostic_btn.configure(fg_color="#228B22", hover_color="#32CD32")
        self.diagnostic_btn.grid(row=7, column=0, pady=5, padx=10, sticky="ew")
                
        # Full Screen Button
        self.fullscreen_btn = create_nav_button(self.nav_frame, "Full Screen", self.toggle_fullscreen)
        self.fullscreen_btn.configure(fg_color="#4c566a", hover_color="#5e6a7a")
        self.fullscreen_btn.grid(row=8, column=0, pady=5, padx=10, sticky="ew")

        # Quit Button
        self.quit_btn = create_nav_button(self.nav_frame, "Quit", self.quit)
        self.quit_btn.configure(fg_color="#cc0000", hover_color="#ff3333")
        self.quit_btn.grid(row=9, column=0, pady=(5, 20), padx=10, sticky="ew")

        # PanedWindow for Options and Results (grid inside column 1)
        self.paned_window = tk.PanedWindow(self, orient="horizontal", sashrelief="raised", sashwidth=8, bg="#1f1f1f")
        self.paned_window.grid(row=0, column=1, sticky="nsew")

        self.options_frame = ctk.CTkFrame(self.paned_window)
        self.results_frame = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.options_frame, minsize=300)
        self.paned_window.add(self.results_frame)

        self.mitre_view = MitreView(self.options_frame, self.results_frame)
        self.malware_view = MalwareBazaarView(self.options_frame, self.results_frame)
        self.api_view = FortiEDRAPIView(self.options_frame, self.results_frame)

        self.show_mitre()
        set_active_nav(self.btn_mitre)

    def clear_frames(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def toggle_fullscreen(self):
        current_state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current_state)
        if not current_state:
            self.fullscreen_btn.configure(fg_color="#4c566a", hover_color="#4c566a")
        else:
            self.fullscreen_btn.configure(fg_color="#1f1f1f", hover_color="#333333")

    def run_diagnostics(self):
        run_all_diagnostics()

    def show_mitre(self):
        self.clear_frames()
        self.mitre_view = MitreView(self.options_frame, self.results_frame)

    def show_malwarebazaar(self):
        self.clear_frames()
        self.malware_view = MalwareBazaarView(self.options_frame, self.results_frame)

    def show_api(self):
        self.clear_frames()
        self.api_view = FortiEDRAPIView(self.options_frame, self.results_frame)

    def show_diagnostics(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        self.result_box = ctk.CTkTextbox(self.results_frame, font=("Courier New", 13))
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.result_box.tag_config("orange", foreground="#FFA500")
        self.result_box.tag_config("red", foreground="red")
        self.result_box.tag_config("green", foreground="#00FF00")
        self.result_box.tag_config("title", foreground="white")

        # Lancer le diagnostic dans un thread pour ne pas bloquer l'UI
        threading.Thread(target=lambda: run_all_diagnostics(self.result_box)).start()

    def show_av_scanner(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        self.result_box = ctk.CTkTextbox(self.results_frame, font=("Courier New", 13))
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)

        self.result_box.tag_config("orange", foreground="#FFA500")
        self.result_box.tag_config("red", foreground="red")
        self.result_box.tag_config("green", foreground="#00FF00")
        self.result_box.tag_config("white", foreground="#ffffff")

        from backend.FortiEDRAvScanner import run_av_scan
        run_av_scan(self.result_box)

if __name__ == "__main__":
    app = FortiEDRDemoTool()
    app.mainloop()
