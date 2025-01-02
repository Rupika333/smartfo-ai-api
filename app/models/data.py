from pydantic import BaseModel


class Credentials(BaseModel):
    username : str
    password : str

class Item(BaseModel):
    query : str

class YamlBody(BaseModel):
    json_value : str

class UpdateBody(BaseModel):
    objId : str
    template : str

class User(BaseModel):
    userName:str
    emailId:str
    role:str

class Register(BaseModel):
    userName:str
    password:str
    