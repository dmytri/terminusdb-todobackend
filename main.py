from terminusdb_client import WOQLClient
from terminusdb_client import WOQLQuery as Q

DB = WOQLClient("https://127.0.0.1:6363", insecure=True)
DB.connect(user="admin", account="admin", key="root",
        db="TodoMVC", insecure=True)

from fastapi import FastAPI

from typing import Literal, Type
from pydantic import BaseModel

app = FastAPI()

class TodoTitle(BaseModel):
    value: str

class TodoCompleted(BaseModel):
    value: bool

@app.get("/todo")
async def state():
    data = Q().woql_and(
        Q().triple("v:doc", "type", "scm:Todo"),
        Q().triple("v:Doc", "scm:title", "v:Title"),
        Q().triple("v:Doc", "scm:completed", "v:Completed")
    ).execute(DB)
    bindings = data['bindings']
    todos = []
    for i in bindings:
        todos.append({
            "id": i["Doc"],
            "title": i["Title"]["@value"],
            "completed": i["Completed"]["@value"]
        })
    return todos 

@app.put("/todo/{id}")
async def create (data: TodoTitle):
    return {"id": id, "title": data.value}

@app.patch("/todo/{id}/title")
async def title(data: TodoTitle):
    return {"id": id, "value": data.value}

@app.patch("/todo/{id}/completed")
async def completed(data: TodoCompleted):
    return {"id": id, "value": data.value}

@app.delete("/todo/{id}/remove")
async def remove():
    return {"id": id}

@app.post("/todo/toggle/")
async def toggle(data: TodoCompleted):
    return {"completed": data.value}

@app.post("/todo/clear")
async def clear():
    return {"clear": "clear"}

