from mysql import connector

connection = connector.connect(
    host='localhost',
    database='flight_game',
    user='dbproject',
    password='dbpassword',
    autocommit=True,
)


def sql_result(sql_str, params=()):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_str, params)
        result = cursor.fetchall()
        if cursor.rowcount < 1:
            #print(f"Ei tuloksia ({sql_str})")
            return None
        return result
    finally:
        cursor.close()


def sql_execute(sql_str, params=()):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_str, params)
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()


def sql_fetchone(sql_str, params=()):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_str, params)
        return cursor.fetchone()
    finally:
        cursor.close()


def test():
    sql = f"select name, municipality from airport where ident='efhk'"
    t = sql_result(sql)
    if not t:
        print("Yhteys asetettu väärin.")
        return

    print("Yhteys asetettu oikein")


if __name__ == "__main__":
    test()
