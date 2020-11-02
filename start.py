import uvicorn

def app():
    uvicorn.run("main:app", reload=True)
