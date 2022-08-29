from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import tkinter_tools_module as ttm
from binary_ops import *
import pandas as pd
# import originpro as op
# import sys


def export_window(master, tree_menu):
    def check_uncheck(e):
        if not every.get():
            for check in checks:
                check.set(True)
        else:
            for check in checks:
                check.set(False)

    def enabling_options(e=None):
        if appending.get():
            my_combo2['state'] = NORMAL
            my_label2['state'] = NORMAL
            if file_ext.get() == 'origin':
                my_combo1['state'] = NORMAL
                my_label1['state'] = NORMAL
            else:
                my_combo1['state'] = DISABLED
                my_label1['state'] = DISABLED
        else:
            my_combo2['state'] = DISABLED
            my_label2['state'] = DISABLED
            my_combo1['state'] = DISABLED
            my_label1['state'] = DISABLED

    def enable_export():
        if any([check.get() for check in checks]):
            my_btn['state'] = NORMAL
        else:
            my_btn['state'] = DISABLED

    top = Toplevel()
    top.resizable(0, 0)
    # top.attributes('-topmost', 'true')
    top.transient(master)
    top.lift()
    top.geometry('450x230')
    top.title('Export tool')
    top.iconbitmap(r'group-30_116053.ico')

    parent_frame = LabelFrame(top, bg='white')
    parent_frame.pack(padx=10, pady=10)

    child_frame = LabelFrame(parent_frame, text="Options", bg='white')
    child_frame.pack(side=RIGHT, fill=X)

    opt_frame = Frame(child_frame, bg='white')
    opt_frame.pack()
    where2_frame = LabelFrame(opt_frame, text="File type", bg='white')
    where2_frame.pack(side=LEFT, fill=BOTH)

    file_ext = StringVar()
    file_ext.set('excel')

    Radiobutton(where2_frame, text="EXCEL", command=enabling_options, variable=file_ext, value='excel', bg='white').pack()
    Radiobutton(where2_frame, text="ORIGIN", command=enabling_options, variable=file_ext, value='origin', bg='white').pack()
    # command=lambda: print(file_ext.get())
    my_frame = LabelFrame(opt_frame, text='Export Mode', bg='white')
    my_frame.pack(side=LEFT, fill=BOTH)

    appending = BooleanVar()

    Radiobutton(my_frame, text="Append", variable=appending, value=True, command=enabling_options, bg='white').pack()
    Radiobutton(my_frame, text="New file", variable=appending, value=False,  command=enabling_options, bg='white').pack()

    child_frame2 = LabelFrame(parent_frame, text='Data selection', bg='White')
    child_frame2.pack(side=RIGHT, fill=BOTH, expand=1)

    my_canvas = Canvas(child_frame2, bg='white')

    my_yscroll = Scrollbar(child_frame2)
    my_xscroll = Scrollbar(child_frame2, orient=HORIZONTAL)
    my_yscroll.pack(side=RIGHT, fill=Y)
    my_xscroll.pack(side=BOTTOM, anchor='e', fill=X)

    my_canvas.pack(side=RIGHT, fill=BOTH, expand=1)

    my_yscroll.configure(command=my_canvas.yview)
    my_xscroll.configure(command=my_canvas.xview)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox('all'), xscrollcommand=my_xscroll.set, yscrollcommand=my_yscroll.set))

    ttm.scroll_bind(my_canvas)

    inner_frame = Frame(my_canvas, bg='white')
    my_canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    every = BooleanVar()
    slc_all = Checkbutton(inner_frame, text='Select all', variable=every, onvalue=True, offvalue=False,
                          command=enable_export, bg='white')
    slc_all.pack(anchor='w', padx=[5, 0])

    # Selecting charts
    checks = [BooleanVar() for i in range(len(tree_menu.dic_charts))]
    keys = []
    i = 0
    for key in tree_menu.dic_charts:
        parent = tree_menu.tree.item(key)  # Getting attributes of item
        Checkbutton(inner_frame, text=parent['text'], variable=checks[i], onvalue=True, offvalue=False,
                    command=enable_export, bg='white').pack(anchor='w', padx=[20, 0])

        # TODO finnish line adding option
        lines_id = tree_menu.tree.get_children(key)
        for line_id in lines_id:
            child = tree_menu.tree.item(line_id)
            Checkbutton(inner_frame, text=child['text'], variable=checks[i], onvalue=True, offvalue=False,
                        bg='white').pack(anchor='w', padx=[35, 0])

        keys.append(key)
        i += 1

    slc_all.bind('<Button-1>', check_uncheck)

    frame3 = Frame(child_frame, bg='white')
    frame3.pack(pady=10)

    Label(frame3, text='File:', bg='white').grid(row=0, column=0, sticky='e')

    entry1 = Entry(frame3, text='Enter path', width=25)
    entry1.grid(row=0, column=1)

    my_combo1 = ttk.Combobox(frame3, width=30)
    my_combo2 = ttk.Combobox(frame3, width=30)
    Button(frame3, text='Browse', bg='azure2', command=lambda: browse(entry1,
                                                                      my_combo1,
                                                                      my_combo2,
                                                                      appending.get(),
                                                                      file_ext.get())).grid(row=0, column=2)
    my_label1 = Label(frame3, text='Book:', bg='white')
    my_label1.grid(row=1, column=0, sticky='e')
    my_combo1.grid(row=1, column=1, columnspan=2)

    my_label2 = Label(frame3, text='Sheet:', bg='white')
    my_label2.grid(row=2, column=0, sticky='e')
    my_combo2.grid(row=2, column=1, columnspan=2)

    my_btn = Button(child_frame,
                    text='Export',
                    bg='azure2',
                    width=10,
                    command=lambda: export_where(file=entry1.get(),
                                                 tree_menu=tree_menu,
                                                 checks=checks,
                                                 keys=keys,
                                                 append=appending.get(),
                                                 extention=file_ext.get(),
                                                 sheet_name=my_combo2.get()))
    my_btn.pack(side=BOTTOM, pady=[0, 5])
    my_btn['state'] = DISABLED

    enabling_options()

    top.mainloop()


def browse(my_entry, my_combo1, my_combo2, append, extention):

    my_entry.delete(0, END)  # Resetting entry upon opening new window

    if append:
        # Getting path for existing file
        file_path = filedialog.askopenfilename()
        my_entry.insert(0, file_path)

        if extention == 'excel':
            reader = pd.ExcelFile(file_path)
            my_combo2['values'] = reader.sheet_names

            reader.close()
        else:
            pass
            # wrk_sheets = get_sheets(file_path)
            # my_combo1['values'] = list(wrk_sheets.keys())
            # my_combo2['values'] = wrk_sheets['Chart1'][1]#

        my_combo1.current(0)
        my_combo2.current(0)
    else:
        file_path = filedialog.asksaveasfilename()
        my_entry.insert(0, file_path)

    return file_path


# def get_sheets(file):
#     # Ensures that the Origin instance gets shut down properly.
#     def origin_shutdown_exception_hook(exctype, value, traceback):
#         op.exit()
#         sys.__excepthook__(exctype, value, traceback)
#
#     if op and op.oext:
#         sys.excepthook = origin_shutdown_exception_hook
#
#     op.open(file=file.replace('/', '\\'), readonly=True)
#
#     # Getting books
#     my_books = []
#     idx = 0
#     while True:
#         book = op.find_book('w', idx)
#         if book is None:
#             break
#         my_books.append(book)
#         idx += 1
#     # Getting sheets of each book
#     my_sheets = {}
#     for book in my_books:
#         book_name = book.name
#         idx = 1
#         sheet_list = []
#         while True:
#             sheet = op.find_sheet('w', f'[{book_name}]{idx}')
#             idx += 1
#             if sheet is None:
#                 break
#             sheet_list.append(sheet)
#         my_sheets[book_name] = [book, sheet_list]
#     # Closing Origin
#     if op.oext:
#         op.exit()
#     return my_sheets


def export_where(file, tree_menu, checks, keys, append, extention, sheet_name):
    if extention == 'excel':
        export2xl(file, tree_menu, checks, keys, append, sheet_name)
    elif extention == 'origin':
        #export2op(file, tree_menu, checks, keys, append, sheet_name)
        pass


# def export2op(file, tree_menu, checks, keys, append, sheet_name):
#     print('to origin')
#     if file != '':
#         if append:
#             export2oldop()
#         else:
#             if file.find('.opju') == -1:
#                 # Checking if file as extension .opju
#                 file = f'{file}.opju'
#
#             selected_keys = get_selected_keys(checks, keys)
#             export2newop(file, selected_keys, tree_menu)


# def export2oldop():
#     pass
#
#
# def export2newop(file, selected_keys, tree_menu):
#     # Ensures that the Origin instance gets shut down properly.
#     def origin_shutdown_exception_hook(exctype, value, traceback):
#         op.exit()
#         sys.__excepthook__(exctype, value, traceback)
#
#     if op and op.oext:
#         sys.excepthook = origin_shutdown_exception_hook
#
#     # Set Origin instance visibility.
#     # Important for only external Python.
#     # Should not be used with embedded Python.
#     #if op.oext:
#     #    op.set_show(True)
#
#     for key in selected_keys:
#
#         chart = tree_menu.dic_charts[key]
#         lines_idxs = tree_menu.tree.get_children(key)
#         i = 0
#         # Getting lines in series list
#         df_holder = pd.DataFrame()
#         for line in chart.series_list:
#             line_name = tree_menu.tree.item(lines_idxs[i])['text']
#             i += 1
#
#             x, y = line.get_data()
#             df = pd.DataFrame(np.array([x, y]).transpose(), columns=[f'Voltage (V) - {line_name}',
#                                                                      f'Current (uA) - {line_name}'])
#             df_holder = pd.concat([df_holder, df], axis=1)
#         item = tree_menu.tree.item(key)
#
#         # Writting in Origin
#         wrk_book = op.new_book('w', lname=item['text'])  # Creating workbook
#         wrk_sheet = op.find_sheet('w', wrk_book.name)  # Getting work sheet
#         wrk_sheet.from_df(df_holder)
#
#     # Saving project
#     file = file.replace('/', '\\')
#     op.save(file)
#     # Closing Origin
#     if op.oext:
#         op.exit()


def export2xl(file, tree_menu, checks, keys, append, sheet_name='None'):
    # print(append)
    print(f'file: {file}')
    try:
        if file != '':
            # Checking if a file was selected
            if file.find('.xlsx') == -1:
                # Checking if file as extension .xlsx
                file = f'{file}.xlsx'

            if not append:
                # Creating new excel file to export data
                pd.DataFrame().to_excel(file)

                selected_keys = get_selected_keys(checks, keys)
                exporting2newxl(file, selected_keys, tree_menu)

            elif append:
                selected_keys = get_selected_keys(checks, keys)
                export2oldxl(file, selected_keys, tree_menu, sheet_name)
    except PermissionError:
        messagebox.showwarning('Permission Error', 'Selected file cannot be accessed. Close file and try again!')


def get_selected_keys(checks, keys):
    selected_keys = []
    for i, check in enumerate(checks):
        if check.get():
            # getting lines
            selected_keys.append(keys[i])

    return selected_keys


def export2oldxl(file, selected_keys, tree_menu, sheet_name):

    with pd.ExcelWriter(file, mode='a', engine='openpyxl', if_sheet_exists='replace') as xl_file:
        for key in selected_keys:
            chart = tree_menu.dic_charts[key]
            lines_idxs = tree_menu.tree.get_children(key)
            i = 0

            df_holder = pd.read_excel(file, sheet_name=sheet_name)
            for line in chart.series_list:
                line_name = tree_menu.tree.item(lines_idxs[i])['text']
                i += 1

                x, y = line.get_data()
                df = pd.DataFrame(np.array([x, y]).transpose(), columns=[f'Voltage (V) - {line_name} append',
                                                                         f'Current (uA) - {line_name} append'])
                df_holder = pd.concat([df_holder, df], axis=1)

            df_holder.to_excel(xl_file, sheet_name=sheet_name, index=False)


def exporting2newxl(file, selected_keys, tree_menu):

    # Getting series list
    with pd.ExcelWriter(file, mode='w', engine='openpyxl') as xl_file:
        for key in selected_keys:

            chart = tree_menu.dic_charts[key]
            lines_idxs = tree_menu.tree.get_children(key)
            i = 0
            # Getting lines in series list
            df_holder = pd.DataFrame()
            for line in chart.series_list:
                line_name = tree_menu.tree.item(lines_idxs[i])['text']
                i += 1

                x, y = line.get_data()
                df = pd.DataFrame(np.array([x, y]).transpose(), columns=[f'Voltage (V) - {line_name}',
                                                                         f'Current (uA) - {line_name}'])
                df_holder = pd.concat([df_holder, df], axis=1)
            item = tree_menu.tree.item(key)
            df_holder.to_excel(xl_file, sheet_name=item['text'], index=False)


