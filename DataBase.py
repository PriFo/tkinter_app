import pymysql


CONN_INFO: dict = {
    'HOST': 'localhost',
    'USER': 'root',
    'PASSWORD': '!2#4%6&8ZxC8&6%4#2!',
    'PORT': 2280,
    'DATABASE': 'test_db',
    'DATABASES': ('game_dev', 'test_db')
}


def get_str(aim_for_str: [tuple, list], need_to_quota, types: dict = None) -> str:
    res_str: str = ''
    index: int = 0
    columns: list
    if types:
        columns = list(types.items())[1:]
    else:
        columns = []
    for i in aim_for_str:
        if need_to_quota and columns:
            if types[columns[index][0]] == 'bit(1)':
                res_str += i
            else:
                res_str += '\'' + i + '\''
        else:
            res_str += i
        if not index + 1 == len(aim_for_str):
            res_str += ', '
        index += 1
    return res_str


class DataBase:
    def __init__(self):
        self.__is_connect: bool = False
        # self.__db = pymysql.connect(host='localhost', user='root', password='!2#4%6&8ZxC8&6%4#2!',
        #                             port=2280, db='game_dev')
        self.__db = pymysql.connect(
            host=CONN_INFO['HOST'],
            user=CONN_INFO['USER'],
            password=CONN_INFO['PASSWORD'],
            port=CONN_INFO['PORT'],
            db=CONN_INFO['DATABASE']
        )
        self.__is_connect = True
        self.__cur = self.__db.cursor()

    def get_columns(self, table: str) -> dict:
        self.__cur.execute("""describe """ + table)
        desc_res = self.__cur.fetchall()
        res: dict = {'columns': (), 'types': ()}
        for i in desc_res:
            res['columns'] += (i[0], )
            res['types'] += (i[1], )
        return res

    def get_values(self, table: str) -> list:
        self.__cur.execute("""select * from """ + table)
        return list(self.__cur.fetchall())

    def get_tables(self) -> tuple:
        self.__cur.execute("""show tables""")
        desc_res = list(self.__cur.fetchall())
        res: tuple = ()
        for i in desc_res:
            res += (i[0],)
        return res

    def input_value(self, columns: tuple, values: tuple, table: str, types: dict):
        db_command: str = """INSERT INTO """ + table + """ (""" + get_str(columns, False) + \
                          """) VALUES (""" + get_str(values, True, types) + ')'
        self.__cur.execute(db_command)
        self.__db.commit()

    def delete_value(self, columns: tuple, values: tuple, table: str, types: dict):
        db_command: str = """DELETE FROM """ + table + """ WHERE """
        for i in range(0, len(columns)):
            db_command += columns[i] + ' = '
            if types[columns[i]] == 'bit(1)':
                db_command += values[i]
            else:
                db_command += '\'' + values[i] + '\''
            if not i + 1 == len(columns):
                db_command += ' and '
        self.__cur.execute(db_command)
        self.__db.commit()

    def update_value(self, columns: tuple, values: tuple, old_values: tuple, table: str, types: dict):
        db_command: str = """UPDATE """ + table + """ SET """
        for i in range(0, len(columns)):
            db_command += columns[i] + ' = '
            if types[columns[i]] == 'bit(1)':
                db_command += values[i]
            else:
                db_command += '\'' + values[i] + '\''
            if not i + 1 == len(columns):
                db_command += ', '
        db_command += ' WHERE '
        for i in range(0, len(columns)):
            db_command += columns[i] + ' = '
            if types[columns[i]] == 'bit(1)':
                db_command += old_values[i]
            else:
                db_command += '\'' + old_values[i] + '\''
            if not i + 1 == len(columns):
                db_command += ' AND '
        self.__cur.execute(db_command)
        self.__db.commit()

    def is_connect(self):
        return self.__is_connect
