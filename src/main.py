from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from validators import (
    is_valid_integer,
    is_valid_string,
    is_valid_test_case_data,
    is_valid_execution_data,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)


class TestCases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )


class ExecutionResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey("test_cases.id"), nullable=False)
    result = db.Column(db.Text, nullable=False)
    execution_time = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def generate_token(username):
    return jwt.encode(
        {
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        app.config["SECRET_KEY"],
    )


def verify_token(token):
    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "User registered successfully,login to get a token to use it to access the api endpoints"
            }
        ),
        201,
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = generate_token(username)
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/api/testcase", methods=["POST"])
def create_test_case():
    if "Authorization" not in request.headers:
        return jsonify({"message": "Authorization header missing"}), 401

    auth_header = request.headers["Authorization"]
    token = auth_header.split("Bearer ")[-1]

    if not verify_token(token):
        return jsonify({"message": "Invalid or expired token"}), 401

    data = request.get_json()
    if not is_valid_test_case_data(data):
        return jsonify({"error": "Invalid test case data"}), 400
    new_test_case = TestCases(name=data["name"], description=data.get("description"))
    db.session.add(new_test_case)
    db.session.commit()
    return (
        jsonify(
            {
                "id": new_test_case.id,
                "name": new_test_case.name,
                "description": new_test_case.description,
            }
        ),
        201,
    )


@app.route("/api/testcase", methods=["GET"])
def get_all_test_cases():

    if "Authorization" not in request.headers:
        return jsonify({"message": "Authorization header missing"}), 401

    auth_header = request.headers["Authorization"]
    token = auth_header.split("Bearer ")[-1]

    if not verify_token(token):
        return jsonify({"message": "Invalid or expired token"}), 401

    test_cases = TestCases.query.all()
    return jsonify(
        [
            {"id": tc.id, "name": tc.name, "description": tc.description}
            for tc in test_cases
        ]
    )


@app.route("/api/testcase/<int:testcase_id>", methods=["GET"])
def get_single_test_case(testcase_id):
    if not is_valid_integer(testcase_id):
        return jsonify({"error": "testcase_id sould be integer"}), 400
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            return jsonify(
                {
                    "id": test_case.id,
                    "name": test_case.name,
                    "description": test_case.description,
                }
            )
        else:
            return jsonify({"error": "Test case not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/testcase/<int:testcase_id>", methods=["PUT"])
def update_test_case(testcase_id):
    if not is_valid_integer(testcase_id):
        return jsonify({"error": "testcase_id sould be integer"}), 400
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            data = request.get_json()
            test_case.name = data["name"]
            test_case.description = data.get("description")
            test_case.updated_at = datetime.datetime.utcnow()
            db.session.commit()
            return jsonify(
                {
                    "id": test_case.id,
                    "name": test_case.name,
                    "description": test_case.description,
                }
            )
        else:
            return jsonify({"error": "Test case not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/testcase/<int:testcase_id>", methods=["DELETE"])
def delete_test_case(testcase_id):
    if not is_valid_integer(testcase_id):
        return jsonify({"error": "testcase_id sould be integer"}), 400
    try:
        test_case = TestCases.query.get(testcase_id)
        if test_case:
            db.session.delete(test_case)
            db.session.commit()
            return jsonify({"message": "Test case deleted successfully"}), 200
        else:
            return jsonify({"error": "Test case not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/execution", methods=["POST"])
def record_execution_result():
    data = request.get_json()
    if not is_valid_execution_data(data):
        return jsonify({"error": "Invalid execution data"}), 400

    test_case_id = data.get("test_case_id")
    result = data.get("result")

    if not test_case_id or not result:
        return jsonify({"error": "test_case_id and result are required"}), 400

    # Record the execution result
    new_execution_result = ExecutionResults(test_case_id=test_case_id, result=result)
    db.session.add(new_execution_result)
    db.session.commit()

    return (
        jsonify(
            {
                "id": new_execution_result.id,
                "test_case_id": test_case_id,
                "result": result,
            }
        ),
        201,
    )


@app.route("/api/execution/<int:test_case_id>", methods=["GET"])
def get_execution_results(test_case_id):
    if not is_valid_integer(test_case_id):
        return jsonify({"error": "testcase_id sould be integer"}), 400

    execution_results = ExecutionResults.query.filter_by(test_case_id=test_case_id)

    if not execution_results:
        return (
            jsonify(
                {"message": "No execution results found for the specified test asset"}
            ),
            404,
        )

    results = [
        {
            "id": result.id,
            "test_case_id": result.test_case_id,
            "result": result.result,
            "execution_time": result.execution_time,
        }
        for result in execution_results
    ]
    return jsonify(results)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
