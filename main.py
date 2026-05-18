import customtkinter as ctk
from gui_app import SimulationApp

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Simulation Core Pro v3.0")
    root.geometry("1100x700")

    app = SimulationApp(root)
    root.mainloop()