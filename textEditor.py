#!/usr/bin/env python3
"""
cool_text_editor.py

A single-file, feature-rich text editor using Tkinter.
Features:
 - New/Open/Save/Save As
 - Cut/Copy/Paste
 - Find & Replace
 - Dark/Light theme toggle
 - Line numbers & status bar
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cool Text Editor")
        self.geometry("800x600")

        # State
        self.filepath = None
        self.dark_mode = False

        # UI Setup
        self._create_menu()
        self._create_toolbar()
        self._create_text_widget()
        self._create_statusbar()
        self._bind_shortcuts()
        self._apply_theme()

    def _create_menu(self):
        menubar = tk.Menu(self)
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace", accelerator="Ctrl+F", command=self.find_replace)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        self.config(menu=menubar)

    def _create_toolbar(self):
        # For future expansion (icons/buttons)
        pass

    def _create_text_widget(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.linenumbers = tk.Text(container, width=4, padx=4, takefocus=0, border=0,
                                   background='lightgrey', state='disabled', wrap='none')
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        # Main text area
        self.text = ScrolledText(container, undo=True, wrap='word')
        self.text.pack(fill=tk.BOTH, expand=True)

        # Update line numbers on events
        self.text.bind("<Any-KeyPress>", lambda e: self._update_linenumbers())
        self.text.bind("<Button-1>", lambda e: self._update_linenumbers())
        self.text.bind("<MouseWheel>", lambda e: self._update_linenumbers())

    def _create_statusbar(self):
        self.status = ttk.Label(self, text="Ln 1, Col 1")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.bind("<KeyRelease>", self._update_status)

    def _bind_shortcuts(self):
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-S>", lambda e: self.save_as())
        self.bind_all("<Control-f>", lambda e: self.find_replace())

    def _apply_theme(self):
        if self.dark_mode:
            bg, fg = "#2e2e2e", "#dcdcdc"
            ln_bg = "#333333"
        else:
            bg, fg = "white", "black"
            ln_bg = "lightgrey"
        self.text.config(bg=bg, fg=fg, insertbackground=fg)
        self.linenumbers.config(background=ln_bg, fg=fg)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def new_file(self):
        if self._confirm_discard():
            self.filepath = None
            self.text.delete(1.0, tk.END)
            self._update_title()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.filepath = path
            self.text.delete(1.0, tk.END)
            self.text.insert(1.0, content)
            self._update_title()
            self._update_linenumbers()

    def save_file(self):
        if self.filepath:
            self._write_to_file(self.filepath)
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            self.filepath = path
            self._write_to_file(path)
            self._update_title()

    def _write_to_file(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text.get(1.0, tk.END))
            self.status.config(text=f"Saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _confirm_discard(self):
        if self.text.edit_modified():
            choice = messagebox.askyesnocancel("Unsaved Changes",
                                               "You have unsaved changes. Save before proceeding?")
            if choice:  # Yes
                self.save_file()
                return True
            elif choice is False:  # No
                return True
            else:
                return False  # Cancel
        return True

    def _update_title(self):
        name = os.path.basename(self.filepath) if self.filepath else "Untitled"
        self.title(f"{name} - Cool Text Editor")
        self.text.edit_modified(False)

    def _update_status(self, event=None):
        line, col = self.text.index(tk.INSERT).split('.')
        self.status.config(text=f"Ln {line}, Col {int(col)+1}")

    def _update_linenumbers(self):
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        row, _ = self.text.index(tk.END).split('.')
        for i in range(1, int(row)):
            self.linenumbers.insert(tk.END, f"{i}\n")
        self.linenumbers.config(state='disabled')

    def find_replace(self):
        find = simpledialog.askstring("Find", "Find:")
        if find:
            replace = simpledialog.askstring("Replace", "Replace with:")
            content = self.text.get(1.0, tk.END)
            new_content = content.replace(find, replace if replace is not None else "")
            self.text.delete(1.0, tk.END)
            self.text.insert(1.0, new_content)
            self.status.config(text=f"Replaced all '{find}'")

if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
