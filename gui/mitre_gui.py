import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data.tests import tests
from backend.mitre_backend import execute_atomic_test
import threading

class MitreView:
    def __init__(self, options_frame, results_frame):
        self.options_frame = options_frame
        self.results_frame = results_frame
        self.selected_test = None
        self.test_buttons = []
        self.setup_ui()

    def setup_ui(self):
        title = ctk.CTkLabel(
            self.options_frame,
            text="Select a MITRE technique to execute",
            font=("Arial", 16, "bold"),
            text_color="#FFA500"
        )
        title.pack(pady=(10, 5), padx=10, anchor="w")

        container = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10)
        container.grid_columnconfigure(0, weight=1)

        self.button_list_frame = ctk.CTkFrame(container, fg_color="transparent", width=340)
        self.button_list_frame.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.test_buttons = []
        for test in tests:
            btn = ctk.CTkButton(self.button_list_frame, text=f"{test['id']} - {test['title']}", width=340, anchor="w", height=30, text_color="white", fg_color="#2e2e2e", hover_color="#444444", command=lambda t=test: self.select_test(t))
            btn.pack(fill="x", pady=2)
            self.test_buttons.append(btn)

        self.command_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.command_frame.grid(row=1, column=0, sticky="e", pady=(5, 5))

        self.exec_button = ctk.CTkButton(self.command_frame, text="Execute", command=self.run_test, width=100)
        self.exec_button.pack(side="right", padx=(5, 0))

        self.cleanup_button = ctk.CTkButton(
            self.command_frame, text="Cleanup", command=self.cleanup_test, width=100,
            fg_color="#2e2e2e", hover_color="#444444", text_color="white"
        )
        self.cleanup_button.pack(side="right", padx=(5, 0))

        self.details_button = ctk.CTkButton(
            self.command_frame, text="Show Details", command=self.details_test, width=100,
            fg_color="#2e2e2e", hover_color="#444444", text_color="white"
        )
        self.details_button.pack(side="right", padx=(5, 0))

        self.clear_button = ctk.CTkButton(self.command_frame, text="Clear", command=self.clear_results, width=100, fg_color="#2e2e2e", hover_color="#444444", text_color="white")
        self.clear_button.pack(side="right", padx=(5, 0))

        self.description_box = ctk.CTkTextbox(container, wrap="word", activate_scrollbars=False)
        self.description_box.grid(row=2, column=0, sticky="nsew", pady=(5, 10))
        self.description_box.configure(state="disabled")

        container.grid_rowconfigure(2, weight=1)

        # self.result_box = ctk.CTkTextbox(self.results_frame)
        self.result_box = ctk.CTkTextbox(self.results_frame, font=("Courier New", 13))
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.result_box.tag_config("orange", foreground="#FFA500")
        self.result_box.tag_config("red", foreground="red")
        #self.result_box.insert("0.0", "Execution results will appear here...")

        if tests:
            self.select_test(tests[0])

    def run_test(self):
        command = self.selected_test["command"] if self.selected_test else ""
        self.exec_button.configure(text="Executing...", state="disabled")
        # self.exec_button.configure(text="⏳ Executing...", state="disabled")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "Executing command:\n", "orange")
        self.result_box.insert("end", f"{command}\n\n")
        threading.Thread(target=lambda: self.execute_and_show_result(command)).start()

    def execute_and_show_result(self, command):
        stdout, stderr = execute_atomic_test(command)
        self.results_frame.after(0, lambda: self.display_result(stdout, stderr))

    def display_result(self, stdout, stderr):
        if stdout: self.result_box.insert("end", "Output:\n", "orange"); self.result_box.insert("end", f"{stdout}\n")
        if stderr: self.result_box.insert("end", "\nErrors:\n", "red"); self.result_box.insert("end", f"{stderr}\n")
        self.exec_button.configure(text="Execute", state="normal")

    def select_test(self, test):
        self.selected_test = test

        for btn in self.test_buttons:
            if btn.cget("text").startswith(test["id"]):
                btn.configure(fg_color="#FFA500", hover_color="#FFA500", text_color="white")
            else:
                btn.configure(fg_color="#2e2e2e", hover_color="#444444", text_color="white")

        self.description_box.configure(state="normal")
        self.description_box.delete("0.0", "end")
        self.description_box.insert("0.0", f"{test['test']}\n", ("orange",))
        self.description_box.insert("end", f"{test['description']}\n\n")
        self.description_box.insert("end", "Violated Policies\n", ("orange",))
        for rule in test["rules"]:
            if rule.startswith("-"):
                self.description_box.insert("end", f"  - {rule[2:]}\n")
            else:
                self.description_box.insert("end", f"{rule}\n")
        self.description_box.insert("end", "\nCommand\n", ("orange",))
        self.description_box.insert("end", f"{test['command']}")
        self.description_box.tag_config("orange", foreground="#FFA500")
        self.description_box.configure(state="disabled")

    def run_command(self, command):
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", f"{command}\n")
        self.result_box.insert("0.0", "Running command:\n", "orange")
        self.result_box.update_idletasks()

        stdout, stderr = execute_atomic_test(command)

        if stdout:
            self.result_box.insert("end", "\n", "orange")
            self.result_box.insert("end", "Output:\n", "orange")
            self.result_box.insert("end", f"{stdout}\n")
        if stderr:
            self.result_box.insert("end", "\n", "red")
            self.result_box.insert("end", "Errors:\n", "red")
            self.result_box.insert("end", f"{stderr}\n")

    def execute_test(self):
        if not self.selected_test:
            messagebox.showwarning("No Test Selected", "Please select a test to execute.")
            return
        command = self.selected_test["command"]
        self.run_command(command)

    def cleanup_test(self):
        if not self.selected_test:
            return
        command = self.selected_test["command"] + " -Cleanup"
        self.run_command(command)

    def details_test(self):
        if not self.selected_test:
            return
        command = self.selected_test["command"] + " -ShowDetails"
        self.run_command(command)

    def clear_results(self):
        self.result_box.delete("0.0", "end")
