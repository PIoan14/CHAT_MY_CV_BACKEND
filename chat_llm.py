import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key= os.getenv("OPENAI_API_KEY"),
)
def get_prompt(question, user_name, pdf, summary):

    prompt = f"""
       You are the personal assistant of {user_name}.

        Your job is to help {user_name} by answering questions using ONLY the provided information.

        Document summary:
        {summary}

        Full document:
        {pdf}

        Question from {user_name}:
        {question}

        Rules:
        - Use the summary and the document to answer the question.
        - Do not invent information.
        - If the answer is not present in the provided information, say: "I cannot provide an answer."
        - Be clear and concise and detailed
        - Act like there exist NO provided documents, you just know them BUT NEVER MENTION THEM

        Answer:
    """

    return prompt

def getRAGanswer(prompt):

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct:groq",
        messages=[
            {
                "role": "system",
                "content": "be clear"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return completion.choices[0].message.content