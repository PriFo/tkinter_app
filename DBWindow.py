from tkinter.ttk import Combobox, Treeview, Frame, Entry, Checkbutton, Radiobutton
from tkinter import messagebox as mb, BooleanVar, IntVar, filedialog as fd
from tkinter import Tk, Label, Button
from pymysql import DatabaseError, OperationalError
from DataBase import DataBase, CONN_INFO
from datetime import datetime as dt
import shutil as sh
import os


class DBWindow(Tk):
    def __init__(self):
        try:
            super().__init__()
            self.attributes(
                "-fullscreen",
                True
            )

            # =====================Variables=====================

            self.__db: DataBase
            self.__r_var = IntVar()
            self.__r_var.set(0)
            self.__old_r_var = IntVar()
            self.__old_r_var.set(self.__r_var.get())
            self.__radio_btns: list = []
            self.__old_record: tuple = ()
            self.__old_path_to_file: str = ''
            self.__old_file_name: str = ''
            self.__path_to_file: str = ''
            self.__file_name: str = ''
            self.__need_to_upload_file: bool = False

            # =======================Dicts=======================

            self.__input_entries: dict = {}
            self.__input_entries_lbls: dict = {}
            self.__input_combos_vars: dict = {}
            self.__column_types: dict = {}
            self.__columns: dict = {}
            self.__input_values: dict = {'names': [], 'values': []}
            self.__input_values_mul: dict = {}

            # ================Initializing DBFrame================

            self.__frame_db = Frame(self)
            self.__frame_table = Frame(self.__frame_db, width=1300, height=650)
            self.__frame_table.pack_propagate(False)
            self.iconbitmap('icon.ico')  # обновление иконки приложения
            self.__table = Treeview(self.__frame_table, columns=(), show='headings', height=650)
            self.__table.bind('<ButtonRelease-1>', self.__select_table_item)
            self.__frame_chosen_table = Frame(self.__frame_db, padding=5)
            # self.__lbl = Label(self.__frame_chosen_table, text="Привет", font=24)  # обычная надпись
            # self.__btn_choose = Button(self.__frame_chosen_table, text="Выбрать", font=24, bg="white", fg="blue",
            #                            command=self.__choose_table_click)  # создание кнопки
            self.__btn_quit = Button(self.__frame_chosen_table, text="Выйти", font=('Comic Sans MS', 12), bg="white",
                                     fg="blue", command=self.__quit_click, height=27)
            # self.__combo = Combobox(self.__frame_chosen_table)  # создание поля выбора
            self.__frame_radio = Frame(self.__frame_db, relief='sunken')
            self.__radio_lbl = Label(self.__frame_radio, text='Выберите таблицу:', font=('Comic Sans MS', 10))
            self.__frame_input_value = Frame(self.__frame_db, relief='ridge')
            self.__input_entries_text = Label(self.__frame_input_value, text='Введите данные: ',
                                              font=('Arial', 10))
            self.__frame_insert_btns = Frame(self.__frame_db, relief='sunken', padding=5, width=1300)
            self.__insert_btn = Button(self.__frame_insert_btns, text='Добавить', font=('Comic Sans MS', 14),
                                       bg='white', fg='blue', command=self.__insert_click, width=1290 // 34 + 1)
            self.__delete_btn = Button(self.__frame_insert_btns, text='Удалить', font=('Comic Sans MS', 14), bg='red',
                                       fg='black', command=self.__delete_click, width=1290 // 34 + 1)
            self.__update_btn = Button(self.__frame_insert_btns, text='Обновить', font=('Comic Sans MS', 14),
                                       bg='white', fg='blue', command=self.__update_click, width=1290 // 34 + 1)

            # ================Initializing LogInFrame================

            self.__frame_log_in = Frame(self)

            self.__frame_input = Frame(self.__frame_log_in)
            self.__frame_input.pack_propagate(False)
            self.__host_lbl = Label(self.__frame_input, text='Enter host:', font=('Comic Sans MS', 10))
            self.__input_host = Entry(self.__frame_input, width=40, font=('Comic Sans MS', 10))
            self.__input_host.insert('end', str(CONN_INFO['HOST']))
            self.__port_lbl = Label(self.__frame_input, text='Enter port:', font=('Comic Sans MS', 10))
            self.__input_port = Entry(self.__frame_input, width=40, font=('Comic Sans MS', 10))
            self.__input_port.insert('end', str(CONN_INFO['PORT']))
            self.__user_lbl = Label(self.__frame_input, text='Enter user:', font=('Comic Sans MS', 10))
            self.__input_user = Entry(self.__frame_input, width=40, font=('Comic Sans MS', 10))
            self.__input_user.insert('end', str(CONN_INFO['USER']))
            self.__password_lbl = Label(self.__frame_input, text='Enter password:', font=('Comic Sans MS', 10))
            self.__input_password = Entry(self.__frame_input, width=40, show='*', font=('Comic Sans MS', 10))
            self.__input_password.insert('end', str(CONN_INFO['PASSWORD']))
            self.__select_db = Combobox(self.__frame_input, width=39, font=('Comic Sans MS', 10))
            self.__set_db_values()
            self.__db_lbl = Label(self.__frame_input, text='Enter database:', font=('Comic Sans MS', 10))
            self.__input_db = Entry(self.__frame_input, width=40, font=('Comic Sans MS', 10))
            self.__input_db.insert('end', str(CONN_INFO['DATABASE']))
            self.__var_check = BooleanVar()
            self.__check_select_db = Checkbutton(self.__frame_input, text='Выбрать базу данных',
                                                 variable=self.__var_check, command=self.__on_change_check)
            self.__frame_login_btns = Frame(self.__frame_input)
            self.__connect_btn = Button(self.__frame_login_btns, text='Подключиться', bg='#28A745',
                                        font=('Comic Sans MS', 14), fg='white', command=self.__connect_click)
            self.__quit_login_btn = Button(self.__frame_login_btns, text='Выйти', bg='#E6676B',
                                           font=('Comic Sans MS', 14), command=self.__quit_click)

            self.__grid_log_in_frame()
        except Exception as e:
            mb.showerror(str(e), str(e.args))

        # ==========================================================

        # self.geometry('1280x720')  # размер окна
        # self.__txt = Entry(self, width=10)  # создание поля ввода информации
        # self.__txt.grid(column=1, row=0)

        # ==========================================================

    def __grid_log_in_frame(self):

        self.title('Log in')

        self.__pack_forget(True)

        # ================Griding LogInFrame================

        for child in self.__frame_input.winfo_children():
            child.grid_configure(padx=5, pady=5)
        for child in self.__frame_login_btns.winfo_children():
            child.grid_configure(padx=10)
        self.__host_lbl.grid(column=0, row=0)
        self.__input_host.grid(column=1, row=0)
        self.__port_lbl.grid(column=0, row=1)
        self.__input_port.grid(column=1, row=1)
        self.__user_lbl.grid(column=0, row=2)
        self.__input_user.grid(column=1, row=2)
        self.__password_lbl.grid(column=0, row=3)
        self.__input_password.grid(column=1, row=3)
        self.__check_select_db.grid(column=1, row=4)
        self.__db_lbl.grid(column=0, row=5)
        self.__input_db.grid(column=1, row=5)
        self.__select_db.grid(column=1, row=5)
        self.__select_db.grid_forget()
        self.__connect_btn.grid(column=0, row=0)
        self.__quit_login_btn.grid(column=1, row=0)
        self.__frame_login_btns.grid(column=1, row=6)
        self.__frame_input.pack()
        self.__frame_log_in.update()
        pady = (int(self.winfo_width()) - int(self.__frame_log_in.winfo_reqwidth())) // 4
        padx = (int(self.winfo_height()) - int(self.__frame_log_in.winfo_reqheight())) // 4
        self.__frame_log_in.pack(fill='both', anchor='center', padx=padx, pady=pady)

    def __grid_db_frame(self):

        self.attributes(
            "-fullscreen",
            True
        )

        self.title('GameDev Application')  # обновление названия приложения
        self.__pack_forget(False)
        self.__init_radio_btns()

        # ================Griding DBFrame================

        self.__radio_lbl.grid(column=0, row=0, sticky='w')
        for i in self.__radio_btns:
            i.grid(column=0, row=i['value'] + 1, sticky='w')
        for child in self.__frame_radio.winfo_children():
            child.grid_configure(padx=5, pady=2)
        self.__frame_radio.grid(row=0, column=0, sticky='nw', padx=10, pady=15)
        self.__table.pack(anchor='nw', fill='both')
        self.__frame_table.grid(row=0, column=1, pady=15)
        # self.__lbl.grid(row=0, column=0, sticky='w')  # функция распределения объектов в форме
        # self.__btn_choose.grid(row=2, column=0, sticky='w')
        self.__btn_quit.pack(fill='both')
        # self.__combo.grid(row=1, column=0, sticky='w', pady=50)
        self.__frame_chosen_table.grid(row=0, column=2)
        self.__input_entries_text.grid(column=0, row=1, padx=5, pady=5)
        self.__frame_input_value.grid(row=1, column=1, sticky='w')
        self.__delete_btn.pack(side='left', fill='both')
        self.__insert_btn.pack(side='left', fill='both')
        self.__update_btn.pack(side='left', fill='both')
        self.__frame_insert_btns.grid(column=1, row=2)
        # self.__set_combo(values=self.__db.get_tables())
        # self.__set_table(columns=self.__db.get_columns(self.__combo.get()),
        #                  values=self.__db.get_values(self.__combo.get()))
        self.__frame_db.pack(fill='both')

    def __init_radio_btns(self):

        # ================Initializing Radiobutton================

        index: int = 0
        for i in self.__db.get_tables():
            self.__radio_btns.append(
                Radiobutton(
                    self.__frame_radio,
                    text=i,
                    variable=self.__r_var,
                    value=index,
                    command=self.__choose_table_click
                )
            )
            self.__input_entries[i] = []
            self.__input_entries_lbls[i] = []
            index += 1

    def __pack_forget(self, db: bool):

        temp: Frame
        if db:
            temp = self.__frame_db
        else:
            temp = self.__frame_log_in
        for i in temp.winfo_children():
            for j in i.winfo_children():
                for k in j.winfo_children():
                    k.pack_forget()
                j.pack_forget()
            i.pack_forget()
        temp.pack_forget()

    def __choose_table_click(self):
        # self.__set_table(columns=self.__db.get_columns(self.__combo.get()),
        #                  values=self.__db.get_values(self.__combo.get()))

        self.__input_values['values'] = []
        self.__column_types = {}
        self.__input_values['names'] = []
        res_columns = self.__db.get_columns(self.__radio_btns[self.__r_var.get()]['text'])
        res_values = self.__db.get_values(self.__radio_btns[self.__r_var.get()]['text'])
        index: int = 0
        self.__columns[self.__radio_btns[self.__r_var.get()]['text']] = res_columns['columns']
        for i in res_columns['types']:
            self.__column_types[res_columns['columns'][index]] = i
            index += 1
        self.__set_table(columns=res_columns['columns'],
                         values=res_values)

        # ================Initializing Entries================

        if self.__input_entries[str(self.__radio_btns[self.__old_r_var.get()]['text'])]:
            for i in self.__input_entries[str(self.__radio_btns[self.__old_r_var.get()]['text'])]:
                i.grid_forget()

        if self.__input_entries_lbls[str(self.__radio_btns[self.__old_r_var.get()]['text'])]:
            for i in self.__input_entries_lbls[str(self.__radio_btns[self.__old_r_var.get()]['text'])]:
                i.grid_forget()

        if not self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']]:
            self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']] = []
            self.__input_entries_lbls[self.__radio_btns[self.__r_var.get()]['text']] = []

            for i in self.__input_values['names']:
                if 'id' in i[:4]:
                    table_exist: bool = True
                    if not self.__radio_btns[self.__r_var.get()]['text'] == i[3:] + 's' and \
                            not self.__radio_btns[self.__r_var.get()]['text'] == i[3:] + 'es':
                        flag: bool = False
                        try:
                            need_to_create: bool = True
                            for j in tuple(self.__db.get_values(i[3:] + 's')):
                                if need_to_create:
                                    self.__input_values_mul[i[3:] + 's'] = ()
                                    need_to_create = False
                                for k in j:
                                    if type(k) is str:
                                        self.__input_values_mul[i[3:] + 's'] += (k,)
                                        break
                        except DatabaseError:
                            flag = True
                        if flag:
                            try:
                                need_to_create: bool = True
                                for j in tuple(self.__db.get_values(i[3:] + 'es')):
                                    if need_to_create:
                                        self.__input_values_mul[i[3:] + 'es'] = ()
                                        need_to_create = False
                                    for k in j:
                                        if type(k) is str:
                                            self.__input_values_mul[i[3:] + 'es'] += (k,)
                                            break
                            except DatabaseError:
                                table_exist = False
                                pass
                        if table_exist:
                            try:
                                self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                                    Combobox(self.__frame_input_value, values=self.__input_values_mul[i[3:] + 's'],
                                             font=('Arial', 8))
                                )
                            except KeyError:
                                try:
                                    self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                                        Combobox(self.__frame_input_value, values=self.__input_values_mul[i[3:] + 'es'],
                                                 font=('Arial', 8))
                                    )
                                except KeyError:
                                    if flag:
                                        mb.showwarning('DB is empty', 'Your table \'' + i[3:]
                                                       + 'es\' is empty, write some records in tables where don\'t open'
                                                         'this window to use this app and after reboot it')
                                    else:
                                        mb.showwarning('DB is empty', 'Your table \'' + i[3:]
                                                       + 's\' is empty, write some records in tables where don\'t open'
                                                         'this window to use this app and after reboot it')
                        else:
                            self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                                Entry(self.__frame_input_value, width=len(i), font=('Arial', 8))
                            )
                    else:
                        self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                            Entry(self.__frame_input_value, width=len(i), font=('Arial', 8))
                        )
                elif 'id' in i:
                    self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                        Entry(self.__frame_input_value, width=len(i) * 2, font=('Arial', 8))
                    )
                elif 'name' in i or 'date' in i:
                    self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                        Entry(self.__frame_input_value, width=len(i) * 2, font=('Arial', 8))
                    )
                elif 'login' in i or 'password' in i or 'patronymic' in i:
                    self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                        Entry(self.__frame_input_value, width=len(i) * 3, font=('Arial', 8))
                    )
                elif 'path' in i[len(i) - 7:] or 'file' in i[len(i) - 7:]:
                    self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                        Button(
                            self.__frame_input_value,
                            width=len(i) * 2,
                            font=('Arial', 8),
                            text='Выбрать файл',
                            command=self.__choose_file
                        )
                    )
                else:
                    if self.__column_types[i] == 'bit(1)':
                        self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(
                            Combobox(self.__frame_input_value, values=('Да', 'Нет'), font=('Arial', 8))
                        )
                    else:
                        self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']].append(Entry(
                            self.__frame_input_value, width=len(i) * 5, font=('Arial', 8))
                        )
                self.__input_entries_lbls[self.__radio_btns[self.__r_var.get()]['text']].append(
                    Label(self.__frame_input_value, text=i, font=('Arial', 8))
                )

        index = 0
        for i in self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']]:
            i.grid(column=index + 1, row=1, padx=5, pady=2)
            index += 1

        index = 0
        for i in self.__input_entries_lbls[self.__radio_btns[self.__r_var.get()]['text']]:
            i.grid(column=index + 1, row=0, padx=5, pady=2, sticky='w')
            index += 1

        self.__old_r_var.set(self.__r_var.get())

    def __select_table_item(self, _):
        self.__input_values['values'] = []
        self.__path_to_file = ''
        cur_item = self.__table.focus()
        values_item = self.__table.item(cur_item)['values']
        index: int = 0
        for i in values_item:
            if type(self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']][index]) is Button:
                self.__path_to_file = i
            else:
                self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']][index].delete(0, 'end')
                self.__input_entries[self.__radio_btns[self.__r_var.get()]['text']][index].insert('end', i)
            self.__input_values['values'].append(i)
            index += 1
        self.__old_record = self.__reformat_input_values(True)
        self.__update_old_file()
        pass
        # print(self.__input_values)

    # def __set_combo(self, values: tuple):
    #     self.__combo['values'] = values
    #     self.__combo.current(0)  # установите вариант по умолчанию

    def __set_table(self, columns: tuple, values: list):
        self.__table.delete(*self.__table.get_children())
        self.__table.configure(columns=columns, show='headings', selectmode='extended')
        for i in columns:
            if 'id' in i[:4]:
                if self.__radio_btns[self.__r_var.get()]['text'] == i[3:] + 's' or \
                        self.__radio_btns[self.__r_var.get()]['text'] == i[3:] + 'es':
                    self.__table.heading(column=i, text='№')
                    self.__table.column(i, minwidth=0, width=len(i) * 8, stretch=False)
                else:
                    self.__table.heading(column=i, text=i[3:])
                    self.__table.column(i, minwidth=0, width=len(i) * 15, stretch=False)
            elif 'name' in i or 'date' in i or 'patronymic' in i:
                if 'name' in i:
                    self.__table.heading(column=i, text=i[:len(i) - 5])
                elif 'date' in i:
                    self.__table.heading(column=i, text=i[len(i) - 4:])
                else:
                    self.__table.heading(column=i, text=i)
                self.__table.column(i, minwidth=0, width=len(i) * 15, stretch=False)
            elif 'log' in i or 'password' in i:
                self.__table.heading(column=i, text=i)
                self.__table.column(i, minwidth=0, width=len(i) * 30, stretch=False)
            else:
                self.__table.heading(column=i, text=i)
                self.__table.column(i, minwidth=0, width=len(i) * 50, stretch=False)
            self.__input_values['names'].append(i)
        index: int
        number: int = 1
        for value in values:
            index = 0
            input_values_mul: tuple = ()
            for i in value:
                if 'id' in columns[index][:4]:
                    if not self.__radio_btns[self.__r_var.get()]['text'] == columns[index][3:] + 's' and \
                            not self.__radio_btns[self.__r_var.get()]['text'] == columns[index][3:] + 'es':
                        flag: bool = False
                        try:
                            next_step: bool = True
                            for j in tuple(self.__db.get_values(columns[index][3:] + 's')):
                                if next_step:
                                    if j[0] == i:
                                        for k in j:
                                            if type(k) is str:
                                                input_values_mul += (k,)
                                                next_step = False
                                                break
                        except DatabaseError:
                            flag = True
                        if flag:
                            try:
                                next_step: bool = True
                                for j in tuple(self.__db.get_values(columns[index][3:] + 'es')):
                                    if next_step:
                                        if j[0] == i:
                                            for k in j:
                                                if type(k) is str:
                                                    input_values_mul += (k,)
                                                    next_step = False
                                                    break
                            except DatabaseError:
                                pass
                elif self.__column_types[columns[index]] == 'bit(1)':
                    if i[0]:
                        temp = list(value)
                        temp[index] = 'Да'
                        value = tuple(temp)
                    else:
                        temp = list(value)
                        temp[index] = 'Нет'
                        value = tuple(temp)
                    pass
                index += 1

            self.__table.insert("", 'end', values=(number,) + input_values_mul + value[1 + len(input_values_mul):])
            number += 1

    def __on_change_check(self):
        if self.__var_check.get():
            self.__db_lbl.config(text='Choose database:')
            self.__input_db.grid_forget()
            self.__select_db.grid(column=1, row=5)
        else:
            self.__select_db.grid_forget()
            self.__db_lbl.config(text='Entry database:')
            self.__input_db.grid(column=1, row=5)
        pass

    def __connect_click(self):
        try:
            CONN_INFO['HOST'] = self.__input_host.get()
            CONN_INFO['PORT'] = int(self.__input_port.get())
            CONN_INFO['USER'] = self.__input_user.get()
            CONN_INFO['PASSWORD'] = self.__input_password.get()
            if self.__var_check.get():
                CONN_INFO['DATABASE'] = self.__select_db.get()
            else:
                CONN_INFO['DATABASE'] = self.__input_db.get()

            self.__db = DataBase()
            if self.__db.is_connect():
                self.__grid_db_frame()

        except DatabaseError and RuntimeError and ConnectionRefusedError and OperationalError:
            mb.showerror('Wrong database info', 'Database connection error! Try entering other data.')

    def __insert_click(self):
        table = self.__radio_btns[self.__r_var.get()]['text']
        try:
            if self.__need_to_upload_file:
                self.__upload_file()
            values = self.__reformat_input_values(False)
            self.__db.input_value(
                table=table,
                columns=tuple(self.__columns[table][1:]),
                values=values,
                types=self.__column_types
            )
            res_columns = self.__db.get_columns(self.__radio_btns[self.__r_var.get()]['text'])
            res_values = self.__db.get_values(self.__radio_btns[self.__r_var.get()]['text'])
            self.__set_table(columns=res_columns['columns'],
                             values=res_values)
            if self.__need_to_upload_file:
                self.__update_old_file()
                self.__need_to_upload_file = False
        except DatabaseError as e:
            mb.showerror('DatabaseError', 'Something went wrong...\n' + str(e.args))
        pass

    def __delete_click(self):
        table = self.__radio_btns[self.__r_var.get()]['text']
        values = self.__reformat_input_values(True)
        try:
            self.__db.delete_value(
                table=table,
                columns=tuple(self.__columns[table][1:]),
                values=values,
                types=self.__column_types
            )
            if not self.__path_to_file == '':
                self.__delete_file()
            res_columns = self.__db.get_columns(self.__radio_btns[self.__r_var.get()]['text'])
            res_values = self.__db.get_values(self.__radio_btns[self.__r_var.get()]['text'])
            self.__set_table(columns=res_columns['columns'],
                             values=res_values)
        except DatabaseError as e:
            mb.showerror('DatabaseError', 'Something went wrong...\n' + str(e.args))
        pass

    def __update_click(self):
        table = self.__radio_btns[self.__r_var.get()]['text']
        try:
            if self.__need_to_upload_file:
                self.__upload_file()
                self.__delete_old_file()
                self.__need_to_upload_file = False
            values = self.__reformat_input_values(True)
            self.__db.update_value(
                table=table,
                columns=tuple(self.__columns[table][1:]),
                values=values,
                types=self.__column_types,
                old_values=self.__old_record
            )
            res_columns = self.__db.get_columns(self.__radio_btns[self.__r_var.get()]['text'])
            res_values = self.__db.get_values(self.__radio_btns[self.__r_var.get()]['text'])
            self.__set_table(columns=res_columns['columns'],
                             values=res_values)
        except DatabaseError as e:
            mb.showerror('DatabaseError', 'Something went wrong...\n' + str(e.args))

    def __reformat_input_values(self, delete_update: bool) -> tuple:
        values: tuple = ()
        table = self.__radio_btns[self.__r_var.get()]['text']
        index: int = 0
        for i in self.__input_entries[table]:
            if not index == 0:
                if type(i) is Entry:
                    if self.__column_types[self.__input_entries_lbls[table][index]['text']] == 'timestamp':
                        if delete_update:
                            values += (i.get().replace('\'', '_').replace('\"', '_'),)
                        else:
                            values += (str(dt.now()),)
                    else:
                        values += (i.get().replace('\'', '_').replace('\"', '_'),)
                elif type(i) is Button:
                    values += (self.__path_to_file.replace('\'', '_').replace('\"', '_'), )
                else:
                    if self.__column_types[self.__input_entries_lbls[table][index]['text']] == 'bit(1)':
                        if 'Да' in i.get():
                            values += (str(1),)
                        else:
                            values += (str(0),)
                    else:
                        mul_table = self.__input_entries_lbls[table][index]['text']
                        try:
                            values += (
                                str(
                                    [
                                        n for n, x in enumerate(
                                            self.__input_values_mul[mul_table[3:] + 's']
                                        ) if i.get() in x
                                    ].pop(0) + 1
                                ),
                            )
                        except KeyError:
                            values += (
                                str(
                                    [
                                        n for n, x in enumerate(
                                            self.__input_values_mul[mul_table[3:] + 'es']
                                        ) if i.get() in x
                                    ].pop(0) + 1
                                ),
                            )
            index += 1
        return values

    def __choose_file(self):
        self.__update_old_file()
        self.__need_to_upload_file = True
        self.__path_to_file = fd.askopenfile()
        if self.__path_to_file is not None:
            self.__path_to_file = self.__path_to_file.name
            lst = self.__path_to_file.replace('\\', '/').split('/')
            self.__file_name = lst[len(lst) - 1]
            self.__update_file_name_entry()

    def __update_old_file(self):
        self.__old_path_to_file = self.__path_to_file
        index: int = 0
        table = self.__radio_btns[self.__r_var.get()]['text']
        for i in self.__input_entries_lbls[table]:
            if 'name' in i['text']:
                self.__old_file_name = self.__input_entries[table][index].get()
                break
            index += 1

    def __upload_file(self):
        table = self.__radio_btns[self.__r_var.get()]['text']
        directory = str(os.getcwd()) + '/' + table
        if not os.path.exists(directory):
            os.makedirs(str(directory))
        try:
            sh.copy(str(self.__path_to_file), directory)
            self.__path_to_file = directory.replace('\\', '/')
        except sh.SameFileError:
            name_lst = self.__file_name.split('.')
            index: int = 0
            self.__file_name = ''
            for i in name_lst:
                if not index + 1 == len(name_lst):
                    self.__file_name += i
                else:
                    self.__file_name += '(copy).' + i
                index += 1
            self.__update_file_name_entry()
            sh.copy(
                str(self.__path_to_file),
                directory + '/' + self.__file_name)
            self.__path_to_file = directory.replace('\\', '/')

    def __delete_old_file(self):
        if os.path.exists(self.__old_path_to_file + '/' + self.__old_file_name):
            os.remove(str(self.__old_path_to_file + '/' + self.__old_file_name))
        else:
            mb.showwarning('Something went wrong...',
                           'File' + self.__path_to_file + '/' + self.__file_name + 'not found...')
        self.__old_path_to_file = ''
        self.__old_file_name = ''

    def __delete_file(self):
        if os.path.exists(self.__path_to_file + '/' + self.__file_name):
            os.remove(self.__path_to_file + '/' + self.__file_name)
        else:
            mb.showwarning('Something went wrong...',
                           'File' + self.__path_to_file + '/' + self.__file_name + 'not found...')
        self.__path_to_file = ''
        self.__file_name = ''

    def __update_file_name_entry(self):
        index: int = 0
        table = self.__radio_btns[self.__r_var.get()]['text']
        for i in self.__input_entries_lbls[table]:
            if 'name' in i['text']:
                self.__input_entries[table][index].delete(0, 'end')
                self.__input_entries[table][index].insert('end', self.__file_name)
                break
            index += 1

    def __quit_click(self):
        question = mb.askokcancel('Quit', 'Are you sure?')
        if question:
            self.destroy()

    def __set_db_values(self, values: tuple = CONN_INFO['DATABASES']):
        self.__select_db['values'] = values
        self.__select_db.current(0)  # установите вариант по умолчанию

    def start(self):
        self.mainloop()
