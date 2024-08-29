import tkinter as tk
from gui import LiteratureReviewApp
import os

def main():
    root = tk.Tk()

    # Load the icon
    icon_path = os.path.join(os.path.dirname(__file__), 'LiTT.png')
    if os.path.exists(icon_path):
        root.iconphoto(True, tk.PhotoImage(file=icon_path))
    else:
        print("Icon file not found, using default icon.")

    app = LiteratureReviewApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

