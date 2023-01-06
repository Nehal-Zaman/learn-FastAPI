from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

import app.models as models
from app.schemas import Vote, TokenData
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Votes']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_or_delete_vote(vote: Vote, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.User.id == user.userID)
    if vote.dir == 1:
        if vote_query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'user {user.userID} has already voted post {vote.post_id}'
            )
        new_vote = models.Vote(post_id = vote.post_id, user_id = user.userID)
        db.add(new_vote)
        db.commit()
        return {'message': 'successfully added vote'}
    else:
        if not vote_query.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'user {user.userID} has not voted post {vote.post_id}'
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {'message': 'successfully deleted vote'}