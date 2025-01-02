from fastapi import HTTPException, APIRouter, Depends
from models.data import User
from api.auth import oauth2_scheme,create_password_hash,isAdmin
from loguru import logger as log
from config.mongo import users

admin_router = APIRouter(prefix="/v1/admin", tags=['admin'])

@admin_router.post("/addUser", dependencies = [Depends(isAdmin)])
def addUser(user:User):
    try:
        status = users.insert_one({
            'userName' : user.userName,
            'password' : None,
            'emailId' : user.emailId,
            'role': user.role
        })
        if(status.acknowledged):
            log.info("Admin added a user successfully")
        else:
            log.warning("Error in adding a user by admin")
            return ""
        return {"userId": str(status.inserted_id), "detail": "user Added Successfully"}
    
    except Exception as e:
        log.error("Exception",e)
        return Exception 


