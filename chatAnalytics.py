from pydantic import BaseModel
from chat_llm import client
from config import get_config

config = get_config()

def get_structured_questions_summary(user_dict):

    try:
        questions = user_dict["questions"]
    except :
        return """To get the best results, please provide a detailed CV and a comprehensive summary of your professional background. The more specific the data, 
        the more tailored the insights will be.
Once our conversation exceeds 5 interactions, the system will automatically generate a personalized analytics dashboard. This report will visualize key themes, recurring topics, 
and data-driven insights based on the specific questions asked about your profile."""
    

    if len(questions) < 5:
        return """To get the best results, please provide a detailed CV and a comprehensive summary of your professional background. The more specific the data, 
        the more tailored the insights will be.
Once our conversation exceeds 5 interactions, the system will automatically generate a personalized analytics dashboard. This report will visualize key themes, recurring topics, 
and data-driven insights based on the specific questions asked about your profile."""
    
    else:
        
        paper_text =" || ".join(user_dict["questions"])
        messages = [
            {
                "role": "system", 
                "content": """Those questions were asked about the current user's skills from CV. 
                You must devide them into 4-5 main cathegories, and provide a json with each cathegory
                and the count of the questions inside. The cathegories must be
                as specific as possible, NEVER use too generic cathegories. One of the keys MUST be called "off topic", even if there are no off topic Questions.
                As a las key I would like a direct summary of what the user should 
                focus on based on the questions provided and be as detailed as possible. IMPORTANT: the summary is addressed to the user
                Please use json for answer at the second person as you. YOU MUST INCLUDE ALL THE QUESTIONS IN ONE OF THE TOPICS
                NEVER OMIT ANY QUESTION"""
            },
            {
                "role": "user", 
                "content": paper_text
            }
        ]

    response = client.chat.completions.create(
        messages=messages,
        model=config["model"]["name"],
        response_format={"type": "json_object"}
    )

    structured_data = response.choices[0].message.content
    print(structured_data)
    return structured_data

