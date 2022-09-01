import tkinter as tk
from tkinter import filedialog

from admittance import OpeningAdmittance, LimitedTimeslot


class App:

    opening_admittance: OpeningAdmittance

    txt_registrations_path: tk.Entry
    btn_browse_registrations_file: tk.Button
    btn_read_registrations: tk.Button

    lb_timeslots: tk.Listbox

    def __init__(self, root: tk.Tk, admittance: OpeningAdmittance):
        root.title("ReStore Admittance System")

        #setting window size
        width = 600
        height = 500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()

        # Open in the middle of the screen
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        tk.Label(root, text="Opening timeslots").grid(row=0, column=0)
        self.lb_timeslots = tk.Listbox(root)

        for n, (timeslot_name, timeslot) in enumerate(admittance.timeslots.items()):
            self.lb_timeslots.insert(n, timeslot_name)
        self.lb_timeslots.insert(n+1, "General Waiting List")
        self.lb_timeslots.grid(row=1, column=0)


        # tk.Label(root, text="Registrations").grid(row=0)
        #
        # self.txt_registrations_path = tk.Entry(root, width=80)
        # self.txt_registrations_path.grid(row=0, column=1)
        # self.btn_read_registrations = tk.Button(root, text="...", command=self.browse_registrations)
        # self.btn_read_registrations.grid(row=0, column=2)
        #
        # self.btn_read_registrations = tk.Button(root, text="Read Registrations")
        # self.btn_read_registrations.grid(row=1, column=1)

        # ft = tkFont.Font(family='Times',size=10)
        # GLabel_980["font"] = ft
        # GLabel_980["fg"] = "#333333"
        # GLabel_980["justify"] = "left"
        # GLabel_980["text"] = "registrations"
        # GLabel_980.place(x=20,y=20,width=100,height=30)

    def browse_registrations(self):
        file_path = filedialog.askopenfilename(
            title="Select Registrations",
            filetypes=(("Comma Separated Values", "*.csv"), ("All Files", "*.*"))
        )
        self.txt_registrations_path.delete(0, len(self.txt_registrations_path.get()))  # clear text
        self.txt_registrations_path.insert(0, file_path)



if __name__ == "__main__":

    admittance = OpeningAdmittance({
        "10:00-11:00": LimitedTimeslot(50),
        "11:00-12:00": LimitedTimeslot(60),
        "12:00-13:00": LimitedTimeslot(70),
    })

    root = tk.Tk()
    app = App(root, admittance)
    root.mainloop()
