from datetime import datetime,date
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,or_

#データベース作成
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
#データベースの定義
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    hobby1 = db.Column(db.String(100))
    hobby2 = db.Column(db.String(100))
    hobby3 = db.Column(db.String(100))
    hobby4 = db.Column(db.String(100))
    hobby5 = db.Column(db.String(100))
    detail = db.Column(db.String(500))
    birthday = db.Column(db.DateTime)


@app.route('/', methods=['GET', 'POST'])
def index():
    #データベースからすべての投稿を取り出し、それをトップページに渡してあげる
    if request.method == 'GET':
        posts = Post.query.order_by(Post.birthday).all()
        return render_template('index.html', posts=posts, today=date.today())
    #データベースにタスクを保存
    else:
        name = request.form.get('name')
        hobby1 = request.form.get('hobby1')
        hobby2 = request.form.get('hobby2')
        hobby3 = request.form.get('hobby3')
        hobby4 = request.form.get('hobby4')
        hobby5 = request.form.get('hobby5')
        detail = request.form.get('detail')
        birthday = request.form.get('birthday')
        birthday = datetime.strptime(birthday, '%Y-%m-%d')
        new_post = Post(name=name, hobby1=hobby1,hobby2=hobby2,
                        hobby3=hobby3,hobby4=hobby4,hobby5=hobby5,
                        detail=detail, birthday=birthday)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

#/createにアクセスしたら、create.htmlを出す
@app.route('/create')
def create():
    return render_template('create.html')

#データベースにあるidを参照し、指定されたタスクの詳細を表示
@app.route('/detail/<int:id>')
def read(id):
    post = Post.query.get(id)
    posts = Post.query.all()
    tags = list(set([post.hobby1]))
    tags.extend(set([post.hobby2]))
    tags.extend(set([post.hobby3]))
    tags.extend(set([post.hobby4]))
    tags.extend(set([post.hobby5]))
    tags = set(tags)
    return render_template('detail.html', post=post, posts=posts,tags=tags)
#指定されたタスクを削除
@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')
#タスクを編集・更新
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.name = request.form.get('name')
        post.hobby1 = request.form.get('hobby1')
        post.hobby2 = request.form.get('hobby2')
        post.hobby3 = request.form.get('hobby3')
        post.hobby4 = request.form.get('hobby4')
        post.hobby5 = request.form.get('hobby5')
        post.detail = request.form.get('detail')
        post.birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d')
        db.session.commit()
        return redirect('/')

@app.route('/knowledges')
def knowledges():
    posts = Post.query.all()
    #Post.hobby1のPostにknowledgesを代入
    tags = list(set([Post.hobby1 for Post in posts]))
    tags.extend(set([Post.hobby2 for Post in posts]))
    tags = set(tags)
    return render_template('knowledges.html', posts=posts, tags=tags)

@app.route('/knowledges/tags/<tag>')
def search_tag(tag):
    search_posts = Post.query.filter(or_(Post.hobby1 == tag, Post.hobby2==tag,
                                         Post.hobby3==tag,Post.hobby4==tag
                                         ,Post.hobby5==tag)).all()
    return render_template('tags.html', search_posts=search_posts, tag=tag)

#due
if __name__ == "__main__":
    app.run(debug=True)