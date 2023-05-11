from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    #cascade 表示级联操作，就是说，如果主键表中被参考字段更新，外键表中也更新，主键表中的记录被删除，外键表中改行也相应删除
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField('Music', blank=True, related_name='like_users')
    dislikes = models.ManyToManyField('Music', blank=True, related_name='dislike_users')
    first_run = models.BooleanField('是否第一次运行 执行冷启动策略', default=True)
    genre_subscribe = models.TextField('流派订阅', blank=True)
    language_subscribe = models.TextField('语言订阅', blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name


class Music(models.Model):
    song_name = models.CharField('歌曲名称', max_length=200)
    song_length = models.IntegerField('歌曲长度 单位为ms')
    genre_ids = models.CharField('歌曲流派', max_length=100)
    artist_name = models.CharField('歌手', max_length=200)
    composer = models.CharField('作曲', max_length=200)
    lyricist = models.CharField('作词', max_length=200)
    language = models.CharField('语种', max_length=20)
    volume = models.IntegerField('播放量')

    def __str__(self):
        return self.song_name

    def viewed(self):
        self.volume+=1
        self.save(update_fields=['volume'])

    class Meta:
        #verbose_name是该对象的一个可读性更好的唯一名字
        verbose_name = '音乐'
        verbose_name_plural = verbose_name
