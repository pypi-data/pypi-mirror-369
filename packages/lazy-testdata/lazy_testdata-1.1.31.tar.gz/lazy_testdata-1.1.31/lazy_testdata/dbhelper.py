'''
Author: yuweipeng
Date: 2023-01-17 09:58:17
LastEditors: yuweipeng
LastEditTime: 2023-04-01 11:13:05
Description: file content
'''
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import records
import pandas as pd


def connet_db(conn_str):
    engine = create_engine(conn_str)
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session


def only_query(conn, sql, params=None):
    """
    使用 records 执行带参数的 SQL 查询
    
    :param conn: 数据库连接字符串或 URI
    :param sql: 带命名参数的 SQL 字符串（如 :phone）
    :param params: 参数字典，如 {"phone": "xxx", "project_id": 123}
    :return: 查询结果列表（每行是一个 dict）
    """
    db = records.Database(conn)
    raw_sql = sql.text if hasattr(sql, 'text') else sql
    try:
        rows = db.query(raw_sql, **(params or {}))  # 支持参数化查询
        return rows
    except Exception as err:
        print(err)
    finally:
        db.close()


def exec_sql(conn, sql, params=None):
    session = connet_db(conn)
    print("SQL:", sql)  # 打印 text() 对象的 SQL
    print("Params:", params)
    try:
        result = session.execute(sql, params or {})
        session.commit()
        return result
    except Exception as err:
        print(err)
    finally:
        session.close()



def write_csv_insert_db(conn, table_name, fieldnames, data, csv_file=None):
    if data:
        if not csv_file:
            csv_file = f'{table_name}.csv'
        with open(csv_file,'w',newline='',encoding='utf-8') as file:
            fieldnames = fieldnames
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)    
        engine = create_engine(conn)
        rows = pd.read_csv(csv_file)
        rows.to_sql(table_name, con=engine, if_exists='append',index=False)
        
        
if __name__ == '__main__':
    CONN = f'mysql+pymysql://root:abc123@11.11.11.11:3306/demo'
    sql = 'select * from ai_workcard_audio limit 10'
    rows = only_query(CONN, sql)
    print(rows)
