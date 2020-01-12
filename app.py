from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text


#
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.id_count = 1
app.users = {}
app.tweets = []
app.follow = []
app.json_encoder = CustomJSONEncoder


@app.route("/ping", methods=['GET'])
def ping():
    return "pong"


"""
@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json
    new_user["id"] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count += 1


    return jsonify(new_user)
"""


@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    if len(tweet) > 300:
        return '300자를 초과했습니다.', 400
    user_id = int(payload['id'])

    app.tweets.append({
        'user_id': user_id,
        'tweet': tweet
    })
    return '', 200


@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다.', 400
    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)
    return jsonify(user)


@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_unfollow = int(payload['unfollow'])
    if user_id not in app.users or user_id_to_unfollow not in app.users:
        return '사용자가 존재하지 않습니다.', 400
    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_unfollow)
    return jsonify(user)


@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]
    return jsonify({
        'user_id': user_id,
        'timeline': timeline
    })


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = app.database.execute(text("""
            INSERT INTO users(name, email, profile, hashed_password) VALUES (
                :name, :email, :profile, :password 
            )
            """), new_user).lastrowid

        row = new_user_id.database.execute(text("""
                SELECT
                id, name, email, profile FROM users WHERE id= :user_id
            """), {
            'user_id': new_user_id
        }).fetchone()

        created_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(created_user)

    return app
