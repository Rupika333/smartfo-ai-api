
from config.fastApi import app
from api.routers.user import user_router
from api.routers.admin import admin_router
from api.auth import auth_router
from fastapi.middleware.cors import CORSMiddleware
import os

os.environ["CURL_CA_BUNDLE"] =''


app.get('/')
def home():
    return {"message": "TOSCA template generation backend is up and running"}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)

origins=["http://localhost:*",
         "http://localhost:3000",
         "http://localhost:3001",
         "http://127.0.0.1:5501"]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
import uvicorn
if __name__ == '__main__': 
    #uvicorn.run(app,host='10.81.76.164',port=8000)
    uvicorn.run(app,host='localhost',port=8001)