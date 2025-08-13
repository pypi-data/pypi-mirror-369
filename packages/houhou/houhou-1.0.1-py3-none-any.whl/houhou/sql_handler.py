from pymysql.converters import escape_string
import json

#构建插入数据sql
def build_insert_sql(build_dict,table):
    '''
    :param build_dict: 根据字典来创建sql
    :param table: 表名
    :return: sql
    '''

    insert_sql = f'insert into {table} ('
    for key in build_dict.keys():
        if build_dict[key] == None:
            continue
        insert_sql += f"`{key}`" + ','
    insert_sql = insert_sql[:-1]
    insert_sql += ') values ('

    for val in build_dict.values():
        if val == None:
            continue
        if isinstance(val, str) == True:
            val = escape_string(val)
        elif isinstance(val, dict) == True or isinstance(val, list) == True:
            val = escape_string(json.dumps(val))
        elif isinstance(val, int) == True:
            val = str(val)

        insert_sql += f"'{str(val)}'" + ','
    insert_sql = insert_sql[:-1]
    insert_sql += ')'
    return insert_sql

