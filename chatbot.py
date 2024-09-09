from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
import os
from langchain_community.document_loaders import  PyPDFLoader, CSVLoader, TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import MongoDBChatMessageHistory, ConversationBufferMemory
from langchain.chains import ConversationChain, create_retrieval_chain
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['Chatbot_database']
    collection = db['chat_memory']
except:
    raise RuntimeError("Failed to connect mongodb")
    
try:
    sec_key = "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"
    os.environ['HUGGINGFACEHUP_API_TOKEN'] = sec_key
    repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
    llm = HuggingFaceEndpoint(repo_id=repo_id, temperature=0.7)
except:
    raise RuntimeError('Failed to setup HuggingFaceEndpoint')
    
class Chatbot():
    
    def __init__(self):
        try:
            self.vector_db = None
            self.memory = ConversationBufferMemory(
            chat_memory=MongoDBChatMessageHistory(session_id='code', connection_string='mongodb://localhost:27017/', database_name='Chatbot_database', collection_name='save_memory')
        )
        except:
            raise RuntimeError('Failed to initialize chat memory')

    def load_documents(self,file):
        print(type(file))
        try:
            for file in file:
                documents = []
                if file.endswith('.txt'):
                    loader = TextLoader(file)
                elif file.endswith('.pdf'):
                    loader = PyPDFLoader(file)
                elif file.endswith('.csv'):
                    loader = CSVLoader(file)
        except:
            raise ValueError("Unsupported file format, Please uplaod the file in format like ('pdf','csv','txt')") 
        documents.extend(loader.load())
        if not documents:
                raise ValueError("No documents were loaded. Please check the file content.")
            
        if documents:
            print('Documents loaded successfully.')
            try:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                final_documents = text_splitter.split_documents(documents)
                embeddings = HuggingFaceHubEmbeddings(huggingfacehub_api_token=sec_key)
                vector_db = FAISS.from_documents(final_documents, embeddings)
                self.vector_db = vector_db
                self.retrival = self.vector_db.as_retriever()
            except:
                raise ValueError("Vector Database is not initialize.")
            
    def generate_response(self, query: str):
        # if not self.vector_db:
        #     raise RuntimeError("Vector database not initialized.")
        # try:
        search_response = self.vector_db.similarity_search(query=query,k=1)
        context = " ".join([doc.page_content for doc in search_response])
        #     print("context: ",context)
        chain = ConversationChain(llm=llm, memory=self.memory)
        #     response = chain.invoke(input=context + " " + query)
        #     self.save_response(query, response)
        #     return response
        # except:
        #     raise RuntimeError('An error occured while generating the responce')
            
        prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context. 
Think step by step before providing a detailed answer.  
<context>
{context}
</context>
Question: {input}""")
        doc_chain = create_stuff_documents_chain(llm=llm,prompt=prompt)
        chain1 = create_retrieval_chain(self.retrival,doc_chain)
        response = chain1.invoke({'comtext':context,'input':query})
        return response['answer']
        
        
    def save_response(self, query: str, response: str):
        try:
            response_document = {
            "query": query,
            "response": response,
            "memory": [msg.dict() for msg in self.memory.chat_memory.messages]
        }
            collection.insert_one(response_document)
            print("Response saved in MongoDB.")
        except:
            raise RuntimeError("Error occured while saving the data into mongodb")