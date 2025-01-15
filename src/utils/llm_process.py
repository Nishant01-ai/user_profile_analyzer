import json
import ast
from openai import OpenAI
from src.config import CONFIG
from src.utils.log_file import logger



def create_marketing_content(customer_info:str)->str:
    """
    This method generates cutomized marketing content based on the user profile details
    """
    
    api_key = CONFIG["OPENAI_API_KEY"]
    client = OpenAI(api_key = api_key)
    with open("src/config/prompts.json", encoding="utf8") as file:
        instruction_context = json.load(file)

    with open("src/config/cluster_descriptions.json", encoding="utf8") as file:
        profile_description = json.load(file)
        
    customer_cluster_id = str(customer_info["cluster_user"])
    user_profile = profile_description[customer_cluster_id]
    customer_info["user_profile_info"] = user_profile
           
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"{instruction_context}"},
            {
                "role": "user",
                "content": f"Generate customized marketing email using the given information: {customer_info}"
            }
        ]
    )
    mktg_content = completion.choices[0].message.content
    content_ = ast.literal_eval(mktg_content)
    email_body = content_["email_body"]
    tag_line = content_["tag_line"]

    return email_body, tag_line

