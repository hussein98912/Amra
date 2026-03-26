from django.core.cache import cache
from django.utils import timezone
 
ONLINE_COUNT_KEY = "online_count_{user_id}"
LAST_SEEN_KEY    = "last_seen_{user_id}"
TIMEOUT          = 60 * 60 * 24  # 24 hours
 
 
def user_connected(user_id: int) -> bool:
    """
    Increment connection counter.
    Returns True if this is the FIRST connection (user was offline).
    """
    count_key = ONLINE_COUNT_KEY.format(user_id=user_id)
    count     = cache.get(count_key, 0)
    was_offline = count == 0
    cache.set(count_key, count + 1, timeout=TIMEOUT)
    return was_offline
 
 
def user_disconnected(user_id: int) -> bool:
    """
    Decrement connection counter.
    Returns True if this was the LAST connection (user is now offline).
    """
    count_key = ONLINE_COUNT_KEY.format(user_id=user_id)
    count     = cache.get(count_key, 0)
    new_count = max(0, count - 1)
 
    if new_count == 0:
        # Truly offline — clean up and save last seen
        cache.delete(count_key)
        cache.set(
            LAST_SEEN_KEY.format(user_id=user_id),
            timezone.now().isoformat(),
            timeout=TIMEOUT
        )
        return True  # went offline
 
    cache.set(count_key, new_count, timeout=TIMEOUT)
    return False  # still has other tabs open
 
 
def is_user_online(user_id: int) -> bool:
    count = cache.get(ONLINE_COUNT_KEY.format(user_id=user_id), 0)
    return count > 0
 
 
def get_last_seen(user_id: int):
    return cache.get(LAST_SEEN_KEY.format(user_id=user_id))
 
 
def get_online_users(user_ids: list) -> dict:
    """Check online status for multiple users at once."""
    return {uid: is_user_online(uid) for uid in user_ids}