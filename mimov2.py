from flask import Flask, request, abort, jsonify

app = Flask(__name__)


# identify list object to store tasks
tasks = [{'id':1, 'title':"t1"}]


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/todo/api/v1/tasks', methods=['POST'])
def post_task():
    if not request.get_json() or 'title' not in request.get_json():
        abort(400)

    # Generate a response
    request_json = request.get_json()

    task = {
        'id': (tasks[-1]['id'] + 1 if tasks else 1),
        'title': request_json.get('title'),
        'description': 'N/A' if not request_json.get('description') else request_json.get('description'),
        'status': 'In Progress' if not request_json.get('status') else request_json.get('status')
    }

    response = jsonify(task)
    response.status_code = 201

    tasks.append(task)
    return response


@app.route('/todo/api/v1/tasks', methods=['GET'])
def get_tasks():
    response = jsonify({'tasks':tasks})
    response.status_code = 200
    return response


@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    response = jsonify({'task':task})
    response.status_code = 200
    return response


@app.route('/todo/api/v1/tasks', methods=['PUT'])
def update_task():
    if not request.get_json() or 'id' not in request.get_json():
        abort(400)

    task_id = request.get_json().get('id')
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)

    item = task[0]
    json_ret = request.get_json()
    if json_ret.get('title'):
        item['title'] = json_ret.get('title')

    if json_ret.get('description'):
        item['description'] = json_ret.get('description')

    if json_ret.get('status'):
        item['status'] = json_ret.get('status')
    # now we only overwrite the value pass and keep others as before
    
    response = jsonify(item)
    response.status_code = 201
    return response


@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)

    tasks.remove(task[0])
    response = jsonify({"Remove": "Success"})
    return response


if __name__ == '__main__':
    app.run(debug=True)

