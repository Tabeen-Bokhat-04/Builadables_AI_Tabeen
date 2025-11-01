from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class TodoIn(BaseModel):
    task: str

todos: List[dict] = [{"id": 1, "task": "Buy groceries"}]
next_id = 2

@app.get('/todos', response_model=List[dict])
def get_todos():
    return todos

@app.post('/todos', status_code=201, response_model=dict)
def add_todo(todo_in: TodoIn):
    global next_id
    if not todo_in.task.strip():
        raise HTTPException(status_code=400, detail="'task' cannot be empty")
    todo = {"id": next_id, "task": todo_in.task}
    todos.append(todo)
    next_id += 1
    return todo
