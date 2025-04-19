import customtkinter as ctk
import tkinter as tk
from dotenv import load_dotenv
import os
from backend.api_backend import run_event_query, run_threat_query, test_api_authentication

EVENT_FORMATS = ["Table", "JSON"]
EVENT_ITEMS = ["1", "5", "10", "50", "No limit"]
EVENT_ACTIONS = ["All", "Block", "SimulationBlock", "Log"]
EVENT_TIMES = ["1 hour", "2 hours", "12 hours", "24 hours", "48 hours"]

THREAT_FORMATS = ["Table", "JSON"]
THREAT_CATEGORIES = ["All", "Process", "File", "Registry", "Network", "Log"]
THREAT_TIMES = ["lastHour", "last12hours", "last24hours", "last7days", "last30days"]
THREAT_ITEMS = ["1", "5", "10", "100"]

def get_default_api_settings():
    return {
        "url": os.getenv("API_URL") or "",
        "username": os.getenv("API_USERNAME") or "",
        "password": os.getenv("API_PASSWORD") or "",
        "organization": os.getenv("API_ORG") or ""
    }
    
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

        # Initialize API settings with values from .env
        from gui.api_gui import get_default_api_settings
        self.api_settings = get_default_api_settings()

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
        
        self.result_box = ctk.CTkTextbox(self.results_frame, font=("Courier New", 13))
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        # self.result_box.insert("0.0", "Waiting for API query...\n\nResults will appear here once you click Search.")
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
            self.url_entry.insert(0, self.api_settings.get("url", ""))

            ctk.CTkLabel(self.inner_frame, text="Username", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.username_entry = ctk.CTkEntry(self.inner_frame, width=entry_width)
            self.username_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.username_entry.insert(0, self.api_settings.get("username", ""))

            ctk.CTkLabel(self.inner_frame, text="Password", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.password_entry = ctk.CTkEntry(self.inner_frame, width=entry_width, show="*")
            self.password_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.password_entry.insert(0, self.api_settings.get("password", ""))

            ctk.CTkLabel(self.inner_frame, text="Organization", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
            self.org_entry = ctk.CTkEntry(self.inner_frame, width=entry_width)
            self.org_entry.pack(pady=(0, 10), anchor="w", padx=10)
            self.org_entry.insert(0, self.api_settings.get("organization", ""))

            # Buttons
            btn_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(10, 10), padx=10)

            self.test_btn = ctk.CTkButton(btn_frame, text="Test", command=self.test_api, width=100)
            self.test_btn.pack(side="right", padx=(5, 0))

            self.reset_btn = ctk.CTkButton(
                btn_frame, text="Reset to Default", command=self.reset_to_default,
                width=140, fg_color="#2e2e2e", hover_color="#444444", text_color="white"
            )
            self.reset_btn.pack(side="right", padx=(5, 0))

            clear_btn_settings = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_results, width=100,
                                               fg_color="#2e2e2e", hover_color="#444444", text_color="white")
            clear_btn_settings.pack(side="right", padx=(5, 0))
    
    def reset_to_default(self):
        load_dotenv()
        self.url_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.org_entry.delete(0, "end")

        self.url_entry.insert(0, os.getenv("API_URL") or "")
        self.username_entry.insert(0, os.getenv("API_USERNAME") or "")
        self.password_entry.insert(0, os.getenv("API_PASSWORD") or "")
        self.org_entry.insert(0, os.getenv("API_ORG") or "")

        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", "API settings reset to default values.\n")
        self.result_box.tag_config("success", foreground="#00FF00")
        self.result_box.tag_add("success", "1.0", "2.0")
            
    def save_api_settings(self):
        # Save current entries to memory
        self.api_settings = {
            "url": self.url_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "organization": self.org_entry.get()
        }

        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", "API settings updated:\n\n")

        text = (
            f'URL: {self.api_settings["url"]}\n'
            f'Username: {self.api_settings["username"]}\n'
            f'Password: {"*" * len(self.api_settings["password"])}\n'
            f'Organization: {self.api_settings["organization"]}\n'
        )
        recap_start = self.result_box.index("end-1c")
        self.result_box.insert("end", text)

        self.result_box.tag_config("field", foreground="#FFA500")
        for field in ["URL", "Username", "Password", "Organization"]:
            self.highlight_word(recap_start, field, "field")

        self.result_box.tag_config("success", foreground="#00FF00")
        self.result_box.tag_add("success", "1.0", "2.0")
            
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

    # JSON FORMAT
    # def test_api(self):
    #     from backend.api_backend import test_api_authentication

    #     self.result_box.delete("0.0", "end")

    #     result = test_api_authentication(
    #         url=self.api_settings["url"],
    #         username=self.api_settings["username"],
    #         password=self.api_settings["password"],
    #         organization=self.api_settings["organization"]
    #     )

    #     if isinstance(result, dict) and result.get("status"):
    #         self.result_box.insert("0.0", "Authentication successful!\n\n")
    #         self.result_box.tag_config("success", foreground="#00FF00")
    #         self.result_box.tag_add("success", "1.0", "2.0")

    #         recap = (
    #             f'URL: {self.api_settings["url"]}\n'
    #             f'Username: {self.api_settings["username"]}\n'
    #             f'Organization: {self.api_settings["organization"]}\n\n'
    #         )
    #         recap_start = self.result_box.index("end-1c")
    #         self.result_box.insert("end", recap)
    #         self.result_box.tag_config("field", foreground="#FFA500")
    #         for field in ["URL", "Username", "Organization"]:
    #             self.highlight_word(recap_start, field, "field")

    #         self.highlight_json(json.dumps(result["data"], indent=2))

    #     else:
    #         self.result_box.insert("0.0", f"Authentication failed.\n\n{result.get('data', 'Unknown error')}")
    #         self.result_box.tag_config("error", foreground="#FF4444")
    #         self.result_box.tag_add("error", "1.0", "3.0")
    
    def test_api(self):
        from backend.api_backend import test_api_authentication

        # Clear previous result
        self.result_box.delete("0.0", "end")

        # Get current values from form fields
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        organization = self.org_entry.get()

        result = test_api_authentication(url, username, password, organization)

        if isinstance(result, dict) and result.get("status"):
            # Authentication success message
            self.result_box.insert("end", "Authentication successful\n\n", "success")
            self.result_box.tag_config("success", foreground="#00FF00")

            # Recap fields
            recap_text = (
                f"URL: {url}\n"
                f"Username: {username}\n"
                f"Organization: {organization}\n\n"
            )
            start = self.result_box.index("end-1c")
            self.result_box.insert("end", recap_text)
            self.result_box.tag_config("field", foreground="#FFA500")
            for word in ["URL", "Username", "Organization"]:
                self.highlight_word(start, word, "field")

            # Display system info summary
            self.display_system_summary(result["data"])

        else:
            self.result_box.insert("0.0", f"Authentication failed.\n\n{result.get('data', 'Unknown error')}")
            self.result_box.tag_config("error", foreground="#FF4444")
            self.result_box.tag_add("error", "1.0", "3.0")

    def display_system_summary(self, data):
        lines = []
        lines.append("System Summary\n==============\n")

        lines.append(f"License Expiration: {data.get('licenseExpirationDate', 'N/A')}")
        lines.append(f"Endpoints Capacity: {data.get('endpointsLicenseCapacity', 'N/A')}")
        lines.append(f"Registered Collectors: {data.get('registeredCollectors', 'N/A')}")
        lines.append(f"Mobile In Use: {data.get('mobileInUse', 'N/A')}\n")

        lines.append("License Features:")
        for feature in data.get("licenseFeatures", []):
            lines.append(f"  - {feature}")
        lines.append("")

        lines.append("Collectors State:")
        for k, v in data.get("collectorsState", {}).items():
            lines.append(f"  {k}: {v}")
        lines.append("")

        lines.append(f"Management Version: {data.get('managementVersion', 'N/A')}")
        lines.append(f"Content Version: {data.get('contentVersion', 'N/A')}\n")

        lines.append("Collector Versions:")
        for version in data.get("collectorVersionsV2", []):
            lines.append(f"  {version['version']} (x{version['count']})")
        lines.append("")

        lines.append("Cores:")
        for core in data.get("cores", []):
            lines.append(f"  {core['name']} - Version: {core['version']}")
        lines.append("")

        lines.append("Aggregators:")
        for aggr in data.get("aggregators", []):
            lines.append(f"  {aggr['name']} - Version: {aggr['version'].strip()}")
        lines.append("")

        lines.append("Repositories:")
        for repo in data.get("repositories", []):
            lines.append(f"  {repo['address']} - Status: {repo['status']}")

        start = self.result_box.index("end-1c")
        self.result_box.insert("end", "\n".join(lines))

        # Color sections
        self.highlight_word(start, "System Summary", "recap")
        self.highlight_word(start, "License Features:", "field")
        self.highlight_word(start, "Collectors State:", "field")
        self.highlight_word(start, "Collector Versions:", "field")
        self.highlight_word(start, "Cores:", "field")
        self.highlight_word(start, "Aggregators:", "field")
        self.highlight_word(start, "Repositories:", "field")

    def highlight_word(self, start, word, tag):
        index = self.result_box.search(word, start, stopindex="end")
        while index:
            end_index = f"{index}+{len(word)}c"
            self.result_box.tag_add(tag, index, end_index)
            index = self.result_box.search(word, end_index, stopindex="end")

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
       
    def clear_results(self):
        self.result_box.delete("0.0", "end")


