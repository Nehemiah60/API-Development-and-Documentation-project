import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('postgres:nehecode@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response=self.client().get('/categories')
        data= json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions(self):
        response=self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    #Test Paginated Questions
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data =jsom.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    # Test Delete Questiom
    def test_delete_questions(self):
        response =self.client().get('/questions/2')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    #Test if Question is Beyond Parameter
    def test_delete_questions_404(self):
        response = self.client().get('/questions/1000')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'], False)

# Request beyond page parameter

    def test_get_questions_404(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"resource not found")
    
    def test_categories_404(self):
        response=self.client().get('/categories/200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    #Test to Create a Question
    def test_create_question(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        









# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()