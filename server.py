import json
from hashlib import md5

from flask import Flask, jsonify, request, session
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Ad, Session, User
from schema import CreateAd, CreateUser, UpdateAd, UpdateUser

app = Flask("app")
app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["JSON_AS_ASCII"] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'


@app.route("/")
def default():
    result = "\u20AC"
    return jsonify(result=result), 200, {"Content-Type": "text/css; charset=utf-8"}


class HttpError(Exception):
    def __init__(self, status_code: int, message: dict | str | list):
        self.status_code = status_code
        self.message = message


def validate(json_data, schema):
    try:
        model = schema(**json_data)
        return model.dict(exclude_none=True)
    except ValidationError as err:
        error_message = json.loads(err.json())
        raise HttpError(400, error_message)


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    http_response = jsonify({"status": "error", "message": er.message})
    http_response.status_code = er.status_code
    return http_response


SALT = "3hiu42r3mi23ij4lk342lnl324*!@##@"


def hash_password(password: str):
    password = f"{SALT}{password}"
    password = password.encode()
    password = md5(password).hexdigest()
    return password


def get_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, "User not found")
    return user


class UserView(MethodView):
    def get(self, users_id):
        with Session() as ses:
            user = get_user(users_id, ses)
            return jsonify({"id": user.id, "name": user.name})

    def post(self):
        json_data = validate(request.json, CreateUser)
        json_data["password"] = hash_password(json_data["password"])
        with Session() as ses:
            new_user = User(**json_data)
            ses.add(new_user)
            try:
                ses.commit()
            except IntegrityError:
                raise HttpError(408, "User already exists")
            return jsonify({"id": new_user.id})
        pass

    def patch(self, users_id):
        json_data = validate(request.json, UpdateUser)
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        with Session() as ses:
            user = get_user(users_id, ses)
            for key, value in json_data.items():
                setattr(user, key, value)
            ses.add(user)
            try:
                ses.commit()
            except IntegrityError:
                raise HttpError(408, "User already exists")
            return jsonify({"status": "success"})

    def delete(self, users_id):
        with Session() as ses:
            user = get_user(users_id, ses)
            ses.delete(user)
            ses.commit()
            return jsonify({"status": "success"})


def get_ad(ads_id: int, session: Session):
    user = session.get(Ad, ads_id)
    if user is None:
        raise HttpError(404, "Ad not found")
    return user


class AdsView(MethodView):
    def get(self, ads_id):
        with Session() as ses:
            ad = get_ad(ads_id, ses)
            return jsonify(
                {
                    "id": ad.id,
                    "headline": ad.headline,
                    "description": ad.description,
                    "owner": ad.owner_id,
                }
            )

    def post(self):
        if "user_id" not in session:
            return jsonify({"message": "Authorization required"}), 401

        current_user_id = session["user_id"]
        json_data = validate(request.json, CreateAd)
        with Session() as ses:
            user = ses.query(User).filter_by(id=current_user_id).first()
            if not user:
                return jsonify({"message": "User not found"}), 404
            new_ad = Ad(
                headline=json_data["headline"],
                description=json_data["description"],
                owner_id=current_user_id,
            )
            ses.add(new_ad)
            try:
                ses.commit()
            except IntegrityError:
                return jsonify({"message": "Error creating ad"}), 500
            return jsonify({"id": new_ad.id})

    def patch(self, ads_id):
        if "user_id" not in session:
            return jsonify({"message": "Authorization required"}), 401

        current_user_id = session["user_id"]
        json_data = validate(request.json, UpdateAd)
        with Session() as ses:
            ad = ses.query(Ad).filter_by(id=ads_id).first()
            if not ad:
                return jsonify({"message": "Ad not found"}), 404
            if ad.owner_id != current_user_id:
                return (
                    jsonify({"message": "You don't have permissions to editing"}),
                    403,
                )
            for key, value in json_data.items():
                setattr(ad, key, value)
            ses.commit()
            return jsonify({"status": "success"})

    def delete(self, ads_id):
        if "user_id" not in session:
            return jsonify({"message": "Authorization required"}), 401

        current_user_id = session["user_id"]
        with Session() as ses:
            ad = ses.query(Ad).filter_by(id=ads_id).first()
            if not ad:
                return jsonify({"message": "Ad not found"}), 404
            if ad.owner_id != current_user_id:
                return jsonify({"message": "You don't have permissions to delete"}), 403
            ses.delete(ad)
            ses.commit()
            return jsonify({"status": "success"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    with (Session() as ses):
        user = ses.query(User).filter_by(name=username).first()
        if not user:
            return jsonify({"message": "Пользователь не найден"}
                           ), 401, {'Content-Type': 'application/json; charset=utf-8'}

        if user.password == hash_password(password):
            session["user_id"] = user.id
            return jsonify({"message": "Аутентификация успешна"}
                           ), 200, {'Content-Type': 'application/json; charset=utf-8'}

        else:
            return jsonify({"message": "Неправильный пароль"}
                           ), 401, {'Content-Type': 'application/json; charset=utf-8'}


users_view = UserView.as_view("users")
app.add_url_rule("/users/", view_func=users_view, methods=["POST"])
app.add_url_rule(
    "/users/<int:users_id>", view_func=users_view, methods=["GET", "PATCH", "DELETE"]
)

ads_view = AdsView.as_view("ads")
app.add_url_rule("/ads/", view_func=ads_view, methods=["POST"])
app.add_url_rule(
    "/ads/<int:ads_id>", view_func=ads_view, methods=["GET", "PATCH", "DELETE"]
)

if __name__ == "__main__":
    app.run()
