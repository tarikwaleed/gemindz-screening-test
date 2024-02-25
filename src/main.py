from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TestCases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    result = db.Column(db.Text, nullable=False)
    execution_time = db.Column(db.TIMESTAMP, default=datetime.utcnow)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/testcase', methods=['POST'])
def create_test_case():
    data = request.get_json()
    # return data
    new_test_case = TestCases(name=data['name'], description=data.get('description'))
    db.session.add(new_test_case)
    db.session.commit()
    return jsonify({'id': new_test_case.id, 'name': new_test_case.name, 'description': new_test_case.description}), 201


@app.route('/api/testcase', methods=['GET'])
def get_all_test_cases():
    test_cases = TestCases.query.all()
    return jsonify([{'id': tc.id, 'name': tc.name, 'description': tc.description} for tc in test_cases])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=5000)
