from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

API_KEY = "secret"
API_KEY_NAME = "X-API-Key"

class TodoIn(BaseModel):
    task: str

todos: List[dict] = [{"id": 1, "task": "Buy groceries"}]
next_id = 2

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

@app.get('/todos', response_model=List[dict])
def get_todos():
    return todos

@app.post('/todos', status_code=201, response_model=dict, dependencies=[Depends(verify_api_key)])
def add_todo(todo_in: TodoIn):
    global next_id
    if not todo_in.task.strip():
        raise HTTPException(status_code=400, detail="'task' cannot be empty")
    todo = {"id": next_id, "task": todo_in.task}
    todos.append(todo)
    next_id += 1
    return todo

@app.delete('/todos/{todo_id}', dependencies=[Depends(verify_api_key)])
def delete_todo(todo_id: int):
    for i, t in enumerate(todos):
        if t['id'] == todo_id:
            todos.pop(i)
            return {"detail": "Deleted"}, 200
    raise HTTPException(status_code=404, detail="Todo not found")
