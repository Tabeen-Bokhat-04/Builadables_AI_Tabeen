from flask import Flask, request, jsonify

app = Flask(__name__)

todos = [{"id": 1, "task": "Buy groceries"}]
next_id = 2

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

@app.route('/todos', methods=['POST'])
def add_todo():
    global next_id
    if not request.is_json:
        return jsonify({"detail": "Request body must be JSON."}), 400
    data = request.get_json()
    task = data.get('task')
    if not task or not isinstance(task, str):
        return jsonify({"detail": "'task' field is required and must be a string."}), 400
    todo = {"id": next_id, "task": task}
    todos.append(todo)
    next_id += 1
    return jsonify(todo), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
