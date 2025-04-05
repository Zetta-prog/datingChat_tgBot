from database.crud import search_finder, set_state_search, get_state, search_finder_with_filters
import asyncio

async def search(user_id: int):
    await set_state_search(user_id)
    
    while await get_state(user_id) == 'search':
        if await search_finder(user_id):
            return True
        await asyncio.sleep(0.5)
    if await get_state(user_id=user_id) == 'found':
        return True
    return False

async def search_with_filters(user_id: int):
    await set_state_search(user_id)
    
    while await get_state(user_id) == 'search':
        if await search_finder_with_filters(user_id=user_id):
            return True
        await asyncio.sleep(0.5)
    if await get_state(user_id=user_id) == 'found':
        return True
    return False
