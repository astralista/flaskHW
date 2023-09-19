from hashlib import md5

from flask import Flask
from flask import jsonify
from flask import request
from flask.views import MethodView

from models import Ad, Session

app = Flask("app")
SALT = '3hiu42r3mi23ij4lk342lnl324*!@##@'


def hash_password(password: str):
    password = f'{SALT}{password}'
    password = password.encode()
    password = md5(password).hexdigest()
    return password


class AdsView(MethodView):
    def get(self, ad_id):
        pass

    def post(self):
        json_data = request.json
        with Session() as session:
            new_ad = Ad(**json_data)
            session.add(new_ad)
            session.commit()
            return jsonify({
                'id': new_ad.id
            })
        pass

    def patch(self, ad_id):
        pass

    def delete(self, ad_id):
        pass


ads_view = AdsView.as_view("ads")
app.add_url_rule("/ads/", view_func=ads_view, methods=["POST"])
app.add_url_rule(
    "/ads/<int:ad_id>", view_func=ads_view, methods=["GET", "PATCH", "DELETE"]
)

if __name__ == "__main__":
    app.run()
