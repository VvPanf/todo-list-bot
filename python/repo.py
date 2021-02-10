import pymysql as pm
from enum import Enum


class STATES(Enum):
    S_START = 0
    S_ENTER_LIST_AND_ITEMS = 1
    S_EDIT_LIST = 2


class MYSQL:
    HOST = 'localhost'
    PORT = 3305
    USER = 'root'
    PASSWD = 'mysql'
    DB = 'todo_list_bot_db'
    CHARSET = 'utf8mb4'


def create_conn():
    return pm.connect(host=MYSQL.HOST, port=MYSQL.PORT, user=MYSQL.USER,
                      password=MYSQL.PASSWD, db=MYSQL.DB, charset=MYSQL.CHARSET)


def find_user_id(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select id from users where user_id=%s", user)
            res = cur.fetchone()
            return res[0] if res is not None else None


def delete_user(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("delete from users where user_id=%s", user)
            con.commit()


def get_list_name(list_id):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select name from lists where id=%s", list_id)
            res = cur.fetchone()
            return res[0] if res is not None else None


def get_lists(user_id):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select id, name from lists where users_id=%s", user_id)
            res = cur.fetchall()
            return res


def get_list_id(user_id, lists):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select id from lists where users_id=%s and name=%s", (user_id, lists))
            res = cur.fetchone()
            return res[0] if res is not None else None


def delete_list(list_id):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("delete from lists where id=%s", list_id)
            con.commit()


def get_items(list_id):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select id, content, checked from item where lists_id=%s", list_id)
            res = cur.fetchall()
            return res


def add_user(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into users (user_id, state, language_code) values (%s,%s,%s)",
                        (user, STATES.S_START.value, 'ru'))
            con.commit()


def add_list(user_id, lists):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into lists (name, users_id) values (%s,%s)", (lists, user_id))
            con.commit()


def add_item(list_id, item):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into item (content, checked, lists_id) values (%s,%s,%s)", (item, False, list_id))
            con.commit()


def add_user_if_not_exists(user):
    if find_user_id(user) is None:
        add_user(user)


def change_state(user, state):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("update users set state=%s where user_id=%s", (state, user))
            con.commit()


def get_state(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select state from users where user_id=%s", user)
            res = cur.fetchone()
            return res[0] if res is not None else None


def change_item_checked(item_id, checked):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("update item set checked=%s where id=%s", (checked, item_id))
            con.commit()
