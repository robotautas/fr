# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import recognize
import os


app = Flask(__name__, static_url_path='/static', static_folder='static')
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

app.secret_key = b'supersecret'


# Sugeneruoja pažįstamų nuotraukų duomenų bazę, kurioje yra relative path iki nuotraukos ir vardas pavardė.

class Known(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(100), unique=True, nullable=False)
    path = db.Column(db.String(100), unique=True, nullable=True)

    def __init__(self, image_file, label):
        self.image_file = image_file
        self.label = label

    def __repr__(self):
        return self.label

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/result', methods=['POST'])
def result():
    '''
    Ištrina failus iš static.
    Pasiima vartotojo pateiktą nuotrauką, praleidžia per atpažinimo funkciją compare().
    '''
    try:
        if request.method == 'POST':

            # filelist = [f for f in os.listdir('./static/unknown')]
            # for f in filelist:
            #     os.remove(os.path.join('./static/unknown', f))

            unknown = request.files['unknown']
            unknown.save(f'./static/unknown/{unknown.filename}')
            filename = unknown.filename
            answer = recognize.compare(unknown=unknown)
            # answer = 'nesvarbu'
            print(filename)
            return render_template('result.html', answer=answer, image=filename)
    except IndexError:
        flash('Something went wrong :(')
        return redirect(url_for('index'))

@app.route('/static/unknown/<filename>')
def get_unknown(filename):
    folder = os.path.join(APP_ROOT, 'static', 'unknown')
    return send_from_directory(folder, filename)


@app.route('/data', methods=['GET', 'POST'])
def show_data():

    if request.method == 'POST':
        image = request.files['known']
        image.save(f'./static/known/{image.filename}')
        label = request.form['label']
        data = Known(image_file=image.filename, label=label)
        db.session.add(data)
        db.session.commit()

    known = Known.query.all()
    return render_template('data.html', instance=known)


@app.route('/about')
def about():

    return render_template('about.html')


@app.route('/static/known/<filename>')
def get_known(filename):
    folder = os.path.join(APP_ROOT, 'static', 'known')
    return send_from_directory(folder, filename)


@app.route('/static/known/<filename>', methods=['POST'])
def delete(filename):
    data = Known.query.filter_by(image_file=filename).first()
    print(data.id)
    db.session.delete(data)
    db.session.commit()
    os.remove(f'./static/known/{filename}')
    return redirect(url_for('show_data'))



if __name__=='__main__':
    # sys.setdefaultencoding('utf-8')
    app.debug = True
    app.run()
