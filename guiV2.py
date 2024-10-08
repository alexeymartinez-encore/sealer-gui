import customtkinter
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from bson.json_util import dumps, loads
import numpy as np
from pymongo import MongoClient
from datetime import datetime, timezone
from threading import Thread

from faroc import FaRoC_Reader, FaRoC_Writer, FaRoC_Mover

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class Extra_Reg(tk.Toplevel):
    def __init__(self,db):
        super().__init__()
        self.db = db
        self.title('Registers Configuration')
        self.geometry('1200x600')
        self.configure(background="#333") 
        
        style = ttk.Style()  # Create a ttk.Style object
        style.theme_use("alt")  # Set the default theme

        # configure grid layout (6x3)
        self.grid_columnconfigure(tuple(range(4)), weight=1)
        self.grid_rowconfigure(tuple(range(8)), weight=1)

class Extra(tk.Toplevel):
    def __init__(self, db):
        super().__init__()
        self.db =db
        self.title('Configure')
        self.geometry('1200x600')
        self.configure(background="#333") 
    
        style = ttk.Style()  # Create a ttk.Style object
        style.theme_use("alt")  # Set the default theme

        # configure grid layout (6x3)
        self.grid_columnconfigure(tuple(range(4)), weight=1)
        self.grid_rowconfigure(tuple(range(8)), weight=1)

class Extra_Lookup(tk.Toplevel):
    def __init__(self, db):
        super().__init__()
        self.db =db

        self.title('Search')
        self.geometry('1600x800')
        self.configure(background="#333") 
    
        style = ttk.Style()  # Create a ttk.Style object
        style.theme_use("alt")  # Set the default theme

        # configure grid layout (6x3)
        self.grid_columnconfigure(tuple(range(24)), weight=1)
        self.grid_rowconfigure(tuple(range(12)), weight=1)

        self.cal = Calendar(self, selectmode="day", date_pattern="yyyy-mm-dd")
        self.cal.grid(row=0, column=0,columnspan=10, padx=(5, 0), pady=(5,0), sticky="nswe")

        button = customtkinter.CTkButton(self, text="Pick Date", command=self.get_selected_date)
        button.grid(row= 1, column=0,columnspan=10, padx=(5,0), pady=40, sticky='nswe')

        self.batch_scrollable_area()
        self.fasteners_scrollable_area()
        self.create_graph_frame()

    def get_selected_date(self):
        selected_date = self.cal.get_date()
        res = self.db.batches.find({"date": selected_date})
        print("Selected Date:", selected_date)
        response_list = list(res)

        # Clear the batch scrollable frame
        for widget in self.batch_scrollable_frame.winfo_children():
            widget.destroy()

        for index, doc in enumerate(response_list):
            batch_values = doc["caps"]
            timestamp = doc["timestamp"]
            self.time = timestamp.time().strftime('%H:%M:%S')

            label = customtkinter.CTkLabel(self.batch_scrollable_frame, text=f"B{index + 1}")
            label.grid(row=index, column=0, padx=(5, 0), pady=5, sticky="nwse")

            label = customtkinter.CTkLabel(self.batch_scrollable_frame, text=f"{self.time}")
            label.grid(row=index, column=1, padx=(5), pady=5, sticky="nwse")

            show_batch_values_button = customtkinter.CTkButton(
                master=self.batch_scrollable_frame,
                fg_color="#206dae",
                text="Show Batch",
                text_color=("gray10", "#DCE4EE"),
                hover_color="#2D4F86",
                command=lambda values=batch_values: self.show_caps(values)
            )

            show_batch_values_button.grid(row=index, column=2, padx=10, pady=5, sticky="nwse")


    def show_caps(self, batch_values):
        # Clear the fasteners scrollable frame
        for widget in self.fasteners_scrollable_frame.winfo_children():
            widget.destroy()

        for index, cap in enumerate(batch_values):
            cap_id = cap["cap_id"]
            cap_successful = cap["cap_successful"]
            cap_values = cap["cap_values"]

            label = customtkinter.CTkLabel(self.fasteners_scrollable_frame, text=f"Cap {index + 1}")
            label.grid(row=index, column=0, padx=(5, 0), pady=5, sticky="nwse")

            result_label = customtkinter.CTkLabel(
                self.fasteners_scrollable_frame, 
                text="Passed" if cap_successful else "Failed", 
                text_color='green' if cap_successful else 'red'
            )
            result_label.grid(row=index, column=1, padx=(5), pady=5, sticky="nwse")

            show_graph_button = customtkinter.CTkButton(
                master=self.fasteners_scrollable_frame,
                fg_color="#206dae",
                text="Show Graph",
                text_color=("gray10", "#DCE4EE"),
                hover_color="#2D4F86",
                command=lambda values=cap_values, column=cap_id: self.show_graph_for_column(values, column)
            )
            show_graph_button.grid(row=index, column=2, padx=10, pady=5, sticky="nwse")

            toggle_var = tkinter.BooleanVar(value=cap_successful)
            toggle = customtkinter.CTkCheckBox(
                self.fasteners_scrollable_frame,
                text="",
                variable=toggle_var,
                command=lambda cap=cap, var=toggle_var, lbl=result_label: self.update_result(cap, var, lbl),
            )
            toggle.grid(row=index, column=3, padx=0, pady=0, sticky="e")

    def update_result(self, cap, toggle_var, result_label):
        cap["cap_successful"] = toggle_var.get()
        result_label.configure(
            text="Passed" if cap["cap_successful"] else "Failed",
            text_color='green' if cap["cap_successful"] else 'red'
        )

    def batch_scrollable_area(self):
        self.batch_scrollable_frame = customtkinter.CTkScrollableFrame(
            self, label_text="Batches"
        )
        self.batch_scrollable_frame.grid(
            row=2, column=0, columnspan=10, rowspan=10, padx=(5,0), pady=(0,10), sticky="nsew"
        )
        self.batch_scrollable_frame.grid_columnconfigure(0, weight=1)
        return self.batch_scrollable_frame
    
    def fasteners_scrollable_area(self):
        self.fasteners_scrollable_frame = customtkinter.CTkScrollableFrame(
            self, label_text="Sealed Fasteners"
        )
        self.fasteners_scrollable_frame.grid(
            row=0, column=10, columnspan=8, rowspan=12, padx=(8,0), pady=(5,10), sticky="nsew"
        )
        self.fasteners_scrollable_frame.grid_columnconfigure(0, weight=1)
        return self.fasteners_scrollable_frame

    def show_graph_for_column(self,values:list, column:int):
        print(column)
        normalized_index, normalized_data = self.interpolate_and_normalize(
            values, len(values)
        )
        self.ax.clear()
        self.ax.plot(normalized_index, normalized_data, linestyle="-", color="b")
        self.ax.set_title(f"Cap {column}")
        self.ax.set_xlabel("Recorded Point")
        self.ax.set_ylabel("Loadcell Value")
        self.canvas.draw()
    
    def create_graph_frame(self):
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.grid(
            row=0, column=20, rowspan=4, columnspan=2,pady=(20,0), sticky='nwse'
        )
        self.graph_frame["border"] = 2

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Real-Time Graph")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nwes")
        self.canvas.get_tk_widget().configure(borderwidth=0, highlightthickness=0)

        self.graph_frame.columnconfigure(0, weight=1)
        self.graph_frame.rowconfigure(0, weight=1)
        return self.graph_frame
    
    def interpolate_and_normalize(self, data_list, target_length):
        interpolated_array = np.interp(
            np.linspace(0, 1, target_length),
            np.linspace(0, 1, len(data_list)),
            data_list,
        )
        normalized_index = (np.arange(target_length) - 0) / (target_length - 1)
        normalized_data = (interpolated_array - min(interpolated_array)) / (
            max(interpolated_array) - min(interpolated_array)
        )
        return normalized_index, normalized_data

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # configure window
        self.title("Cap Analyzer")
        self.geometry("1420x800")

        # Initialize MongoDB connection
        self.init_db()

        self.connected = False

        style = ttk.Style()
        style.theme_use("default")

        self.grid_columnconfigure(tuple(range(24)), weight=1)
        self.grid_rowconfigure(tuple(range(8)), weight=1)

        self.data_to_write = []
        self.current_batch = [] # initial batch of caps

        # CREATE SIDEBAR
        self.sidebar_frame()
        self.create_sidebar_logo(text="Menu")
        self.create_sidebar_button(btn_text="Set Registers", row=1,col=0,command=self.create_reg_window)
        self.create_sidebar_button(btn_text="Configure", row=2,col=0,command=self.create_config_window)
        self.create_sidebar_button(btn_text="Search", row=3,col=0,command=self.create_lookup_window)
        self.appearance_modes()

        # MIDDLE
        self.create_graph_frame()

        self.value_input(row=2, col=2, label='Crush',placeholder_text=f"5")
        self.value_input(row=3, col=2, label="Pressure", placeholder_text=f"6 psi")
        self.value_input(row=4, col=2, label="Cure Time",placeholder_text=f"7 ms")
          
        self.connection_button(connection_type=self.toggle_connection)

        self.scrollable_area()

        self.analysis_button(col=14, text="Clear", command=self.clear_batch)
        self.analysis_button(col=16, text="Submit", command=self.save_batch)

    # DATABASE INITIALIZATION
    def init_db(self):
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client["uv_sealer"]
            self.batches_collection = self.db["batches"]
            print("Connected to MongoDB")
        except Exception as e:
            messagebox.showerror("Database Connection Error", str(e))

    def sidebar_frame(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, columnspan=2, rowspan=8, sticky="nsew")
        self.sidebar_frame.columnconfigure(0, weight=1)
        self.sidebar_frame.rowconfigure(7, weight=1)
        return self.sidebar_frame      

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def appearance_modes(self):
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(
            row=7, column=0, padx=50, pady=(0, 0), sticky="s"
        )

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(
            row=8, column=0, pady=(0, 30), sticky="ns"
        )
        self.appearance_mode_optionemenu.set("Dark")

        return self.appearance_mode_optionemenu

    def create_sidebar_button(self, btn_text:str, row:int, col:int, command):
        button = customtkinter.CTkButton(self.sidebar_frame, text=btn_text, command=command)
        button.grid(row= row, column=col, padx=20, pady=10)
        return button
    
    def create_sidebar_logo(self, text:str):
        logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text=text,
        )
        logo_label.grid(row=0, column=0, pady=20, sticky="nsew")
        return logo_label

    def create_graph_frame(self):
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.grid(
            row=0, column=2, rowspan=1, columnspan=6, padx=15, pady=15, sticky="nsew"
        )
        self.graph_frame["border"] = 2

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Real-Time Graph")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nwes")
        self.canvas.get_tk_widget().configure(borderwidth=0, highlightthickness=0)

        self.graph_frame.columnconfigure(0, weight=1)
        self.graph_frame.rowconfigure(0, weight=1)
        return self.graph_frame
    
    def show_graph_for_cap(self,values:list, column:int):
        print(column)
        normalized_index, normalized_data = self.interpolate_and_normalize(
            values, len(values)
        )
        self.ax.clear()
        self.ax.plot(normalized_index, normalized_data, linestyle="-", color="b")
        self.ax.set_title(f"Cap {column}")
        self.ax.set_xlabel("Recorded Point")
        self.ax.set_ylabel("Loadcell Value")
        self.canvas.draw()

    def value_input(self, row: int, col: int, label:str, placeholder_text):
        container_frame = customtkinter.CTkFrame(self, fg_color="transparent")

        self.param_label = customtkinter.CTkLabel(
            container_frame,
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text=f"{label}:",
        )
        self.param_label.grid(row=0, column=0, )

        self.param_entry = customtkinter.CTkEntry(container_frame, placeholder_text=placeholder_text)
        self.param_entry.grid(row=0, column=1, padx=40)

        self.param_entry_button = customtkinter.CTkButton(
            master=container_frame,
            fg_color="#206dae",
            text="Enter",
            text_color=("gray10", "#DCE4EE"),
            hover_color="#2D4F86",
            command=lambda: self.submit_value(label)
        )
        self.param_entry_button.grid(row=0, column=2)

        container_frame.grid(row=row, column=col, sticky="e")
        return container_frame

    def connection_button(self, connection_type):
        self.start_button = customtkinter.CTkButton(
            master=self,
            fg_color="#206dae",
            text="Connect",
            text_color=("gray10", "#DCE4EE"),
            hover_color="#2D4F86",
            command=connection_type
        )

        self.start_button.grid(row=2, column=7, padx=5, sticky="news")
        return self.start_button

    def scrollable_area(self):
        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            self, label_text="Cap Results"
        )
        self.scrollable_frame.grid(
            row=0, column=8, columnspan=16, rowspan=7, padx=15, pady=10, sticky="nsew"
        )
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []

        for doc in self.current_batch:
            cap_id = doc["cap_id"]
            cap_successful = doc["cap_successful"]
            cap_numbers = doc["cap_values"]

            button = customtkinter.CTkButton(
                self.scrollable_frame, 
                text=f"Graph {cap_id}", 
                command=lambda values=cap_numbers, column=cap_id: self.show_graph_for_cap(values, column)
            )
            button.grid(row= cap_id, column=1, padx=5, pady=5, sticky="ne")

            result_label = customtkinter.CTkLabel(
                self.scrollable_frame, 
                text="Passed" if cap_successful else "Failed", 
                text_color="green" if cap_successful else "red"
            )
            result_label.grid(row=cap_id, column=2, padx=25, pady=0, sticky="w")

            toggle_var = tkinter.BooleanVar(value=cap_successful)
            toggle = customtkinter.CTkCheckBox(
                self.scrollable_frame,
                text="",
                variable=toggle_var,
                command=lambda cap=doc, var=toggle_var, lbl=result_label: self.update_result(cap, var, lbl),
            )
            toggle.grid(row=cap_id, column=3, padx=0, pady=0, sticky="e")

        return self.scrollable_frame

    def update_result(self, cap, toggle_var, result_label):
        cap["cap_successful"] = toggle_var.get()
        result_label.configure(
            text="Passed" if cap["cap_successful"] else "Failed",
            text_color='green' if cap["cap_successful"] else 'red'
        )

    def analysis_button(self,col:int, text:str, command):
        button = customtkinter.CTkButton(
            master=self,
            fg_color="#206dae",
            text=text,
            text_color=("gray10", "#DCE4EE"),
            command=command,
        )
        button.grid(row=7, column=col, ipadx=10, ipady=5, sticky="new")
        return button

    def establish_connection(self):
        self.robot_read = FaRoC_Writer()
        self.robot_read.connect()
        self.robot_read.status()
        self.connected = True
        
        self.capNo = 1

        flag=True
        while self.connected:
            dataRO = self.getRO(3)
            while dataRO != 0:
                dataRO = self.getRO(3) 
                data = self.getReg(37)
                print(data)
                self.data_to_write.append(data)
                if dataRO == 0:
                    self.cap_successful = True
                    target_length = 100
                    normalized_index, normalized_data = self.interpolate_and_normalize(
                        self.data_to_write, target_length
                    )
                    
                    if normalized_data is None:
                        print("Skipping analysis due to lack of data variation.")
                        self.cap_successful = False  # You might want to consider how to handle this case
                    else:
                        differences = np.diff(normalized_data) * 100

                        if any(abs(diff) > 5 for diff in differences[-20:]):
                            print("At least one value in the last 20 elements differences is over 5.")
                            self.cap_successful = False
                        else:
                            print("No value in the last 20 elements differences is over 5.")
                            self.cap_successful = True
                    
                    self.current_batch.append(
                        {
                            "cap_id": self.capNo,
                            "cap_successful": self.cap_successful,
                            "cap_values": self.data_to_write,
                        }
                    )
                    self.capNo += 1
                    print()
                    self.data_to_write = []
                    self.scrollable_area()
                    break


    def getReg(self, reg_no):
        dataReg = self.robot_read.get_reg(reg_no)
        dataReg = dataReg[2]
        return dataReg[0]
    
    def getRO(self,ro_no):
        dataRO = self.robot_read.get_rdo(ro_no)
        dataRO = dataRO[2]
        return dataRO[0]

    def toggle_connection(self):
        if not self.connected:
            self.data_collection_running = (
                True  # Set the flag to indicate data collection is running
            )
            self.data_thread = Thread(target=self.establish_connection)
            self.data_thread.start()
            self.start_button.configure(text="Disconnect", fg_color="#FF0000",hover_color="#852d2d",)
        else:
            self.disconnect()
            self.data_collection_running = False

            self.start_button.configure(text="Connect", fg_color="#206dae", hover_color="#2D4F86")

    def disconnect(self):
        self.robot_read.disconnect()
        self.robot_read.status()
        self.connected = False
        print(self.connected)

    def submit_value(self, label):
        param_value = self.param_entry.get()
        print(f"{label}:", param_value) 
        reg = 6
        if self.connected:
            self.robot_read.set_reg(reg,val=param_value,cmt=f"{label} Value")

    def clear_batch(self):
        self.current_batch = []
        self.scrollable_area()
        
    def save_batch(self):
        if self.current_batch:
            try:
                current_date = datetime.now()
                date_string = current_date.strftime("%Y-%m-%d")
                self.batches_collection.insert_one(
                    {
                        "caps":self.current_batch, 
                        "date": date_string, 
                        "timestamp":datetime.now(timezone.utc)
                    }
                )
                self.current_batch = []
                self.scrollable_area()
                self.capNo = 1
                messagebox.showinfo("Success", "Data inserted successfully")
            except ValueError:
                messagebox.showerror("Error", "Age must be an integer")
        else:
            messagebox.showerror("Error", "All fields are required")
            pass

    def interpolate_and_normalize(self, data_list, target_length):
        try:
            if len(data_list) == 0:
                raise ValueError("The input data_list cannot be empty.")
            
            if target_length <= 0:
                raise ValueError("The target_length must be a positive integer.")
            
            interpolated_array = np.interp(
                np.linspace(0, 1, target_length),
                np.linspace(0, 1, len(data_list)),
                data_list,
            )
            
            normalized_index = (np.arange(target_length) - 0) / (target_length - 1)
            
            data_min = min(interpolated_array)
            data_max = max(interpolated_array)
            
            if data_min == data_max:
                print("No variation in data; skipping normalization.")
                return None, None  # Indicate that normalization isn't possible due to no variation

            normalized_data = (interpolated_array - data_min) / (data_max - data_min)
            
            return normalized_index, normalized_data

        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None, None
        except TypeError as te:
            print(f"TypeError: {te}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None

    def create_config_window(self):
        global extra_window
        extra_window = Extra(self.db)
        pass

    def create_reg_window(self):
        global extra_window
        extra_window = Extra_Reg(self.db)
        pass

    def create_lookup_window(self):
        global extra_window
        extra_window = Extra_Lookup(self.db)
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()

