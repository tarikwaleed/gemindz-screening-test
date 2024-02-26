import unittest
import json
from main import app, db, TestCases, ExecutionResults


class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.test_request_context()
        self.ctx.push()
        with self.app:
            db.create_all()

    def tearDown(self):
        with self.app:
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
            db.session.remove()
            db.drop_all()
        self.ctx.pop()

    def test_create_test_case(self):
        data = {"name": "Test Case 1", "description": "Description 1"}
        response = self.app.post("/api/testcase", json=data)
        self.assertEqual(response.status_code, 201)

        test_case = TestCases.query.filter_by(name=data["name"]).first()
        self.assertIsNotNone(test_case)
        self.assertEqual(test_case.description, data["description"])

    def test_get_all_test_cases(self):
        with self.app:
            db.session.add(TestCases(name="Test Case 1", description="Description 1"))
            db.session.add(TestCases(name="Test Case 2", description="Description 2"))
            db.session.commit()
        response = self.app.get("/api/testcase")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_single_test_case(self):
        with self.app:
            test_case = TestCases(name="Test Case 1", description="Description 1")
            db.session.add(test_case)
            db.session.commit()
        response = self.app.get(f"/api/testcase/{test_case.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], test_case.name)

    def test_update_test_case(self):
        with self.app:
            test_case = TestCases(name="Test Case 1", description="Description 1")
            db.session.add(test_case)
            db.session.commit()
        data = {"name": "Updated Test Case", "description": "Updated Description"}
        response = self.app.put(f"/api/testcase/{test_case.id}", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], data["name"])

    def test_delete_test_case(self):
        with self.app:
            test_case = TestCases(name="Test Case 1", description="Description 1")
            db.session.add(test_case)
            db.session.commit()
        response = self.app.delete(f"/api/testcase/{test_case.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Test case deleted successfully")

    def test_record_execution_result(self):
        data = {"test_case_id": 1, "result": "pass"}

        response = self.app.post("/api/execution", json=data)

        self.assertEqual(response.status_code, 201)

        with self.app:
            execution_result = ExecutionResults.query.first()
            self.assertIsNotNone(execution_result)
            self.assertEqual(execution_result.test_case_id, data["test_case_id"])
            self.assertEqual(execution_result.result, data["result"])

    def test_get_execution_results(self):
        test_case_id = 1
        execution_data = [
            {"test_case_id": test_case_id, "result": "pass"},
            {"test_case_id": test_case_id, "result": "fail"},
        ]

        with self.app:
            for data in execution_data:
                db.session.add(ExecutionResults(**data))
            db.session.commit()

        response = self.app.get(f"/api/execution/{test_case_id}")

        self.assertEqual(response.status_code, 200)

        expected_results = [
            {
                "id": result.id,
                "test_case_id": result.test_case_id,
                "result": result.result,
                "execution_time": result.execution_time.isoformat(),
            }
            for result in ExecutionResults.query.filter_by(test_case_id=test_case_id)
        ]
        self.assertEqual(response.json, expected_results)


if __name__ == "__main__":
    unittest.main()
