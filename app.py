from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)  # Initialize API

# Database Model
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# REST API Resource
class TodoResource(Resource):
    def get(self, sno=None):
        """Fetch all Todos or a specific one by sno"""
        if sno:
            todo = Todo.query.get(sno)
            if not todo:
                return {'message': 'Todo not found'}, 404
            return {'sno': todo.sno, 'title': todo.title, 'desc': todo.desc, 'date_created': str(todo.date_created)}
        
        todos = Todo.query.all()
        return [{'sno': todo.sno, 'title': todo.title, 'desc': todo.desc, 'date_created': str(todo.date_created)} for todo in todos]

    def post(self):
        """Create a new Todo"""
        data = request.get_json()
        new_todo = Todo(title=data['title'], desc=data['desc'])
        db.session.add(new_todo)
        db.session.commit()
        return {'message': 'Todo created successfully', 'todo_id': new_todo.sno}, 201

    def put(self, sno):
        """Update an existing Todo"""
        todo = Todo.query.get(sno)
        if not todo:
            return {'message': 'Todo not found'}, 404

        data = request.get_json()
        todo.title = data['title']
        todo.desc = data['desc']
        db.session.commit()
        return {'message': 'Todo updated successfully'}

    def delete(self, sno):
        """Delete a Todo"""
        todo = Todo.query.get(sno)
        if not todo:
            return {'message': 'Todo not found'}, 404

        db.session.delete(todo)
        db.session.commit()
        return {'message': 'Todo deleted successfully'}

# Add API Routes
api.add_resource(TodoResource, '/api/todo', '/api/todo/<int:sno>')

# Home Route (UI)
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
        return redirect("/")

    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

if __name__ == "__main__":
    app.run(debug=True)


