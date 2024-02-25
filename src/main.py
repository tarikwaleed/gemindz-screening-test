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

@app.route('/api/testcase/<int:testcase_id>', methods=['GET'])
def get_single_test_case(testcase_id):
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            return jsonify({'id': test_case.id, 'name': test_case.name, 'description': test_case.description})
        else:
            return jsonify({'error': 'Test case not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/testcase/<int:testcase_id>', methods=['PUT'])
def update_test_case(testcase_id):
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            data = request.get_json()
            test_case.name = data['name']
            test_case.description = data.get('description')
            test_case.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'id': test_case.id, 'name': test_case.name, 'description': test_case.description})
        else:
            return jsonify({'error': 'Test case not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/testcase/<int:testcase_id>', methods=['DELETE'])
def delete_test_case(testcase_id):
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            db.session.delete(test_case)
            db.session.commit()
            return jsonify({'message': 'Test case deleted successfully'}), 200
        else:
            return jsonify({'error': 'Test case not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execution', methods=['POST'])
def record_execution_result():
    data = request.get_json()

    test_case_id = data.get('test_case_id')
    result = data.get('result')

    if not test_case_id or not result:
        return jsonify({'error': 'test_case_id and result are required'}), 400

    # Record the execution result
    new_execution_result = ExecutionResults(test_case_id=test_case_id, result=result)
    db.session.add(new_execution_result)
    db.session.commit()

    return jsonify({'id': new_execution_result.id, 'test_case_id': test_case_id, 'result': result}), 201

@app.route('/api/execution/<int:test_case_id>', methods=['GET'])
def get_execution_results(test_case_id):
    if not test_case_id:
        return jsonify({'message': 'invalid test case id'}), 404

    execution_results = ExecutionResults.query.filter_by(test_case_id=test_case_id)

    if not execution_results:
        return jsonify({'message': 'No execution results found for the specified test asset'}), 404

    results = [{'id': result.id, 'test_case_id': result.test_case_id, 'result': result.result, 'execution_time': result.execution_time} for result in execution_results]
    return jsonify(results)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=5000)
