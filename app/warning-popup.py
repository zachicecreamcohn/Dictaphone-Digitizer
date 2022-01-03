import tkinter as tk
from tkinter import messagebox

def alert(title, alert_content):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, alert_content)



