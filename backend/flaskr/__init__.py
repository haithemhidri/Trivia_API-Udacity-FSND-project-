import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request_func(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)

    categories_type = {}
    for category in categories:
      categories_type[category.id] = category.type

    return jsonify({
        'success': True,
        'categories': categories_type
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
  def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions_formatted = [question.format() for question in questions]
    current_questions = questions_formatted[start:end]

    return current_questions

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()

    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)
    categories = Category.query.order_by(Category.id).all()

    categories_type = {}
    for category in categories:
      categories_type[category.id] = category.type

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': 'All',
        'categories': categories_type
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(
          Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
          'success': True,
          'deleted': question_id
      })
    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    search_term = body.get('searchTerm', None)

    if search_term:
      questions = Question.query.order_by(Question.id).filter(
          Question.question.ilike('%{}%'.format(search_term))).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': 'All'
      })
    else:
      try:
        question = Question(question=new_question, answer=new_answer,
                            difficulty=new_difficulty, category=new_category)
        question.insert()
        return jsonify({
            'success': True,
            'created': question.id
        })
      except:
        abort(500)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_catogory(category_id):
    questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    category = Category.query.filter(Category.id == category_id).one_or_none()

    return jsonify({
      'success': True,
      'questions': current_questions,
      'current_category': category.type
    })


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
  def play_quiz():
        try:

            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable entity'
      }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
      return jsonify({
        'success': False,
        'error': 500,
        'message': ' server error'
      }), 500

    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
      }), 400

  
  return app

    