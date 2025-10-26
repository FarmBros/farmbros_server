from typing import List, Optional

from aiocache import caches, Cache, RedisCache
import hashlib

caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'endpoint': "127.0.0.1",
        'port': 6379,
        'timeout': 1,
        'serializer': {
            'class': "aiocache.serializers.JsonSerializer",
        },
    }
})



def gen_user_key(user_id: str, *parts) -> str:
    return f"u:{user_id}:{':'.join(map(str, parts))}"

def gen_query_hash(filters: dict) -> str:
    if not filters:
        return "default"
    return hashlib.md5(
        str(sorted(filters.items())).encode()
    ).hexdigest()[:8]

async def invalidate_patterns(user_id: str, patterns: List[str]):
    try:
        keys_to_delete = []

        cache = caches.get('default')
        client = cache.client

        for pattern in patterns:
            full_pattern = gen_user_key(user_id, pattern)

            matching = [key async for key in client.scan_iter(match=full_pattern)]
            keys_to_delete.extend(matching)

        # Bulk delete
        if keys_to_delete:
             for key in keys_to_delete:
                await client.delete(key)
        return True
    except Exception:
        return False

async def invalidate_user_cache(user_id: str, resource: Optional[str] = None):
    if resource:
        await invalidate_patterns(user_id, [f"{resource}:*"])
    else:
        # Clear everything for this user
        await invalidate_patterns(user_id, ["*"])

async def clear_all_cache():
    """Clear the entire Redis cache"""
    try:
        cache = caches.get('default')
        client = cache.client
        await client.flushdb()
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False