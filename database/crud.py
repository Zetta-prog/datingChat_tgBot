from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm.attributes import flag_modified

from database.init_database import User, engine


async_session = async_sessionmaker(bind=engine)


async def check_user(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
    if user:
        return user
    else:
        return None

async def add_user(user_id: int):
    data = await check_user(user_id=user_id)
    if data is None:
        async with async_session() as session:
            user = User(user_id=user_id)
            session.add(user)
            await session.commit()        

async def add_gender(user_id: int, gender: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.gender = gender
        await session.commit()

async def add_name(user_id: int, name: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.name = name
        await session.commit()  

async def add_age(user_id: int, age: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.age = age
        await session.commit()  

async def commit_form(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.ready = True
        await session.commit()  

async def set_state_search(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.chat_state = 'search'
        await session.commit() 

async def set_state_exit(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.chat_state = 'exit'
        await session.commit() 

async def get_state(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.chat_state

async def get_companion_id(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.companion_id

async def search_finder(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        finder = await session.execute(select(User).where(
            and_(
                User.chat_state == 'search',
                User.user_id != user_id,
                or_(
                        User.filters == None,
                        User.filters == {'gender': user.gender}
                    )
            )
        ))
        finder = finder.scalar()
        if finder:            
            finder.chat_state, user.chat_state = 'found', 'found'
            
            user.companion_id = finder.user_id
            finder.companion_id = user_id
            await session.commit()
            return True
    return False

async def get_filters(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.filters

async def add_filter_gender(user_id: int, filter_gender: str):
    async with async_session() as session:
        user = await session.get(User, user_id) 
        user.filters = {'gender':filter_gender}
        await session.commit()

async def reset_filter_gender(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id) 
        user.filters = None
        await session.commit()

async def search_finder_with_filters(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        finder = await session.execute(
            select(User).where(
                and_(
                    User.gender == user.filters.get('gender'),
                    User.chat_state == 'search',
                    User.user_id != user_id,
                    or_(
                        User.filters == None,
                        User.filters == {'gender': user.gender}
                    )
                )
            )
        )
        finder = finder.scalars()
        if finder:
            finder.chat_state, user.chat_state = 'found', 'found'
            
            user.companion_id = finder.user_id
            finder.companion_id = user_id
            await session.commit()
            return True
    return False

async def amount_of_users():
    async with async_session() as session:
        amount = await session.scalar(func.count(User.user_id))
        return amount

async def get_all_users_id():
    async with async_session() as session:
        users = await session.execute(select(User.user_id))
        users = users.scalars().all()
        return users

async def like_user(from_user_id: int, to_user_id: int):
    async with async_session() as session:
        to_user = await session.get(User, to_user_id)

        if to_user.raiting is None:
            to_user.raiting = {'likes': []}

        if 'likes' not in to_user.raiting:
            to_user.raiting['likes'] = []

        if from_user_id in to_user.raiting['likes']:
            return False

        to_user.raiting['likes'].append(from_user_id)
        flag_modified(to_user, 'raiting')
        await session.commit()
        return True

async def dislike_user(from_user_id: int, to_user_id: int):
    async with async_session() as session:
        to_user = await session.get(User, to_user_id)

        if to_user.raiting is None:
            to_user.raiting = {'dislikes': []}

        if 'dislikes' not in to_user.raiting:
            to_user.raiting['dislikes'] = []
        
        if from_user_id in to_user.raiting['dislikes']:
            return False

        to_user.raiting['dislikes'].append(from_user_id)
        flag_modified(to_user, 'raiting')
        await session.commit()
        return True
