import sqlite3 as sql
from enum import Enum

CREATE_QUERY_FILE = '../sql/create.sql'


class STATES(Enum):
    S_START = 0
    S_ENTER_LIST_AND_ITEMS = 1
    S_EDIT_LIST = 2


connection = None


def get_con():
    global connection
    if connection is None:
        connection = sql.connect(':memory:', check_same_thread=False)
    return connection


def create_tebles():
    cur = get_con().cursor()
    with open(CREATE_QUERY_FILE, encoding='UTF-8') as queryfile:
        cur.executescript(queryfile.read())
        get_con().commit()


def find_user_id(user):
    cur = get_con().cursor()
    cur.execute("select id from users where user_id=?", (user,))
    res = cur.fetchone()
    return res[0] if res is not None else None


def delete_user(user):
    cur = get_con().cursor()
    cur.execute("delete from users where user_id=?", (user,))
    get_con().commit()


def get_list_name(list_id):
    cur = get_con().cursor()
    cur.execute("select name from lists where id=?", (list_id,))
    res = cur.fetchone()
    return res[0] if res is not None else None


def get_lists(user_id):
    cur = get_con().cursor()
    cur.execute("select id, name from lists where users_id=?", (user_id,))
    res = cur.fetchall()
    return res


def get_list_id(user_id, lists):
    cur = get_con().cursor()
    cur.execute("select id from lists where users_id=? and name=?", (user_id, lists))
    res = cur.fetchone()
    return res[0] if res is not None else None


def delete_list(list_id):
    cur = get_con().cursor()
    cur.execute("delete from lists where id=?", (list_id,))
    get_con().commit()


def get_items(list_id):
    cur = get_con().cursor()
    cur.execute("select id, content, checked from item where lists_id=?", (list_id,))
    res = cur.fetchall()
    return res


def add_user(user):
    cur = get_con().cursor()
    cur.execute("insert into users (user_id, state, language_code) values (?,?,?)",
                (user, STATES.S_START.value, 'ru'))
    get_con().commit()


def add_list(user_id, lists):
    cur = get_con().cursor()
    cur.execute("insert into lists (name, users_id) values (?,?)", (lists, user_id))
    get_con().commit()


def add_item(list_id, item):
    cur = get_con().cursor()
    cur.execute("insert into item (content, checked, lists_id) values (?,?,?)", (item, False, list_id))
    get_con().commit()


def add_user_if_not_exists(user):
    if find_user_id(user) is None:
        add_user(user)


def change_state(user, state):
    cur = get_con().cursor()
    cur.execute("update users set state=? where user_id=?", (state, user))
    get_con().commit()


def get_state(user):
    cur = get_con().cursor()
    cur.execute("select state from users where user_id=?", (user,))
    res = cur.fetchone()
    return res[0] if res is not None else None


def change_item_checked(item_id, checked):
    cur = get_con().cursor()
    cur.execute("update item set checked=? where id=?", (checked, item_id))
    get_con().commit()
