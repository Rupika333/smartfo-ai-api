from fastapi import APIRouter, Depends
import json
from ruamel.yaml import YAML
import yaml
import io
from config.azure import client
from config.mongo import collection_1,collection_2
from models.data import Item,YamlBody,UpdateBody
from fastapi import Depends
from fastapi.responses import JSONResponse,FileResponse
from bson.objectid import ObjectId
from loguru import logger as log
from api.auth import isUser
from fastapi import APIRouter
from config.task_config import task_config
import os
from fastapi.responses import PlainTextResponse
from bson import ObjectId
from loguru import logger as log
from pymongo import MongoClient

 
user_router = APIRouter(prefix="/v1/user", tags=['user'])

history_file="chat_history.txt"





def log_chat_history(user_query, response, history_file="chat_history.txt"):

    chat_entry = f"User Query: {user_query}\n" \
                 f"Response: {response}\n\n"

    with open(history_file, "a") as file:
        file.write(chat_entry)

def clear_chat_history():

    if os.path.exists(history_file):
        os.remove(history_file)

def validate_account_number(field_value):
    global account_number_valid
    result = collection_1.find_one({"Account Number": int(field_value)})
    
    if result:

        message = "Account number validated successfully"  
        return message
    else:
        account_number_valid = False
        print(account_number_valid)
        message = f"Invalid account number {field_value}. Please provide once again."
        return message

def validate_pid(field_value):
    global pid_valid
    result = collection_2.find_one({"Pid": field_value})
    
    if result:
        message =  "PID validated successfully"  
        return message
    else:
        pid_valid = False
        message = f"Invalid PID {field_value}. Please provide once again."
        return message





predefined_intents = [
    {"intent": task_name, "description": task_config[task_name]["description"]}
    for task_name in task_config
]
 

predefined_intents_str = "\n".join([f"{intent['intent']}: {intent['description']}" for intent in predefined_intents])
 
def prompt_template_llm(query):
    Instructions = f"""\
    1. Fill out the task template for all fields that are relevant to the query.
    2. Use the inputs provided only as a reference for data extraction.
    3. Leave any fields that are not relevant to the query blank. Do not fill any field with "None". You can fill with "No Context".
    4. Do not generate a new template. If needed, add additional required components under the relevant section in case it is required based on the query.
    5. The intent should match exactly one of the following from the list of predefined intents. Do not generate any other similar intent names.only extract the intent from the query.Dont extarct any other information.
    6. Your response should consist of exactly one JSON object, formatted as key-value pairs. Example shown below:
    {{
        "intent": "A short title or classification for the given task (Use only these types: {predefined_intents_str})"
    }}
    7. The "intent" should be a short description, keyword, or title summarizing the task query.
    """
   
    prompt = f"""
    [INST]:
    {Instructions}
    query: {query}
    """
    return prompt
 
def prompt_template_field_extraction(query, required_fields, optional_fields):
    Instructions = f"""
    Your task is to extract the following fields from the user's query and return them as key-value pairs in a JSON object.
 
    **Required Fields**: {', '.join(required_fields)}
    **Optional Fields**: {', '.join(optional_fields)}
 
    For each field, if it is found in the query, extract the corresponding value.
    If a field is not mentioned, set its value to "No Context".

 
    Additionally, please identify any missing **required** fields (those that are necessary for the task) and list them explicitly.

    while extracting the fields , if any special charaters present in the field it should be included mandatorily.
    special characters: !@#@$%^&*()
    for example : 
        pid: #34567777
 
    Your response should be in the following JSON format:
     {{
        "fields": {{
            # Extract both required fields and optional fields in a key value pair.
            for example:
            "account_number": "Extracted account number"
            In the above format all the required fields and optional fields should be extracted.
        }},
        "missing_required_fields": [
            # List missing required fields here .
            # For example: ["account_number", "phone"]
        ]
        When a missing field is detected and the user provides that information, you need to extract it without reprocessing the entire query.
        After extracting the fields in the first pass, check if there are any missing fields.
        if there are missing fields, prompt the user with those specific fields to be filled in.
        Once the user provides the missing field(s), extract them from the new input and proceed with the task.

        Instructions : If the missing required fields is provided by the user please update the extracted fields 
        with the provided details.

        For suppose, if the user provides the department as the missing required fields, fill the extracted field with the provided input.

    }}
    """
    prompt = f"""
    [INST]:
    {Instructions}
    query: {query}
    """
    return prompt

def prompt_template_missing_fields(query, missing_required_fields,extracted_required_fields):

    Instructions = f"""
    Your task is to extract the missing **required** fields from the user's query.
    We have previously identified that the following fields are missing:

    **Missing Required Fields**: {', '.join(missing_required_fields)}

    Below are the fields that have already been extracted for this query:
    {json.dumps(extracted_required_fields, indent=2)}

    

    Dont extract the fields that already been extracted. 

    For each of these fields, please extract their corresponding value from the provided query.
    If a field is mentioned in the query, extract its value and update the list of extracted_required_fields.
    If a field is not mentioned, leave it as "No Context".

    while extracting the fields , if any special charaters present in the field it should be included mandatorily.
    special characters: !@#@$%^&*()
    for example : 
        pid: #34567777

    Your response should be in the following JSON format:
    {{
        "fields": {{
            # Extract  required fields  in a key value pair.
            for example:
            "department": "Extracted department"
            In the above format all the required fields should be extracted.only return fields.
        }},
    """
    
    prompt = f"""
    [INST]:
    {Instructions}
    query: {query}
    """
    return prompt


 
import pandas as pd
 

df=pd.DataFrame(list(collection_1.find()))
#df = df = pd.read_json('C:/Users/rupika02/Documents/charter/Charter.accounts.json')
df.drop('_id', axis=1, inplace=True)
dp=pd.read_csv(r'C:\Users\rupika02\Documents\charter\dropdown 2.csv')
tec=pd.read_csv(r'C:\Users\rupika02\Documents\charter\tecidmap 2.csv')
print("tec",tec)


current_intent = None
extracted_required_fields = {}
missing_required_fields = []
missing_fields_requested=None
missing_fields_request_done=None
confirmation_fields = {}
updation = None
account_number_valid = True
pid_valid = True



@user_router.post("/search")
async def llmsearch(item: Item):
    global current_intent
    global missing_fields_requested
    global missing_required_fields
    global extracted_required_fields
    global description
    global fields_one
    global missing_fields_request_done
    global update_message
    global confirmation_fields
    global updation
    global account_number_valid
    global pid_valid
    

    try:
        query = item.query
        print(f"Received query: {query}")
        print(f"Current Intent: {current_intent}")

        if current_intent is None:
            prompt_1 = prompt_template_llm(query)

            completion_1 = client.chat.completions.create(
                model='gpt4',
                messages=[{
                    "role": "system", "content": "Your AI assistant for extracting the details in the given text to variables in JSON"
                }, {
                    "role": "user", "content": prompt_1
                }]
            )

            gpt_response_1 = completion_1.choices[0].message.content
            log.info("Response fetched successfully from LLM (Intent classification)")

            description = json.loads(gpt_response_1)
            selected_intent = description["intent"]
            current_intent = selected_intent
            print(f"Selected Intent: {current_intent}")

        else:
            selected_intent = current_intent

        required_fields = task_config[selected_intent]["required_fields"]
        optional_fields = task_config[selected_intent]["additional_fields"]

        if missing_fields_requested is None:
            prompt_2 = prompt_template_field_extraction(query, required_fields, optional_fields)

            completion_2 = client.chat.completions.create(
                model='gpt4',
                messages=[{
                    "role": "system", "content": "Extract required and optional fields from the user's query, and detect missing required fields."
                }, {
                    "role": "user", "content": prompt_2
                }]
            )

            gpt_response_2 = completion_2.choices[0].message.content
            log.info("Response fetched successfully from LLM (Field extraction)")

            extracted_fields = json.loads(gpt_response_2)
            fields_one = extracted_fields["fields"]

            extracted_required_fields = {field: fields_one.get(field, "No Context") for field in required_fields}
            missing_required_fields = [field for field in required_fields if fields_one.get(field) == "No Context"]

            print(f"Extracted Fields: {extracted_required_fields}")
            print(f"Missing Required Fields: {missing_required_fields}")

            if not missing_required_fields:
                confirmation_fields = {}
               

                for field, value in fields_one.items():
                    confirmation_fields[field] = value

                confirmation_fields["Are these details correct? (yes/no)"] = ""
                missing_fields_request_done = 1
                missing_fields_requested = True

                

                log_chat_history(item.query, confirmation_fields)

                return PlainTextResponse(content=f"Please confirm the details below:\n{json.dumps(confirmation_fields, indent=1)}")

            else:
                missing_fields_prompt = "Please provide the following required details: "
                missing_fields_prompt += "\n".join(missing_required_fields)

                log_chat_history(query, missing_fields_prompt)
                missing_fields_requested = True
                missing_fields_request_done = None  

                return PlainTextResponse(content=missing_fields_prompt.strip())

        elif missing_fields_request_done is None:
            while missing_required_fields:
                print("i am here")
                prompt_3 = prompt_template_missing_fields(query, missing_required_fields, extracted_required_fields)

                completion_3 = client.chat.completions.create(
                    model='gpt4',
                    messages=[{
                        "role": "system", "content": "Extract the missing required fields from the user query."
                    }, {
                        "role": "user", "content": prompt_3
                    }]
                )

                gpt_response_3 = completion_3.choices[0].message.content
                log.info("Response fetched successfully from LLM (Extract missing fields)")

                try:
                    extracted_fields_3 = json.loads(gpt_response_3)
                    fields_upd = extracted_fields_3.get("fields", {})

                    for field, value in fields_upd.items():
                        if field in fields_one:
                            fields_one[field] = value

                    print(f"Updated Fields after extraction: {fields_one}")
                except json.JSONDecodeError as e:
                    log.error(f"Failed to decode GPT response: {e}")
                    continue

                missing_required_fields = [field for field in required_fields if fields_one.get(field) == "No Context"]

                if missing_required_fields:
                    missing_fields_prompt = "Please provide the following required details: "
                    missing_fields_prompt += "\n".join(missing_required_fields)

                    log_chat_history(query, missing_fields_prompt)
                    return PlainTextResponse(content=missing_fields_prompt.strip())

            missing_fields_request_done = True
            confirmation_fields = {}
               

            for field, value in fields_one.items():
                    confirmation_fields[field] = value

            confirmation_fields["Are these details correct? (yes/no)"] = ""
            missing_fields_request_done = 1
            missing_fields_requested = True

                

            log_chat_history(item.query, confirmation_fields)

            return PlainTextResponse(content=f"Please confirm the details below:\n{json.dumps(confirmation_fields, indent=2)}")

        validation_fields = task_config[selected_intent]["validation_fields"]

        validation_status = []

        


        if query.lower() == 'yes':
            for field in validation_fields:
                if field in fields_one:
                    field_value = fields_one[field]

                if field == "account_number":
                    field_value = int(field_value)
                    
                    validation_status.append(validate_account_number(field_value))
                  
                    
                elif field == "pid":
                 
                    validation_status.append(validate_pid(field_value))
                  

            return validation_status

        elif query.lower() == 'no':
                    

                    updation = True
                    update_message = "Please provide the updated fields in the format: field_name: new_value"
                    log_chat_history(query, update_message)

                    return PlainTextResponse(content=update_message)
        
        if updation is not None:

            
            updated_fields = query.split(',')

        
            for updated_field in updated_fields:
            
                field, value = updated_field.split(':')

            
                field = field.strip()
                value = value.strip()

                
                if field in fields_one:
                    fields_one[field] = value  

                else:
                    
                    update_message += f"\nThe field '{field}' does not exist in the current data."
                
                print(fields_one)
                updation = True
                print(updation)

                for field in validation_fields:
                    if field in fields_one:
                            field_value = fields_one[field]

                    if field == "account_number":
                        field_value = int(field_value)
                        
                        validation_status.append(validate_account_number(field_value))
                    
                        
                    elif field == "pid":
                    
                        validation_status.append(validate_pid(field_value))
                  

                return validation_status
            
      
            
            
        if not account_number_valid:
            account_number = query
            print(account_number)
            while not account_number_valid:
                    
                    validation_status.append(validate_account_number(account_number))
                    print(account_number_valid)
                    if not account_number_valid:
                        return validation_status
                    else:
                        
                        fields_one["account_number"] = account_number
                        account_number_valid = True
                        print(fields_one)
        
        if not pid_valid:
            pid = query
            print(pid)
            while not pid_valid:
               
                    validation_status.append(validate_pid(pid))
                    print(pid_valid)
                    if not pid_valid:
                         return validation_status
                    else:
                        
                        fields_one["pid"] = pid
                        pid_valid = True
                        print(fields_one)

      
    
    except Exception as e:
        log.error(f"Error in processing the query: {str(e)}")
        return PlainTextResponse(content="Error in Processing")


clear_chat_history()
    

   
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
def store(query, description, value, metadata):
    try:
        status = collection.insert_one({
            "Query" : query,
            "Description" : description,
            "Template" : json.dumps(value),
            "userId": 123,
            "Metadata" : metadata
        })
        if(status.acknowledged):
            log.info("Successfully saved in the db")
        else:
            log.warning("Error in storing the DB")
            return ""
        return str(status.inserted_id)
   
    except Exception as e:
        log.error("Exception",e)
        return Exception
 
 
 
def yamlConvertion(jsonValue):
   
    yml = YAML()
    yml.preserve_quotes = True
    yml.indent(mapping=2, sequence=4, offset=2)
 
    stream = io.StringIO()
    yml.dump(jsonValue,stream)
    yaml_res = stream.getvalue()
 
    headers = {
        'content-type':'application/yaml',
        'Content-Disposition':'attachment; filename = "yaml_res.yaml"'
    }
    return yaml_res
 
file_path = "template.yaml"
 
 
@user_router.get("/getTemplates/{userId}")
async def getTemplates(userId:int):
    log.info("Fetching the templates")
    objects = list(collection.find({'userId': userId}))
    for data in objects:
        data['_id'] = str(data['_id'])
    log.info("Templates fetched successfully")
    return objects
 
 
 
@user_router.patch("/updateCollection")
async def updateCollection(item:UpdateBody):
    try:
        log.info("update collection started")
        document_id = ObjectId(item.objId)
        value = json.loads(item.template)
        status = collection.update_one(
            {'_id':document_id},
            {'$set':{'Template':json.dumps(value)}}
        )
        log.info("collection updated succesfully")
        return status.acknowledged
    except Exception as e:
        log.error("Exception",e)
        return Exception
 
@user_router.post("/YamlConverter/")
async def getYamlFile(item:YamlBody):
    try:
        log.info("File writing started")
        json_val= json.loads(item.json_value)
        result = yamlConvertion(json_val)
        with open(file_path, 'w') as yaml_file:
            yaml_file.truncate()
        with open(file_path, 'a') as yaml_file:
            yaml_file.write(result)
        with open(file_path) as f:
            data = f.read()
        log.info("Get yamlFile successful")
        return FileResponse(path=file_path,media_type="text/yaml",filename="template.yaml")
    except Exception as e:
        log.error(e)
        return Exception
 
def findDB(docId):
    try:
        objId = ObjectId(docId)
        Obj = collection.find_one({'_id':objId})
        if Obj and 'Template' in Obj:
            template_value = Obj['Template']
        else:
            return None
        return template_value
    except Exception as e:
        log.error("Exception",e)
        return Exception