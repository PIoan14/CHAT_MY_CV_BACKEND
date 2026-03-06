from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore
from models import User
from fastapi import HTTPException, status
from hasher import hash_password

app = FastAPI()
cred = credentials.Certificate("database_referance.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.post("/registerUser")
def server_register(user : User):
    
    hashed_password = hash_password(user.password)
    
    user.password = hashed_password
    db.collection("users").add(user.model_dump())
    #Add to DB
    return {
        "Username" : user.username,
        "password" : hashed_password
        }

