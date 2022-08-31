from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.colors import to_hex
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from peak_search_engine_v2 import search4peak as s4p
import pp_search as ppss
import numpy as np
from tkinter import TclError
import threading

"""
This modules contains classes to create useful complex widgets.

Syntax example:

        example 1: ToolTip(my_button, tip_text='This is a button')
        example 2: rm_menu = RightMouse(root).add_items(["Build Ramps", "Properties", "Analysis"],
                                         [RampEditorTop.call, function, function])
                   
                   
This class is useful to add additional information to help the user using the  GUI 
without taking much space from the screen.
"""


def scroll_bind(widget):
    def scroll_yfunction(event):
        try:
            if event.delta > 0:
                widget.yview_scroll(-1, "unit")
            else:
                widget.yview_scroll(1, "unit")
        except TclError:
            widget.unbind_all('<MouseWheel>')
            widget.unbind_all('<Control-MouseWheel>')

    def scroll_xfunction(event):
        try:
            if event.delta > 0:
                widget.xview_scroll(-1, "unit")
            else:
                widget.xview_scroll(1, "unit")
        except TclError:
            widget.unbind_all('<MouseWheel>')
            widget.unbind_all('<Control-MouseWheel>')

    widget.bind_all('<MouseWheel>', scroll_yfunction)
    widget.bind_all('<Control-MouseWheel>', scroll_xfunction)


def in_thread(fun):
    """
    Decorator function to run a callable in a thread
    """

    def wrapper(*args, **kwargs):
        t1 = threading.Thread(target=fun, args=args, kwargs=kwargs)
        t1.start()

    return wrapper


class ToolTip:
    """
    This class is useful to add additional information to help the user using the  GUI
    without taking much space from the screen.
    """

    def __init__(self, widget, tip_text=None, font=("tahoma", "8", "normal"), auto=True, follow=False):
        self.widget = widget
        self.tip_text = tip_text
        self.font = font
        self.tip_window = None
        self.label = None
        if auto:
            self.widget.bind('<Enter>', self.mouse_enter)
            self.widget.bind('<Leave>', self.mouse_leave)
        if follow:
            self.create_window()
            self.add_label()
            # for some reason .bind_all must be used instead of just .bind. Using just .bind interferes with the
            # functionality of the matplotlib toolbar
            self.widget.bind_all('<Motion>', self.motion_)

    def motion_(self, event):
        try:
            self.label.configure(text=self.tip_text)
            cx = self.widget.winfo_pointerx() - self.widget.winfo_rootx() * 0.15
            cy = self.widget.winfo_pointery()
            self.tip_window.geometry("+%d+%d" % (cx, cy))
        except TclError:
            self.widget.unbind_all('<Motion>')

    def mouse_enter(self, _event):
        self.show_tooltip()

    def mouse_leave(self, _event):
        self.hide_tooltip()

    def show_tooltip(self, dinamic=False):
        """ Creates a new window"""
        # Getting the position at which the tooltip will pop-up
        x_left = self.widget.winfo_rootx()
        y_top = self.widget.winfo_rooty() - 18
        # Creating a new window and configuring it
        # self.tip_window = Toplevel(self.widget)
        # self.tip_window.overrideredirect(True)
        self.create_window()
        self.tip_window.geometry("+%d+%d" % (x_left, y_top))
        # Adding a label to display the information wanted
        # label = Label(self.tip_window, text=self.tip_text, justify=LEFT, background="#ffffe0", relief=SOLID,
        #              borderwidth=1, font=self.font)
        # label.pack(ipadx=1)
        self.add_label()

    def create_window(self):
        self.tip_window = Toplevel(self.widget)
        self.tip_window.overrideredirect(True)
        self.tip_window.attributes('-topmost', 'true')

    def add_label(self):
        self.label = Label(self.tip_window, text=self.tip_text, justify=LEFT, background="#ffffe0", relief=SOLID,
                           borderwidth=1, font=self.font)
        self.label.pack(ipadx=1)

    def hide_tooltip(self):
        """Destroys the created window"""
        # if self.tip_window:
        self.tip_window.destroy()

    def __del__(self):
        print('Object deleted')


class ProgressBarWidget:
    """ Creates a progress bar """

    def __init__(self, master, tasks=1000):
        """
        Displays a progress bar.

        :param master: tkinter master
            Widget where the bar will be placed
        :param tasks: int
            Number of tasks expected to complete the progress bar

        """
        self.master = master
        self.frame = Frame(master, bg='white')
        self.frame.pack(side=BOTTOM, fill=Y)

        self.tasks = tasks
        self.bar = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', length=150)
        self.bar.pack(side=BOTTOM)

        self.text = '0%'
        self.label = Label(self.frame, text=self.text, bg='white')
        self.label.pack(side=TOP)

    def progress(self):
        """ Increases the progress of the bar """
        self.bar['value'] = 1 + int(self.bar['value'])
        self.update_label()

    def reset(self, tasks):
        """ Resets bar"""
        self.tasks = tasks
        self.bar.config(maximum=self.tasks)
        self.bar.stop()

    def complete(self):
        """ Completely fill the bar"""
        self.bar['value'] = self.tasks
        self.update_label()

    def update_label(self):
        """ Updates the progress label"""
        self.text = str(round(self.bar['value'] / self.tasks * 100)) + '%'
        self.label.config(text=self.text)


class RightMouse:
    """
    Creates a right mouse menu that pops-up every time the user clicks the right mouse.
    The menu can be bound to any master, like: root, buttons, frames, labels.
    The master that is bounded is called master
    """

    def __init__(self, master):
        self.master = master
        self.menu = Menu(master, tearoff=False)
        master.bind('<Button-3>', self.mouse_menu)

    def mouse_menu(self, _event):
        # This function pops up the menu
        self.menu.tk_popup(_event.x_root, _event.y_root)

    """
    This methods bellow, can be used to add and remove items from the menu. 
    The command should be a function created in the working module
    """

    def add_item(self, item_name, _command):
        self.menu.add_command(label=item_name, command=_command)

    def add_items(self, item_list, command_list):
        for i in range(len(item_list)):
            self.menu.add_command(label=item_list[i], command=command_list[i])

    def remove_item(self, item_name):
        self.menu.deletecommand(item_name)


class TkinterChart:
    """
    TkinterGraph creates a Chart in the window. This Chart can be used to plot real time values together
    with NewSeries.

    """

    def __init__(self, master, title='', size=None, xlabel='x', ylabel='y', add_toolbar=False):
        """
        Initializes and displays a new empty axes in a tkinter window.

        :param master: tkinter master
            Widget where the axes will display, generally a frame
        :param title: str
            Title of the axes
        :param size:
            Figure size, default is [7, 5]
        :param xlabel: str
            Label of the x-axis
        :param ylabel: str
            Label of the y-axis
        :param logscale: boolean
            To change the axis scale to logarithm
        :param add_toolbar: boolean
            To add a toolbar for control the axes
        """

        if size is None:
            size = [7, 5]
        self.master = master
        self.title = title
        self.size = size
        self.xlabel = xlabel
        self.ylabel = ylabel
        # Counts the number of series in this chart up to 14, than resets
        self.series_counter = 0
        self.series_list = []
        self.tech_list = []
        self.peak_list = []
        self.legend = None

        # Building figure and main Axes
        self.figure = Figure(figsize=self.size)
        self.axes_ = self.figure.add_subplot(111)
        self.axes_.grid(True, which='both')
        self.axes_.set_title(self.title)
        self.axes_.set_xlabel(self.xlabel)
        self.axes_.set_ylabel(self.ylabel)

        # Limits of the axes
        self.x_upper_limit = 1
        self.x_lower_limit = -1
        self.y_upper_limit = 1
        self.y_lower_limit = -1

        # Builds canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.canvas.draw()

        # Add toolbar
        if add_toolbar:
            toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=True)
            toolbar.update()
            toolbar.pack()

    def add_legend_(self, labels):
        self.legend = self.axes_.legend(self.series_list, labels, loc=0)

    def __del__(self):
        print('Chart destroyed')


class NewSeries:
    """ NewSeries creates and plots series of data en the desired Chart.

    Possible styles for plotting:

    lineStyles = {'': '_draw_nothing', ' ': '_draw_nothing', '-': '_draw_solid', '--': '_draw_dashed',
                  '-.': '_draw_dash_dot', ':': '_draw_dotted', 'None': '_draw_nothing'}

    markers = {'.': 'point', ',': 'pixel', 'o': 'circle', 'v': 'triangle_down', '^': 'triangle_up',
               '<': 'triangle_left', '>': 'triangle_right', '1': 'tri_down', '2': 'tri_up', '3': 'tri_left',
               '4': 'tri_right', '8': 'octagon', 's': 'square', 'p': 'pentagon', '*': 'star', 'h': 'hexagon1',
               'H': 'hexagon2', '+': 'plus', 'x': 'x', 'D': 'diamond', 'd': 'thin_diamond', '|': 'vline', '_': 'hline',
               'P': 'plus_filled', 'X': 'x_filled', 0: 'tickleft', 1: 'tickright', 2: 'tickup', 3: 'tickdown',
               4: 'caretleft', 5: 'caretright', 6: 'caretup', 7: 'caretdown', 8: 'caretleftbase', 9: 'caretrightbase',
               10: 'caretupbase', 11: 'caretdownbase', 'None': 'nothing', None: 'nothing', ' ': 'nothing',
               '': 'nothing'}
    """

    def __init__(self, chart, tech, style=None):
        self.chart = chart
        self.xx = []
        self.yy = []

        # Attributes the style of the new series
        if style is None:
            if self.chart.series_counter == 0:
                self.style = 'b.'
            elif self.chart.series_counter == 1:
                self.style = 'r.'
            elif self.chart.series_counter == 2:
                self.style = 'g.'
            elif self.chart.series_counter == 3:
                self.style = 'c.'
            elif self.chart.series_counter == 4:
                self.style = 'm.'
            elif self.chart.series_counter == 5:
                self.style = 'y.'
            elif self.chart.series_counter == 6:
                self.style = 'k.'
            elif self.chart.series_counter == 7:
                self.style = 'b*'
            elif self.chart.series_counter == 8:
                self.style = 'r*'
            elif self.chart.series_counter == 9:
                self.style = 'g*'
            elif self.chart.series_counter == 10:
                self.style = 'c*'
            elif self.chart.series_counter == 11:
                self.style = 'm*'
            elif self.chart.series_counter == 12:
                self.style = 'y*'
            elif self.chart.series_counter == 13:
                self.style = 'k*'
            elif self.chart.series_counter == 14:
                self.style = 'bD'
            elif self.chart.series_counter == 15:
                self.style = 'rD'
            elif self.chart.series_counter == 16:
                self.style = 'gD'
            elif self.chart.series_counter == 17:
                self.style = 'cD'
            elif self.chart.series_counter == 18:
                self.style = 'mD'
            elif self.chart.series_counter == 19:
                self.style = 'yD'
            elif self.chart.series_counter == 20:
                self.style = 'kD'
                self.chart.series_counter = -1
        else:
            self.style = style

        # Updates the number of series on the current chart
        self.chart.series_counter += 1

        self.line = self.chart.axes_.plot([], [], self.style, markersize=3)[0]

        self.chart.series_list.append(self.line)
        self.chart.tech_list.append(tech)
        self.chart.peak_list.append([])

    def add_coordinates(self, x, y):
        """ Stores the x and y data in the same vector and plots the points by calling draw_()"""
        self.xx.append(x)
        self.yy.append(y)
        self.draw_()

    def add_coordinate_list(self, xlist, ylist):
        self.xx = xlist
        self.yy = ylist
        self.draw_()

        return self.line

    def delete_coordinates(self):
        """ Clears the storing vectors"""
        self.xx = []
        self.yy = []

        self.draw_()

    def draw_(self):
        """ Displays the point in the axes_ and rescales"""
        self.line.set_data(self.xx, self.yy)
        self.rescale()

    def rescale(self):
        """ Rescales the x and y axis to show all plots in the chart """
        x_max = max(self.xx)
        x_min = min(self.xx)
        y_min = min(self.yy)
        y_max = max(self.yy)

        xlimits = self.chart.axes_.get_xlim()
        ylimits = self.chart.axes_.get_ylim()

        new_xlimits = [xlimits[0], xlimits[1]]
        new_ylimits = [ylimits[0], ylimits[1]]

        if x_min < xlimits[0]:
            new_xlimits[0] = x_min
        if x_max > xlimits[1]:
            new_xlimits[1] = x_max
        if y_min < ylimits[0]:
            new_ylimits[0] = y_min
        if y_max > ylimits[1]:
            new_ylimits[1] = y_max

        if new_xlimits[0] != new_xlimits[0] or new_xlimits[1] != xlimits[1]:
            self.chart.axes_.set_xlim(new_xlimits[0], new_xlimits[1])
        if new_ylimits[0] != new_ylimits[0] or new_ylimits[1] != ylimits[1]:
            self.chart.axes_.set_ylim(new_ylimits[0], new_ylimits[1])

        self.chart.canvas.draw()


class NewTabGUI:
    """
    Creates a new tab. Allows management of the collected or loaded data.

    """

    def __init__(self, master, label='New tab'):
        """
        Adds a new tab in notebook

        :param
        -----------------------------
        master: ttk.Notebook

        label: str

        """
        self.master = master
        self.label = label
        self.tab = Frame(self.master, bd=0)
        self.master.add(self.tab, text=self.label)
        head_frame = Frame(self.tab, bg="white")
        head_frame.pack(side=TOP, fill=X)

        self.chart = TkinterChart(self.tab, xlabel='Potential/V', ylabel='Current/uA', add_toolbar=True)

        self.data_array = []
        self.headers = ['Voltage V', 'Current uA']

        Button(head_frame, text="x", command=self.crash_tab, width=2, height=1, bg="tomato2", bd=1).pack(side=RIGHT,
                                                                                                         anchor='n')
        Button(head_frame, text="Peak search", command=self.peak_search).pack(side=LEFT)
        Button(head_frame, text="Manual search", command=self.peak_search_semi_auto).pack(side=LEFT)
        Button(head_frame, text="Table", command=self.show_table).pack(side=LEFT)

        self.pot_mode = BooleanVar()
        self.pot_mode.set(True)
        Checkbutton(head_frame,
                    text='Enable potenciometric analysis',
                    var=self.pot_mode,
                    onvalue=True,
                    offvalue=False,
                    background='white').pack(side=LEFT)

        self.tree = None

    @staticmethod
    def decorator_tree_selection(fun):
        def wrapper(*args, **kwargs):
            try:
                fun(*args, **kwargs)
            except IndexError:
                print('mistake')

        return wrapper

    # @decorator_tree_selection
    @in_thread
    def peak_search(self, window=None):
        """ Call the peak search algorithm """
        x, y, tech, name = self.get_data_array()
        x, y = np.array(x), np.array(y)

        # Setting up the indexes to restrict data
        if window is not None:
            win0 = window[0]
            win1 = window[1]
            idx0 = np.where(x >= win1)[0][0]
            idx1 = np.where(x >= win0)[0][0]
        else:
            idx0 = 0
            idx1 = len(x)-1
        # TODO find way to look for peaks in anodic current signals and CV
        # Chossing the selected algorithm for peak search voltammetry mode/ potenciometry mode
        if self.pot_mode.get():
            xx = x[min([idx1, idx0]):max([idx1, idx0])]
            yy = y[min([idx1, idx0]):max([idx1, idx0])]

            if len(xx) > 0:  # ensuring that the user selected a valid interval
                peaks, params_, area, ph, xb0, xb1, yb0, yb1 = ppss.search(xx, yy)
                if peaks != -1:
                    line, serie_index = self.get_line()[:2]
                    color = line.get_color()
                    baseline = self.chart.axes_.plot([xb0, xb1], [yb0, yb1], color=color)
                    vlines = self.chart.axes_.vlines(x=xx[peaks], ymin=yy[peaks] - ph, ymax=yy[peaks], color=color)
                    note_peak = self.chart.axes_.annotate(f'   {round(ph, 4)}' + u'\u00B5A',
                                                          (xx[peaks], yy[peaks]),
                                                          color=color,
                                                          fontsize='large')
                    note_area = self.chart.axes_.annotate(f'   {round(area, 4)}' + u'\u00B5A\u00B7V',
                                                          (xx[peaks], yy[peaks]-ph/2),
                                                          color=color,
                                                          fontsize='large')
                    self.chart.peak_list[serie_index].append([vlines, baseline, note_peak, note_area, peaks, params_])
                    self.chart.canvas.draw()
                else:
                    messagebox.showwarning('No peak found!', 'No peak was found, please try selecting a different window!')
        else:
            results, combl = s4p(x[idx1:idx0], y[idx1:idx0], name=name, display=False)
            x_pp, ph, area, pot1, pot2, curr1, curr2, y_peak = results

            # Ploting results
            # Getting line
            line, serie_index = self.get_line()[:2]
            color = line.get_color()

            # calculating base line equation
            m = (curr2 - curr1) / (pot2 - pot1)
            b = curr1 - m * pot1
            ybl = m * x_pp + b

            # Saving lines of each visual result
            peak_info = [None] * 4
            peak_info[0] = self.chart.axes_.plot(x_pp, y_peak, color + '*')[0]
            peak_info[1] = self.chart.axes_.plot([pot1, pot2], [curr1, curr2], color)[0]
            peak_info[2] = self.chart.axes_.plot([x_pp, x_pp], [y_peak, ybl], color + '--')[0]
            peak_info[3] = self.chart.axes_.annotate(f'   {round(ph)}' + u'\u00B5A', (x_pp, y_peak), color=color,
                                                     fontsize='large')
            self.chart.canvas.draw()

            # Storing info in tracking list
            # Cheking if an peak was already calculated and if so delete and replacing it with the new one
            peak = self.chart.peak_list[serie_index]
            if peak is not None:
                [item.remove() for item in peak[0]]
            self.chart.canvas.draw()
            self.chart.peak_list[serie_index] = [peak_info]

    def peak_search_semi_auto(self):
        def on_press1(event):
            def on_press2(event2):
                x2 = event2.xdata
                print(f'Window ={x1} to {x2}')
                self.peak_search(window=(min([x1, x2]), max([x1, x2])))
                self.chart.canvas.mpl_disconnect(cid2)
                tp.hide_tooltip()
                tp.__del__()
                tp1.hide_tooltip()
                tp1.__del__()
                self.master.config(cursor='arrow')

            tp1.tip_text = '2'
            x1 = event.xdata
            print('you pressed', event.button, event.xdata, event.ydata)
            self.chart.canvas.mpl_disconnect(cid1)
            cid2 = self.chart.canvas.mpl_connect('button_press_event', on_press2)

        # Popping current chart up. Note it migth not be the same as self.chart
        # chart = self.tree.lift_chart(e=None)
        if self.get_line():  # Making sure user selects a line before starting the algorithm
            self.master.config(cursor='cross')
            cid1 = self.chart.canvas.mpl_connect('button_press_event', on_press1)
            print('Select Window')
            tp = ToolTip(self.master, tip_text='Select Potential Window', auto=False, font=("tahoma", "12", "bold"))
            tp.show_tooltip()
            tp1 = ToolTip(self.chart.canvas.get_tk_widget(), tip_text='1', auto=False, font=("tahoma", "10", "bold"),
                          follow=True)

    def update_tree(self, tree):
        self.tree = tree

    def crash_tab(self):
        """
        Destroys the tab and removes it from the associated widgets
        :return:
        """
        answer = messagebox.askquestion(f'Close tab: {self.label}?', 'Are you sure you want to close this tab?'
                                                                     '\nAny unsaved data will be lost!')

        # self.chart.__del__()
        if answer == 'no':
            pass
        elif answer == 'yes':
            self.tab.destroy()
            self.tab = None
            self.tree.delete_parent(self.chart)
            self.master.remove_tab(self)

    def get_line(self):
        """
        Finds selected line and returns it
        """
        row = self.tree.tree.selection()[0]
        if int(row) not in self.tree.dic_charts:
            parent_row = int(self.tree.tree.parent(row))
            # Checking if selected row is a parent
            serie_index = self.tree.tree.get_children(parent_row).index(row)
            line = self.chart.series_list[serie_index]
            return line, serie_index, row, parent_row

    def get_data_array(self):
        """
        get the data stored in the graphs and saves it in self.data_array.

        """
        line, serie_index, row, parent_row = self.get_line()
        x, y = line.get_data()
        tech = self.chart.tech_list[serie_index]
        name = self.tree.tree.item(row)['text']
        return x, y, tech, name

    @in_thread
    def show_table(self):
        """
        Displays a window with the numerical data of the plots.

        """
        x, y, tech, name = self.get_data_array()

        top = Toplevel()
        top.iconbitmap(r'group-30_116053.ico')
        top.resizable(0, 0)
        top.title(f'Table - {name}')
        top.geometry('350x400')

        # Adding color bar
        line = self.get_line()[0]
        my_canvas = Canvas(top, height=5, bg=to_hex(line.get_color()))
        my_canvas.pack()

        # Creating main frames
        frame1 = Frame(top)
        frame1.pack(expand=1, fill=BOTH)
        frame2 = Frame(top)
        frame2.pack(fill=BOTH)

        # Creating tree view
        my_tree = ttk.Treeview(frame1)
        my_tree['columns'] = ('Row', 'Potential', 'Current')
        my_tree.column('#0', width=0, stretch=NO)
        my_tree.column('Row', width=35, minwidth=35, stretch=NO)
        my_tree.column('Potential', width=120, minwidth=120)
        my_tree.column('Current', width=120, minwidth=120)
        my_tree.heading('#0', text="", anchor=W)
        my_tree.heading('Row', text='Row', anchor=W)
        my_tree.heading('Potential', text="Potential (V)", anchor=W)
        my_tree.heading('Current', text="Current (uA)", anchor=W)

        # Adding scroll function
        my_yscrollbar = ttk.Scrollbar(frame1)
        my_yscrollbar.configure(command=my_tree.yview)
        my_tree.configure(yscrollcommand=my_yscrollbar.set)
        my_yscrollbar.pack(side=RIGHT, fill=Y)

        my_tree.pack(fill=BOTH, expand=1)

        # Adding data to tree view
        # TODO add progress bar while loading big sets of data
        for i in range(len(x)):
            my_tree.insert(parent='', index=i, iid=i, text="", value=(i, float(x[i]), float(y[i])))

        # Adding copy to clipboard function
        my_frame = Frame(frame2)
        my_frame.pack()
        indices = ["Potential (V)", u"Current (\u00B5A)"]
        var0, var1 = IntVar(), IntVar()
        chk_btn1 = Checkbutton(my_frame, text=indices[0], variable=var0, onvalue=1)
        chk_btn2 = Checkbutton(my_frame, text=indices[1], variable=var1, onvalue=2)
        chk_btn1.pack(side=LEFT)
        chk_btn2.pack(side=LEFT)
        chk_btn1.select()
        chk_btn2.select()

        # Adding button to use copy to clipboard functionality
        Button(frame2, text="Copy to Clipboard",
               command=lambda: self.copy2clbd(top, [var0.get(), var1.get()], indices),
               bg='azure2').pack()

        # top.mainloop()

    def copy2clbd(self, master, idxs, indices):
        """
        Copying data to clipboard in a \t delimited text
        :param master: widget to call clipboard function
        :param idxs: indexes of the columns to be copied
        :param indices: columns headings of the data array
        :return: clipboard containing data. Can be pasted in txt files, excel tables or origin workbooks
        """

        # Selecting only the interested indexes
        idxs = [i - 1 for i in idxs if i != 0]

        # Filtrate headings and converting to \t delimited text
        my_headings = [indices[i] for i in idxs]
        my_str = ''
        length = len(my_headings)
        for i, item in enumerate(my_headings):
            if i == length - 1:  # to remove the extra \t from the string
                my_str = my_str + item
            else:
                my_str = my_str + item + '\t'
        my_str = my_str + '\n'

        # Filtrating data and convert to \t delimited text
        str_row = ''
        my_data = self.get_data_array()[0:2]
        my_data = np.transpose(np.array(list(my_data)))  # Arranging my_data structure
        my_data = my_data[:, idxs]
        for row in my_data:
            length = len(row)
            for i, item in enumerate(row):
                if i == length - 1:
                    str_row += f'{item}'
                else:
                    str_row += f'{item}\t'
            str_row += '\n'

        # Joining headings and data together in \t delimited text
        my_str = my_str + str_row

        # Clearing clipboard and updating new data
        master.clipboard_clear()
        master.clipboard_append(my_str)


class DetailsTree:
    """
    Creates a Treeview tkinter master, and defines some functionalities. This Tree will hold all the plots (Charts)
    and their 2d lines.
    """

    def __init__(self, master, parameters_label):
        """
        Creates treeView
        :param
        master: tkinter
            tkinter master capable to hold a Treeview
        """
        self.master = master
        self.parameters_label = parameters_label
        self.dic_charts = {}  # To store the working charts

        self.id = 1  # Track the treeView itens
        self.parent_id = 0  # track the charts (parents of the 2D lines)

        # Formating style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.map('Treeview', background=[('selected', 'azure2')], foreground=[('selected', 'black')])

        # Creating TreeView
        self.tree = ttk.Treeview(self.master)
        self.tree.column('#0', width=120, minwidth=25)
        self.tree.heading('#0', text='Data Manager', anchor=W)
        self.tree.pack(fill=BOTH)

        # Filling first row with irrelevant item. To prevent errors in future blocks of code
        self.tree.insert(parent='', index='end', iid=self.parent_id, text='-----------------------')

        self.tree.bind_all('<Button-1>', self.update_parameters)
        self.tree.bind('<Double-Button-1>', self.lift_chart)

        self.color_dic = {'b': 'blue', 'r': 'red', 'g': 'green', 'y': 'darkgoldenrod2', 'k': 'black', 'c': 'cyan3',
                          'm': 'magenta3'}

    def lift_chart(self, e):
        line_params = self.get_line()
        chart, parent_id = line_params[1], line_params[4]
        my_tab = chart.master
        tab_list = my_tab.master.winfo_children()
        for i, tab in enumerate(tab_list):
            if tab == my_tab:
                tab_id = i

        my_tab.master.select(tab_id)

        return chart

    def update_parameters(self, e):
        row = self.tree.focus()
        if row != '' and int(row) not in self.dic_charts and int(row) != 0:
            parent_row = int(self.tree.parent(row))

            # Checking if selected row is a parent
            chart = self.dic_charts[parent_row]
            serie_index = self.tree.get_children(parent_row).index(row)
            parameters = chart.tech_list[serie_index]
            self.parameters_label.config(text=parameters)
        else:
            self.parameters_label.config(text='')

    def add_chart(self, chart, text):
        """
        Every time a new tap is created. The chart (plot) is loaded to the widget view as a parent.
        To hold future 2d lines (children)
        :param chart: TkinterChart
        :param text: str
        """
        self.parent_id = self.id
        self.dic_charts[self.parent_id] = chart
        self.tree.insert(parent='', index='end', iid=self.parent_id, text=text)
        self.id += 1

    def add_line(self, line, chart, name=None):
        """
        Everytime a NewSeries is created, the 2D lines of the respective charts are added to the widget
        :param name: str, filename
        :param line: 2D line
        :param chart: TkinterChart
        """
        # if not isinstance(line, Line2D):
        #     raise TypeError("Object is not a Line2D. No data was read from selected port")

        line_color = line.get_color()
        tk_color = self.color_dic[line_color]

        self.tree.tag_configure(line_color, foreground=tk_color)

        for key in self.dic_charts:
            if self.dic_charts[key] == chart:
                self.parent_id = key

        if name is None:
            name = f'line {self.id}'  # - {tk_color}
        self.tree.insert(parent=str(self.parent_id), index='end', iid=self.id, text=name,
                         tags=(line_color,))
        self.id += 1

    def move_line_up(self):
        line, chart, serie_index, row, parent_row = self.get_line()
        key_list = list(self.dic_charts.keys())
        index = key_list.index(int(parent_row))
        if index > 0:
            index -= 1

            xy_data = line.get_data()
            style = line.get_color() + line.get_marker()
            tech = chart.tech_list[serie_index]
            peak = chart.peak_list[serie_index]
            if peak is not None:
                [item.remove() for item in peak[0]]
            # removing xy_data from axes and updating canvas
            line.remove()
            chart.canvas.draw()
            # Removing 2D xy_data from list and parameters
            chart.series_list.remove(line)
            chart.tech_list.remove(tech)
            chart.peak_list.remove(peak)

            # Selecting the new chart to move data in
            new_parent = key_list[index]
            chart = self.dic_charts[new_parent]
            # Adding new series to the new chart
            new_serie = NewSeries(chart, tech, style)
            new_serie.add_coordinate_list(xy_data[0], xy_data[1])

            self.tree.move(row, new_parent, 'end')

    def move_line_down(self):
        line, chart, serie_index, row, parent_row = self.get_line()
        key_list = list(self.dic_charts.keys())
        index = key_list.index(parent_row)
        if index < len(key_list) - 1:
            index += 1

            xy_data = line.get_data()
            style = line.get_color() + line.get_marker()
            tech = chart.tech_list[serie_index]
            peak = chart.peak_list[serie_index]
            if peak is not None:
                [item.remove() for item in peak[0]]
            # removing xy_data from axes and updating canvas
            line.remove()
            chart.canvas.draw()
            # Removing 2D xy_data from list and parameters
            chart.series_list.remove(line)
            chart.tech_list.remove(tech)
            chart.peak_list.remove(peak)

            # Selecting the new chart to move data in
            new_parent = key_list[index]
            chart = self.dic_charts[new_parent]
            # Adding new series to the new chart
            new_serie = NewSeries(chart, tech, style)
            new_serie.add_coordinate_list(xy_data[0], xy_data[1])

            self.tree.move(row, new_parent, 'end')

    def get_line(self):
        """ Selectecing respective line and returns it"""
        row = self.tree.selection()[0]

        """Checking if selected item is a line"""
        if int(row) not in self.dic_charts:
            parent_row = int(self.tree.parent(row))
            chart = self.dic_charts[parent_row]
            serie_index = self.tree.get_children(parent_row).index(row)
            line = chart.series_list[serie_index]
        elif int(row) in self.dic_charts:
            parent_row = int(row)
            row = None
            chart = self.dic_charts[parent_row]
            serie_index = None
            line = None

        return line, chart, serie_index, row, parent_row

    def hide_all(self):
        line, chart, serie_index, row, parent_row = self.get_line()
        for line in chart.series_list:
            line.set_visible(False)
        for line_peaks in chart.peak_list:
            if line_peaks:
                for peak in line_peaks:
                    peak[0].set_visible(False)  # vline
                    peak[1][0].set_visible(False)  # baseline
                    peak[2].set_visible(False)  # Annotation
                    peak[3].set_visible(False)  # Annotation
        chart.canvas.draw()

    def show_all(self):
        line, chart, serie_index, row, parent_row = self.get_line()
        for line in chart.series_list:
            line.set_visible(True)
        for line_peaks in chart.peak_list:
            if line_peaks:
                for peak in line_peaks:
                    peak[0].set_visible(True)  # vline
                    peak[1][0].set_visible(True)  # baseline
                    peak[2].set_visible(True)  # Annotation
                    peak[3].set_visible(True)  # Annotation
        chart.canvas.draw()

    def hide_line(self):
        """ Hides the selected line """
        self.visibility_line(False)

    def show_line(self):
        """ Shows the selected line """
        self.visibility_line(True)

    def visibility_line(self, visibility):
        """ Configures the visibility of the selected line"""
        line, chart, serie_index, row, parent_row = self.get_line()
        line.set_visible(visibility)
        line_peaks = chart.peak_list[serie_index]
        if line_peaks:
            for peak in line_peaks:
                peak[0].set_visible(visibility)  # vline
                peak[1][0].set_visible(visibility)  # baseline
                peak[2].set_visible(visibility)  # Annotation
                peak[3].set_visible(visibility)  # Annotation

        chart.canvas.draw()

    @in_thread
    def clear_peaks(self):
        """ Clears peaks from potentiometric analysis"""
        line, chart, serie_index, row, parent_row = self.get_line()
        line_peaks = chart.peak_list[serie_index]
        if line_peaks:
            for peak in line_peaks:
                peak[0].remove()  # vline
                peak[1][0].remove()  # baseline
                peak[2].remove()  # Annotation
                peak[3].remove()  # Annotation

        chart.peak_list[serie_index] = []  # removing all peaks of the line
        chart.canvas.draw()

    @in_thread
    def delete_line(self):
        """
        Deletes the 2D line from all the widgets and removes it from the chart
        """
        line, chart, serie_index, row, parent_id = self.get_line()
        # removing line from axes and updating canvas
        line.remove()
        line_peaks = chart.peak_list[serie_index]
        if line_peaks:
            for peak in line_peaks:
                peak[0].remove()  # vline
                peak[1][0].remove()  # baseline
                peak[2].remove()  # Annotation
                peak[3].remove()  # Annotation

        chart.canvas.draw()
        # Removing 2D line from list and parameters
        chart.series_list.remove(line)
        chart.tech_list.remove(chart.tech_list[serie_index])
        chart.peak_list.remove(chart.peak_list[serie_index])

        # removing line from treeview
        self.tree.delete(row)

    def delete_parent(self, chart):
        """
        Deletes the chart from the widget view.
        :param chart: TkinterChart
        """
        for key in self.dic_charts:
            if self.dic_charts[key] == chart:
                row = key
                self.tree.delete(row)
                self.dic_charts.pop(key)
                break

    def rename_line(self):
        """
        Opens a small window allowing the user to change the name of the selected line from the tree view
        """
        row = self.tree.focus()
        if int(row) not in self.dic_charts and int(row) != 0:
            popup = EntryTop(self.master, self.tree)
            popup.show_window()

    def get_data4jason(self):
        # getting charts id and removing first values because is '0'
        charts = []
        for chart_id in self.tree.get_children()[1:]:
            chart = self.dic_charts[int(chart_id)]
            # Getting chart Name
            chart_name = self.tree.item(chart_id)['text']
            # Getting lines id ate treeView to get their names
            lines_id = self.tree.get_children(chart_id)
            lines4jason = []
            # Getting technical data of the lines from Charts and name from treeView
            for i, line in enumerate(chart.series_list):
                xx = line.get_xdata()
                yy = line.get_ydata()
                tech = chart.tech_list[i]
                peaks = chart.peak_list[i]
                lines4jason.append({'Name': self.tree.item(lines_id[i])['text'], 'tech': tech, 'x': xx,
                                    'y': yy, 'peaks': peaks})
            charts.append({'ChartName': chart_name, 'Lines': lines4jason})
        dic4json = {'Charts': charts}
        return dic4json


class EntryTop:
    def __init__(self, master, widget_func):
        """
        Creates a small window for user inputs.
        :param master: tkinter widget
            master widget where the window will po up
        :param widget_func: tkinter widget
            widget that will receive the input
        """
        self.master = master
        self.top_window = None  # initializing the variable
        self.name = 'Empty'
        self.widget = widget_func
        self.selection = self.widget.focus()
        self.entry = None

    def show_window(self):
        """ Creates a new window"""
        # Getting the position at which the tooltip will pop-up
        x_left = self.master.winfo_rootx()
        y_top = self.master.winfo_rooty() + 5
        # Creating a new window and configuring it
        self.top_window = Toplevel(self.master)
        self.top_window.overrideredirect(True)
        self.top_window.geometry("+%d+%d" % (x_left, y_top))
        self.top_window.attributes('-topmost', 'true')
        # self.top_window.transient(self.widget.master.master)
        self.entry = Entry(self.top_window, background="#ffffe0")
        self.entry.pack(side=LEFT, fill=BOTH)
        self.entry.focus_set()
        button = Button(self.top_window, text='Apply', command=self.destroy_window, bg="azure2")
        button.pack(side=RIGHT)
        self.entry.bind('<Return>', self.destroy_window)
        self.entry.bind('<Escape>', self.destroy_window)

    def destroy_window(self, e=None):
        """Destroys the created window"""
        print(e.keysym)
        if e.keysym != 'Escape':
            self.name = self.entry.get()
            self.widget.item(self.selection, text=self.name)  # Updating widget
        self.top_window.destroy()
