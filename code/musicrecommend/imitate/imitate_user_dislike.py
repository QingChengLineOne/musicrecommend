import pymysql
conn = pymysql.connect(host='localhost',user='root',password='123456',database='musicrecommend')
cur=conn.cursor()

genre = ['流行','舞曲','R&B/Soul','民族','电子','民谣','英伦','金属','朋克','古风','后摇',
                 '爵士','拉丁','蓝调','雷鬼','世界音乐','摇滚','说唱','古典','乡村']
language = ['华语','日语','英语','台语','纯音乐','韩语','粤语']

cur.execute("update music_userprofile set genre_subscribe='流行' where id=5")
conn.commit()
cur.close()