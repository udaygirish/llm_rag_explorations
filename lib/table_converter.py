import json
import pandas as pd 
from openai import OpenAI
from tqdm import tqdm , trange

def template_text_formatting(dataframe, custom_prompt_definition:dict = None) -> list:
    out_list = []
    if custom_prompt_definition is not None:
        # USUALLY CYSTOM PROMPT should be something related to header or modified version 
        # of the header
        # Create a string of the text
        for i in range(len(dataframe)):
            temp_text = ""
            for col in dataframe.columns:
                temp_text += f"{custom_prompt_definition[col]}: {dataframe[col][i]},"
            out_list.append(temp_text)
    else:
        # If custom prompt is not provided, then just use the column name
        for i in range(len(dataframe)):
            temp_text = ""
            for col in dataframe.columns:
                temp_text += f"{col}: {dataframe[col][i]},"
            out_list.append(temp_text)
                
    return out_list

def language_modelled_text(template_formatted_text, model_name="llama", model_url="http://localhost:1234/v1", api_key="lm-studio") -> list:
    # prompt = "You're are language model who is working on a structured dataset. \
    #          Now I want you to convert every row of the dataset into a text format. \
    #         construct a flowable text format taking column as the primary key. \
    #             For example, a dataset is given with column names Name of the person, Age of the person, Disease \
    #             the output should be like this: Person <Name of the Person> is <Age of the Person> years old and is suffering from <Disease>.\
    #                 I don't want code execute the code if needed i want the result as text"
    prompt = "You're are language model who is working on a structured dataset. \ Convert the given text so that it makes sense and readable.  \ I dont want code execute the code if needed i want the result as text"
    
    out_list = []     
    # print("Template Formatted Text: ", template_formatted_text)
    for i in tqdm(template_formatted_text):
        # Hit the API with [prompt + template_formatted_text]
        
        prompt = {"Your_task": prompt,
                "Data": i}
        
        # Convert prompt to a string
        prompt_str = prompt #json.dumps(prompt)
        
        # Hit the API with prompt_str
        # Get the response
        local_client = OpenAI(base_url=model_url, api_key=api_key)
        completion = local_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt_str["Your_task"]},
                {"role": "user", "content": prompt_str["Data"]},
            ],
            temperature=0.7,
        )
    
        # Convert the response to a list of strings
        text = completion.choices[0].message
        out_list.append(text)
    
    return out_list

