#用来实现生成注册用户功能

import requests

url = 'http://127.0.0.1:8000/sign_up' # 用您实际要注册的网站的URL替换此处
for i in range(4,101):
    user_name = f'admin{i}'
    pass_word = f'admin'
    data = {
        'username': user_name,
        'password': pass_word,
        'password_1': pass_word # 填写两次密码以进行验证
    }

    response = requests.post(url, data=data)

    if response.ok:
        print('注册成功！')
    else:
        print('注册失败：', response.text)
