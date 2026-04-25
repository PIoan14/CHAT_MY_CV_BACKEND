from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore
from models import User
from fastapi import HTTPException, status
from hasher import hash_password
from files_management import delete_file, delete_folder
from chat_llm import getLLManswer, get_prompt
from RAG_prep import dump_RAG_DB, load_RAG_DB
from fastapi.responses import StreamingResponse
import uvicorn
import os
import json
from dotenv import load_dotenv
from chatAnalytics import get_structured_questions_summary
load_dotenv()

app = FastAPI()

firebase_creds_json = os.getenv("FIREBASE_CRED")

if firebase_creds_json:
   
    cred_dict = json.loads(firebase_creds_json)
  
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    print("EROARE")

db = firestore.client()

def add_Question_to_used(question, user_id):
    try:

        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "questions": firestore.ArrayUnion([question])
        })
        print(f"Succes: '{question}' was added")
    except Exception as e:
        print(f"Eroare: {e}")

def split_long_strings(strings, max_words=20):
    new_list = []
    for s in strings:
        words = s.split()  # împarte string-ul în cuvinte
        if len(words) <= max_words:
            new_list.append(s)
        else:
            # împarte în bucăți de maxim max_words
            for i in range(0, len(words), max_words):
                chunk = " ".join(words[i : i + max_words])
                new_list.append(chunk)
    return new_list


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
def server_login(user: User):

    hashed_password = hash_password(user.password)

    user_details = get_user_details("users", user.username)

    all_details = get_all_user_details("users")

    passwords_check = [y["password"] for y in all_details]

    if user_details and hashed_password in passwords_check:
        return user_details
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorect username or password")


@app.post("/registerUser")
def server_register(user: User):

    hashed_password = hash_password(user.password)

    details = get_all_user_details("users")

    registered_username = [x["username"] for x in details]

    passwords_check = [y["password"] for y in details]

    if hashed_password not in passwords_check and user.username not in registered_username:
        user.password = hashed_password
        db.collection("users").add(user.model_dump())

        # Add to DB
        return {"Username": user.username, "password": hashed_password}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password Exists")


@app.post("/updateUser")
def server_user_update(doc_id, element, value):

    try:
        doc_ref = db.collection("users").document(doc_id)

        if not doc_ref.get().exists:
            return {"status": 404, "message": "No such document in firebase"}

        if element == "password":
            value = hash_password(value)

        if element == "CV_content" or element == "text_summary":
            doc_ref.update({element: value})
            doc_ref = get_user_details_by_id(doc_id=doc_id)
            if element == "CV_content":
                pdf_cv_content = value
                summary = doc_ref["text_summary"]
            else:
                summary = value
                pdf_cv_content = doc_ref["CV_content"]

            doc_ref = get_user_details_by_id(doc_id=doc_id)

            string_for_RAG_DB = pdf_cv_content + "\n" + summary

            list_for_RAG_DB = [x.strip() for x in string_for_RAG_DB.split(".") if x != ""]

            go_to_update = split_long_strings(list_for_RAG_DB)

            dump_RAG_DB(doc_id, go_to_update)

        doc_ref.update({element: value})

        return {"status": 200, "message": "Document was updated in firebase"}

    except Exception as e:
        return {"status": 500, "message": str(e)}
    

@app.post("/deleteUser")
def delete_document(document_id):
    try:
        doc_ref = db.collection("users").document(document_id)
        
        doc_ref.delete()

        delete_file(f"./Knowledge_faiss_index/{document_id}")
        delete_folder(f"./Knowledge_index_rows/{document_id}")
        
        print(f"Document {document_id} deleted from {"users"}.")

    except Exception as e:
        print(f"A apărut o eroare la ștergere: {e}")


@app.post("/chatCompletions")
def chat_with_CV(doc_id, question, RAG=False):

    print(question)
    print(RAG)
    try:
        doc_ref = get_user_details_by_id(doc_id=doc_id)

        pdf_cv_content = doc_ref["CV_content"]
        summary = doc_ref["text_summary"]
        full_skills = pdf_cv_content+"/n/n"+ summary
        if pdf_cv_content.strip() == "" or summary.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="PDF CV or Summary text were not uploaded"
            )
        
        if RAG == "True":

            rag_db = load_RAG_DB(doc_id)
            prompt = get_prompt(question, doc_ref["username"], rag_db)
        else:
            
            prompt = get_prompt(question, doc_ref["username"], False ,full_skills)        

        def stream():
            for chunk in getLLManswer(prompt=prompt, username=doc_ref["username"]):
                yield chunk

        add_Question_to_used(question=question, user_id= doc_id)

        return StreamingResponse(stream(), media_type="text/plain")

        # return getRAGanswer(prompt=prompt, username=doc_ref["username"])
        # return {"status": 200, "message": answer}

    except Exception as e:
        return {"status": 500, "message": str(e)}
    
@app.post("/chatAnalytics")
def chat_with_CV(doc_id):
    user = get_user_details_by_id(doc_id)
    return get_structured_questions_summary(user_dict=user)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)