import pymysql as pm

MYSQL_HOST = 'localhost'
MYSQL_PORT = 3305
MYSQL_USER = 'root'
MYSQL_PASSWD = 'mysql'
MYSQL_DB = 'schedule'
MYSQL_CHARSET = 'utf8mb4'


def create_conn():
    return pm.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                      password=MYSQL_PASSWD, db=MYSQL_DB, charset=MYSQL_CHARSET)


def find_by_username(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select * from users where user_id=%s", user)
            res = cur.fetchone()
            return res


def get_lists(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select * from lists where users_id=%s", user)
            res = cur.fetchall()
            return res


def get_list(user_id, lists):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select * from lists where users_id=%s and name=%s", (user_id, lists))
            res = cur.fetchone()
            return res


def get_items(list_id):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("select * from item where lists_id=%s", list_id)
            res = cur.fetchall()
            return res


def add_user(user):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into users (user_id, language_code) values (%s,%s)", (user, 'ru'))
            con.commit()


def add_list(user_id, lists):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into lists (name, user_id) values (%s,%s)", (lists, user_id))
            con.commit()


def add_item(list_id, item):
    with create_conn() as con:
        with con.cursor() as cur:
            cur.execute("insert into item (content, lists_id) values (%s,%s)", (item, list_id))
            con.commit()