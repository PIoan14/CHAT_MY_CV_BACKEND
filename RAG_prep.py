from datasets import Dataset
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import pandas as pd
import numpy as np
import time
import json
from datasets.search import FaissIndex
from datasets import load_from_disk

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def dump_RAG_DB(user_col_id, data_list):

    print(f"Dumping index for {user_col_id}")
    data = pd.DataFrame(data_list, columns=["chunks"])

    hf_dataset = Dataset.from_pandas(data)


    hf_dataset = hf_dataset.map(lambda x: {"embeddings": model.encode(x["chunks"], normalize_embeddings=True)})
   
    hf_dataset.add_faiss_index(column="embeddings", metric_type=faiss.METRIC_INNER_PRODUCT)
    print("Break")
    hf_dataset.save_faiss_index("embeddings", f"Knowledge_faiss_index/{user_col_id}")
    hf_dataset.drop_index("embeddings")
    hf_dataset.save_to_disk(f"Knowledge_index_rows/{user_col_id}")

    print(f"DB saved at Knowledge_faiss_index/{user_col_id}")
    
    
def load_RAG_DB(user_col_id):

    loaded_dataset = load_from_disk(f"Knowledge_index_rows/{user_col_id}")

    loaded_dataset.load_faiss_index(index_name="embeddings", file=f"Knowledge_faiss_index/{user_col_id}")

    return loaded_dataset

    

def call_RAG_DB(loaded_dataset, question):

    rag_knowledge = ""
    query_embedding = model.encode([question], normalize_embeddings=True)
    
    scores, examples = loaded_dataset.get_nearest_examples("embeddings", query_embedding[0], k=10)

    most_relevant_chunks = [x for x in examples["chunks"] if len(x.split()) > 3]

    for elem in most_relevant_chunks:
        rag_knowledge += f"- {elem}\n" 

    return rag_knowledge



