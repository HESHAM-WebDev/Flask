# Import Flask app
from flask import Flask, jsonify, render_template, redirect, flash, request

# Import Restfull needs
from flask_restful import Api, Resource, abort

# Configure Log Module
import logging

# Import DB handler, Todo Class
from models import db, Todo

logging.basicConfig(filename='/home/minos/Work-Space/Flask-Intro/flask.logs', level=logging.DEBUG,
                    format=" %(asctime)s %(message)s %(levelname)s")
# Configure Flask app
todo_flask_app = Flask(__name__)

# Configure Restful APi
todo_api = Api(todo_flask_app)

# Configure Secret Key
todo_flask_app.config['SECRET_KEY'] = '0zx5c34as65d4654&%^#$#$@'

# Configure Database
todo_flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
todo_flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

todo_list = [
    {'name': 'a', 'id': 0, 'priority': 5},
    {'name': 'b', 'id': 1, 'priority': 5},
    {'name': 'c', 'id': 2, 'priority': 5}
]


# --------------------------
# Normal Views
# --------------------------

# Hello View
@todo_flask_app.route('/', methods=['GET'])
def hello_view():
    print(request.args)
    print('name -> ', request.args.get('name'))
    print('age -> ', request.args.get('age'))
    print("Request -> ", request)
    print("req method -> ", request.method)
    return f'Hello {request.args.get("name")} from flask your age is {request.args.get("age")}'


@todo_flask_app.route('/todo/', methods=['GET', 'POST'])
@todo_flask_app.route('/todo', methods=['GET', 'POST'])
def list_todo_tasks():
    if request.method == 'GET':
        return jsonify(todo_list)
    elif request.method == 'POST':
        print(request.form)
        task_name = request.form.get('task_name')
        task_id = request.form.get('task_id')
        task_priority = request.form.get('task_priority')

        todo_list.append(
            {'name': task_name, 'id': task_id, 'priority': task_priority}

        )
        return jsonify(todo_list)


@todo_flask_app.route('/todo/<int:task_id>', methods=['GET', 'DELETE'])
def todoRD(task_id):
    if request.method == 'GET':
        return jsonify(todo_list[task_id])

    elif request.method == 'DELETE':
        del todo_list[task_id]
        return {'message': 'deleted task'}, 200


@todo_flask_app.route('/todo/<string:task_name>', methods=['GET'])
def task_detail(task_name):
    try:
        print(task_name)
        return jsonify(todo_list[1])
    except Exception as e:
        pass
    return "No task found"


# --------------------------
# Templates
# --------------------------
@todo_flask_app.route('/index', methods=['GET'])
def index_view():
    return render_template('index.html', iti_tasks=todo_list, title='TODO INDEX')


@todo_flask_app.route('/task-detail/<int:task_id>')
def task_detail_view(task_id):
    task = todo_list[task_id]
    return render_template('task_detail.html', task=task)


@todo_flask_app.route('/task-delete/<int:task_id>')
def task_delete_view(task_id):
    del todo_list[task_id]
    return redirect('/index')


@todo_flask_app.route('/task-create', methods=['GET', 'POST'])
def task_create_view():
    if request.method == 'GET':
        return render_template('create_task.html', title='TASK CREATE')
    elif request.method == 'POST':
        data = {
            'name': request.form.get('task_name'),
            'id': request.form.get('task_id'),
            'priority': request.form.get('task_priority'),

        }
        todo_list.append(data)
        flash('Successfully Added Task')
        return redirect('/index')


# --------------------------
# Restful
# --------------------------

class TodoRUD(Resource):
    def get(self, **kwargs):
        # Get TOdo id from request
        todo_id = kwargs.get('todo_id')
        # Get Todo object
        print("id ->", todo_id)
        task = Todo.query.get(todo_id)
        if not task:
            abort(404, message='Not Found')

        data = {
            'id': task.id,
            'name': task.name,
            'priority': task.priority,
            'description': task.description,
            'finished': task.finished
        }

        return data, 200

    def delete(self, *args, **kwargs):
        # Get TOdo id from request
        todo_id = kwargs.get('todo_id')
        # Get Todo object
        print("id ->", todo_id)
        todo_obj = Todo.query.get(todo_id)

        print('todo obj -> ', todo_obj)

        db.session.delete(todo_obj)  # delete query
        db.session.commit()

        return {'message': 'Deleted Successfully'}, 200

    def patch(self):
        pass


class TodoLC(Resource):
    def post(self):
        try:
            data = {
                'name': request.form.get('name'),
                'priority': request.form.get('priority'),
                'description': request.form.get('description'),
                'finished': False
            }

            # todo_list.append(data)

            todo_obj = Todo(**data)  # create object of Todo
            db.session.add(todo_obj)  # insert query inside the db
            db.session.commit()  # commit to db

            return {'message': 'Task Created Successfully'}, 201
        except Exception as e:
            abort(500, message='Internal Server Error')

    def get(self):
        try:
            todo_objects = Todo.query.filter().all()
            print("TD OBJS -> ", todo_objects)

            limit = request.args.get('limit')
            # my_list = []
            #
            # if limit:
            #     my_list = todo_list[:int(limit)]
            # else:
            #     my_list = todo_list

            my_new_list = []

            for task in todo_objects:
                data = {
                    'id': task.id,
                    'name': task.name,
                    'priority': task.priority,
                    'description': task.description,
                    'finished': task.finished
                }

                my_new_list.append(data)

            if limit:
                print(type(limit))
                my_new_list = my_new_list[:int(limit)]

            return my_new_list

        except Exception as e:
            abort(500, message="Internal Server Error {}".format(e))


# Register The TodoLC Resource class
todo_api.add_resource(TodoLC, '/api/v1/todo')

# Register TodoRud Resource class
todo_api.add_resource(TodoRUD, '/api/v1/todo/<int:todo_id>')

# Attach Sqlalchemy to app
db.init_app(todo_flask_app)


# Create Database Tables
@todo_flask_app.before_first_request
def initiate_data_base_tables():
    db.create_all()


# Run Server
todo_flask_app.run(port=5080, debug=True)
