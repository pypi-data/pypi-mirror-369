from .gui_main import ConfigurableGUI
from .ui_dict import UiDictionary
import tkinter as tk
import argparse

def main():
    parser = argparse.ArgumentParser(description='GUI Script Runner')
    parser.add_argument('--config', default='config.json', help='Main configuration file')
    parser.add_argument('--dict', default='dict.txt', help='UI dictionary file')
    args = parser.parse_args()
    
    root = tk.Tk()
    app = ConfigurableGUI(root, args.dict, args.config)
    root.mainloop()

if __name__ == "__main__":
    main()