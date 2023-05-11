import pandas as pd
from django.contrib import messages
from django.http import HttpRequest
from surprise import NMF, SVD, SVDpp, KNNBasic, KNNWithMeans, KNNWithZScore, CoClustering
from surprise import Dataset, Reader, Prediction
from surprise import accuracy
from surprise.model_selection import GridSearchCV, cross_validate
from surprise.model_selection import KFold

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth.models import User
from music.models import UserProfile, Music
from django.db.models import Sum

current_request = None



#构建数据集
def build_df():
    data = []
    for user_profile in UserProfile.objects.all():
        for like_music in user_profile.likes.all():
            data.append([user_profile.user.id, like_music.pk, 1])
            # print("喜欢的音乐:")
            # print(like_music.pk)
        for dislike_music in user_profile.dislikes.all():
            data.append([user_profile.user.id, dislike_music.pk, 0])
            # print("不喜欢的音乐:")
            # print(dislike_music.pk)

    return pd.DataFrame(data, columns=['userID', 'itemID', 'rating'])


def build_predictions(df: pd.DataFrame, user: User):
    profile = UserProfile.objects.filter(user=user)
    if profile.exists():
        profile_obj: UserProfile = profile.first()
    else:
        return []

    # 先构建训练集，用SVD训练，再把所有评分过的歌曲放到测试集里，
    # 接着把测试集的数据通过训练的算法放到结果集里
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)

    # 构建训练集
    #所有已知的评分数据转化为Surprise库中的Trainset对象
    trainset = data.build_full_trainset()

    #超参数调优
    # n_factors：给定隐因子的数目，默认为100
    # n_epochs：梯度下降的迭代次数，默认为20
    # biased：给定模型中是否使用偏置项，默认为True，及BiasSVD分解模型；设置为False，表示用FunkSVD
    # lr_all：给定学习率，全部参数使用相同的学习率，默认为0.005
    # reg_all：给定正则化系数，全部参数使用相同的正则化系数，默认为0.02
    param_grid = {'n_factors': [50, 100, 150], 'n_epochs': [10, 20, 30], 'lr_all': [0.002, 0.005, 0.01],
                  'reg_all': [0.01, 0.02, 0.05]}
    gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)
    gs.fit(data)
    # 输出最佳RMSE结果和对应的参数组合
    print(gs.best_score['rmse'])
    print(gs.best_params['rmse'])

    algo = SVD(n_factors=gs.best_params['rmse']['n_factors'],n_epochs=gs.best_params['rmse']['n_epochs'],
               lr_all=gs.best_params['rmse']['lr_all'],reg_all=gs.best_params['rmse']['reg_all'])

    # 数据拟合
    algo.fit(trainset)

    # 取出当前所有有人评分过的歌曲
    subsets = df[['itemID']].drop_duplicates()
    # 测试集
    testset = []
    # for row in subsets.iterrows():
    #     testset.append([userId, row[1].values[0], 0])

    #该方法返回所有用户和所有没有被用户评分的物品的组合，因此返回的测试集包含了所有可能的推荐项。
    testset = trainset.build_anti_testset()
    # 通过测试集构建预测集
    predictions = algo.test(testset, verbose=True)

    # 计算RMSE
    #r_ui即真实评分,est为预测评分
    accuracy.rmse(predictions, verbose=True)

    result_set = []

    user_like = profile_obj.likes.all()
    user_dislike = profile_obj.dislikes.all()

    for item in predictions:
        prediction: Prediction = item
        if prediction.est > 0.99:
            music = Music.objects.get(pk=prediction.iid)
            # 去重，不推荐用户已经喜欢的 或不喜欢的音乐
            if music in user_like:
                continue
            if music in user_dislike:
                continue
            result_set.append(music)

    if len(result_set) == 0:
        messages.error(current_request, '你听的歌太少了，多听点歌再来吧~')
        messages.error(current_request, '将为您推荐播放量最高的10首歌曲')

    return result_set

def build_genre_predictions(user: User):
    predictions = []
    profile = UserProfile.objects.filter(user=user)
    if profile.exists():
        profile_obj: UserProfile = profile.first()
    else:
        return predictions

    genre_subscribe = profile_obj.genre_subscribe.split(',')
    user_like = profile_obj.likes.all()
    user_dislike = profile_obj.dislikes.all()

    for music in Music.objects.filter(genre_ids__in=genre_subscribe):
        if music in user_like:
            continue
        if music in user_dislike:
            continue
        predictions.append(music)

    return predictions


def build_language_predictions(user: User):
    predictions = []
    profile = UserProfile.objects.filter(user=user)
    if profile.exists():
        profile_obj: UserProfile = profile.first()
    else:
        return predictions

    language_subscribe = profile_obj.language_subscribe.split(',')
    user_like = profile_obj.likes.all()
    user_dislike = profile_obj.dislikes.all()

    for music in Music.objects.filter(language__in=language_subscribe):
        if music in user_like:
            continue
        if music in user_dislike:
            continue
        predictions.append(music)

    return predictions


def build_recommend(request: HttpRequest, user: User):
    global current_request
    current_request = request
    predictions = []
    if build_genre_predictions(user)==[] and build_language_predictions(user)==[]:
        messages.error(current_request, '你听的歌太少了，多听点歌再来吧~')
        messages.error(current_request, '将为您推荐播放量最高的10首歌曲')
        for music in Music.objects.annotate(total_volume=Sum('volume')).order_by('-volume')[:10]:
            predictions.append(music)
    else:
        predictions.extend(build_predictions(build_df(), user))
        predictions.extend(build_genre_predictions(user))
        predictions.extend(build_language_predictions(user))

    return predictions


if __name__ == '__main__':
    build_recommend()
