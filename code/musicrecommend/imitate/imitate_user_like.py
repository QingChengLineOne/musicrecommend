import random

import pymysql
conn = pymysql.connect(host='localhost',user='root',password='123456',database='musicrecommend')
cur=conn.cursor()

ret = random.randint(3,63716)


for i in range(20,100):
    like_list = []
    cur.execute(f"select genre_subscribe,language_subscribe from auth_user as a,music_userprofile as m "
                 f"where a.id=m.user_id and m.id={i}")
    results = cur.fetchall()
    genre = results[0][0]
    language = results[0][1]
    cur.execute(f"select id from music_music where language='{language}' or genre_ids = '{genre}'")
    results_new = cur.fetchall()
    for j in range(len(results_new)):
        like_list.append(results_new[j][0])
    for k in range(2):
        ret = random.choice(like_list)
        cur.execute(f"insert into music_userprofile_likes(userprofile_id,music_id) values({i},{ret})")
        print(f"正在插入第{k+1}条数据")
    # for j in range(10):
    #    cur.execute(f"insert into music_userprofile_likes(userprofile_id,music_id) values({i},{ret})")

conn.commit()
cur.close()