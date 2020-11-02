from typing import Literal, Type

from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

class TodoCreated(BaseModel):
    id: str
    title: str

class TodoAlteredTitle(BaseModel):
    value: str

class TodoAlteredCompleted(BaseModel):
    key:  Literal['completed']
    value: bool

class TodoRemoved(BaseModel):
    id: str

class TodoToggled(BaseModel):
    completed: bool

@app.post("/create/{todo_created}")
async def create (todo: TodoCreated):
    return {"id": todo.id, "title": todo.title}

@app.patch("/alter/title/{todo_altered_title}")
async def alter(todo: TodoAlteredTitle):
    return {"id": todo.id, "value": todo.value}

@app.patch("/alter/completed/{todo_altered_completed}")
async def alter(todo: TodoAlteredCompleted):
    return {"id": todo.id, "value": todo.value}

@app.delete("/remove/{todo_removed}")
async def remove(todo: TodoRemoved):
    return {"id": todo.id}

@app.post("/toggle/{todo_toggled}")
async def toggle(todo: TodoToggled):
    return {"conmpleted": todo.completed}

@app.post("/clear")
async def clear():
    return {"clear": "clear"}

@app.get("/state")
async def state():
    return {"state": "state"}

