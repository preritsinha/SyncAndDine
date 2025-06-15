from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('main/index.html', title='Welcome to SyncAndDine')

@main.route('/home')
@login_required
def home():
    return render_template('main/home.html', title='Home')