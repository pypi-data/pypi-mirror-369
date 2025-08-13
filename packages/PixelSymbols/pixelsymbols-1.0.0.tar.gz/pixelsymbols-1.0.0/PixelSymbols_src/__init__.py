# PixelSymbols/__init__.py
import os
import tkinter as tk

class PixelSymbols:
    def __init__(self, path=None):
        # Always use font folder inside package if path not given
        base_dir = os.path.dirname(__file__)
        fonts_dir = os.path.join(base_dir, "font") if path is None else path

        self.root = tk.Tk()
        self.root.withdraw()
        self.symbols = {}
        self._load_symbols(fonts_dir)

    def _load_symbols(self, path):
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Symbol folder '{path}' not found.")

        for filename in os.listdir(path):
            if filename.lower().endswith(".png"):
                name = os.path.splitext(filename)[0]
                img_path = os.path.join(path, filename)
                self.symbols[name] = tk.PhotoImage(file=img_path)

    def get(self, name):
        return self.symbols.get(name)

    def list_symbols(self):
        return list(self.symbols.keys())
