import json
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from webbrowser import open_new
import serialcom
import serial.serialutil
import tkinter_tools_module as ttm
import threading
import pandas as pd
import time
import process_data as pro
from export2xl_tool import export_window
from binary_ops import *
from RampEditorTop import RampEditor


def connection():
    # Creates the window that opens when option connection is selected from the menu
    top = Toplevel()
    # top.attributes('-topmost', 'true')
    top.geometry("400x400")
    top.resizable(False, False)
    top.transient(root)
    top.lift()

    def refresh_listbox():
        # Identifies the available ports for communication
        port_list = serialcom.see_ports()
        my_listbox.delete(0, END)
        for i in range(0, len(port_list)):
            my_listbox.insert(0, port_list[i])

    def connect_port(e=None):
        # establishes the connection to the selected port
        port_name = my_listbox.get(ANCHOR)
        port_name = port_name.split(' ')
        portID = port_name[0]

        global channel  # variable that tracks current connected port
        # channel = serialcom.connect_to(portID, int(bauds.get()))
        global ser
        ser = serial.Serial(portID, baudrate=int(bauds.get()), parity=serial.PARITY_ODD, timeout=1)
        channel = portID

        if channel != "None":
            # if connection is established successfully to the desired port
            statusbar.config(text="Connected to: " + portID)
            main_status.config(text="Connected to: " + portID)
            # serialcom.read_port(channel)
        else:
            # if connection is not established successfully to the desired port
            statusbar.config(text="Connection failed")
            main_status.config(text="Connection failed")

        if e is not None:
            close_top()

    def scroll_function(event):
        if event.delta > 0:
            my_listbox.xview_scroll(-1, "unit")
        else:
            my_listbox.xview_scroll(1, "unit")

    def close_top():
        my_listbox.unbind_all('<MouseWheel>')
        top.destroy()

    # creates the input for the bauds number
    f_properties = LabelFrame(top, text="Connection properties")
    f_properties.pack()
    l_bauds = Label(f_properties, text="Bauds")
    bauds = Entry(f_properties, fg="grey")
    bauds.insert(0, 153600)
    l_bauds.grid(row=0, column=0)
    bauds.grid(row=0, column=1)

    # Create interactive display port window
    my_frame = LabelFrame(top, text="Ports")
    my_frame.pack()
    my_scrollbarX = Scrollbar(my_frame, orient=HORIZONTAL)
    my_scrollbarY = Scrollbar(my_frame, orient=VERTICAL)
    my_listbox = Listbox(my_frame, width=50, xscrollcommand=my_scrollbarX.set, yscrollcommand=my_scrollbarY.set)
    my_scrollbarY.config(command=my_listbox.yview)
    my_scrollbarX.config(command=my_listbox.xview)
    my_scrollbarY.pack(side=RIGHT, fill=Y)
    my_scrollbarX.pack(side=BOTTOM, fill=X)
    my_listbox.pack()

    my_listbox.bind_all('<MouseWheel>', scroll_function)
    my_listbox.bind('<Return>', connect_port)

    # creates a bar that tells crucial information to the user
    statusbar = Label(top, text="status", width=43, bd=1, relief=SUNKEN, fg="grey")
    statusbar.pack()

    # creates the buttons for interaction
    b_connect = Button(top, text="Connect", width=20, command=connect_port)
    b_refresh = Button(top, text="Refresh", width=20, command=refresh_listbox)
    b_close = Button(top, text="Save and Close", width=20, command=close_top)
    b_connect.pack()
    b_refresh.pack()
    b_close.pack()

    # automatically updates the list of available ports
    refresh_listbox()


def load_xldata(file):
    """
    Loads the data from a excel file.
    :param
    filename: str
        string with the path to the desired file
    :return:
    xx: ndarray
        array with the frequencies
    yy: complex ndarray
        impedance array
    """
    df = pd.read_excel(io=file)

    # Getting only values as numpy array
    array = df.values

    volt = array[:, 0]
    curr = array[:, 1]

    flag = 'Not available!'

    add_data(xx=volt.tolist(), yy=curr.tolist(), flag=flag, filename=file.split('/')[-1].replace('.xlsx', ''))


def load_txtdata(file):
    with open(file, 'r') as data:
        data = data.read()

        # Getting flag
    try:
        flag, data = data.split('-tear-')
    except ValueError:
        flag = 'Not available!'

    volt = []
    curr = []
    for item in data.split('\n'):
        try:
            values = item.split('\t')
            volt.append(float(values[0]))
            curr.append(float(values[1]))
        except ValueError:
            pass
        except IndexError:
            pass

    add_data(xx=volt, yy=curr, flag=flag, filename=file.split('/')[-1].replace('.txt', ''))


def load_elchem(file):
    with open(file, 'r') as data:
        jsonStr = data.read()
    pyDic = json.loads(jsonStr)

    nCharts = len(pyDic['Charts'])
    for chart in pyDic['Charts']:
        add_chart()
        for line in chart['Lines']:
            # add lines to chart
            volt = line['x']
            curr = line['y']
            flag = line['tech']
            name = line['Name']
            add_data(xx=volt, yy=curr, flag=flag, filename=name)


def load_from_file():
    """ loads data from a CSV or space delimited file """
    file = filedialog.askopenfilename()

    if file.find('.txt') != -1:
        load_txtdata(file)
    elif file.find('.xlsx') != -1:
        load_xldata(file)
    elif file.find('.elchem') != -1:
        load_elchem(file)
    else:
        messagebox.showerror('File type not valid', 'It is not possible to read this file. Only .txt or .xlsx files can'
                                                    ' be used!')


def add_data(xx, yy, flag, filename):
    # TODO is this try/except block really needed
    try:
        Active_tab = update_tabs()
        # Extracting graph (axes) from tab
        voltam_graph = Active_tab.chart

        # Creating series in graphs (axes)
        voltam_series = ttm.NewSeries(voltam_graph, flag)
        line = voltam_series.add_coordinate_list(xx, yy)
        my_tree_menu.add_line(line, chart=Active_tab.chart, name=filename)
    except UnboundLocalError:
        print('Selected file not valid for data reading')


def add_chart():
    global char_num
    # Creating new tab
    char_num += 1
    Active_tab = my_notebook.add_costume_tab(label=f'Chart {char_num}')
    # Loading widget view to second tab and defining the working chart
    Active_tab.update_tree(my_tree_menu)
    my_tree_menu.add_chart(Active_tab.chart, 'Chart' + str(char_num))
    # Lifting New tab
    my_notebook.select(Active_tab.tab)
    return Active_tab


def update_tabs():
    """
    This function dchecks if new tabs need to be created and updates the variables tracking the tabs (Charts).
    tabs_list, Active_tab, and the treeview
    """
    try:
        Active_tab = my_notebook.get_costume_tab()
    except TclError:
        Active_tab = add_chart()

    return Active_tab


def start_coms():
    # TODO fix: When all tabs are destroyed and run is pressed in overlay mode. There is no tab to plot data
    # updating parameters label
    with open('Active_parameters.txt', 'r') as file:
        text = file.read()
    para_label.config(text=text)
    name, parameters = pro.get_parameters()

    # Disabling button start while measuring
    b_start['state'] = DISABLED
    b_stop['state'] = NORMAL

    update_tabs()
    # Defining Plots and series
    voltam_graph = Active_tab.chart
    voltam_series = ttm.NewSeries(voltam_graph, text)
    my_tree_menu.add_line(voltam_series.line, chart=Active_tab.chart)

    cr = my_combo.get()
    if cr == '1 mA':
        cr = 1000  # uA
    elif cr == '100 nA':
        cr = 0.1  # uA
        # gain_factor = 10
    elif cr == '10 nA':
        cr = 0.01
    else:  # If current range in uA
        cr = int(my_combo.get().split(' ')[0])
    # else:
    #     gain_factor = int(my_combo.get().split(' ')[0])/100
    gain_factor = int(cr / 100)

    # Start actual measure. Serial communication
    try:
        ser.reset_input_buffer()
        """ Ramps parameters"""
        nRepeat = 1
        if name == 'Linear Cyclic Voltammetry' \
                or name == 'Staircase Cyclic Voltammetry' \
                or name == 'Linear Sweep Voltammetry':
            nStep = round(parameters['E step (V)']/parameters['Scan rate (V/s)'] * 1000 / 5)
        else:
            nStep = 1
        print(f'nStep = {nStep}')

        nRamps, ramps = get_parameters(nStep)
        npts = number_pts(ramps[:, 2])

        # Configuring progress bar
        pb.reset(npts)
        print(f'nRamps = {nRamps}')
        """ Sending data to the platform"""
        # t0 = time.perf_counter()  # Starting timing
        byte_array = bytes([nRamps, nRepeat, nStep])
        ser.write(b'R')
        ser.write(byte_array)
        for ramp in ramps:
            for i, item in enumerate(ramp):
                # 16-bit
                bit16 = decimal2signed16bit(round(item))
                byte16 = bits2bytes(bit16, order="RL")
                ser.write(byte16)
        # t1 = time.perf_counter() - t0
        # print(f'Loading elapsed time: {t1 * 1000} ms')
        ser.read(1)

        """ Openning cell"""
        ser.write(b'O')
        ser.read(2)

        """ Setting current range"""
        print(f'gain = {gain}')
        ser.write(b'G')
        ser.write(gain)
        ser.read(2)

        """ Starting measure"""
        pts_x = []
        pts_y = []

        def plot_thread():
            """
            This function is thread to plot the accuired point in the main graph from the GUI
            :return: displays the measured points in the graph
            """
            # tt0 = time.perf_counter()
            while running:
                try:
                    time.sleep(0.2)
                    i_volt = len(pts_x) - 1
                    i_curr = len(pts_y) - 1
                    index = min(i_volt, i_curr)

                    py, px = pro.process_this(name, pts_x[0:index+1], pts_y[0:index+1], parameters)
                    voltam_series.add_coordinate_list(px, py)

                except IndexError:
                    print('IndexError in plot thread')
            # my_tree_menu.add_line('Line', chart=Active_tab.chart)
            # tt1 = time.perf_counter() - tt0
            # print(f'Plot thread finished in: {tt1*1000} ms')

        # t0 = time.perf_counter()  # Starting timing
        ser.write(b'M')
        ser.write(bytes([config, 0, 0, 0, 0]))
        var = 'PreCon'
        com = 0

        running = True
        threading.Thread(target=plot_thread).start()  # Threading the plot

        while com != b'Z':
            if var == 'PreCon':
                com = ser.read(size=2)
                var = 'Status'

            elif var == 'Status':
                com = ser.read(size=1)
                var = 'Volt'

            elif var == 'Volt':
                com = ser.read(size=2)
                volt = volt_dac(com)
                pts_x.append(volt)
                var = 'Curr'

            elif var == 'Curr':
                com = ser.read(size=2)
                curr = current_conversor(com)
                curr = curr*gain_factor  # According to gain the current will be reported in mA, uA or nA
                pts_y.append(curr*10**6)
                var = 'Status'
                pb.progress()
            print(com)
            # print(com.hex())

        # t1 = time.perf_counter() - t0
        # print(f'Measure elapsed time: {t1 * 1000} ms')

        running = False

        dataXY = np.array([np.asarray(pts_x), np.asarray(pts_y)])
        with open('mydataXY.txt', 'w') as file:
            file.write(str(dataXY))
        """ Closing cell"""
        ser.write(b'F')
        print(ser.read(1).hex())

        pb.complete()  # Completing pb

    except AttributeError:
        messagebox.showwarning("Warning", "Unable to start communication. Active port: " + channel)
    except NameError:
        messagebox.showwarning("Warning", "Unable to start communication. Active port: " + channel)
    except serial.serialutil.SerialException:
        messagebox.showwarning("Warning", "Unable to start communication. Active port: " + channel)
    except ValueError:
        messagebox.showerror("Error", f"Decrease number of ramps!")

    b_start['state'] = NORMAL
    b_stop['state'] = DISABLED


def stop_coms():
    # Tells the microcontroller to stop
    b_stop['state'] = DISABLED
    try:
        # global Active_control
        # if Active_control == 'Start':
        ser.write(b'A')
        ser.read(1)

    except AttributeError:
        messagebox.showwarning("Warning",
                               "Unable to stop communication. No communication occurring. Active port: " + channel)
    b_stop['state'] = NORMAL


def combo_select(e):
    global gain
    if my_combo.get() == '10 nA':
        gain = bytes([1])
    elif my_combo.get() == '100 nA':
        gain = bytes([2])
    elif my_combo.get() == u"1 \u03bcA":
        gain = bytes([3])
    elif my_combo.get() == u"10 \u03bcA":
        gain = bytes([4])
    elif my_combo.get() == u'100 \u03bcA':
        gain = bytes([5])
    elif my_combo.get() == '1 mA':
        gain = bytes([6])
    meas_frame.focus_set()


def config_update(opt):
    """
    Updates the byte related to the config var from the platform.
    :param opt: str
        option to be added or removed
    """
    global config
    if opt == 'mp' and mp.get():
        # Enabling electrode protection during measure
        config += 0b00010000
    elif opt == 'mp' and not mp.get():
        # Disabling electrode protection during measure
        config -= 0b00010000
    elif opt == 'pp' and pp.get():
        # Enabling electrode protection during precondition
        config += 0b00000001
    elif opt == 'pp' and not pp.get():
        # Disabling electrode protection during precondition
        config -= 0b00000001


def export_to():
    export_window(root, my_tree_menu)
    pass


def help_me():
    open_new(r'C:\Users\ssilva50548\OneDrive - INL\Documents\PYTHON\GUI - ElectrochemistryV3\QUICK GUIDE - Elchem.pdf')


def good_bye():
    if messagebox.askokcancel("Quit", "Do you want to quit this program?\nAny unsaved data will be lost!"):
        root.destroy()


def calibrate():
    try:
        main_status.config(text="Calibrating!!!")
        ser.write(b'C')
        ser.read(13)  # completing calibration. takes 5s
        main_status.config(text="Calibration complete")
    except NameError:
        messagebox.showerror('Connection error!', 'No module is connected to this device!')


def save_elchem():
    dic4json = my_tree_menu.get_data4jason()
    jsonStr = json.dumps(dic4json)

    filename = filedialog.asksaveasfilename(title='Save to file',
                                            filetypes=(('Elchem data file', '*.elchem'), ('All files', "*.*")))
    filename += '.elchemdata'

    with open(filename, 'w') as file:
        file.write(jsonStr)


class CostumeNoteBook(ttk.Notebook):
    """
    Costume Notebook. Implemented methods to add and remove costume tabs and variables to track existent tabs
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tabs_list = []
        self.idx = 1

    def add_costume_tab(self, **kwargs):
        cost_tab = ttm.NewTabGUI(self, **kwargs)
        self.tabs_list.append(cost_tab)
        return cost_tab

    def remove_tab(self, costume_tab):
        self.tabs_list.remove(costume_tab)

    def get_costume_tab(self):
        """ Retrieves the active costume tab """
        return self.tabs_list[self.index(self.select())]


root = Tk()
root.title('Elchem')
root.iconbitmap(r'group-30_116053.ico')
root.geometry('800x500')
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", good_bye)

# ser = None
channel = "None"  # tracks the current serial port connected to the program
Active_technic = "None"  # tracks the current electrochemical technic and its parameters
Active_control = "None"  # tracks which actions are currently on going on the serial communication control panel
Active_read = False
gain = bytes([6])
config = 0b00000000

#
# Creates the main Menu
my_menu = Menu(root)

root.config(menu=my_menu)

my_file = Menu(my_menu, tearoff=0)
my_file.add_command(label='Help', command=help_me)
my_file.add_separator()
my_file.add_command(label="Quit", command=root.quit)
my_settings = Menu(my_menu, tearoff=0)
my_settings.add_command(label="Connection", command=connection)
my_settings.add_command(label="Electrochemistry", command=lambda: RampEditor(root))
my_settings.add_command(label="Calibrate", command=calibrate)
my_data = Menu(my_menu, tearoff=0)
my_data.add_command(label="Load data", command=load_from_file)
my_data.add_command(label="Export to...", command=export_to)
my_data.add_command(label="Save as .elchem", command=save_elchem)


mp = BooleanVar()
pp = BooleanVar()
my_opt = Menu(my_menu, tearoff=0)
my_opt.add_checkbutton(label='During measure', onvalue=True, offvalue=False, variable=mp, command=lambda: config_update('mp'))
my_opt.add_checkbutton(label='During precondition',
                       onvalue=True, offvalue=False, variable=pp, command=lambda: config_update('pp'))


my_menu.add_cascade(label="File", menu=my_file)
my_menu.add_cascade(label="Settings", menu=my_settings)
my_menu.add_cascade(label='Electrode protection', menu=my_opt)
my_menu.add_cascade(label="Data", menu=my_data)


""" Control panel """
# Creates the control buttons to control the serial communication
main_frame = LabelFrame(root, text="Control Panel", bg="white")
main_frame.pack(side=LEFT, fill=BOTH)

f_control = Frame(main_frame, bg="white")
f_control.pack(side=TOP, fill=X)

b_start = Button(f_control, text="Run", width=15, height=2, bg="azure2",
                 command=lambda: threading.Thread(target=start_coms).start())
b_start.pack(padx=5)

# b_stop = Button(f_control, text="Stop", width=15, height=2, bg="azure2",
#                command=lambda: threading.Thread(target=stop_coms).start())
b_stop = Button(f_control, text="Stop", width=15, height=2, bg="azure2", command=stop_coms)
b_stop.pack(padx=5)
b_stop['state'] = DISABLED

# Creates a label that tells the user relevant information
main_status = Label(main_frame, text="Connected to: None", bd=1, fg="grey", relief=SUNKEN)
main_status.pack(fill=X, side=BOTTOM)

# Add progress bar
pb = ttm.ProgressBarWidget(main_frame)


""" Control panel 2 """
f_control2 = LabelFrame(main_frame, text='Run Mode', bg="white")
f_control2.pack(side=TOP, fill=X)

make_unique = BooleanVar()

Radiobutton(f_control2, text="Make Unique", variable=make_unique, value=True, bg="white").pack(anchor="w")
Radiobutton(f_control2, text="Overlay", variable=make_unique, value=False, bg="white").pack(anchor="w")
Button(f_control2, text='Add Chart', command=add_chart).pack(fill=BOTH)

""" Measure control panel"""
meas_frame = LabelFrame(main_frame, text='Current range', bg="white")
meas_frame.pack(side=TOP, fill=X)
my_combo = ttk.Combobox(meas_frame, value=['10 nA', '100 nA', u"1 \u03bcA", u"10 \u03bcA", u'100 \u03bcA', '1 mA'])
my_combo.current(3)
my_combo.bind("<<ComboboxSelected>>", combo_select)
my_combo.pack()

""" Notebook """
# Creates the frame and tabs for data visualization in top
f_tabframe = LabelFrame(root, text="Data Visualization", padx=10, bg="whitesmoke")
f_tabframe.pack(side=LEFT, fill=BOTH, expand=True)

my_notebook = CostumeNoteBook(master=f_tabframe)
my_notebook.pack(side=LEFT, anchor="n", fill=BOTH, expand=True)

char_num = 1
Active_tab = my_notebook.add_costume_tab(label=f'Chart {char_num}')

""" TreView and details """
# Creating the frame to hold the treeview and the details of the measure.
# Creating and Adding the first chart to the widget view
aux_frame = LabelFrame(root, text="Details", bg="white")
aux_frame.pack()

f_control3 = LabelFrame(aux_frame, text='Line parameters', bg="white")
para_label = Label(f_control3, text='None', bg="white", width=22)

my_tree_menu = ttm.DetailsTree(aux_frame, para_label)
my_tree_menu.add_chart(Active_tab.chart, 'Chart'+str(char_num))

# Adding rigth mouse menu to treeView
tree_menu = ttm.RightMouse(my_tree_menu.tree)
tree_menu.add_item('Hide all',  my_tree_menu.hide_all)
tree_menu.add_item('Show all',  my_tree_menu.show_all)
tree_menu.add_item('Hide',  my_tree_menu.hide_line)
tree_menu.add_item('Show',  my_tree_menu.show_line)
tree_menu.add_item('Move line up', my_tree_menu.move_line_up)
tree_menu.add_item('Move line down', my_tree_menu.move_line_down)
tree_menu.add_item('Rename', my_tree_menu.rename_line)
tree_menu.add_item('Clear peaks', my_tree_menu.clear_peaks)
tree_menu.add_item('Delete', my_tree_menu.delete_line)

# Loading the widget view to the first tab
Active_tab.update_tree(my_tree_menu)

# Displaying the measure parameters
# f_control3 = LabelFrame(aux_frame, text='Parameters', bg="white")
f_control3.pack(side=TOP, fill=X)
# para_label = Label(f_control3, text='None', bg="white", width=22)
para_label.pack(side=LEFT, fill=X)

root.mainloop()
