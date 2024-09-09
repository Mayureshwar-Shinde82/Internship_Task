from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from secrets import token_hex
from typing import List
import shutil
import os
from chatbot import Chatbot

app = FastAPI()
obj = Chatbot()

class QueryRequest(BaseModel):
    query: str
  

@app.post("/upload_documents/")
async def load_document(files: List[UploadFile] = File(...)):
    doc = []
    try:
        for file in files:
            # Generate a temporary file path for each uploaded file
            temp_file_path = f"Documents/{file.filename}"
            
            # Save the file to the temporary file path
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Check the file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ['.txt', '.pdf', '.csv']:
                raise ValueError(f"Unsupported file format: {file.filename}. Please upload the file in format like ('pdf','csv','txt')")
            
            # Append the path of the saved document to the doc list
            doc.append(temp_file_path)
        
        # Process the documents (assuming obj.load_documents(doc) is your processing function)
        obj.load_documents(doc)
        
        return {'message': 'Documents loaded successfully'}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up: Remove all saved files after processing
        for temp_file_path in doc:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
@app.post("/chat/")
async def chat(request: QueryRequest):
    try:
        response = obj.generate_response(request.query)
        return {"query": request.query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")