import tkinter as tk
from banker_gui import BankerGUI

def main():
    root = tk.Tk()
    app = BankerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 