from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

import app.models as models
from app.schemas import UserCreated, User, Token, TokenData
from app.database import get_db
from app.utils import hash, verify_pwd
from app.oauth2 import create_access_token, get_current_user

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserCreated)
def create_user(user: User, db: Session = Depends(get_db)):
    user_exists = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'user with email: {user.email} already exists.'
        )
    user.password = hash(user.password)
    userObj = models.User(**user.dict())
    db.add(userObj)
    db.commit()
    db.refresh(userObj)

    return userObj

@router.get('/{id}', response_model=UserCreated)
def get_single_user(id: int, db: Session = Depends(get_db), user_data: TokenData = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id: {id} does not exists.'
        )

    if user.id != user_data.userID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'user with id: {user_data.userID} is not authorized to view user with id: {user.id}'
        )
        
    return user

@router.post('/login', response_model=Token)
def login_user(user: User, db: Session = Depends(get_db)):
    user_in_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user_in_db or not verify_pwd(user.password, user_in_db.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='invalid credentials.'
        )
    # create token and return
    return {
        'access_token': create_access_token({'userID': user_in_db.id}),
        'token_type': 'bearer'
    }