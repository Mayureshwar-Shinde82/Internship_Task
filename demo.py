from fastapi import FastAPI, UploadFile, File
from typing import List
import uvicorn

app = FastAPI()

@app.post('/upload_doc')
async def upload_doc(file: List[UploadFile] = File(...)):
    documents = []
    for i in file:
        documents.append(i.filename)
    print(file)
    print(documents)
    return file

if __name__ == "__main__":
    uvicorn.run(app)