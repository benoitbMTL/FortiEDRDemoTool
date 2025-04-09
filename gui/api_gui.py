import customtkinter as ctk
import tkinter as tk
from dotenv import load_dotenv
import os
from backend.api_backend import run_event_query, run_threat_query, test_api_authentication

load_dotenv()

DEFAULT_API_URL = os.getenv("API_URL") or ""
DEFAULT_API_USERNAME = os.getenv("API_USERNAME") or ""
DEFAULT_API_PASSWORD = os.getenv("API_PASSWORD") or ""
DEFAULT_API_ORG = os.getenv("API_ORG") or ""

EVENT_FORMATS = ["Table", "JSON"]
EVENT_ITEMS = ["1", "5", "10", "50", "No limit"]
EVENT_ACTIONS = ["All", "Block", "SimulationBlock", "Log"]
EVENT_TIMES = ["1 hour", "2 hours", "12 hours", "24 hours", "48 hours"]

THREAT_FORMATS = ["Table", "JSON"]
THREAT_CATEGORIES = ["All", "Process", "File", "Registry", "Network", "Log"]
THREAT_TIMES = ["lastHour", "last12hours", "last24hours", "last7days", "last30days"]
THREAT_ITEMS = ["1", "5", "10", "100"]

class FortiEDRAPIView:
    def __init__(self, options_frame, results_frame):
        self.options_frame = options_frame
        self.results_frame = results_frame
        self.selected_mode = "Events"
        self.ev_vars = {}
        self.th_vars = {}
        self.test_btn = None
        self.button_width = 100

        self.ev_buttons = {"format": [], "items": [], "action": [], "time": []}
        self.th_buttons = {"format": [], "items": [], "category": [], "time": []}

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self.options_frame, text="FortiEDR API", font=("Arial", 16, "bold"), text_color="#FFA500").pack(pady=(10, 5), padx=10, anchor="w")

        self.api_mode = ctk.CTkSegmentedButton(
            self.options_frame,
            values=["Events", "Threat Hunting", "API Settings"],
            command=self.switch_mode
        )
        self.api_mode.set("Events")
        self.api_mode.pack(pady=(0, 10), padx=10, anchor="w")

        canvas = tk.Canvas(self.options_frame, bg="#212121", highlightthickness=0, bd=0)
        canvas.pack(side="top", fill="both", expand=True, padx=10)

        inner_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        window_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def on_configure(event): canvas.configure(scrollregion=canvas.bbox("all"))
        def resize(event): canvas.itemconfig(window_id, width=event.width)
        inner_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", resize)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self.inner_frame = inner_frame

        self.bottom_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=(5, 20))

        self.clear_button = ctk.CTkButton(self.bottom_frame, text="Clear", command=self.clear_results, width=100,
                                        fg_color="#2e2e2e", hover_color="#444444", text_color="white")

        self.search_btn = ctk.CTkButton(self.bottom_frame, text="Search", command=self.execute, width=100)

        self.test_btn = ctk.CTkButton(self.bottom_frame, text="Test", command=self.test_api, width=100)
        
        self.result_box = ctk.CTkTextbox(self.results_frame, font=("Courier", 12))
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.result_box.insert("0.0", "Waiting for API query...\n\nResults will appear here once you click Search.")
        self.result_box.tag_config("recap", foreground="#FFA500")

        self.switch_mode("Events")

    def switch_mode(self, mode):
        self.selected_mode = mode
        self.build_ui(mode)

    def build_ui(self, mode):
        # Clear previous content
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Always forget buttons to avoid duplicates
        self.clear_button.pack_forget()
        self.search_btn.pack_forget()
        self.test_btn.pack_forget()

        # === EVENTS MODE ===
        if mode == "Events":
            if self.test_btn:
                self.test_btn.pack_forget()

            self.ev_buttons = {"format": [], "items": [], "action": [], "time": []}
            self.ev_vars = {"format": "Table", "items": "1", "action": "All", "time": "1 hour"}

            self.search_btn.pack(in_=self.bottom_frame, side="right", padx=(5, 0))
            self.clear_button.pack(in_=self.bottom_frame, side="right", padx=(5, 0))
            
            container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            container.pack(pady=0)

            col1 = ctk.CTkFrame(container, fg_color="transparent", width=180)
            col1.pack(side="left", padx=(0, 30), fill="y")

            col2 = ctk.CTkFrame(container, fg_color="transparent", width=180)
            col2.pack(side="left", padx=(30, 0), fill="y")

            # Column 1: Format + Items
            ctk.CTkLabel(col1, text="Format", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(10, 2))
            for opt in EVENT_FORMATS:
                btn = ctk.CTkButton(col1, text=opt, width=140,
                    command=lambda v=opt: self.set_var("format", v, "ev"),
                    fg_color="#FFA500" if opt == "Table" else "#2e2e2e",
                    hover_color="#FFA500" if opt == "Table" else "#444444",
                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.ev_buttons["format"].append(btn)

            ctk.CTkLabel(col1, text="Number of Events", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(15, 2))
            for opt in EVENT_ITEMS:
                btn = ctk.CTkButton(col1, text=opt, width=140, command=lambda v=opt: self.set_var("items", v, "ev"),
                                    fg_color="#FFA500" if opt == "1" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "1" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.ev_buttons["items"].append(btn)

            # Column 2: Action + Time
            ctk.CTkLabel(col2, text="Action Filter", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(10, 2))
            for opt in EVENT_ACTIONS:
                btn = ctk.CTkButton(col2, text=opt, width=140, command=lambda v=opt: self.set_var("action", v, "ev"),
                                    fg_color="#FFA500" if opt == "All" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "All" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.ev_buttons["action"].append(btn)

            ctk.CTkLabel(col2, text="Time Range", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(15, 2))
            for opt in EVENT_TIMES:
                btn = ctk.CTkButton(col2, text=opt, width=140, command=lambda v=opt: self.set_var("time", v, "ev"),
                                    fg_color="#FFA500" if opt == "1 hour" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "1 hour" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.ev_buttons["time"].append(btn)

        # === THREAT HUNTING MODE ===
        elif mode == "Threat Hunting":
            if self.test_btn:
                self.test_btn.pack_forget()

            # Réinitialiser les boutons et les valeurs sélectionnées
            self.th_buttons = {"format": [], "items": [], "category": [], "time": []}
            self.th_vars = {"format": "Table", "items": "1", "category": "All", "time": "lastHour"}

            self.search_btn.pack(in_=self.bottom_frame, side="right", padx=(5, 0))
            self.clear_button.pack(in_=self.bottom_frame, side="right", padx=(5, 0))

            container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            container.pack(pady=0)

            col1 = ctk.CTkFrame(container, fg_color="transparent", width=180)
            col1.pack(side="left", padx=(0, 30), fill="y")

            col2 = ctk.CTkFrame(container, fg_color="transparent", width=180)
            col2.pack(side="left", padx=(30, 0), fill="y")

            # Column 1: Format + Items
            ctk.CTkLabel(col1, text="Format", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(10, 2))
            for opt in THREAT_FORMATS:
                btn = ctk.CTkButton(col1, text=opt, width=140, command=lambda v=opt: self.set_var("format", v, "th"),
                                    fg_color="#FFA500" if opt == "Table" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "Table" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.th_buttons["format"].append(btn)

            ctk.CTkLabel(col1, text="Items", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(15, 2))
            for opt in THREAT_ITEMS:
                btn = ctk.CTkButton(col1, text=opt, width=140, command=lambda v=opt: self.set_var("items", v, "th"),
                                    fg_color="#FFA500" if opt == "1" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "1" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.th_buttons["items"].append(btn)

            # Column 2: Category + Time
            ctk.CTkLabel(col2, text="Category", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(10, 2))
            for opt in THREAT_CATEGORIES:
                btn = ctk.CTkButton(col2, text=opt, width=140, command=lambda v=opt: self.set_var("category", v, "th"),
                                    fg_color="#FFA500" if opt == "All" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "All" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.th_buttons["category"].append(btn)

            ctk.CTkLabel(col2, text="Time Range", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", pady=(15, 2))
            for opt in THREAT_TIMES:
                btn = ctk.CTkButton(col2, text=opt, width=140, command=lambda v=opt: self.set_var("time", v, "th"),
                                    fg_color="#FFA500" if opt == "lastHour" else "#2e2e2e",
                                    hover_color="#FFA500" if opt == "lastHour" else "#444444",
                                    text_color="white")
                btn.pack(pady=2, fill="x")
                self.th_buttons["time"].append(btn)

        # === API SETTINGS MODE ===
        elif mode == "API Settings":
            self.search_btn.pack_forget()

            entry_width = 360

            ctk.CTkLabel(self.inner_frame, text="API URL", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.url_entry = ctk.CTkEntry(self.inner_frame, width=entry_width)
            self.url_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.url_entry.insert(0, DEFAULT_API_URL)

            ctk.CTkLabel(self.inner_frame, text="Username", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.username_entry = ctk.CTkEntry(self.inner_frame, width=entry_width)
            self.username_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.username_entry.insert(0, DEFAULT_API_USERNAME)

            ctk.CTkLabel(self.inner_frame, text="Password", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.password_entry = ctk.CTkEntry(self.inner_frame, width=entry_width, show="*")
            self.password_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.password_entry.insert(0, DEFAULT_API_PASSWORD)

            ctk.CTkLabel(self.inner_frame, text="Organization", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.org_entry = ctk.CTkEntry(self.inner_frame, width=entry_width)
            self.org_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.org_entry.insert(0, DEFAULT_API_ORG)

            # Right-aligned Test button
            btn_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(10, 10), padx=10)
            
            self.test_btn = ctk.CTkButton(btn_frame, text="Test", command=self.test_api, width=100)
            self.test_btn.pack(side="right", padx=(5, 0))

            self.clear_button.pack_forget()  
            clear_btn_settings = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_results, width=100,
                                            fg_color="#2e2e2e", hover_color="#444444", text_color="white")
            clear_btn_settings.pack(side="right", padx=(5, 0))

    def execute(self):
        self.result_box.delete("0.0", "end")

        try:
            if self.selected_mode == "Events":
                vals = self.ev_vars

                result = run_event_query(
                    output_format=vals.get("format", "table"),
                    items=vals.get("items", "1"),
                    action=vals.get("action", "All"),
                    time_range=vals.get("time", "1 hour")
                )

                recap = f"FortiEDR Events — Format: {vals.get('format')} | Time: {vals.get('time')} | Action: {vals.get('action')} | Items: {vals.get('items')}\n\n"

                if vals.get("format", "Table").lower() == "json":
                    self.result_box.insert("0.0", recap)
                    self.result_box.tag_add("recap", "1.0", "3.0")
                    self.highlight_json(result)
                else:
                    full_output = recap + result + "\n"
                    self.result_box.insert("0.0", full_output)
                    self.result_box.tag_add("recap", "1.0", "3.0")

            elif self.selected_mode == "Threat Hunting":
                vals = self.th_vars

                result = run_threat_query(
                    fmt=vals.get("format", "table"),
                    items=vals.get("items", "1"),
                    category=vals.get("category", "All"),
                    time_range=vals.get("time", "lastHour")
                )

                recap = f"Threat Hunting — Format: {vals.get('format')} | Time: {vals.get('time')} | Category: {vals.get('category')} | Items: {vals.get('items')}\n\n"

                if vals.get("format", "Table").lower() == "json":
                    self.result_box.insert("0.0", recap)
                    self.result_box.tag_add("recap", "1.0", "3.0")
                    self.highlight_json(result)
                else:
                    full_output = recap + result + "\n"
                    self.result_box.insert("0.0", full_output)
                    self.result_box.tag_add("recap", "1.0", "3.0")

            else:
                self.result_box.insert("0.0", "Nothing to execute in this mode.")

        except Exception as e:
            self.result_box.delete("0.0", "end")
            self.result_box.insert("0.0", f"[ERROR] {str(e)}")

    def highlight_json(self, text):
        # Insérer après recap
        insert_point = self.result_box.index("end-1c")
        self.result_box.insert(insert_point, text + "\n")

        # Définir les tags de couleur
        self.result_box.tag_config("key", foreground="#FFA500")     # orange
        self.result_box.tag_config("string", foreground="#00FF00")  # vert
        self.result_box.tag_config("number", foreground="#00BFFF")  # bleu
        self.result_box.tag_config("boolean", foreground="#FF69B4") # rose
        self.result_box.tag_config("null", foreground="#FF0000")    # rouge

        # Index de départ réel après l'insertion
        start_index = int(float(insert_point.split('.')[0]))

        lines = text.splitlines()
        for i, line in enumerate(lines):
            line_index = f"{start_index + i}.0"

            if ':' not in line:
                continue

            key_part, value_part = line.split(':', 1)
            key_len = len(key_part)
            value = value_part.strip()

            # Appliquer les couleurs
            self.result_box.tag_add("key", line_index, f"{line_index}+{key_len}c")

            value_index = f"{line_index}+{key_len + 1}c"
            if value.startswith('"'):
                self.result_box.tag_add("string", value_index, f"{value_index}+{len(value)+1}c")
            elif value in ["true", "false"]:
                self.result_box.tag_add("boolean", value_index, f"{value_index}+{len(value)+1}c")
            elif value == "null":
                self.result_box.tag_add("null", value_index, f"{value_index}+{len(value)+1}c")
            else:
                self.result_box.tag_add("number", value_index, f"{value_index}+{len(value)+1}c")

    def test_api(self):
        result = test_api_authentication()
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", result)

    def set_var(self, key, value, mode_prefix):
        # Set selected value
        if mode_prefix == "ev":
            self.ev_vars[key] = value
            group = self.ev_buttons.get(key, [])
        elif mode_prefix == "th":
            self.th_vars[key] = value
            group = self.th_buttons.get(key, [])
        else:
            return

        # Update button colors in this group
        for btn in group:
            try:
                if btn.cget("text") == value:
                    btn.configure(fg_color="#FFA500", hover_color="#FFA500")
                else:
                    btn.configure(fg_color="#2e2e2e", hover_color="#444444")
            except tk.TclError:
                continue


    def test_api(self):
        result = "API test successful.\n\nURL: {}\nUser: {}\nOrg: {}".format(
            DEFAULT_API_URL, DEFAULT_API_USERNAME, DEFAULT_API_ORG
        )
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", result)
        
    def clear_results(self):
        self.result_box.delete("0.0", "end")
