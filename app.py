# 作者 ： 赖鑫
# 2023年01月10日11时14分42秒
from flask import Flask, url_for, render_template, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from markupsafe import escape
import os, click

app = Flask(__name__)  # 实例化Flask程序实例
# 写入配置的语句一般会放在扩展类实例化语句之前
app.config['SECRET_KEY'] = 'dev'  # 等同于app.secret_key='dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例app


# 一个类就表示一个表，模型类要声明继承db.Model
class User(db.Model):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # id主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
def initdb(drop):
    """初始化数据库"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库')  # 输出提示信息


@app.cli.command()
def forge():
    """生成假数据"""
    db.create_all()

    name = 'Clay Lai'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('数据添加成功')


# 模版上下文处理函数
# 该函数返回的变量(以字典的形式)将会统一注入到每一个模版的上下文
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 返回字典，等同于{'user':user}


# 注册一个错误处理函数，当404错误发生时，触发此函数
@app.errorhandler(404)  # 传入要处理的错误函数
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模版和状态码


# 使用装饰器对视图函数进行注册
# 将视图函数绑定到对应的url，当用户在浏览器访问这个url时，就会触发这个函数，获取返回值，并将这个返回值显示到浏览器窗口
@app.route('/', methods=['GET', 'POST'])
# 视图函数：处理某个请求的函数
def index():
    # 请求方法为post时
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('invalid input')
            return redirect(url_for('index'))
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回首页
    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # 处理编辑表单的提交请求
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input')
            return redirect(url_for('edit', movie_id=movie_id))

        # 更新数据
        movie.title = title
        movie.year = year
        db.session.commit()  # 提交数据库会话
        flash('item updated')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['GET', 'POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    # 删除完毕时，重定向到首页
    return redirect(url_for('index'))


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
    print(url_for('test_url_for', num=2))
    return 'Test page'


if __name__ == '__main__':
    app.run(debug=True)
