from models.data import Credentials
from loguru import logger as log
from fastapi import HTTPException,APIRouter,Depends,status
from typing import Optional
from datetime import datetime,timedelta,timezone
from jose import JWTError, jwt
from config.mongo import users
from config.fastApi import app
from models.data import User,Register
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

auth_router = APIRouter(prefix='/auth/v1', tags=['auth'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/v1/login")

ALGORITHM = "HS256"
SECRET_KEY = ""

def create_password_hash(plain_password):
    return pwd_context.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try: 
        usr_name = form_data.username
        pwd = form_data.password
        user =  users.find_one({'userName':usr_name},{'_id':0})

        if( user['password'] == None or user['password'] == " " ):

            # raise HTTPException(
            #     status_code= status.HTTP_204_NO_CONTENT,
            #     detail= "Need to set the password"
            #)
            log.info("user verified")
            access_token_expires = timedelta(minutes=60)
            user['userName']='Bala'
            token = create_access_token( data={"user": user['userName']},
                expires_delta=access_token_expires
            )
            return {"access_token": token, "token_type": "bearer"}
        
        else:
            if(usr_name == user['userName'] and verify_password(pwd,user['password'])):
                log.info("user verified")
                access_token_expires = timedelta(minutes=60)
                token = create_access_token(
                    data={"user": user['userName']}, expires_delta=access_token_expires
                )
                return {"access_token": token, "token_type": "bearer"}
            else:
                log.info("User unauthorized")
                raise HTTPException(
                    status_code=404 ,detail="User not Found"
                )
    except Exception as e:
        log.error(e)
        return e.__cause__

@app.post("/register")
def createPassword(register:Register):
    userName =register.userName
    hashedPassword = create_password_hash(register.password)

    try:
        log.info("password update started")
        status = users.update_one(
            {'userName':userName},
            {'$set':{'password':hashedPassword}}
        )
        log.info("password updated succesfully")
        return status.acknowledged
    except Exception as e:
        log.error("Exception",e)
        return Exception

def verifyToken(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        userName : str = payload.get("user")
        if userName is None:
            raise HTTPException(status_code=403,detail="Token is invalid/expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")
    

def refreshJwtToken(currentToken):
    try:
        payload = jwt.decode(currentToken,SECRET_KEY,algorithms=[ALGORITHM])
        if(datetime.utcnow() > datetime.fromtimestamp(payload['exp'])):
            new_token = create_access_token(payload['user'])
            return new_token
        else:
            return currentToken
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Token has expired"
        )
    
@auth_router.post("/protected-route")
async def protected_route(token:str = Depends(oauth2_scheme)):
    refreshed_token = refreshJwtToken(token)
    return{"access_token":refreshed_token,"token_type":"bearer"}



    

def getActiveUser(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        log.info(datetime.fromtimestamp(payload['exp']))
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user =  users.find_one({'userName':username},{'_id':0})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def isAdmin(user: User = Depends(getActiveUser)):
    allowed_roles = ['admin']
    if user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return True

def isUser(user: User = Depends(getActiveUser)):
    allowed_roles = ['user', 'admin']
    if user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return True