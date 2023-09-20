from hashlib import md5
import json

from flask import Flask
from flask import jsonify
from flask import request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Ad, Session, User
from schema import CreateUser, UpdateUser


app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: dict | str | list):
        self.status_code = status_code
        self.message = message


def validate(json_data, schema):
    try:
        model = schema(**json_data)
        return model.dict()
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


class AdsView(MethodView):
    def get(self, users_id):
        pass

    def post(self):
        json_data = validate(request.json, CreateUser)
        json_data["password"] = hash_password(json_data["password"])
        with Session() as session:
            new_user = User(**json_data)
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(408, 'User already exists')
            return jsonify({"id": new_user.id})
        pass

    def patch(self, users_id):
        pass

    def delete(self, users_id):
        pass


ads_view = AdsView.as_view("users")
app.add_url_rule("/users/", view_func=ads_view, methods=["POST"])
app.add_url_rule(
    "/users/<int:ad_id>", view_func=ads_view, methods=["GET", "PATCH", "DELETE"]
)

if __name__ == "__main__":
    app.run()
