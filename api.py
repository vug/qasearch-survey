import json

from flask import Flask, request, render_template, abort, jsonify
import flask_sqlalchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey-results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy()
ANSWER_KEYS = ['email', 'correct', 'question_no', 'answer']


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode)

    def __init__(self, email):
        self.email = email


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode)
    correct = db.Column(db.Boolean)
    question_no = db.Column(db.Integer)
    answer = db.Column(db.Unicode)

    def __init__(self, email, correct, question_no, answer):
        self.email = email
        self.correct = correct
        self.question_no = question_no
        self.answer = answer

    def to_dict(self):
        return {
            'email': self.email,
            'correct': self.correct,
            'question_no': self.question_no,
            'answer': self.answer
        }


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/questions/<int:qa_id>')
def questions(qa_id):
    with app.open_resource('static/survey-data/{}.json'.format(qa_id), 'r') as f:
        contents = json.load(f)
    return json.dumps(contents)


@app.route('/answers', methods=['GET', 'POST'])
def responses():
    if request.method == 'GET':
        return get_all_answers()

    req = request.get_json()
    for key in ANSWER_KEYS:
        if key not in req:
            return 'missing key "{}"'.format(key), 400
    email = req['email']
    correct = req['correct']
    question_no = req['question_no']
    answer_str = req['answer']
    print(email, correct, question_no, answer_str)
    # print(type(email), type(correct), type(question_no), type(answer_str))
    answer = Answer(email, correct, question_no, answer_str)
    db.session.add(answer)
    db.session.commit()
    return 'saved {}th answer'.format(Answer.query.count())


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
    db.create_all()


@app.cli.command('test_data')
def test_data_command():
    """Insert test data into DB.

    Two student emails.
    """
    print('inserting example data...')
    db.session.add(Participant('student1@nyu.edu'))
    db.session.add(Participant('student2@nyu.edu'))
    db.session.commit()


def main():
    db.init_app(app)
    app.run(debug=True, port=7000)


if __name__ == '__main__':
    main()
