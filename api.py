import json
from datetime import datetime
import logging

from flask import Flask, request, render_template, jsonify
import flask_sqlalchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey-results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_envvar('QASEARCH_SURVEY_SETTINGS')
db = flask_sqlalchemy.SQLAlchemy()
ANSWER_KEYS = ['email', 'correct', 'question_no', 'answer']


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode)

    def __init__(self, email):
        self.email = email

    def __str__(self):
        return '<Participant id={}, email={}>'.format(self.id, self.email)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode)
    correct = db.Column(db.Boolean)
    question_no = db.Column(db.Integer)
    answer = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime)

    def __init__(self, email, correct, question_no, answer, timestamp):
        self.email = email
        self.correct = correct
        self.question_no = question_no
        self.answer = answer
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'email': self.email,
            'correct': self.correct,
            'question_no': self.question_no,
            'answer': self.answer,
            'timestamp': self.timestamp
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    req = request.get_json()
    if 'email' not in req:
        return 'missing key "email"', 400
    email = req['email']
    p = get_participant(email)
    if p is None:
        return '{} has not been registered'.format(email), 401
    message = 'unigram' if p.id % 2 == 0 else 'ngram'
    return message, 200


@app.route('/questions/<int:qa_id>')
def questions(qa_id):
    auth = request.headers.get('Authorization')
    if auth is None:
        return 'Not authorized', 401
    p = get_participant(auth)
    if p is None:
        return 'Not authorized', 401
    # unigram questions to even IDs, ngram questions to odd IDs
    questions_folder = 'unigram-questions' if p.id % 2 == 0 else 'ngram-questions'
    with app.open_resource('static/{}/{}.json'.format(questions_folder, qa_id), 'r') as f:
        contents = json.load(f)
    return json.dumps(contents)


@app.route('/answers', methods=['GET', 'POST'])
def responses():
    if request.method == 'GET':
        auth_token = request.args.get('token')
        if auth_token is None or auth_token != app.config['AUTH_TOKEN']:
            return 'Not authorized', 401
        return get_all_answers()

    req = request.get_json()
    logging.info(req)
    for key in ANSWER_KEYS:
        if key not in req:
            return 'missing key "{}"'.format(key), 400
    email = req['email']
    correct = req['correct']
    question_no = req['question_no']
    answer_str = req['answer']
    timestamp_str = req['timestamp']  # '2017-01-28T17:08:00.485Z'
    timestamp = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    # print(type(email), type(correct), type(question_no), type(answer_str), type(timestamp))
    answer = Answer(email, correct, question_no, answer_str, timestamp)
    db.session.add(answer)
    db.session.commit()
    return 'saved {}th answer'.format(Answer.query.count())


@app.route('/participants', methods=['GET', 'POST', 'DELETE'])
def participants():
    if request.method == 'GET':
        auth_token = request.args.get('token')
        if auth_token is None or auth_token != app.config['AUTH_TOKEN']:
            return 'Not authorized', 401
        all_participants = Participant.query.all()
        return jsonify([str(p) for p in all_participants])

    elif request.method == 'POST':
        req = request.get_json()
        email = req['email']
        p = Participant(email)
        db.session.add(p)
        db.session.commit()
        return 'saved {}th participant'.format(Participant.query.count())

    elif request.method == 'DELETE':
        req = request.get_json()
        email = req['email']
        p = Participant.query.filter_by(email=email).first()
        db.session.delete(p)
        db.session.commit()


def get_all_answers():
    answers = Answer.query.all()
    answer_dicts = [answer.to_dict() for answer in answers]
    return jsonify(answer_dicts), 200


def get_participant(email):
    """Query DB for participant of given email."""
    return Participant.query.filter_by(email=email).first()


@app.cli.command('init_db')
def init_db_command():
    """Initialize the database."""
    print('initializing database...')
    db.init_app(app)
    db.create_all()


@app.cli.command('test_data')
def test_data_command():
    """Insert test data into DB.

    Two student emails.
    """
    print('inserting example data...')
    db.init_app(app)
    db.session.add(Participant('student1@nyu.edu'))
    db.session.add(Participant('student2@nyu.edu'))
    db.session.commit()


def main():
    logging.basicConfig(filename='requests.log', level=logging.INFO)
    db.init_app(app)
    app.run(debug=True, port=7000)


if __name__ == '__main__':
    main()
