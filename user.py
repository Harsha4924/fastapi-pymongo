from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from models import Users,Login
from config import get_user_collection
from pymongo.collection import Collection
from passlib.context import CryptContext
import oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashpassword(password):
    return pwd_context.hash(password)

def check_password(plain_password,hashedone):
    return pwd_context.verify(plain_password, hashedone)



@router.post('/register')
async def register_user(new_user:Users,user_collection: Collection = Depends(get_user_collection)):
    try:
        if user_collection.find_one({'email':new_user.email}):
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

        hashed_password = hashpassword(new_user.password)

        user_data = {
            'name':new_user.name,
            'email':new_user.email,
            'password': hashed_password
        }

        one_user = user_collection.insert_one(user_data)

        return {
            "status": "success",
            "user_id": str(one_user.inserted_id),
            "message": "User registered successfully"
        }
    
    except HTTPException as http_exc:
        
        raise http_exc
    
    except Exception as e:
        print(f"Unexpected error: {e}")  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    
@router.post('/login')
async def login(credentials:OAuth2PasswordRequestForm = Depends(),user_collection: Collection = Depends(get_user_collection)):
    try:
        user = user_collection.find_one({'email':credentials.username})
        print(user['_id'])
        print(type(user['_id']))
        if not user:
            return 'invalid credentials'
        if not check_password(credentials.password,user['password']):
            return 'invalid credentials'
        
        check_user = str(user['_id'])
        
        access_token = oauth2.create_token(data={'user_id':check_user})
        print(access_token)
        return {'access_token':access_token,"token_type":"bearer"}
    except Exception as e:
        print(e)

