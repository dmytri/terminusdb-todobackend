from terminusdb_client import WOQLClient
from terminusdb_client import WOQLQuery as Q

DB = WOQLClient("https://127.0.0.1:6363", insecure=True)
DB.connect(user="admin", account="admin", key="root",
        db="TodoMVC", insecure=True)

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse

from typing import List
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
    id: str
    title: str
    completed: bool

class TodoId(BaseModel):
    id: str

class TodoTitle(BaseModel):
    value: str

class TodoCompleted(BaseModel):
    value: bool

class ErrorMessage(BaseModel):
    message: str

@app.get("/todo", response_model=List[Todo])
async def state():
    data = Q().woql_and(
        Q().triple("v:Doc", "type", "scm:Todo"),
        Q().triple("v:Doc", "scm:title", "v:Title"),
        Q().triple("v:Doc", "scm:completed", "v:Completed")
    ).execute(DB)
    bindings = data["bindings"]
    todos = []
    for item in bindings:
        todos.append({
            "id": item["Doc"],
            "title": item["Title"]["@value"],
            "completed": item["Completed"]["@value"]
        })
    return todos 

@app.get("/todo/{id}", response_model=Todo)
async def item(id: str):
    data = Q().limit(1).woql_and(
        Q().triple(id, "type", "scm:Todo"),
        Q().triple("v:Doc", "type", "scm:Todo"),
        Q().triple("v:Doc", "scm:title", "v:Title"),
        Q().triple("v:Doc", "scm:completed", "v:Completed")
    ).execute(DB)
    if data["bindings"]:
        item = data["bindings"][0]
        todo = {
            "id": item["Doc"],
            "title": item["Title"]["@value"],
            "completed": item["Completed"]["@value"]
        }
    return todo 


@app.post("/todo/{id}", status_code=201, responses={
    201: {"model": TodoId},
    409: {"model": ErrorMessage}
})
async def create (id: str, data: TodoTitle):
    result = Q().woql_and(
            Q().add_triple(id, 'type', 'scm:Todo'),
            Q().add_triple(id, 'title',
                Q().literal(data.value, 'string')),
            Q().add_triple(id, 'completed',
                Q().literal(False, 'boolean'))
        ).execute(DB)
    if result["inserts"] == 0:
        return JSONResponse(status_code=409,
            content={"message": "Conflict"})
    return {"id": id}

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

