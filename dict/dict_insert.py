import pymysql
import re

f = open('dict.txt')
db = pymysql.connect('localhost',
    'root','123456','dict')

cursor = db.cursor()

for line in f:
    l = re.split(r'\s+',line)
    word = l[0] # 列表第一个是单词
    interpret = ' '.join(l[1:]) # 把所有后面的合并
    sql = '''insert into words (word,interpret) 
     values('%s','%s')'''%(word,interpret)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
f.close()