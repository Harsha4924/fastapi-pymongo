from typing import Optional
from pydantic import BaseModel,Field
from datetime import datetime


class Products(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    createdat: datetime = Field(default_factory=datetime.now)

    
    @property
    def createdat_timestamp(self) -> int:
        return int(self.createdat.timestamp())
    
    class Config:
        arbitrary_types_allowed = True
class Users(BaseModel):

    email:str
    name:str
    password: str

class Login(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None