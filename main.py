from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore
from models import User
from fastapi import HTTPException, status
from hasher import hash_password
import json 
from chat_llm import getRAGanswer, get_prompt


app = FastAPI()
cred = credentials.Certificate("database_referance.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_user_details_by_id(doc_id):
    try:
        doc_ref = db.collection("users").document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict()
    except:
        print("No such user found")
    pass



def get_user_details(colection, username):
    
    try:
        docs = db.collection(colection).stream()    
        for doc in docs:
            data = doc.to_dict()
            if data["username"] == username:
                data.update({"logged_in_id": doc.id})

                return data
    except:
        print("Firebase is not available")
        return False

    return False

def get_all_user_details(colection):

    try:
        details = []
        docs = db.collection(colection).stream()
        
        for doc in docs:
            data = doc.to_dict()

            details.append(data)

        return details
    except:
        print("Firebase is not available")
        return False


        

@app.post("/loginUser")
def server_login(user : User):
    
    hashed_password = hash_password(user.password)
    
    user_details = get_user_details("users", user.username)

    all_details = get_all_user_details("users")

    passwords_check = [y["password"] for y in all_details]


    if user_details and hashed_password in passwords_check:

        return user_details
    else :
    
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorect username or password"
        )   


@app.post("/registerUser")
def server_register(user : User):
    
    hashed_password = hash_password(user.password)
    
    details = get_all_user_details("users")

    registered_username = [x["username"] for x in details]
    

    passwords_check = [y["password"] for y in details]

    if hashed_password not in passwords_check and user.username not in registered_username:
        user.password = hashed_password
        db.collection("users").add(user.model_dump())
        
        #Add to DB
        return {
            "Username" : user.username,
            "password" : hashed_password
        }
    else :
      
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password Exists"
        )
    


@app.post("/updateUser")
def server_user_update(doc_id, element, value):
    
    try:
        doc_ref = db.collection("users").document(doc_id)
        
        if not doc_ref.get().exists:
            return {"status": 404, "message": "No such document in firebase"}
        

        if element == "password":
            value = hash_password(value)
        doc_ref.update({
            element : value
        })
        
        return {"status": 200, "message": "Document was updated in firebase"}
        
    except Exception as e:
        return {"status": 500, "message": str(e)}
    

@app.post("/chatCompletions")
def chat_with_CV(doc_id, question):
    
    try:
        doc_ref = get_user_details_by_id(doc_id=doc_id)
        pdf_cv_content = doc_ref["CV_content"]
        summary = doc_ref["text_summary"]

        prompt = get_prompt(question, doc_ref["username"], pdf_cv_content,summary)
        answer = getRAGanswer(prompt=prompt, username= doc_ref["username"])
        print(answer)
        return {"status": 200, "message": answer}
        
    except Exception as e:
        return {"status": 500, "message": str(e)}


