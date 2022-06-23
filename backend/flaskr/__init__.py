import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    formatted_question= questions[start:end]
    return formatted_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if categories is None:
            abort(404)
        cat = [category.format() for category in categories]
        categ = {category.id: category.type for category in categories}
        return jsonify({
            'success' : True,
            'categories': categ,
            'total_categories' :len(cat)
           
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_question = paginate_questions(request, questions)
        if len(current_question) == 0:
            abort(404)
        categories = Category.query.order_by(Category.type).all()
        if categories is None:
            abort(404 )
        cat = {category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': len(questions),
            'categories': cat

        })
   
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question =  Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
        selection = Question.query.all()
        current_question = paginate_questions(request, selection)
        return jsonify({
        'success' : True,
        'deleted' : question_id,
        'total_questions' : len(Question.query.all())
    })
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions', methods =['POST'])
    def create_question():
            body= request.get_json()
            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)
            if ((new_question is None) | (new_answer is None) | (new_category is None)|(new_difficulty is None)):
                abort(422)
            else:
                questions = Question(
                question = new_question,
                answer = new_answer,
                category = new_category,
                difficulty = new_difficulty)
            questions.insert()
            selection= Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)
        
            return jsonify({
                'success' : True,
                'created' : questions.id,
                'total_questions':len(Question.query.all())
            })



    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route("/questions/search", methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm')
      
        selection = Question.query.filter(Question.question.ilike(f"% {search_term}%")).all()
        if selection is None:
                abort(400)
        current_question = paginate_questions(request, selection)
        if current_question is None:
                abort(400)

        return jsonify({
                "success": True,
                "questions": current_question,
                "total_questions": len(selection)
            })
        

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category_id(category_id):
        categories = Category.query.get(category_id)
        try:
            questions = Question.query.filter_by(
                category=str(category_id)).all()

            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': categories.type,
                'total_questions': len(questions)

            })
        except BaseException:
            abort(400)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        category_id = quiz_category['id']
        try:
            if not (
                'quiz_category' in body and
                'previous_questions' in body):
                abort(400)
               
            if category_id is None:
                questions = Question.query.order_by(Question.id).all().one_or_none()
                
                if questions is None:
                    abort(422)

                quest = [question.format() for question in questions if question.id not in previous_questions]
                random_question = random.sample(quest, len(quest))

            else:

                questions = Question.query.filter_by(
                    category=category_id).all()
                quest = [question.format(
                ) for question in questions if question.id not in previous_questions]
                random_question = random.sample(quest, len(quest))

                if len(random_question) > 0:
                    question = random_question[0]
                else:
                    question = None

            return jsonify({
                'success': True,
                'question': question,
            }), 200

        except:
            abort(400)

           
        return jsonify({
            'success' : True,
            'question' :question.format()
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    return app

