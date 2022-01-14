import time
import queue
import logging
import threading
import itertools
from domain.cook import Cook

logger = logging.getLogger(__name__)

lock = threading.Lock()


class Kitchen:
    def __init__(self, port, dh_port, id_, cooks, ovens, stoves, food_list):
        self.port = port
        self.dh_port = dh_port
        self.id_ = id_
        self.cooks = [Cook(self, data['id'], data['name'], data['rank'], data['proficiency'], data['catch-phrase']) for i, data in enumerate(cooks)]
        self.food_items_q = queue.PriorityQueue()
        self.food_list = food_list
        self.order_list = []
        self.WAITING_COEFFICIENT = 2
        # https://stackoverflow.com/questions/40205223/priority-queue-with-tuples-and-dicts
        self.counter = itertools.count()
        self.ovens_q = queue.Queue(ovens)
        self.stoves_q = queue.Queue(stoves)

        self.nr_apparatuses = ovens + stoves

        for i in range(ovens):
            self.ovens_q.put_nowait(i)
        for i in range(stoves):
            self.stoves_q.put_nowait(i)

        logger.info(f'kitchen configured, cooks: {len(self.cooks)}, ovens: {self.ovens_q.qsize()}, stoves: {self.stoves_q.qsize()}')

    def start_kitchen(self):
        for cook in self.cooks:
            threading.Thread(target=cook.cook_work, name=f'K{self.id_}', daemon=True).start()

    def calculate_waiting_time(self, order):
        '''
        (A / B + C / D) * (E + F) / F
            where:
            - A = total preparing time for all foods from order which do not require apparatus
            - B = total sum of cooks proficiencies
            - C = total preparing time for all foods from order which require cooking apparatus
            - D = number of cooking apparatus
            - E = total number of foods which are in waiting list for current moment of time. Foods from orders which was registered by the kitchen but was not yet prepared
            - F = number of foods from current order
        '''

        lock.acquire()
        items = order['items']

        a, b, c, d, e, f = 0, 0, 0, 0, 0, 0

        d = self.nr_apparatuses
        e = self.food_items_q.qsize()
        f = len(items)

        for cook in self.cooks:
            b += int(cook.proficiency)

        for item in items:
            food = next((f for f in self.food_list if f['id'] == item), None)
            apparatus = food['cooking-apparatus']
            if apparatus is not None:
                c += int(food['preparation-time'])
            else:
                a += int(food['preparation-time'])

        lock.release()
        logger.info(f'Kitchen - {self.id_} items: {items} estimation formula: a={a}, b={b}, c={c}, d={d}, e={e}, f={f}')
        return (((a / b) + (c / d)) * (e + f)) / f

    def receive_new_order(self, data):
        priority = -int(data['priority'])
        kitchen_order = {
            'order_id': data['order_id'],
            'table_id': data['table_id'] if 'table_id' in data else None,
            'waiter_id': data['waiter_id'] if 'waiter_id' in data else None,
            'items': data['items'],
            'priority': priority,
            'max_wait': data['max_wait'],
            'received_time': time.time(),
            'cooking_details': queue.Queue(),
            'is_done_counter': 0,
            'time_start': data['time_start'],
        }
        self.order_list.append(kitchen_order)
        waiting_estimation = 0
        for item_id in data['items']:
            food = next((f for i, f in enumerate(self.food_list) if f['id'] == item_id), None)
            if food is not None:
                waiting_estimation += food['preparation-time']
                self.food_items_q.put_nowait(((
                                                  priority,  # order - food priority (negated so highest will be on top)
                                                  0,  # time the food item spend in queue
                                                  next(self.counter)  # in case the previous values are the same, just prioritize by counter
                                              ), {
                                                  'food_id': food['id'],
                                                  'order_id': data['order_id'],
                                                  'priority': priority,
                                                  'queue_start_time': time.time()  # start time of item waiting in this queue
                                              }))

        return {'estimated_waiting_time': self.calculate_waiting_time(data)}
