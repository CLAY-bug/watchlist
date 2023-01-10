# 作者 ： 赖鑫
# 2023年01月10日11时14分42秒
from flask import Flask, url_for
from markupsafe import escape

app = Flask(__name__)


# 使用装饰器对视图函数进行注册
# 将视图函数绑定到对应的url，当用户在浏览器访问这个url时，就会触发这个函数，获取返回值，并将这个返回值显示到浏览器窗口
@app.route('/')
# 视图函数：处理某个请求的函数
def hello():
    return 'hello!'


@app.route('/user/<name>/')
def user_page(name):
    return f'User : {escape(name)}'


@app.route('/test/')
def test_url_for():
    # url_for函数可以通过视图函数来生成URL
    print(url_for('hello'))
    print((url_for('user_page', name='clay')))
    print((url_for('user_page', name='xgg')))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'Test page'


if __name__ == '__main__':
    app.run(debug=True)
