from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.database.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('video.index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error = None

        if not username:
            error = 'El nombre de usuario es requerido.'
        elif not email:
            error = 'El correo electrónico es requerido.'
        elif not password:
            error = 'La contraseña es requerida.'
        elif password != confirm_password:
            error = 'Las contraseñas no coinciden.'
        elif User.get_by_username(username) is not None:
            error = f'El usuario {username} ya está registrado.'
        elif User.get_by_email(email) is not None:
            error = f'El correo {email} ya está registrado.'

        if error is None:
            user = User.create(username, email, password)
            if user:
                login_user(user)
                flash('¡Registro exitoso!', 'success')
                return redirect(url_for('video.index'))
            else:
                error = 'Error al crear el usuario.'

        flash(error, 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('video.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = User.get_by_username(username)

        if user is None:
            error = 'Usuario incorrecto.'
        elif not user.check_password(password):
            error = 'Contraseña incorrecta.'

        if error is None:
            login_user(user)
            next_page = request.args.get('next')
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(next_page or url_for('video.index'))

        flash(error, 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))