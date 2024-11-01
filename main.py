from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session

from models import Base, User, Post
from database import engine, session_local
from schemas import UserCreate, User as DbUser, PostCreate, PostResponse

app = FastAPI()

# создаем БД на основе моделей:
Base.metadata.create_all(bind=engine)


# подключение к БД
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=DbUser)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> DbUser:
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()  # коммит в ручном режиме, т.к. авт. сохранение отключено
    db.refresh(db_user)  # обновляем БД

    return db_user


@app.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    db_user = db.query(User).filter(User.id == post.author_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_post = Post(title=post.title, body=post.body, author_id=post.author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.get("/posts/", response_model=List[PostResponse])
async def posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


# ____________________________________________
#
# @app.get("/")
# async def home() -> dict[str, str]:
#     return {"data": "message99"}
#
#
# @app.get("/contacts")
# async def contacts() -> int:
#     return 36
#
#
# @app.get("/index")
# async def index() -> int:
#     return 39
#
# posts = [
#     {'id': 1, 'title': 'News 1', 'body': 'Text 1'},
#     {'id': 2, 'title': 'News 2', 'body': 'Text 2'},
#     {'id': 3, 'title': 'News 3', 'body': 'Text 3'},
#     {'id': 4, 'title': 'News 4', 'body': 'Text 4'},
# ]
#
# @app.get("/items")
# async def items() -> list[dict]:
#     return posts
#
# @app.get("/items/{id}")
# async def items(id: int): -> dict:
#     for post in posts:
#         if post['id'] == id:
#             return post
#
#     raise HTTPException(status_code=404, detail='Post not found')
#
# @app.get("/search")
# async def search(post_id: Optional[int] = None) -> dict:
#     if post_id:
#         for post in posts:
#             if post['id'] == post_id:
#                 return post
#         raise HTTPException(status_code=404, detail='Post not found')
#     else:
#         return{"data": "No post id provided"}
