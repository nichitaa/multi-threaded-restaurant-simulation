import queue
import consts
import logging
import requests
import threading
from domain.Table import Table
from domain.Waiters import Waiters

logger = logging.getLogger(__name__)
lock = threading.Lock()


class DinningHall:
    def __init__(self, config):
        self.config = config
        self.id_ = config["restaurant_id"]
        self.name = f'DH-{self.id_}'
        self.done_orders = []
        self.orders = []
        self.tables = [Table(self, i) for i in range(config['tables_no'])]
        self.waiters = [Waiters(self, i) for i in range(config['waiters_no'])]
        self.orders_q = queue.Queue()
        self.rating_stars = []
        self.avg_rating = config['rating']
        self.TIME_UNIT = 1
        self.free_tables = queue.Queue()

    def start_dinning_workers(self):
        for table in self.tables:
            self.free_tables.put_nowait(table)

        for waiter in self.waiters:
            threading.Thread(target=waiter.search_order, args=(self.free_tables, ), daemon=True).start()

    def get_restaurant_data(self):
        return {'config': self.config}

    def get_menu(self):
        return {'menu': self.config['menu'], 'restaurant_name': self.config['name']}

    def order(self, data):
        logger.info(f'{self.name}, NEW order: {data["order_id"]} | request to kitchen PORT: {self.config["kitchen_port"]}\n')
        self.orders.append(data)
        res = requests.post(f'http://{consts.KH_HOST}:{self.config["kitchen_port"]}/order', json=data)
        return res.json()

    def get_order(self, order_id):
        logger.info(f'{self.name}, client requested for order: {order_id}\n')
        order = next((x for x in self.done_orders if x['order_id'] == order_id), None)
        if order is not None:
            logger.info(f'{self.name}, client received order: {order_id}\n')
            return {**order, 'is_ready': True}
        else:
            logger.info(f'{self.name}, client order: {order_id} is not ready!\n')
            return {'order_id': order_id, 'is_ready': False, 'estimated_waiting_time': 3}

    def distribution(self, order):
        self.done_orders.append(order)
        if order['table_id'] is not None:
            # serve the order to table
            logger.info(f'{self.name} NEW distribution for table: {order["table_id"]}')
            waiter = next((w for w in self.waiters if w.id == order['waiter_id']), None)
            waiter.serve_order(order)
        else:
            # keep the order, so client can request it
            logger.info(f'{self.name} NEW distribution for client service')
        return {'isSuccess': True}

    def update_rating(self, data):
        lock.acquire()
        self.rating_stars.append(data['stars'])
        avg = float(sum(s for s in self.rating_stars)) / len(self.rating_stars)
        self.avg_rating = avg
        lock.release()
        logger.info(f'{self.name} order_id: {data["order_id"]} | updated RATING: {self.avg_rating}')
        return {'updated_rating': self.avg_rating}
