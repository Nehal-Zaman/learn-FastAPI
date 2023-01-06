from pydantic import BaseModel, EmailStr
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    #rating : Optional[int] = None

class Post(PostBase):
    pass

class UserBase(BaseModel):
    email: EmailStr

class UserCreated(UserBase):
    id: int
    class Config:
        orm_mode = True

class PostResponse(PostBase):
    user_id: int
    id: int
    user: UserCreated
    class Config:
        orm_mode = True

class AllPosts(BaseModel):
    Post: PostResponse
    votes: int
    class Config:
        orm_mode = True

class User(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    userID: Optional[int]

class Vote(BaseModel):
    post_id: int
    dir: int