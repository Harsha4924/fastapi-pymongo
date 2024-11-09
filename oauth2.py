from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime,timedelta 
import models
from fastapi.security import OAuth2PasswordBearer

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "HARSHAQWT1234"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(data:dict):
    encode_data = data.copy()
    expiretime = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({'exp':expiretime})

    jwttoken = jwt.encode(encode_data,SECRET_KEY, algorithm=ALGORITHM)
    print('executed5')

    return jwttoken


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = models.TokenData(id=id)
        # print(token_data)
        # print(type(token_data))

    except JWTError:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data



def get_current_user(token: str = Depends(oauth2_scheme)):
    # return verify_jwt_token(token)
    token_data = verify_jwt_token(token)
    return token_data.id


