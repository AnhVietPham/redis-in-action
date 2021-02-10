import threading
import time
import unittest
import uuid

import redis

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25
client = redis.Redis(host='127.0.0.1', port=6379)


def publisher(n):
    time.sleep(1)
    for i in range(n):
        client.publish('channel', i)
        time.sleep(1)


def run_pubsub():
    threading.Thread(target=publisher, args=(3,)).start()
    pubsub = client.pubsub()
    pubsub.subscribe(['channel'])
    count = 0
    for item in pubsub.listen():
        print(item)
        count += 1
        if count == 4:
            pubsub.unsubscribe()
        if count == 5:
            break


def add_to_cart(conn, session, item, count):
    if count <= 0:
        conn.hrem('cart:' + session, item)
    else:
        conn.hset('cart:' + session, item, count)


def update_token_using_set(conn, token, user, item=None):
    timestamp = time.time()
    conn.hset('login:', token, user)
    conn.zadd('recent:', {token: timestamp})
    if item:
        conn.zadd('viewed:' + token, {item: timestamp})
        conn.zremrangebyrank('viewed:' + token, 0, -26)


# <start id="exercise-update-token"/>
def update_token_using_list(conn, token, user, item=None):
    timestamp = time.time()
    conn.hset('login:', token, user)
    conn.zadd('recent:', token, timestamp)
    if item:
        key = 'viewed:' + token
        conn.lrem(key, item)
        conn.rpush(key, item)
        conn.ltrim(key, -25, -1)
        conn.zincrby('viewed:', item, -1)


# <end id="exercise-update-token"/>

class TestCh03(unittest.TestCase):
    def setUp(self):
        import redis
        self.conn = redis.Redis(db=15)

    def test_update_token_using_set(self):
        conn = self.conn
        token = str(uuid.uuid4())
        update_token_using_set(conn, token, 'username', 'itemX')
        print("And add an item to the shopping cart")
        add_to_cart(conn, token, "itemY", 3)

    # def test_update_token_using_list(self):


if __name__ == '__main__':
    # unittest.main()
    run_pubsub()
