import customtkinter as ctk

def create_nav_button(parent, text, command, fg="#1f1f1f", hover="#333333", text_color="white"):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=fg,
        hover_color=hover,
        text_color=text_color,
        corner_radius=6,
        font=("Arial", 12, "bold")
    )
