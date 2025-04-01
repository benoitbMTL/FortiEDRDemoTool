import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tests import tests

class MitreView:
    def __init__(self, options_frame, results_frame):
        self.options_frame = options_frame
        self.results_frame = results_frame
        self.selected_test = None
        self.test_buttons = []
        self.setup_ui()

    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(
            self.options_frame,
            text="Select a MITRE technique to execute",
            font=("Arial", 16, "bold"),
            text_color="#FFA500"
        )
        title.pack(pady=(10, 5), padx=10, anchor="w")

        # Main container using grid layout
        container = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10)

        container.grid_columnconfigure(0, weight=1)

        # === Frame for test buttons ===
        self.button_list_frame = ctk.CTkFrame(container, fg_color="transparent", width=340)
        self.button_list_frame.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.test_buttons = []
        for test in tests:
            btn = ctk.CTkButton(
                self.button_list_frame,
                text=f"{test['id']} - {test['title']}",
                width=340,
                anchor="w",
                height=30,
                text_color="white",
                fg_color="#2e2e2e",
                hover_color="#444444",
                command=lambda t=test: self.select_test(t)
            )
            btn.pack(fill="x", pady=2)
            self.test_buttons.append(btn)

        # === Execute / Reset buttons ===
        self.command_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.command_frame.grid(row=1, column=0, sticky="e", pady=(5, 5))

        self.exec_button = ctk.CTkButton(self.command_frame, text="Execute", command=self.execute_test, width=100)
        self.exec_button.pack(side="right", padx=(5, 0))

        self.reset_button = ctk.CTkButton(
            self.command_frame,
            text="Reset",
            command=self.reset_results,
            width=100,
            fg_color="#2e2e2e",
            hover_color="#444444",
            text_color="white"
        )
        self.reset_button.pack(side="right", padx=(0, 5))

        # === Description Box (just under Execute) ===
        self.description_box = ctk.CTkTextbox(container, wrap="word", activate_scrollbars=False)
        self.description_box.grid(row=2, column=0, sticky="nsew", pady=(5, 10))
        self.description_box.configure(state="disabled")

        container.grid_rowconfigure(2, weight=1)

        # === Results on the right side ===
        self.result_box = ctk.CTkTextbox(self.results_frame)
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.result_box.insert("0.0", "Execution results will appear here...")

        # Preselect the first test
        if tests:
            self.select_test(tests[0])

    def select_test(self, test):
        self.selected_test = test

        # Update button colors
        for btn in self.test_buttons:
            if btn.cget("text").startswith(test["id"]):
                btn.configure(fg_color="#FFA500", hover_color="#FFA500", text_color="white")
            else:
                btn.configure(fg_color="#2e2e2e", hover_color="#444444", text_color="white")

        # Fill the description box with highlighted sections
        self.description_box.configure(state="normal")
        self.description_box.delete("0.0", "end")

        # Test name (highlighted)
        self.description_box.insert("0.0", f"{test['test']}\n", ("orange",))
        self.description_box.insert("end", f"{test['description']}\n\n")

        # FortiEDR Violated Policies (highlighted)
        self.description_box.insert("end", "Violated Policies\n", ("orange",))
        for rule in test["rules"]:
            if rule.startswith("-"):
                # Sub-rule: add dash + indent
                self.description_box.insert("end", f"  - {rule[2:]}\n")
            else:
                # Main rule: category name
                self.description_box.insert("end", f"{rule}\n")

        # Command section
        self.description_box.insert("end", "\nCommand\n", ("orange",))
        self.description_box.insert("end", f"{test['command']}")

        # Tag style (bold not supported in CTkTextbox)
        self.description_box.tag_config("orange", foreground="#FFA500")

    def execute_test(self):
        if not self.selected_test:
            messagebox.showwarning("No Test Selected", "Please select a test to execute.")
            return

        # Simulated output (to be replaced later by real execution)
        command = self.selected_test["command"]
        output = f"Executing test:\n\n{command}\n\n[Simulated command output here...]"

        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", output)

    def reset_results(self):
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", "Execution results will appear here...")
