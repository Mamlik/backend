import sqlalchemy.exc
from flask import Blueprint, jsonify, render_template, request, Response
from data import db_session
from data.model import Model
from data.user import User
from flask import Flask, abort, send_from_directory
from sqlalchemy.sql import text
import random
import json

Server = 'localhost'  # api сервер
Port = 8080  # порт регистрации


db_session.global_init("db/data.db")  # подключение к базе данных

users_blueprint = Blueprint(
    'hahaprof_app_api',
    __name__
)


@users_blueprint.route('/api/get_all_models', methods=['GET'])  # функция для получения словаря всех моделей
def get_all_models():
    session = db_session.create_session()
    models = session.query(Model).values(Model.name, Model.id)
    d = {}
    for name, id in models:
        d[name] = id
    return jsonify(d)


@users_blueprint.route('/api/get_model/<int:id>', methods=['GET'])  # получение модели по id
def get_model(id):
    session = db_session.create_session()
    try:
        filename = session.query(Model).filter(Model.id == id).one().file
    except sqlalchemy.exc.NoResultFound:
        return 'Model not found', 400

    print(filename)

    try:
        return send_from_directory(app.config['models_dir'], filename)
    except FileNotFoundError:
        abort(401)


@users_blueprint.route('/register/user', methods=['POST'])  # регистрация пользователя в базу данных
def register_user():
    try:
        session = db_session.create_session()
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_find = session.query(User).filter(User.name == username)
        user_find_2 = session.query(User).filter(User.mail == email)
        if session.query(user_find.exists()).scalar() or session.query(user_find_2.exists()).scalar():
            return json.dumps({'status': 'fail', 'message': 'User or Email already registered'}), 667
        print(username)
        user = User(name=username, mail=email, password=password)
        session.add(user)
        session.commit()
        return json.dumps({'status': 'success', 'message': 'Registered correctly'}), 200
    except TypeError:
        return json.dumps({'status': 'fail', 'message': 'Authorization terminated due to unknown exception'}), 1490


@users_blueprint.route('/login/user', methods=['GET'])  # авторизация пользователя в базу данных
def login_user():
    try:
        session = db_session.create_session()
        password = request.args.get('password')
        email = request.args.get('email')
        if session.query(User).filter(User.mail == email).count() == 0:
            return json.dumps({'status': 'fail', 'message': 'User Not Found'}), 404
        user = session.query(User).filter(User.mail == email).one()
        if password != user.password:
            return json.dumps({'status': 'fail', 'message': 'Incorrect Password '}), 1487
        return json.dumps({'status': 'success', 'message': 'User logined'}), 200
    except TypeError:
        return json.dumps({'status': 'fail', 'message': 'Authorization terminated due to unknown exception'}), 1490


app = Flask(__name__)  # создание flask приложения
app.config['SECRET_KEY'] = 'secret_key'  # ключ для конфигурации
app.config['models_dir'] = '/Users/egorurov/PycharmProjects/backend/models'  # путь для хранения моделей

if __name__ == '__main__':  # запуск api сервера
    app.register_blueprint(users_blueprint)
    app.run(Server, Port)