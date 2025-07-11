import mysql.connector
from mysql.connector import Error


class MySQLDatabase:
    def __init__(self, database,host="localhost", user="root", password="1234",encoding="utf8mb4"):
        self._connection = None
        try:
            self._connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset=encoding
            )
        except Error as e:
            print(f"\033[1;31mThe error '{e}' occurred\033[0m")

    def show_basic_inf(self):
        cursor = self._connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # 表头格式
        header_ch = "| {:<17} | {:<13} | {:<8} | {:<8} | {:<13} | {:<17} |"
        header = "| {:<19} | {:<15} | {:<10} | {:<10} | {:<15} | {:<20} |"
        separator = "+" + "-" * 21 + "+" + "-" * 17 + "+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 17 + "+" + "-" * 22 + "+"

        for table in tables:
            table_name = table[0]
            centered_name = table_name.center(len(separator))
            print(centered_name)
            print(separator)
            print(header_ch.format("字段名", "数据类型", "允许NULL", "键类型", "默认值", "额外属性"))
            print(separator)

            cursor.execute(f"DESCRIBE {table_name}")
            for row in cursor.fetchall():
                print(header.format(
                    str(row[0]),  # 字段名
                    str(row[1]),  # 数据类型
                    str(row[2]),  # 是否允许NULL
                    str(row[3] if row[3] else ""),  # 键类型
                    str(row[4] if row[4] else "NULL"),  # 默认值
                    str(row[5] if row[5] else "")  # 额外属性
                ))
            print(separator)

    def execute_query(self, query, params=None):
        cursor = self._connection.cursor()
        notice_str=""
        try:
            cursor.execute(query, params)
            self._connection.commit()
            notice_str="Query executed successfully"
        except Error as e:
            notice_str=f"\033[1;31mThe error '{e}' occurred\033[0m"
            print(notice_str)
        finally:
            cursor.close()
        return notice_str

    def fetch_data(self, query, params=None):
        cursor = self._connection.cursor()
        result = None
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
        return result

    def close_connection(self):
        if self._connection.is_connected():
            self._connection.close()
