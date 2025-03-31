from typing import Optional
from functionsGA1 import *
from functionsGA2 import *
from functionsGA3 import *
from functionsGA4 import *
from functionsGA5 import *

from routes import *

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],    # Allows all HTTP methods
    allow_headers=["*"],    # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/")
@app.post("/api")
async def gen_response(
    question: str = Form(...), 
    file: Optional[UploadFile] = Form(None)  # Make file optional
):
    q_id = get_q_id(question)
    print(q_id)
    
    # Handle case when no file is uploaded
    answer = await get_solution(q_id, question, file if file else None)

    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)