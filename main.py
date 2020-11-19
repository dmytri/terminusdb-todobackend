from terminusdb_client import WOQLClient
from terminusdb_client import WOQLQuery as Q

DB = WOQLClient("https://127.0.0.1:6363", insecure=True)
DB.connect(user="admin", account="admin", key="root",
        db="TodoMVC", insecure=True)

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse

from typing import List, Dict
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
    id: str
    title: str
    completed: bool
    links: Dict

class State(BaseModel):
    todos: List[Todo]
    links: Dict

class TodoId(BaseModel):
    id: str

class TodoTitle(BaseModel):
    value: str

class TodoCompleted(BaseModel):
    value: bool

class ErrorMessage(BaseModel):
    message: str

@app.get("/todo", response_model=State)
async def state():
    result = Q().woql_and(
        Q().triple("v:Doc", "type", "scm:Todo"),
        Q().triple("v:Doc", "scm:title", "v:Title"),
        Q().triple("v:Doc", "scm:completed", "v:Completed")
    ).execute(DB)
    bindings = result["bindings"]
    todos = []
    for item in bindings:
        ID = item["Doc"].split("///data/")[1]
        todos.append({"id": ID,
            "title": item["Title"]["@value"],
            "completed": item["Completed"]["@value"],
            "links": {
                "todo": f"/todo/{ID}",
                "remove": f"/todo/{ID}/remove",
                "title": f"/todo/{ID}/title",
                "completed": f"/todo/{ID}/completed"
        }})
    state = {"todos": todos,
            "links": {
                 "toggle": f"/todo/toggle",
                 "clear": f"/todo/clear",
            }}
    return state

@app.get("/todo/{ID}", response_model=Todo)
async def item(ID: str):
    data = Q().limit(1).woql_and(
        Q().triple(ID, "type", "scm:Todo"),
        Q().triple(ID, "scm:title", "v:Title"),
        Q().triple(ID, "scm:completed", "v:Completed")
    ).execute(DB)
    if data["bindings"]:
        item = data["bindings"][0]
        todo = {
            "id": ID,
            "title": item["Title"]["@value"],
            "completed": item["Completed"]["@value"],
            "links": {
                "todo": f"/todo/{ID}",
                "remove": f"/todo/{ID}/remove",
                "title": f"/todo/{ID}/title",
                "completed": f"/todo/{ID}/completed"
            }
        }
    return todo 

@app.post("/todo/{ID}", status_code=201, responses={
    201: {"model": TodoId},
    409: {"model": ErrorMessage}
})
async def create (ID: str, data: TodoTitle):
    result = Q().woql_and(
        Q().add_triple(ID, 'type', 'scm:Todo'),
        Q().add_triple(ID, 'title',
            Q().literal(data.value, 'string')),
        Q().add_triple(ID, 'completed',
            Q().literal(False, 'boolean'))
    ).execute(DB)
    if result["inserts"] == 0:
        return JSONResponse(status_code=409,
            content={"message": "Conflict"})
    return {"id": ID}

@app.patch("/todo/{ID}/title")
async def title(ID: str, data: TodoTitle):
    result = Q().woql_and(
        Q().triple(ID, 'title', 'v:Value'),
        Q().delete_triple(ID, 'title', 'v:Value'),
        Q().add_triple(ID, 'title',
            Q().literal(data.value, 'string'))
    ).execute(DB)
    return {"id": ID, "value": data.value}

@app.patch("/todo/{ID}/completed")
async def completed(ID: str, data: TodoCompleted):
    result = Q().woql_and(
        Q().triple(ID, 'completed', not data.value),
        Q().delete_triple(ID, 'completed', not data.value),
        Q().add_triple(ID, 'completed',
            Q().literal(data.value, 'boolean'))
    ).execute(DB)
    return {"id": ID, "value": data.value, "result": result}

@app.delete("/todo/{ID}/remove")
async def remove(ID: str):
    result = Q().woql_and(
        Q().triple(ID, 'v:Predicate', 'v:Object'),
        Q().delete_triple(ID, 'v:Predicate', 'v:Object')
    ).execute(DB)
    return {"id": ID, "result": result}

@app.post("/todo/toggle/")
async def toggle(data: TodoCompleted):
    result = Q().woql_and(
        Q().triple('v:Doc', 'completed',
            Q().literal(not data.value, 'boolean')),
        Q().delete_triple('v:Doc', 'completed',
            Q().literal(not data.value, 'boolean')),
        Q().add_triple('v:Doc', 'completed',
            Q().literal(data.value, 'boolean'))
    ).execute(DB)
    return {"result": result}

@app.delete("/todo/clear")
async def clear():
    result = Q().woql_and(
        Q().triple('v:Doc', 'completed',
            Q().literal(True, 'boolean')),
        Q().triple('v:Doc', 'v:Predicate', 'v:Object'),
        Q().delete_triple('v:Doc', 'v:Predicate', 'v:Object')
    ).execute(DB)
    return {"result": result}

