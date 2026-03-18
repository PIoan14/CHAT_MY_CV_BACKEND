import os
from openai import OpenAI
from dotenv import load_dotenv
from config import get_config
import requests
import json

load_dotenv()

#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

config = get_config()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key= os.getenv("OPENAI_API_KEY"),
)
def get_prompt(question, user_name, pdf, summary):

    prompt = f"""

        Your job is to help answer questions about {user_name}s skillset using ONLY the provided information.

        Full document:
        {pdf}

        More information in a summary:
        {summary}

        Question about {user_name} potential skills:
        {question}

        Rules:
        - Use the summary and the document to answer the question.
        - Do not invent information.
        - If the answer is not present in the provided information, say ONLY: "I cannot provide an answer."
        - Be clear and concise and detailed
        - Act like there exist NO provided documents, you just know them BUT NEVER MENTION THEM
        - If you are asked for a skill which is not provieded in the data just say f"{user_name} has no knowledge in that domain".

        IMPORTANT:

        - Write the evaluation in a positive, promotional tone. Highlight strengths and potential. When mentioning missing skills, frame them as areas for growth rather than weaknesses. Avoid negative or critical phrasing. Emphasize the candidate’s suitability and potential for the role.
        - If you simple see greetings, just greet back and STOP.
        - If {user_name} has no skills provided for a specific domain, just mention "{user_name} is not suitable for this domain" ONLY, NOTHING MORE. 

        Answer:
    """

    return prompt

def getRAGanswer(prompt,username):

    completion = client.chat.completions.create(
        model = config["model"]["name"],
        #model = "Qwen/Qwen3-Coder-Next:novita",
        #model="meta-llama/Llama-3.3-70B-Instruct:groq",
        messages=[
            {
                "role": "system",
                "content": f"You are the personal assistant of {username}. You know nothing else except about {username}."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return completion.choices[0].message.content