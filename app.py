from datetime import datetime,date
from flask import Flask, render_template, request, redirect, url_forgit 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,or_,func
from collections import Counter


#データベース作成
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
#データベースの定義
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    sex = db.Column(db.String(10),nullable=False)
    syussinti = db.Column(db.String(100))

    hobby1 = db.Column(db.String(100))
    hobby2 = db.Column(db.String(100))
    hobby3 = db.Column(db.String(100))
    hobby4 = db.Column(db.String(100))
    hobby5 = db.Column(db.String(100))


    tokui1 = db.Column(db.String(100))
    like1 = db.Column(db.String(100))
    destination1 = db.Column(db.String(100))
    detail = db.Column(db.String(500))
    sodan1 = db.Column(db.String(500))
    birthday = db.Column(db.DateTime)

    age = db.Column(db.Integer)


@app.route('/', methods=['GET', 'POST'])
def index():
    #データベースからすべての投稿を取り出し、それをトップページに渡してあげる
    if request.method == 'GET':
        #年上順に並べ替える
        posts = Post.query.order_by(Post.birthday).all()
        today=date.today()
        return render_template('index.html', posts=posts, today=today)
    #データベースにタスクを保存
    else:
        today=date.today()
        name = request.form.get('name')
        sex = request.form.get('sex')
        syussinti = request.form.get('syussinti')
        hobby1 = request.form.get('hobby1')
        hobby2 = request.form.get('hobby2')
        hobby3 = request.form.get('hobby3')
        hobby4 = request.form.get('hobby4')
        hobby5 = request.form.get('hobby5')
        tokui1 = request.form.get('tokui1')
        like1 = request.form.get('like1')
        destination1 = request.form.get('destination1')
        detail = request.form.get('detail')
        sodan1 = request.form.get('sodan1')
        birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d')

        age = (int(today.strftime("%Y%m%d")) - int(birthday.strftime("%Y%m%d"))) // 10000

        new_post = Post(name=name, sex=sex,syussinti=syussinti,
                        hobby1=hobby1,hobby2=hobby2,
                        hobby3=hobby3,hobby4=hobby4,hobby5=hobby5,
                        tokui1=tokui1,like1=like1,destination1=destination1,
                        detail=detail, sodan1=sodan1,birthday=birthday, age=age)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

#/createにアクセスしたら、create.htmlを出す
@app.route('/create')
def create():
    return render_template('create.html')

#趣味タグランキング
@app.route('/ranking_hobby')
def r_h():
    posts = Post.query.all()
    #プロフ登録者すべてのhobbyを集める
    tags = []
    for i in posts:
        tags.append(i.hobby1)
        tags.append(i.hobby2)
        tags.append(i.hobby3)
        tags.append(i.hobby4)
        tags.append(i.hobby5)

    frequency = Counter(tags)
    frequency = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    frequency = [x for x in frequency if x[0] != '']
    return render_template('ranking_hobby.html', frequency=frequency, posts=posts,tags=tags)


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

#特定のユーザーとの共通点数え
@app.route('/same/<int:id>')
def same(id):
    same_counts = {}

    post_id = Post.query.get(id)
    posts = Post.query.all()

    tags_id = list(set([post_id.hobby1]))
    tags_id.extend(set([post_id.hobby2]))
    tags_id.extend(set([post_id.hobby3]))
    tags_id.extend(set([post_id.hobby4]))
    tags_id.extend(set([post_id.hobby5]))
    tags_id = set(tags_id)

    for i in posts:
        tags = list(set([i.hobby1]))
        tags.extend(set([i.hobby2]))
        tags.extend(set([i.hobby3]))
        tags.extend(set([i.hobby4]))
        tags.extend(set([i.hobby5]))
        tags = set(tags)

        same_count = len(set(tags)&set(tags_id))-1
        same_counts[i]=same_count
    
    sames = []
    same_counts = sorted(same_counts.items(), key=lambda x:x[1], reverse=True)
    #same_counts=sames

    for i in range(len(same_counts)):
        sames.append(same_counts[i][0])
    
    return render_template('same.html', post_id=post_id, posts=posts,tags_id=tags_id,
                           sames=sames,same_counts=same_counts,id=id)

#指定されたタスクを削除
@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>/sodan1')
def delete_sodan(id):
    post = Post.query.get(id)
    post.sodan1=""
    db.session.commit()
    #もといた詳細画面に戻るようにした
    return redirect(url_for('read',id=id))

#タスクを編集・更新
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.name = request.form.get('name')
        post.sex = request.form.get('sex')
        post.syussinti = request.form.get('syussinti')
        post.hobby1 = request.form.get('hobby1')
        post.hobby2 = request.form.get('hobby2')
        post.hobby3 = request.form.get('hobby3')
        post.hobby4 = request.form.get('hobby4')
        post.hobby5 = request.form.get('hobby5')
        post.tokui1 = request.form.get('tokui1')
        post.like1 = request.form.get('like1')
        post.destination1 = request.form.get('destination1')
        post.detail = request.form.get('detail')
        post.sodan1 = request.form.get('sodan1')
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
    count = len(search_posts)
    return render_template('tags.html', search_posts=search_posts, tag=tag,count=count)

@app.route('/knowledges/tags_sex/<sex>')
def search_sex(sex):
    search_sexs = Post.query.filter(Post.sex == sex).all()
    count = len(search_sexs)
    return render_template('tags_sex.html', search_sexs=search_sexs, sex=sex,count=count)

@app.route('/count')
def count_sex():
    counts = {}
    posts = Post.query.all()
    sexs = list(set([Post.sex for Post in posts]))
    for i in sexs:
        search_sexs = Post.query.filter(Post.sex == i).all()
        count = len(search_sexs)
        counts[i]=count
    return render_template('count.html', sexs=sexs,counts=counts)

#すべてのタグの共通数を数え、共通点も表示したい

#due
if __name__ == "__main__":
    app.run(debug=True)