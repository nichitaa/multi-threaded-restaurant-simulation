import time
import uuid
import utils
import consts
import logging
import requests

logger = logging.getLogger(__name__)


class OrderManager:
    def __init__(self):
        self.restaurants = []

    def make_order(self, order):
        orders = order['orders']
        response = {'order_id': uuid.uuid4().hex[0:7], 'orders': []}
        logger.info(f'Order Manager, NEW order: {utils.json_log(order)} | order_id: {response["order_id"]}')
        for i, data in enumerate(orders):
            rest = next((x for x in self.restaurants if x['restaurant_id'] == data['restaurant_id']), None)
            dh_url = f'http://{consts.DH_HOST}:{rest["dinning_port"]}/v2/order'
            payload = {**data, 'order_id': response['order_id']}
            logging.info(f'Order Manager, REQUEST to dh: {dh_url} | \npayload: {utils.json_log(payload)}')
            res = requests.post(dh_url, json=payload)
            json_ = res.json()
            logger.info(f'Order Manager, RESPONSE from dh: {dh_url} | \nresponse: {utils.json_log(json_)}')
            response['orders'].append({
                'restaurant_id': rest['restaurant_id'],
                'restaurant_address': rest['dinning_port'],
                'order_id': i,
                'created_time': order['created_time'],
                'registered_time': time.time(),
                'estimated_waiting_time': json_['estimated_waiting_time'],
                'max_wait': data['max_wait']
            })
        logger.info(f'Order Manager, order: {response["order_id"]} \nAggregated response: {response}')
        return response

    def register(self, data):
        self.restaurants.append(data)
        logger.info(f'Order Manager, REGISTERED new restaurant: {data["name"]}\n')
        return {'isSuccess': True, 'message': f'Restaurant {data["name"]} was successfully registered!'}

    def get_menu(self):
        menu = [{'name': data['name'], 'restaurant_id': data['restaurant_id'], 'menu': data['menu']} for i, data in enumerate(self.restaurants)]
        logger.info(f'Order Manager,  Provided {len(menu)} menus !\n')
        return {'restaurants': len(self.restaurants), 'restaurants_data': menu}

    @staticmethod
    def rating(data):
        res = requests.post(f'http://{consts.DH_HOST}:{data["dh_address"]}/rating', json=data)
        return res.json()
