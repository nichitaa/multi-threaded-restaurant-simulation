import time
import consts
import logging
import requests
import threading

logger = logging.getLogger(__name__)


class Cook:
    def __init__(self, kitchen, id_, name, rank, proficiency, catch_phrase):
        self.kitchen = kitchen
        self.id_ = id_
        self.name = name
        self.rank = rank
        self.proficiency = proficiency
        self.concurrent_items = 0
        self.catch_phrase = catch_phrase
        self.TIME_UNIT = 1

    def cook_work(self):
        while True:
            try:
                q_item = self.kitchen.food_items_q.get_nowait()
                food_item = q_item[1]

                food_details = next((f for f in self.kitchen.food_list if f['id'] == food_item['food_id']), None)
                (order_idx, order_details) = next(((idx, order) for idx, order in enumerate(self.kitchen.order_list) if order['order_id'] == food_item['order_id']), (None, None))

                if self.can_prepare(food_details, order_details):
                    threading.Thread(target=self.prepare, args=(food_details, order_idx, order_details), daemon=True).start()

                else:
                    # cook hand could not prepare this order, put it back to queue and change the priority based on waiting time in queue
                    tup = q_item[0]
                    diff = time.time() - food_item['queue_start_time']
                    # if diff > 15:
                    #     diff = 0
                    self.kitchen.food_items_q.put_nowait(((tup[0], diff, tup[2]), food_item))

            except Exception as e:
                pass

    def prepare(self, food_details, order_idx, order_details):
        time.sleep(int(food_details['preparation-time']) * self.TIME_UNIT)

        self.kitchen.order_list[order_idx]['is_done_counter'] += 1
        self.kitchen.order_list[order_idx]['cooking_details'].put_nowait({'food_id': food_details['id'], 'cook_id': self.id_})

        if self.kitchen.order_list[order_idx]['is_done_counter'] == len(self.kitchen.order_list[order_idx]['items']):
            # notify dinning hall
            logger.debug(f'#K-{self.kitchen.id_} C-{self.name} P-{self.concurrent_items} PREPARED orderId: "{order_details["order_id"]}" | priority: {order_details["priority"]}\n')
            payload = {
                **self.kitchen.order_list[order_idx],
                'cooking_time': int(time.time() - self.kitchen.order_list[order_idx]['received_time']),
                'cooking_details': list(self.kitchen.order_list[order_idx]['cooking_details'].queue)
            }
            requests.post(f'http://{consts.DH_HOST}:{self.kitchen.dh_port}/distribution', json=payload)

        self.concurrent_items -= 1

        # add new free cooking apparatus to queue
        apparatus = food_details['cooking-apparatus']
        if apparatus == 'oven':
            n = self.kitchen.ovens_q.qsize()
            self.kitchen.ovens_q.put_nowait(n)
        elif apparatus == 'stove':
            n = self.kitchen.stoves_q.qsize()
            self.kitchen.stoves_q.put_nowait(n)

    def can_prepare(self, food, order):
        if self.concurrent_items <= self.proficiency:
            if food['complexity'] == self.rank or food['complexity'] - 1 == self.rank:
                apparatus = food['cooking-apparatus']
                if apparatus == 'oven':
                    try:
                        o = self.kitchen.ovens_q.get_nowait()
                        self.concurrent_items += 1
                        logger.warning(f'#K-{self.kitchen.id_} C-{self.name} P-{self.concurrent_items} COOKING  foodId: {food["id"]} | orderId: "{order["order_id"]}" | priority: {order["priority"]} | oven: {o}\n')
                        return True
                    except Exception as e:
                        return False
                elif apparatus == 'stove':
                    try:
                        s = self.kitchen.stoves_q.get_nowait()
                        self.concurrent_items += 1
                        logger.warning(f'#K-{self.kitchen.id_} C-{self.name} P-{self.concurrent_items} COOKING foodId: {food["id"]} | orderId: "{order["order_id"]}" | priority: {order["priority"]} | stove: {s}\n')
                        return True
                    except Exception as e:
                        return False
                elif apparatus is None:
                    self.concurrent_items += 1
                    logger.warning(f'#K-{self.kitchen.id_} C-{self.name} P-{self.concurrent_items} COOKING foodId: {food["id"]} | orderId: "{order["order_id"]}" | priority: {order["priority"]} (hands)\n')
                    return True
                return False
            return False
        return False
