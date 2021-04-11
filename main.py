import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, Response, jsonify, render_template, session, redirect
import os
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Data/WorkTracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = "arf1q3df!sa2@"

'''
err1 -> admin/month -> no data found for precise date
err2 -> / -> dashboard -> if data of selected month and year not found
err3 -> admin/specificmonth -> invalid year
'''


class Admin(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(200), nullable=False)
    upassword = db.Column(db.String(200), nullable=False)
    token = 'MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJBRW/kfl5hv0bAjUkvP0UxV0HLqk8yrx9RkWHH74dvcX72TCFAlCubTjphQiboZdMK+XEZikdmhTCbsO1co630CAwEAAQ=='

    def __repr__(self):
        return '<User %r>' % self.uname


class Timer(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    pc = db.Column(db.String(10), nullable=True)
    seconds = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Timer PC:{0} Day:{1} >'.format(self.pc, self.day)


def getDataByMonth():
    mTimer = db.session.query(Timer).all()
    if len(mTimer) != 0:
        date = datetime.datetime.now()
        month_name = '{0} {1}'.format(date.strftime('%b'), date.strftime('%Y'))
        month = date.strftime('%x').split('/')[0]
        year = date.strftime('%x').split('/')[2]
        monthArr = []
        pcArr = []
        for time in mTimer:
            splittedMonth = time.day.split('/')[0]
            splittedYear = time.day.split('/')[2]
            if splittedMonth == month and splittedYear == year:
                pcArr.append(time.pc)
                monthArr.append(time)
        pcs = set(pcArr)
        pcs = list(pcs)
        data = []
        for pc in pcs:
            pcSET = {}
            temp = []
            pc_data = {
                'minutes': 0,
                'hours': 0,
                'seconds': 0,
            }
            for time in monthArr:
                if time.pc == pc:
                    if pc_data['seconds'] + int(time.seconds) > 59:
                        pc_data['minutes'] += 1 + int(time.minutes)
                        pc_data['seconds'] += int(time.seconds)
                        pc_data['seconds'] = pc_data['seconds'] % 60
                    else:
                        pc_data['seconds'] += int(time.seconds)
                        pc_data['minutes'] += int(time.minutes)
                    if pc_data['minutes'] > 60:
                        pc_data['hours'] += 1 + int(time.hours)
                        pc_data['minutes'] = pc_data['minutes'] % 60
                    else:
                        pc_data['hours'] += int(time.hours)
            pc_data['pc'] = pc
            data.append(dict(pc_data))
        return dict({'list': data, 'mm': month_name})
    else:
        return dict({'list': [], 'mm': 'error'})


def getDataBySpecificMonth(month, year):
    mTimer = db.session.query(Timer).all()
    if len(mTimer) != 0:
        date = datetime.datetime(year, month, 1)
        month_name = '{0} {1}'.format(date.strftime('%b'), date.strftime('%Y'))
        month = date.strftime('%x').split('/')[0]
        year = date.strftime('%x').split('/')[2]
        monthArr = []
        pcArr = []
        for time in mTimer:
            splittedMonth = time.day.split('/')[0]
            splittedYear = time.day.split('/')[2]
            if splittedMonth == month and splittedYear == year:
                pcArr.append(time.pc)
                monthArr.append(time)
        pcs = set(pcArr)
        pcs = list(pcs)
        data = []
        for pc in pcs:
            pcSET = {}
            temp = []
            pc_data = {
                'minutes': 0,
                'hours': 0,
                'seconds': 0,
            }
            for time in monthArr:
                if time.pc == pc:
                    if pc_data['seconds'] + int(time.seconds) > 59:
                        pc_data['minutes'] += 1 + int(time.minutes)
                        pc_data['seconds'] += int(time.seconds)
                        pc_data['seconds'] = pc_data['seconds'] % 60
                    else:
                        pc_data['seconds'] += int(time.seconds)
                        pc_data['minutes'] += int(time.minutes)
                    if pc_data['minutes'] > 60:
                        pc_data['hours'] += 1 + int(time.hours)
                        pc_data['minutes'] = pc_data['minutes'] % 60
                    else:
                        pc_data['hours'] += int(time.hours)
            pc_data['pc'] = pc
            data.append(dict(pc_data))
            print('here', data)
        return dict({'list': data, 'mm': month_name})
    else:
        pass


@app.route("/user/settime", methods=['Post'])
def setup():
    data = request.get_json()
    print(data)
    if data == None:
        return jsonify({'message': 'Invalid request.'}), 400
    if 'seconds' not in data or 'minutes' not in data or 'hours' not in data or 'pc' not in data or 'day' not in data:
        return jsonify({'message': 'Invalid request.'}), 400
    else:
        exist = Timer.query.filter_by(day=data['day'], pc=data['pc']).first()
        if exist == None:
            mTimer = Timer(pc=data['pc'], seconds=data['seconds'],
                           minutes=data['minutes'], hours=data['hours'], day=data['day'])
            db.session.add(mTimer)
            db.session.commit()
            return jsonify({'message': 'Time Added Successfully'}), 200
        else:
            exist.seconds = data['seconds']
            exist.minutes = data['minutes']
            exist.hours = data['hours']
            db.session.commit()
            return jsonify({'message': 'Time Updated Successfully'}), 200


@app.route("/admin/specificmonth", methods=['POST'])
def smonth():
    if session['loginSuccess']:
        if request.method == "POST":
            data = request.form
            if 'month' not in data and 'year' not in data:
                return redirect('/')
            if len(data['year']) != 4:
                return redirect('/?err3=True')
            print(int(data['month']), int(data['year']))
            temp = dict(getDataBySpecificMonth(int(data['month']), int(data['year'])))
            if len(temp['list']) == 0:
                return redirect('/?err2=True')
            else:
                return render_template('byMonth.html', data=temp['list'], mm=temp['mm'])
    else:
        return redirect('/')


@app.route("/", methods=['Get'])
def done():
    if session['loginSuccess']:
        data = dict(getDataByMonth())
        err1 = request.args.get('err1')
        err2 = request.args.get('err2')
        err3 = request.args.get('err3')
        err4 = request.args.get('err4')
        if session['errorDisplayed']:
            session['errorDisplayed'] = False
            return redirect('/')
        if err1 and session['errorDisplayed'] != True:
            session['errorDisplayed'] = True
            return render_template('dashboard.html', data=data['list'], mm=data['mm'], error="Record of selected date have not been found!")
        if err2 and session['errorDisplayed'] != True:
            session['errorDisplayed'] = True
            return render_template('dashboard.html', data=data['list'], mm=data['mm'], error="Records of selected Month have not been found!")
        if err3 and session['errorDisplayed'] != True:
            session['errorDisplayed'] = True
            return render_template('dashboard.html', data=data['list'], mm=data['mm'], error="Enter valid year!")
        return render_template('dashboard.html', data=data['list'], mm=data['mm'])
    else:
        return redirect('/admin/login')


@app.route("/user/getTime", methods=['Post'])
def getTime():
    data = request.get_json()
    print(data)
    if data == None:
        return jsonify({'message': 'Invalid request.'}), 400
    if 'pc' not in data:
        return jsonify({'message': 'Invalid request.'}), 400
    x = datetime.datetime.now()
    timer = Timer.query.filter_by(pc=data['pc'], day=x.strftime('%x')).first()
    print(timer)
    if timer == None:
        return jsonify({'seconds': 0, 'minutes': 0, 'hours': 0, 'day': x.strftime("%x")}), 200
    return jsonify({'seconds': timer.seconds, 'minutes': timer.minutes, 'hours': timer.hours, 'day': timer.day}), 200


@app.route("/admin/getall", methods=['Get'])
def getAll():
    # to get from mAdmin => mAdmin.keyname such as mAdmin.password
    mAdmin = db.session.query(Timer).all()
    pcs = []
    for admin in mAdmin:
        pcs.append(admin.pc)
    pcs = set(pcs)
    pcs = list(pcs)
    data = []
    for pc in pcs:
        pcSET = {}
        temp = []
        for time in mAdmin:
            if time.pc == pc:
                pc_data = {}
                pc_data['seconds'] = time.seconds
                pc_data['minutes'] = time.minutes
                pc_data['hours'] = time.hours
                pc_data['day'] = time.day
                temp.append(pc_data)
            pcSET = {pc: temp}
        data.append(dict(pcSET))
    return jsonify({'data': data}), 200


@app.route("/admin/month", methods=['Post', 'Get'])
def getbyMonth():
    if session['loginSuccess']:
        if request.method == "GET":
            data = getDataByMonth()
            return redirect('/')
    if request.method == 'POST':
        if session['loginSuccess']:
            data = request.form
            if data['date'] != '':
                arr = data['date'].split('-')
                date = datetime.datetime(int(arr[0]), int(arr[1]), int(arr[2]))
                mTimer = Timer.query.filter_by(
                    day=date.strftime('%x')).all()
                if len(mTimer) == 0:
                    data = dict(getDataByMonth())
                    return redirect('/?err1=true')
                x = '{0} {1} {2}'.format(date.strftime(
                    '%b'), date.strftime('%d'), date.strftime('%Y'))
                return render_template('detail.html', data=mTimer, date=x)
        else:
            return redirect('/')


@app.route("/admin/login", methods=['Post', 'Get'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    # to get data from request body syntax => data['key']
    data = request.form
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid request.'}), 400
    else:
        # to get from mAdmin => mAdmin.keyname such as mAdmin.password
        mAdmin = Admin.query.filter_by(uname=data['username']).first()
        if mAdmin != None:
            if(data['password'] == mAdmin.upassword):
                data = getDataByMonth()
                session['loginSuccess'] = True
                session['errorDisplayed'] = False
                return redirect("/")
            else:
                return render_template('index.html', error="Invalid Credentials")
        else:
            return render_template('index.html', error="No User Exists!")


@app.route("/admin/logout", methods=['Post'])
def logout():
    print(session['loginSuccess'])
    session['loginSuccess'] = False
    return redirect('/')


@app.route("/admin/register", methods=['Post'])
def register():
    # to get data from request body syntax => data['key']
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid request.'}), 400
    else:
        mAdmin = Admin(uname=data['username'], upassword=data['password'])
        db.session.add(mAdmin)
        db.session.commit()
        return jsonify({'message': 'Successfully Registered'}), 200


if __name__ == "__main__":
    if not os.path.isdir('Data'):
        absPath = os.path.join(os.getcwd(), 'Data')
        os.mkdir(absPath)
        if not os.path.isfile('./Data/WorkTracker.db'):
            db.create_all()
    app.run(debug=True)
