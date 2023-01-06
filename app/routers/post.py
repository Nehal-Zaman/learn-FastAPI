from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, status, HTTPException, Response, APIRouter

import app.models as models
from app.schemas import PostResponse, Post, TokenData, AllPosts
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

# import psycopg2
# import time

# while True:
#     try:
#         conn = psycopg2.connect(
#             host='localhost',
#             port=5433,
#             database='fastapi_db',
#             user='postgres',
#             password='31337',
#             cursor_factory=RealDictCursor
#         )
#         cursor = conn.cursor()
#         print("[*] Database connection successful.")
#         break

#     except Exception as e:
#         print("[-] Database connection failed.")
#         print(e)
#         time.sleep(2)

@router.get('/', response_model=List[AllPosts])
def get_posts(db: Session = Depends(get_db), user: TokenData = Depends(get_current_user), limit: int = 10, skip: int = 0, search: str = ''):
    # Through psycopg2
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()

    #posts = db.query(models.Post).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.get('/own', response_model=List[PostResponse])
def find_own_posts(db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    posts = db.query(models.Post).filter(models.Post.user_id == user.userID).all()
    return posts

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(payload: Post, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    # Through psycopg2
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING *""",
    #     (payload.title, payload.content, payload.published, payload.rating)
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(user.userID)
    new_post = models.Post(user_id = user.userID,**payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get('/{id}', response_model=PostResponse)
def get_single_post(id: int, db: Session = Depends(get_db)):
    # Through psycopg2
    # cursor.execute(
    #     """SELECT * FROM posts WHERE id = %s""",
    #     (id,)
    # )
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'post with id: {id} was not found.'
        )
    return post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_single_post(id: int, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    # Through psycopg2
    # cursor.execute(
    #     """DELETE FROM posts WHERE id = %s RETURNING *""",
    #     (id,)
    # )
    # post = cursor.fetchone()
    # conn.commit()
    #print(user.userID)
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'post with id: {id} was not found.'
        )

    if post.first().user_id != user.userID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Bhosdike IDOR socha tha kya XD'
        )

    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@router.put('/{id}', response_model=PostResponse)
def update_single_post(id: int, post: Post, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    # Through psycopg2 
    # cursor.execute(
    #     """UPDATE posts SET title=%s, content=%s, published=%s, rating=%s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, post.rating, id)
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_in_db = post_query.first()

    if not post_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'post with id: {id} was not found.'
        )

    if post_in_db.user_id != user.userID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Not authorized to perform the action.'
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()