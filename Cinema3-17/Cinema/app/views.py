import os
import base64

from flask import render_template, redirect, request, url_for, flash, session, jsonify, g
import json

from flask_wtf import file
from sqlalchemy import Integer, or_
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app
from .models import User

from . import db
from flask_login import login_user, logout_user, current_user, login_required

from flask_login import current_user

from .models import Films, FilmSchedule, Order
from .forms import UploadForm, SearchForm, TimeForm, FilmScheduleForm, RegistrationForm, LoginForm
from datetime import datetime,timedelta


# home page
@app.route('/')
def homepage():
    film_info = []
    films = Films.query.all()  # 这种都是对象
    for film in films:
        genre = ''
        for tag in film.Genre.all():
            genre += tag.name + ' '
        afilm = [film.image, film.FilmName, film.Blurb, film.Certificate, film.Director, film.LeadActors,
                 film.FilmLength, genre, film.Ranking, film.FilmID]
        film_info.append(afilm)
    return render_template('index.html', title='homepage', films=film_info)


# 以下 是 web端的 注册 登陆响应
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already Log in')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        flash('Log in Successfully')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


# 以下 是 web端的 注册 登陆响应
@app.route('/logout')
def logout():
    logout_user()
    flash('Log out')
    return redirect(url_for('index'))


# 以下 是 web端的 注册 登陆响应
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Cannot Register, already Log in')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/search_schedule', methods=['GET', 'POST'])
def search_schedule():
    film_info = []
    form = TimeForm()
    if form.validate_on_submit():
        schedules = FilmSchedule.query.filter_by(Date=form.Date.data).all()
        for schedule in schedules:
            afilm = [schedule.film.FilmName, schedule.Room, schedule.Date, schedule.Time, schedule.film.image]
            film_info.append(afilm)
        return render_template('search.html', title='schedules', schedules=film_info, form=form)
    return render_template('search.html', title='search book', form=form)


@app.route('/<id>/<Name>')
def findall(id, Name):
    Filmimage = Films.query.get(id)
    schedules = FilmSchedule.query.filter(FilmSchedule.FID == id).all()
    film_info = []
    for schedule in schedules:
        afilm = [schedule.film.FilmName, schedule.Room, schedule.Date, schedule.Time, schedule.ScheduleID]
        film_info.append(afilm)
    # print(film_info)
    return render_template('ScheduleForEach.html', title='homepage', schedules=film_info, id=id, Name=Name,
                           Film=Filmimage)


@app.route('/delete/<id>')
def delete(id):
    Film = Films.query.get(id)
    db.session.delete(Film)
    db.session.commit()
    return redirect(url_for('homepage'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'static', secure_filename(file.filename))
        file.save(upload_path)

        t = Films(FilmName=form.FilmName.data,
                  Blurb=form.Blurb.data,
                  Certificate=form.Certificate.data,
                  Director=form.Director.data,
                  LeadActors=form.LeadActors.data,
                  FilmLength=form.FilmLength.data,
                  Ranking=form.Ranking.data,
                  image=file.filename)
        # append 添加多对多关系 在第三个表中
        for tag in form.Genre.data:
            t.Genre.append(tag)

        db.session.add(t)
        db.session.commit()
        flash('Upload Sccusss')
        return redirect(url_for('homepage'))

    return render_template('UploadNewFilm.html', title='homepage', form=form)


# 上架时间段
@app.route('/upload1/<id>/<Name>', methods=['GET', 'POST'])
def FilmScheduleArrange(id, Name):
    films = Films.query.get(id)
    form = FilmScheduleForm()
    if request.method == 'POST' and form.validate_on_submit():
        t = FilmSchedule(FID=id,
                         Room=form.Room.data,
                         Date=form.Date.data,
                         Price=form.Price.data,
                         Time=form.Time.data)
        db.session.add(t)
        db.session.commit()
        flash('Upload Sccusss')
        return redirect(url_for('findall', id=id, Name=Name))

    return render_template('ScheduleUpload.html', title='Upload', form=form)


# 下架某一时间段
@app.route('/delete/schedule/<SchedulID>')
def deleteSchedul(SchedulID):
    Schedule = FilmSchedule.query.get(SchedulID)
    db.session.delete(Schedule)
    db.session.commit()
    return redirect(url_for('homepage'))


# 后端返回图片编码，以及全部电影信息
@app.route('/user/home')
def user_home():
    # 用于 储存搜索到的信息，用于后续转换成jason格式
    film_info = []

    films = Films.query.all()
    current_dir = os.path.dirname(__file__)
    print(current_dir)
    for film in films:
        genre = ''
        for tag in film.Genre.all():
            genre += tag.name + ' '
        per_film = {}  # 存放每一步信息
        per_film["FilmID"] = film.FilmID
        per_film["FilmName"] = film.FilmName
        per_film["Blurb"] = film.Blurb
        per_film["Certificate"] = film.Certificate
        per_film["Director"] = film.Director
        per_film["LeadActors"] = film.LeadActors
        per_film["FilmLength"] = film.FilmLength
        per_film["genre"] = genre
        per_film["Ranking"] = film.Ranking
        image = base64.b64encode(open(current_dir + '/static/' + film.image, 'rb').read())
        image = str(image, encoding='utf-8')
        per_film["Image"] = image
        film_info.append(per_film)

    return jsonify({'All_info': film_info})


# 获取 某电影的所有场次
@app.route('/user_schedule', methods=['GET', 'POST'])
def user_schedule():
    # 用于 储存搜索到的信息，用于后续转换成jason格式
    schedul_info = []

    schedules = FilmSchedule.query.filter_by(FID=request.form['filmid']).all()
    print(schedules)
    current_dir = os.path.dirname(__file__)

    for schedule in schedules:
        per_film = {}  # 存放每一步信息
        per_film["ID"] = schedule.ScheduleID
        per_film["Room"] = schedule.Room
        per_film["Date"] = schedule.Date
        per_film["Time"] = schedule.Time
        per_film["Price"] = schedule.Price
        # per_film["Booked_seats"] = schedule.Seat
        schedul_info.append(per_film)

    return jsonify({'all_schedul_info': schedul_info})


# 用户使用的服务
@app.route('/app_register1', methods=['POST'])
def reg():
    # form  = RegistrationForm()
    regist_user = User.query.filter_by(username=request.form['username']).all()
    if regist_user.__len__() is not 0:
        return '1'
    new_user = User(username=request.form['username'], password=request.form['password'])
    db.session.add(new_user)
    db.session.commit()
    return '0'


# 安卓端登陆 响应
@app.route('/app/user', methods=['POST'])
def check_user():
    haveregisted = User.query.filter_by(username=request.form['username']).all()
    if haveregisted.__len__() is not 0:  # 判断是否已被注册
        passwordRight = User.query.filter_by(username=request.form['username'], password=request.form['password']).all()
        if passwordRight.__len__() is not 0:
            # 我裂开了傻逼玩意 不能返回int？
            return str(passwordRight[0].UserID)
        else:
            # 密码错误
            return 'M'
    else:
        # 没有账号
        return 'N'

    # form  = RegistrationForm()
    # print("dfafasfasddsfafsda")
    # regist_user = User.query.filter_by(username=request.form['username']).all()
    # if regist_user.__len__() is not 0:
    #   return  '1'


# 安卓端 获取某一场电影 的所有订单中的座位ID
# 前端传回 schedule ID
@app.route('/Get_sold', methods=['GET', 'POST'])
def Get_sold():
    scheduleID = request.form['schedulID']
    all_orders = Order.query.filter_by(SID=scheduleID).all()
    All_seatsID = ''
    for order in all_orders:
        seatid = order.Seat
        All_seatsID = All_seatsID + str(seatid) + ' '
    return All_seatsID


# 上传 订单 到数据库中 #Java 前端需要传回的有 1.用户ID 2.schedule ID 3.当前时间
# 当然 应该在 app中记录一下一共几个订单
# 我是打算一个座位生成一个订单？---->每个座位一个订单（当然这只是对数据库来说）
# 不行，那用户则呢么查看自己的订单呢？--->可以之后在flask 里做手脚
# 基本上完成
@app.route('/order_upload', methods=['POST'])
def upload_order():
    new_order = Order(CustomerID=request.form['UserID'],
                      SID=request.form['schedulID'],
                      Seat=request.form['SeatID'],
                      DealTime=request.form['CurrentTime']
                      )
    db.session.add(new_order)
    db.session.commit()
    return 'S'


# 用户查询自己的订单
@app.route('/check_order', methods=['GET', 'POST'])
def check_order():
    UID = request.form['UserID']
    all_own_order = Order.query.filter_by(CustomerID=UID).all()
    # 这个订单该怎么返回呢？ json？嗯 应该可以
    order_info = []
    for order in all_own_order:
        per_order = {}  # 存放每一步信息
        per_order["OrderID"] = order.OrderID
        per_order["ScheduleID"] = order.SID
        per_order["SeatID"] = order.Seat  # 这个座位ID 有问题 mmp不能这样弄
        per_order["CurrentTime"] = order.DealTime
        order_info.append(per_order)

    return jsonify({'own_order_info': order_info})

    return '1'


@app.route('/monthincome/', methods=['GET', 'POST'])
def monthincome():

    if request.method == 'POST':
        startdate = request.form.get('startdate')
        date_format = '%Y-%m-%d'

        try:
            startdate = datetime.strptime(startdate, date_format)
        except Exception:
            startdate = datetime.now().strftime(date_format)
            startdate = datetime.strptime(startdate, date_format)
        
        startdate = startdate - timedelta(days=startdate.weekday())
        enddate = startdate + timedelta(weeks=1)

        startdate = startdate.strftime(date_format)
        enddate = enddate.strftime(date_format)

        sql = "select films.FilmID,films.FilmName, IFNULL(A.Sum, 0) as Sum from films " \
                "left join ( " \
                "select schedules.FID,sum(schedules.Price) as Sum from orders " \
                "left join schedules on orders.SID = schedules.ScheduleID " \
                "where orders.DealTime >= '{}' " \
                "and orders.DealTime <= '{}' " \
                "group by schedules.FID) as A on films.FilmID = A.FID;".format(startdate, enddate)

        try:
            query = db.session.execute(sql)
            rows = query.fetchall()
        except Exception:
            rows = []

        rows = [dict(row) for row in rows]

        return jsonify({
            'startdate': startdate,
            'enddate': enddate,
            'rows': rows
        })
    return render_template("monthincome.html")


@app.route('/income/', methods=['GET', 'POST'])
def income():
    if request.method == 'POST':
        begin = request.form.get("begin")
        end = request.form.get("end")
        date_format = '%Y-%m-%d'

        if not end:
            end = datetime.now().strftime(date_format)

        end = datetime.strptime(end, date_format)

        if not begin:
            begin = end - timedelta(days=6)
        else:
            begin = datetime.strptime(begin, date_format)

        datelist = []

        while begin <= end:
            time_str = datetime.strftime(begin, date_format)
            datelist.append(time_str)
            begin = begin + timedelta(days=1)

        selectedIds = request.form.getlist('selectedIds[]')

        movies_sql = "select films.FilmID,films.FilmName from films where films.FilmID in ({})".format(','.join(selectedIds))
        movie_rows = db.session.execute(movies_sql).fetchall()

        data = []
        for movie_row in movie_rows:
            movie = dict(movie_row)
            movie_data = []
            for date in datelist:
                begin_str = '{} 00:00:00'.format(date)
                end_str = '{} 23:59:59'.format(date)
                income_sql = "select sum(schedules.Price) as Sum from orders " \
                "left join schedules on orders.SID = schedules.ScheduleID " \
                "where orders.DealTime >= '{}' " \
                "and orders.DealTime <= '{}' " \
                "and schedules.FID = {} ".format(begin_str, end_str, movie.get('FilmID'))
                income_query = db.session.execute(income_sql).fetchone()
                income = income_query[0]
                if not income:
                    income = 0
                movie_data.append(income)

            total_income = sum(movie_data)
            
            movie_data.append(total_income)

            movie.update([('data', movie_data)])

            data.append(movie)

        currentYear = datetime.now().year

        datelist = [date.replace('{}-'.format(currentYear), '') for date in datelist]

        if len(datelist) > 0:
            datelist.append('total')

        return jsonify({
            'begin': begin,
            'end': end,
            'datelist': datelist,
            'movies': data
        })

    if request.method == 'GET':
        movies_sql = "select films.FilmID,films.FilmName from films"
        movie_rows = db.session.execute(movies_sql).fetchall()
        return render_template("income.html", movies=movie_rows)
 