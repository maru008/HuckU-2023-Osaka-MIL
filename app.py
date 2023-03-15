from datetime import datetime,date
from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,or_,func
from collections import Counter
from calendar import isleap

#　＊【変更点】＊
#プロフから、like1に対応していた欄を削除した
#出身地を都道府県の選択肢から選ばせるようにした
#行きたい場所ランキングを作成

#knowledges.html は使わないので、アクセス用のボタンを消した
#今日が誕生日かどうかの判定方法が、年月日参照だったが、月日だけで判断するようになった

#2/29生まれの人は、うるう年でないとき、3/1を誕生日扱いするように
#同じ出身地の人を、タグクリックで検索する機能追加

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

    #like1 = db.Column(db.String(100))

    destination1 = db.Column(db.String(100))
    detail = db.Column(db.String(500))
    sodan1 = db.Column(db.String(500))
    birthday = db.Column(db.DateTime)

    birthday_md = db.Column(db.String(50))

    age = db.Column(db.Integer)


@app.route('/', methods=['GET', 'POST'])
def index():
    #データベースからすべての投稿を取り出し、それをトップページに渡してあげる
    if request.method == 'GET':
        #年上順に並べ替える
        posts = Post.query.order_by(Post.birthday).all()
        today=date.today()
        md=today.strftime('%m-%d')
        year = today.strftime('%Y')
        year=int(year)
        uru=isleap(year)
        return render_template('index.html', posts=posts, md=md,year=year,
                               uru=uru
                               )
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
        #like1 = request.form.get('like1')
        destination1 = request.form.get('destination1')
        detail = request.form.get('detail')
        sodan1 = request.form.get('sodan1')
        birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d')
        birthday_md = birthday.strftime('%m-%d')
        #birthday_m= datetime.strptime(request.form.get('birthday'), '%m')
        #birthday_d= datetime.strptime(request.form.get('birthday'), '%d')

        age = (int(today.strftime("%Y%m%d")) - int(birthday.strftime("%Y%m%d"))) // 10000

        new_post = Post(name=name, sex=sex,syussinti=syussinti,
                        hobby1=hobby1,hobby2=hobby2,
                        hobby3=hobby3,hobby4=hobby4,hobby5=hobby5,
                        tokui1=tokui1,
                        destination1=destination1,
                        detail=detail, sodan1=sodan1,birthday=birthday, 
                        birthday_md=birthday_md,
                        age=age)
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

#destinationランキング
@app.route('/ranking_destination')
def r_d():
    posts = Post.query.all()
    #プロフ登録者すべてのdestinationを集める
    tags = []
    for i in posts:
        tags.append(i.destination1)

    frequency = Counter(tags)
    frequency = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    frequency = [x for x in frequency if x[0] != '']
    return render_template('ranking_destination.html', frequency=frequency, posts=posts,tags=tags)

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
    today=date.today()
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

        same_count = len(set(tags)&set(tags_id))
        for j in tags_id:
            if j == "":
                same_count-=1
                break
    
        if same_count<0:
            same_count=0
        same_counts[i]=same_count
    
    sames = []
    same_counts = sorted(same_counts.items(), key=lambda x:x[1], reverse=True)
    #same_counts=sames

    for i in range(len(same_counts)):
        sames.append(same_counts[i][0])
    
    return render_template('same.html', post_id=post_id, posts=posts,tags_id=tags_id,
                           sames=sames,same_counts=same_counts,id=id,today=today)

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
        #post.like1 = request.form.get('like1')
        post.destination1 = request.form.get('destination1')
        post.detail = request.form.get('detail')
        post.sodan1 = request.form.get('sodan1')
        #today=date.today()
        #post.birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d')
        #post.age = (int(today.strftime("%Y%m%d")) - int(post.birthday.strftime("%Y%m%d"))) // 10000
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

@app.route('/knowledges/tags_syussinti/<syussinti>')
def search_syussinti(syussinti):
    search_syussinti = Post.query.filter(Post.syussinti == syussinti).all()
    count = len(search_syussinti)
    return render_template('tags_syussinti.html', search_syussinti=search_syussinti,count=count,syussinti=syussinti)
"""
@app.route('/count')
def count():
    counts_sex = {}
    posts = Post.query.all()
    sexs = list(set([Post.sex for Post in posts]))
    for i in sexs:
        search_sexs = Post.query.filter(Post.sex == i).all()
        count = len(search_sexs)
        counts_sex[i]=count

    counts_syussinti = {}
    syussintis = list(set([Post.syussinti for Post in posts]))
    for i in syussintis:
        search_syussintis = Post.query.filter(Post.syussinti == i).all()
        count = len(search_syussintis)
        counts_syussinti[i]=count
    return render_template('count.html', sexs=sexs,counts_sex=counts_sex,
                           syussintis=syussintis,counts_syussinti=counts_syussinti)

"""
@app.route('/count')
def count_ss():
    posts = Post.query.all()
    tags_sex = []
    tags_syu = []
    for i in posts:
        tags_sex.append(i.sex)
        tags_syu.append(i.syussinti)

    frequency_sex = Counter(tags_sex)
    frequency_sex = sorted(frequency_sex.items(), key=lambda x:x[1], reverse=True)
    frequency_sex = [x for x in frequency_sex if x[0] != '']

    frequency_syu = Counter(tags_syu)
    frequency_syu = sorted(frequency_syu.items(), key=lambda x:x[1], reverse=True)
    frequency_syu = [x for x in frequency_syu if x[0] != '']
    return render_template('count.html', frequency_sex=frequency_sex, posts=posts,tags_sex=tags_sex,
                           frequency_syu=frequency_syu,tags_syu=tags_syu)

@app.route('/nearbirthday')
def nearbirthday():
    posts = Post.query.all()
    today=date.today()
    nears = {}
    for i in posts:
        birthday=i.birthday.date()
        y = today.strftime('%Y')
        y=int(y)
        uru=isleap(y)
        if birthday.strftime('%m-%d')=='02-29' and uru==False:
            birthday=birthday.replace(month=3,day=1)
        #birthday_md = birthday.strftime('%m-%d')
        birthday=birthday.replace(year=y)
        t=today.timetuple().tm_yday
        b=birthday.timetuple().tm_yday
        near=b-t

        #near = (int(today.strftime('%Y%m%d')) - int(birthday.strftime("%m%d")))
        #age = (int(today.strftime("%Y%m%d")) - int(birthday.strftime("%Y%m%d"))) // 10000
        #md=today.strftime('%m-%d')
        nears[i]=near
    nears = sorted(nears.items(), key=lambda x:x[1], reverse=False)
    for n in nears:
        if n[1]<0:
            nears.append(nears.pop(0))
    
    return render_template('nearbirthday.html', posts=posts,today=today,nears=nears)
    


#すべてのタグの共通数を数え、共通点も表示したい

#due
if __name__ == "__main__":
    app.run(debug=True)