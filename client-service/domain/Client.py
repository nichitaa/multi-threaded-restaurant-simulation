import time
import uuid
import consts
import random
import logging
import requests
import threading
from util import json_log
from dto.order import ClientOrderDto, OrderDto

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, i):
        self.name = f'Client-{i}'

    def generate_order(self):
        # request menu to food ordering service
        response = requests.get(f'http://{consts.FO_HOST}:{consts.FO_PORT}/menu')
        data = response.json()

        # pick some random restaurants
        rests = random.sample(data['restaurants_data'], random.randint(1, int(data['restaurants'])))

        # build a order for each of the restaurants
        client_order = ClientOrderDto(client_id=uuid.uuid4().hex[0:4], orders=[])

        for i, rest in enumerate(rests):
            single_order = OrderDto(restaurant_id=rest['restaurant_id'], items=[], max_wait=0, priority=random.randint(1, 5), time_start=time.time())
            for j in range(random.randint(1, 5)):
                food = random.choice(rest['menu'])
                single_order.items.append(food['id'])
                if single_order.max_wait < food['preparation-time']:
                    single_order.max_wait = food['preparation-time']
            single_order.max_wait *= 1.6
            client_order.orders.append(single_order)
        client_order.created_time = time.time()

        # send order to food ordering service
        response = requests.post(f'http://{consts.FO_HOST}:{consts.FO_PORT}/order', json=client_order.dict())
        json_ = response.json()

        logger.info(f'\n{self.name} New order: {json_log(client_order.dict())}\nFO response: {json_log(json_)}')

        # client wait x time for each suborder from order
        for i, data in enumerate(json_['orders']):
            threading.Thread(target=self.client_wait_single_order, args=(json_, data), daemon=True).start()

    def client_wait_single_order(self, fo_response, single_order):
        start_waiting = time.time()
        logger.info(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | waiting time: {single_order["estimated_waiting_time"]}')
        time.sleep(single_order['estimated_waiting_time'])
        is_ready = False
        while not is_ready:
            # find out if order is done
            logger.warning(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | request to dinning-hall: {single_order["restaurant_address"]}')
            response = requests.get(f'http://{consts.DH_HOST}:{single_order["restaurant_address"]}/v2/order/{fo_response["order_id"]}')
            json_ = response.json()
            logger.warning(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | dinning-hall: {single_order["restaurant_address"]} | \nresponse: {json_log(json_)}')
            # if order is not ready wait for more time
            if json_['is_ready']:
                prep_time = int(time.time() - start_waiting)
                logger.debug(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | dinning-hall: {single_order["restaurant_address"]} | max_wait: {single_order["max_wait"]} | prep_time: {prep_time}  DONE!')

                # calculate rating stars
                stars = self.rating_stars(single_order["max_wait"], prep_time)
                logger.info(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | dinning-hall: {single_order["restaurant_address"]} | STARS: {stars}')
                req = {"order_id": fo_response["order_id"], "stars": stars, "dh_address": single_order["restaurant_address"]}
                res = requests.post(f'http://{consts.FO_HOST}:{consts.FO_PORT}/rating', json=req)
                logger.info(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | new RATING: {res.json()["updated_rating"]}')
                is_ready = True
                threading.Thread(target=self.generate_order, daemon=True, name=f'{self.name}').start()

            else:
                logger.debug(f'{self.name} order: "{fo_response["order_id"]}" | suborder: {single_order["order_id"]} | dinning-hall: {single_order["restaurant_address"]} NOT DONE!')
                time.sleep(json_['estimated_waiting_time'])

    @staticmethod
    def rating_stars(max_wait, total):
        stars = 0
        if max_wait >= total:
            stars = 5
        elif max_wait * 1.1 >= total:
            stars = 4
        elif max_wait * 1.2 >= total:
            stars = 3
        elif max_wait * 1.3 >= total:
            stars = 2
        elif max_wait * 1.4 >= total:
            stars = 1

        return stars
