import customtkinter as ctk
from gui_app import SimulationApp
from database_handler import DBHandler

if __name__ == "__main__":
    db = DBHandler()
    root = ctk.CTk()
    app = SimulationApp(root, db)
    root.mainloop()