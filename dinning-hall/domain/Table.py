import uuid
import time
import random
import logging

logger = logging.getLogger(__name__)


class Table:
    def __init__(self, dh, i):
        self.dh = dh
        self.order_id = None
        self.status = 'FREE'
        self.id = i

    def generate_order(self):
        time.sleep(random.randint(1, 4) * self.dh.TIME_UNIT)
        max_wait = 0
        items = []
        for i in range(random.randint(1, 5)):
            food = random.choice(self.dh.config['menu'])
            if max_wait < food['preparation-time']:
                max_wait = food['preparation-time']
            items.append(food['id'])
        max_wait *= 1.6
        order_id = uuid.uuid4().hex[0:7]
        order = {
            'id': order_id,
            'items': items,
            'priority': random.randint(1, 5),
            'max_wait': max_wait,
            'table_id': self.id
        }
        self.order_id = order_id
        self.status = 'WAITING_FOR_ORDER'
        logger.info(f'{self.dh.name} Table-{self.id} generated new order-{order_id}')
        return order

    def serve(self):
        logger.info(f'{self.dh.name} Table-{self.id} order-{self.order_id} will free the table in a few seconds')
        time.sleep(random.randint(2, 4) * self.dh.TIME_UNIT)
        self.order_id = None
        self.status = 'FREE'
        self.dh.free_tables.put_nowait(self)
