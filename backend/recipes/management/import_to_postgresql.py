import json
import psycopg2
# import os

# Подключение к базе
conn = psycopg2.connect(user='django_user',
                        dbname='django',
                        password='mysecretpassword',
                        host='db',
                        port='5432')


cur = conn.cursor()

# Открываем файл для загрузки
with open('./recipes/management/ingredients.json') as my_file:
    data = json.load(my_file)

query_sql = ''' insert into recipes_ingredient(name,measurement_unit)
             select name,measurement_unit 
             from json_populate_recordset(NULL::recipes_ingredient, %s) '''
cur.execute(query_sql, (json.dumps(data),))

conn.commit()


with open('./recipes/management/tags.json') as my_file:
    data = json.load(my_file)

query_sql = ''' insert into recipes_tag(name,color,slug)
             select name,color,slug
             from json_populate_recordset(NULL::recipes_tag, %s) '''
cur.execute(query_sql, (json.dumps(data),))

conn.commit()

cur.close()
conn.close()
