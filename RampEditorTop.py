from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Global variables

ramps = []


technic_dictionary = {'CV': 'Linear Cyclic Voltammetry',
                      'SCV': 'Staircase Cyclic Voltammetry',
                      'DPV': 'Differential Pulse Voltammetry',
                      'SW': 'Square Wave Voltammetry',
                      'NPV': 'Normal Pulse Voltammetry',
                      'LSV': 'Linear Sweep Voltammetry',
                      'CHRAMP': 'Chronoamperommetry'}

technic_library = ['Linear Cyclic Voltammetry',
                   'Staircase Cyclic Voltammetry',
                   'Differential Pulse Voltammetry',
                   'Square Wave Voltammetry',
                   'Normal Pulse Voltammetry',
                   'Linear Sweep Voltammetry',
                   'Chronoamperommetry']

para_dic = {'CV': ["E begin (V)", "E vertex1 (V)", "E vertex2 (V)", "E step (V)", "Scan rate (V/s)", "Scan number"],
            'SCV': ["E begin (V)", "E vertex1 (V)", "E vertex2 (V)", "E step (V)", "Scan rate (V/s)", "Scan number"],
            'DPV': ["E begin (V)", "E end (V)", "E step (V)", "E pulse (V)", "t pulse (s)", "Scan rate (V/s)"],
            'SW': ["E begin (V)", "E end (V)", "E step (V)", "Amplitude (V)", "Frequency (Hz)"],
            'NPV': ["E begin (V)", "E end (V)", "E step (V)", "t pulse (s)", "Scan rate (V/s)"],
            'LSV': ["E begin (V)", "E end (V)", "E step (V)", "Scan rate (V/s)"],
            'CHRAMP': ["E begin (V)", "t interval (s)", "t duration (s)"]}


def read_method(file_name):
    """ Load a method file and returns the arrange data contained inside the file"""
    with open(file_name, 'r') as file:
        parameters = file.read().split('\n')

    tech_name = parameters[0]
    para = [value.split('\t')[1] for value in parameters[1:] if value != '']
    return tech_name, para


class RampEditor:
    def __init__(self, master):
        self.root = Toplevel()
        # root.attributes('-topmost', 'true')
        self.root.transient(master)
        self.root.lift()
        self.root.title('Elchem - Electrochemistry')
        self.root.iconbitmap(r'group-30_116053.ico')
        self.root.geometry('900x550')
        self.root.resizable(False, False)
        self.Active_technic = 'CV'
        self.inner_frame = None

        # creating main frame
        main_frame = LabelFrame(self.root, text="Control Panel")
        main_frame.pack(side=LEFT)

        self.my_combo = ttk.Combobox(main_frame, value=technic_library, width=35)
        # self.my_combo.current(technic_library.index(tech_name))
        self.my_combo.bind("<<ComboboxSelected>>", self.combo_select)
        self.my_combo.pack(padx=10)

        # creates the frames for condition settings input and parameters settings input
        f_condition = LabelFrame(main_frame, text="Pretreatment Settings")
        f_condition.pack()

        # Builds the condition inputs
        Econdition = Label(f_condition, text="E condition", padx=6)
        self.e_Econdition = Entry(f_condition, fg="grey", width=20)
        self.e_Econdition.insert(0, "0")
        time_condition = Label(f_condition, text="t condition", padx=6)
        self.e_time_condition = Entry(f_condition, fg="grey", width=20)
        self.e_time_condition.insert(0, "0")

        Econdition.grid(row=0, column=0, padx=3)
        time_condition.grid(row=1, column=0, padx=3)
        self.e_Econdition.grid(row=0, column=1, padx=5)
        self.e_time_condition.grid(row=1, column=1, padx=5)

        # parameters settings input
        self.plastic_frame = Frame(main_frame)
        self.plastic_frame.pack()

        # creating the button that saves the parameters values
        f_buttons = Frame(main_frame)
        b_plot = Button(f_buttons, text="Plot", command=self.plot_ramp, width=7)
        b_save = Button(f_buttons, text="Apply",
                        command=lambda: self.save_table(ramps * 1000, len(ramps), np.size(ramps, 1)), width=7)
        f_buttons.pack()
        b_plot.pack(side=LEFT)
        b_save.pack(side=RIGHT)

        # Creating the plot to visualize the ramps formed
        plot_frame = Frame(self.root)
        plot_frame.pack(side=RIGHT)

        # Builds figure
        figure = Figure()
        self.graph = figure.add_subplot(111)
        self.graph.grid(True)
        self.graph.set_xlabel('Time/s')
        self.graph.set_ylabel('Potential/V')
        self.graph.set_xlim(-1, 1)
        self.graph.set_ylim(-1, 1)
        self.plot_line = self.graph.plot([], [], 'b-')[0]  # var that will be used for data plot

        # Builds canvas
        self.canvas = FigureCanvasTkAgg(figure, plot_frame)
        self.canvas.get_tk_widget().pack(side=TOP)
        self.canvas.draw()

        # Adding tool bar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=BOTTOM, fill=X)

        # Adding main menu
        my_menu = Menu(self.root)
        self.root.config(menu=my_menu)

        my_menu.add_command(label='Load method', command=self.load_method)
        my_menu.add_command(label='Save method', command=self.save_method)

        self.load_method(path='Active_parameters.txt')
        # top.state('zoomed')
        self.root.mainloop()

    def combo_select(self, e):
        self.update_(tech_name=self.my_combo.get())

    def frame_maker(self, values=None):

        global entry_lib, label_lib
        if self.inner_frame is not None:
            self.inner_frame.destroy()
        self.inner_frame = LabelFrame(self.plastic_frame, text=technic_dictionary[self.Active_technic])
        self.inner_frame.pack()

        my_frameR = Frame(self.inner_frame)
        my_frameL = Frame(self.inner_frame)
        my_frameR.pack(side=RIGHT)
        my_frameL.pack(side=LEFT)

        entry_lib = []
        label_lib = []

        params = para_dic[self.Active_technic]
        for para in params:
            label_lib.append(Label(my_frameL, text=para, width=11))
            entry_lib.append(Entry(my_frameR, width=20))
            label_lib[-1].pack()
            entry_lib[-1].pack(padx=5)

        # Adding values to entries
        if values is not None:
            for i, entry in enumerate(entry_lib):
                entry.insert(0, values[i])

    def plot_ramp(self):
        global ramps
        ramps = self.tryRamps()
        # print(ramps)

        xdata = np.array([0, ramps[0, 2]])  # Initial time
        ydata = np.array(ramps[0, 0:2])  # initial ramp
        for i in range(1, np.size(ramps, 0)):
            xdata = np.concatenate((xdata, [xdata[-1], xdata[-1] + ramps[i, 2]]))
            ydata = np.concatenate((ydata, ramps[i, 0:2]))

        self.plot_data(xdata, ydata)

    def update_(self, tech_name, values=None):
        key = [key for key, name in technic_dictionary.items() if name == tech_name][0]
        self.Active_technic = key
        self.my_combo.current(technic_library.index(tech_name))
        if values is None:
            self.frame_maker()
        else:
            self.frame_maker(values=values)

    def load_method(self, path=None):
        if path is None:
            path = filedialog.askopenfilename()
        tech_name, values = read_method(path)
        self.update_(tech_name, values)
        self.plot_ramp()

    def save_method(self):
        filepath = filedialog.asksaveasfilename()
        self.save_parameters(filepath)

    def save_parameters(self, path='Active_parameters.txt'):
        values = self.translate_entries()
        with open(path, 'w') as file:
            file.write(technic_dictionary[self.Active_technic] + '\n')
            for i, item in enumerate(label_lib):
                file.write(item.cget("text") + '\t')
                file.write(str(values[i]) + '\n')

    def tryRamps(self):
        # verifies if the input data are numerical values and returns the variables of each technic
        try:
            if self.Active_technic == "CV":
                vi, v1, v2, step, scanrate, scans, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, v1=v1, v2=v2, step=step, scanrate=scanrate, scans=scans, vc=vc, tc=tc):
                    ramps = self.build_linearCV_ramp(vi, v1, v2, step, scanrate, scans, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "SCV":
                vi, v1, v2, step, scanrate, scans, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, v1=v1, v2=v2, step=step, scanrate=scanrate, scans=scans, vc=vc, tc=tc):
                    ramps = self.build_staircaseCV_ramp(vi, v1, v2, step, scanrate, scans, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "SW":
                vi, vf, step, amplitude, freq, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, vf=vf, step=step, amplitude=amplitude, freq=freq, vc=vc, tc=tc):
                    ramps = self.build_SW_ramp(vi, vf, step, amplitude, freq, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "DPV":
                vi, vf, step, v_pulse, t_pulse, scanrate, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, vf=vf, step=step, vpulse=v_pulse, tpulse=t_pulse, scanrate=scanrate, vc=vc, tc=tc):
                    ramps = self.build_DPV_ramp(vi, vf, step, v_pulse, t_pulse, scanrate, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "NPV":
                vi, vf, step, t_pulse, scanrate, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, vf=vf, step=step, tpulse=t_pulse, scanrate=scanrate, vc=vc, tc=tc):
                    ramps = self.build_NPV_ramp(vi, vf, step, t_pulse, scanrate, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "LSV":
                vi, vf, step, scanrate, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, vf=vf, step=step, scanrate=scanrate, vc=vc, tc=tc):
                    ramps = self.build_LSV_ramp(vi, vf, step, scanrate, vc, tc)
                    self.save_parameters()
                    return ramps
            elif self.Active_technic == "CHRAMP":
                vi, t_int, t_total, vc, tc = self.translate_entries()
                if self.ValidateValues(vi=vi, t_int=t_int, t_total=t_total, vc=vc, tc=tc):
                    ramps = self.build_chrono_ramp(vi, t_int, t_total, vc, tc)
                    self.save_parameters()
                    return ramps

        except ValueError:
            messagebox.showerror("Value Error", "Invalid entries in one or more parameters. All inputs must be numerical")

    def translate_entries(self):
        # convert the type of the input values (Tk Entry) to floats
        x = []
        for i in range(len(entry_lib)):
            x.append(float(entry_lib[i].get()))

        x.append(float(self.e_Econdition.get()))
        x.append(float(self.e_time_condition.get()))

        return x

    def ValidateValues(self, vi=0, v1=-5, v2=5, vf=0, step=1, scanrate=1, vpulse=0, tpulse=0.001, amplitude=1, freq=1,
                       scans=1, t_int=1, t_total=1, vc=0, tc=0):

        # Check if the input values make sense in the scope of the selected electrochemical technic
        error = False  # this variable ensures that only one error will pup up per turn
        if vi < -5 or v1 < -5 or v2 < -5 or vf < -5 or vpulse < -5 or vc < -5 or vi > 5 or v1 > 5 or v2 > 5 or vf > 5 \
                or vpulse > 5 or vc > 5:
            messagebox.showerror('Invalid value', "The voltage range should be between -5V and 5V")
            error = True

        if v1 < vi > v2 or v1 > vi < v2 and not error:
            messagebox.showerror('Invalid value', 'Starting voltage (E begin) must sit between vertex1 and '
                                                  'vertex2 voltage')
            error = True

        if step <= 0 and not error:
            messagebox.showerror('Invalid value', 'Step must be a positive number smaller than 1V')
            error = True

        if (scanrate <= 0 or scanrate > 50) and not error:
            messagebox.showerror('Invalid value', 'Scan rate must be a positive number in the interval [0, 50]V')
            error = True

        if (0.001 > tpulse or tpulse > 0.300) and not error:
            messagebox.showerror('Invalid value', 'The pulse time must be between 0.001s and 0.300s')
            error = True

        if (0.001 > amplitude or amplitude > 1) and not error:
            messagebox.showerror('Invalid value', 'Amplitude must be between 0.001V and 1V')
            error = True

        if (1 > freq or freq > 500) and not error:
            messagebox.showerror('Invalid value', 'Frequency must range from 1Hz to 500Hz')
            error = True

        if scans <= 0 and not error:  # also see if is an integer
            messagebox.showerror('Invalid value', 'Number of scans must be a positive integer')
            error = True

        if (0.001 > t_int or t_int > 300 or t_int > t_total) and not error:
            messagebox.showerror('Invalid value', 'Interval time must be between 0.001s and 300s. And the running time must'
                                                  ' be higher than interval time')
            error = True

        if tc < 0 and not error:
            messagebox.showerror('Invalid value', 'Condition time must be a positive number')
            error = True

        if tpulse >= step/scanrate:
            messagebox.showerror('Invalid value', 'Pulse time must be smaller than step time (step/sacan rate)')
            error = True

        return not error

    def build_linearCV_ramp(self, vi, v1, v2, step, scanrate, scans, vc, tc):
        # builds the ramps for linear cv analysis
        lines = np.array([[vc, vc, tc]])  # Initialize vector

        for i in range(0, 2*int(scans)):
            if i == 0:
                time = step / scanrate * abs(v1 - vi) / step
                lines = np.concatenate((lines, [[vi, v1, time]]))
            else:
                if i % 2 != 0:
                    time = step / scanrate * abs(v2 - v1) / step
                    lines = np.concatenate((lines, [[v1, v2, time]]), axis=0)
                else:
                    time = step / scanrate * abs(v2 - v1) / step
                    lines = np.concatenate((lines, [[v2, v1, time]]), axis=0)
        print(len(lines))
        return lines

    def build_staircaseCV_ramp(self, vi, v1, v2, step, scanrate, scans, vc, tc):
        # builds the ramps for linear cv analysis
        lines = np.array([[vc, vc, tc]])  # Initialize vector
        time = step / scanrate
        vnext = vi
        scan = 1
        while scan <= scans:
            lines = np.concatenate((lines, [[vnext, vnext, time]]))
            if vi < v1:
                while vnext <= v1:
                    vnext += step
                    lines = np.concatenate((lines, [[vnext, vnext, time]]))
                while vnext >= v2:
                    vnext -= step
                    lines = np.concatenate((lines, [[vnext, vnext, time]]))
            elif vi > v1:
                while vnext >= v1:
                    vnext -= step
                    lines = np.concatenate((lines, [[vnext, vnext, time]]))
                while vnext <= v2:
                    vnext += step
                    lines = np.concatenate((lines, [[vnext, vnext, time]]))
            scan += 1
        print(len(lines))
        return lines

    def build_LSV_ramp(self, vi, vf, step, scanrate, vc, tc):
        lines = np.array([[vc, vc, tc]])  # Conditioning
        time = step/scanrate * abs(vf - vi) / step
        lines = np.concatenate((lines, [[vi, vf, time]]), axis=0)
        print(len(lines))
        return lines

    def build_DPV_ramp(self, vi, vf, step, v_pulse, t_pulse, scanrate, vc, tc):
        # DPV with a staircase base profile
        lines = np.array([[vc, vc, tc]])  # Conditioning
        # parameters
        delta_t = step/scanrate
        t_base = (delta_t - t_pulse)

        base = vi
        pulse = base
        if vi <= vf:
            while pulse <= vf:
                lines = np.concatenate((lines, [[base, base, t_base]]), axis=0)
                pulse = base + v_pulse
                lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
                base = base + step
        else:
            while pulse >= vf:
                lines = np.concatenate((lines, [[base, base, t_base]]), axis=0)
                pulse = base - v_pulse
                lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
                base = base - step
        print(len(lines))
        return lines

    def build_SW_ramp(self, vi, vf, step, amplitude, freq, vc, tc):
        # DPV with a staircase base profile
        lines = np.array([[vc, vc, tc]])  # Conditioning
        # parameters
        delta_t = round(1/freq, 3)

        base = vi
        lines = np.concatenate((lines, [[base, base, delta_t / 2]]), axis=0)
        if vi <= vf:
            base = base + amplitude
            lines = np.concatenate((lines, [[base, base, delta_t / 2]]), axis=0)
            while base <= vf:
                base = round(base - 2*amplitude, 3)
                lines = np.concatenate((lines, [[base, base, delta_t/2]]), axis=0)
                base = round(base + 2*amplitude + step, 3)
                lines = np.concatenate((lines, [[base, base, delta_t/2]]), axis=0)
        else:
            base = base - amplitude
            lines = np.concatenate((lines, [[base, base, delta_t / 2]]), axis=0)
            while base >= vf:
                base = round(base + 2*amplitude, 3)
                lines = np.concatenate((lines, [[base, base, delta_t/2]]), axis=0)
                base = round(base - 2*amplitude - step, 3)
                lines = np.concatenate((lines, [[base, base, delta_t/2]]), axis=0)
        print(len(lines))
        return lines

    def build_NPV_ramp(self, vi, vf, step, t_pulse, scanrate, vc, tc):
        lines = np.array([[vc, vc, tc]])  # Conditioning
        # parameters
        delta_t = step/scanrate
        base_t = delta_t-t_pulse

        base = vi
        lines = np.concatenate((lines, [[base, base, base_t]]), axis=0)
        if vi <= vf:
            pulse = base + step
            lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
            while pulse <= vf:
                lines = np.concatenate((lines, [[base, base, base_t]]), axis=0)
                pulse = pulse + step
                lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
        else:
            pulse = base - step
            lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
            while pulse >= vf:
                lines = np.concatenate((lines, [[base, base, base_t]]), axis=0)
                pulse = pulse - step
                lines = np.concatenate((lines, [[pulse, pulse, t_pulse]]), axis=0)
        print(len(lines))
        return lines

    def build_chrono_ramp(self, vi, t_int, t_total, vc, tc):
        lines = np.array([[vc, vc, tc]])  # Conditioning
        base = vi
        lines = np.concatenate((lines, [[base, base, t_total]]), axis=0)
        print(len(lines))
        return lines

    def plot_data(self, xdata, ydata):
        # Code for graphic update
        self.plot_line.set_xdata(xdata)
        self.plot_line.set_ydata(ydata)

        # This block rescales the x and y range on the graph, so that all point are shown
        xmax, ymax, xmin, ymin = max(xdata), max(ydata), min(xdata), min(ydata)
        if ymax >= 0:
            y_upper_limit = ymax*1.1
        else:
            y_upper_limit = ymax*0.9
        if ymin > 0:
            y_lower_limit = ymin*0.9
        else:
            y_lower_limit = ymin*1.1

        x_upper_limit = xmax*1.1
        x_lower_limit = xmin

        self.graph.set_xlim(x_lower_limit, x_upper_limit)
        self.graph.set_ylim(y_lower_limit, y_upper_limit)

        self.canvas.draw()

    def save_table(self, data, rows, column):
        self.plot_ramp()

        with open('Ramps.txt', 'w') as file:
            for i in range(rows):
                for j in range(column):
                    my_string = str(data[i, j])
                    my_string = my_string.replace(' [', '')
                    my_string = my_string.replace('[', '')
                    my_string = my_string.replace(']', '')
                    file.write(my_string)
                    if j < column-1:
                        file.write('\t')
                file.write('\n')

        self.root.destroy()


