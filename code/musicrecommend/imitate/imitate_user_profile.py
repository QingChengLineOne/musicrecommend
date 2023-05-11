import pymysql
import random
conn = pymysql.connect(host='localhost',user='root',password='123456',database='musicrecommend')
cur=conn.cursor()

genre = ['流行','舞曲','R&B/Soul','民族','电子','民谣','英伦','金属','朋克','古风','后摇',
                 '爵士','拉丁','蓝调','雷鬼','世界音乐','摇滚','说唱','古典','乡村']
language = ['华语','日语','英语','台语','纯音乐','韩语','粤语']


for i in range(6,107):
    genre_new = genre[random.randrange(len(genre))]
    language_new = language[random.randrange(len(language))]
    cur.execute(f"update music_userprofile set genre_subscribe='{genre_new}',language_subscribe='{language_new}' where id={i}")
    print(f"插入第{i-5}条数据完成")
conn.commit()
cur.close()