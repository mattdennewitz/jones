# -*- coding: utf-8 -*-

import json

import redis


class DumpArtworkToDatabase(object):
    def __init__(self, redis_hostname, redis_port, redis_db, queue_key):
        self.redis_hostname = redis_hostname
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.queue_key = queue_key

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_hostname=crawler.settings.get('REDIS_HOSTNAME', 'localhost'),
            redis_port=crawler.settings.get('REDIS_PORT', 6379),
            redis_db=crawler.settings.get('REDIS_DB', 0),
            queue_key=crawler.settings.get('REDIS_NEW_ARTWORK_KEY', 'naq'),
        )

    def open_spider(self, spider):
        self.client = redis.StrictRedis(host=self.redis_hostname,
                                        port=self.redis_port,
                                        db=self.redis_db)

    def process_item(self, item, spider):
        """Exports artwork to collection database
        """

        # flatten item elements
        flattened = {
            key: (','.join(item[key])
                  if isinstance(item[key], list)
                  else item[key])
            for key
            in item.keys()
        }

        # cast `on_display` field to boolean
        flattened['on_display'] = bool(int(flattened['on_display']))

        # shove into redis queue
        self.client.rpush(self.queue_key, json.dumps(flattened))

        return item
