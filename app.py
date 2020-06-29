import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
        

class TinyWebDB(db.Model):
    __tablename__ = 'tinywebdb'
    tag = db.Column(db.String, primary_key=True, nullable=False)
    value = db.Column(db.String, nullable=False)


db.create_all()
db.session.commit()

@app.route('/')
def main_method():
    return 'QuikDB is working'

@app.route('/store', methods=['POST'])
def store_a_value():
    tag = request.form['tag']
    value = request.form['value']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if tag:
        if tag == 'dbpass':
            return return_error('Not possible to do any action to password record.')
        else:
            # --------------------
            if getpassword:
                password = request.form['pass']
                if password != getpassword.value:
                    return return_error('Incorrect password.')
            # --------------------
            existing_tag = TinyWebDB.query.filter_by(tag=tag).first()
            if existing_tag:
                existing_tag.value = value
                db.session.commit()
            else:
                data = TinyWebDB(tag=tag, value=value)
                db.session.add(data)
                db.session.commit()
        return jsonify(action="STORED", tag=tag, value=value)
    return return_error('Please specify a tag name.')

@app.route('/get', methods=['POST'])
def get_value():
    tag = request.form['tag']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if tag:
        if tag == 'dbpass':
            return return_error('Not possible to do any action to password record!')
        else:
            # --------------------
            if getpassword:
                password = request.form['pass']
                if password != getpassword.value:
                    return return_error('Inccorect password!')
            # --------------------
            value = TinyWebDB.query.filter_by(tag=tag).first().value
            return jsonify(action="GOT", tag=tag, value=value)
    return return_error('Could not find the tag.')

@app.route('/auth/data', methods=['POST'])
def get_data():
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        # --------------------
        password = request.form['pass']
        if password != getpassword.value:
            return return_error('Incorrect password.')
        # --------------------
        tags = TinyWebDB.query.all()
        datalist = []
        for tg in tags:
            if tg.tag != 'dbpass':
                datalist.append([tg.tag, tg.value])
        return jsonify(action="DATA", data=datalist)
    return return_error('Please set a password first.')

@app.route('/getall', methods=['POST'])
def get_all():
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        # --------------------
        password = request.form['pass']
        if password != getpassword.value:
            return return_error('Incorrect password.')
        # --------------------
    tags = TinyWebDB.query.all()
    taglist = []
    for tg in tags:
    	if tg.tag != 'dbpass': 
            taglist.append(tg.tag)
    return jsonify(action="TAGS", tag=taglist)

@app.route('/delete', methods=['POST'])
def delete_entry():
    tag = request.form['tag']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if tag:
        if tag == 'dbpass':
            return return_error('Not possible to do any action to password record!')
        else:
            # --------------------
            if getpassword:
                password = request.form['pass']
                if password != getpassword.value:
                    return return_error('Incorrect password.')
            # --------------------
            deleted = TinyWebDB.query.filter_by(tag=tag).first()
            db.session.delete(deleted)
            db.session.commit()
            return jsonify(action="DELETED", tag=tag)
    return return_error('Could not find the tag.')

@app.route('/format', methods=['POST'])
def delete_all():
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        # --------------------
        password = request.form['pass']
        if password != getpassword.value:
            return return_error('Incorrect password.')
        # --------------------
    try:
        count = db.session.query(TinyWebDB).delete()
        db.session.commit()
        return jsonify(action="FORMATTED", count=count)
    except:
        db.session.rollback()
        return return_error('Something went wrong while performing this action.')

@app.route('/auth/password', methods=['POST'])
def set_key():
    newpassword = request.form['newpass']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if newpassword:
        if getpassword:
            oldpassword = request.form['oldpass']
            if getpassword.value == oldpassword:
                getpassword.value = newpassword
                db.session.commit()
                return jsonify(action="CHANGED PASSWORD", oldpass=oldpassword, newpass=newpassword)
            else:
                return return_error('Incorrect old password.')
        else:
            data = TinyWebDB(tag='dbpass', value=newpassword)
            db.session.add(data)
            db.session.commit()
            return jsonify(action="SET PASSWORD", newpass=newpassword)
    return return_error('Please specify a new password.')

@app.route('/auth/unlock', methods=['POST'])
def remove_key():
    password = request.form['pass']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        if getpassword.value == password:
            deleted = TinyWebDB.query.filter_by(tag='dbpass').first()
            db.session.delete(deleted)
            db.session.commit()
            return jsonify(action="DELETED PASSWORD", password=password)
        else:
        	return return_error('Incorrect password.')
    return return_error('There is no password to delete. Set a password first.')

@app.route('/istrue', methods=['POST'])
def is_true():
    password = request.form['pass']
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        # --------------------
        if password != getpassword.value:
            return jsonify(action="IS CORRECT",result=False)
        # --------------------
    return jsonify(action="IS CORRECT",result=True)
        

@app.route('/count')
def count_all():
    tags = TinyWebDB.query.all()
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    resl = len(tags)
    if getpassword:
    	resl = resl - 1
    return jsonify(action="COUNT", count=resl)

@app.route('/version')
def version():
    return jsonify(action="VERSION", result="1.0")

@app.route('/islocked')
def is_locked():
    getpassword = TinyWebDB.query.filter_by(tag='dbpass').first()
    if getpassword:
        return jsonify(action="IS LOCKED",result=True)
    else:
        return jsonify(action="IS LOCKED",result=False)

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(action="ERROR",result="Method is not allowed."), 405

@app.errorhandler(404)
def not_found(e):
    return jsonify(action="ERROR",result="The requested URL was not found."), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify(action="ERROR",result="Internal server error."), 500

def return_error(message):
    response = jsonify(action="ERROR",result=message)
    response.status_code = 400
    return response
        

if __name__ == '__main__':
    app.run()
