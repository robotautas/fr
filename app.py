# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import recognize
import os
from shutil import copyfile


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


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    """
    Ištrina failus iš static/unknown.Pasiima vartotojo pateiktą nuotrauką, praleidžia per atpažinimo funkciją compare().
    Jeigu nuotrauka tinka algoritmui, sugereruoja atsakymą ir atiduoda į render template parametrus.
    Jeigu ne - siunčia pranešimą, kad nepavyko.
    """
    try:
        if request.method == 'POST':

            filelist = [f for f in os.listdir('./static/unknown')]
            for f in filelist:
                os.remove(os.path.join('./static/unknown', f))

            unknown = request.files['unknown']
            unknown.save(f'./static/unknown/{unknown.filename}')
            filename = unknown.filename
            answer = recognize.compare(unknown=unknown)

            return render_template('result.html', answer=answer, image=filename, unrec='Unrecognized Person')

    except IndexError:
        flash("Algorithm couldn't properly encode a face in your image:(")
        return redirect(url_for('index'))


@app.route('/static/unknown/<filename>', methods=['GET', 'POST'])
def get_unknown(filename):
    folder = os.path.join(APP_ROOT, 'static', 'unknown')
    return send_from_directory(folder, filename)


@app.route('/data', methods=['GET', 'POST'])
def show_data():

    """
    praleidžia nuotrauką per filtrą, ir prideda į duomenų bazę. Jei nepraeina filtro - siunčia pranešimą, kad netinka.
    taip pat nuskaito visus duomenis iš DB ir prideda į render parametrus, iš kurių paskui jau su jinja2 formuojama
    manage data skiltis.
    """

    if request.method == 'POST':
            image = request.files['known']
            image.save(f'./static/known/{image.filename}')
            if recognize.validate(image):
                label = request.form['label']
                data = Known(image_file=image.filename, label=label)
                db.session.add(data)
                db.session.commit()
            else:
                os.remove(f'./static/known/{image.filename}')
                flash("Image didn't pass validation filter.")

    known = Known.query.all()
    return render_template('data.html', instance=known)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/static/known/<filename>')
def get_known(filename):
    """
    Funkcija skirta nuskaityti failus iš nurodyto katalogo
    """

    folder = os.path.join(APP_ROOT, 'static', 'known')
    return send_from_directory(folder, filename)


@app.route('/static/known/<filename>', methods=['POST'])
def delete(filename):
    """
    Funkcija paleidžiama iš 'remove' mygtukų manage data skiltyje.
    """
    data = Known.query.filter_by(image_file=filename).first()
    db.session.delete(data)
    db.session.commit()
    os.remove(f'./static/known/{filename}')
    return redirect(url_for('show_data'))


@app.route('/<filename>', methods=['GET', 'POST'])
def add_unrecognized(filename):

    """
    Jeigu nuotrauka nuskaityta, bet neatpažinta, home skiltyje atsiranda galimybė pridėti neatpažintą veidą į DB
    Ši funkcija pririšta prie atsirandančios html formos.
    """

    if request.method == 'POST':
        copyfile(f'./static/unknown/{filename}', f'./static/known/{filename}')
        label = request.form['add_unrecognized']
        data = Known(image_file=filename, label=label)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
