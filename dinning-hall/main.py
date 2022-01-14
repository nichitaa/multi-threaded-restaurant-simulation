'''
PR v2 - Dinning hall

<author>: <pasecinic nichita>
faf 192
'''
import utils
import consts
import logging
import requests
import threading
import coloredlogs
from flask import Flask, request
from domain.DinningHall import DinningHall

logging.basicConfig(filename='dinning.log', level=logging.DEBUG, format='%(asctime)s: %(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


# 4 dinning hall servers
# dinning hall   on 400X
# kitchen        on 500X
def simulation():
    restaurants = utils.get_restaurants()

    # start new Flask application for each dinning hall server
    for r in restaurants:
        app = Flask(r['name'])
        dinning = DinningHall(r)

        requests.post(f'http://{consts.FO_HOST}:{consts.FO_PORT}/register', json=r)

        # POST /distribution : exposed for Kitchens
        @app.route('/distribution', methods=['POST'])
        def distribution(app_dh=dinning):
            order = request.get_json()
            return app_dh.distribution(order)

        # GET /menu            : exposed for Client Service
        @app.route('/menu', methods=['GET'])
        def menu(app_dh=dinning):
            return app_dh.get_menu()

        # POST /v2/order       : exposed for Client Service
        @app.route('/v2/order', methods=['POST'])
        def order_v2(app_dh=dinning):
            data = request.get_json()
            return app_dh.order(data)

        # GET /v2/order/id     : exposed for Food Ordering
        @app.route('/v2/order/<order_id>', methods=['GET'])
        def get_order(order_id, app_dh=dinning):
            return app_dh.get_order(order_id)

        # GET /restaurant_data : exposed for Kitchens
        @app.route('/restaurant_data', methods=['GET'])
        def get_restaurant_data(app_dh=dinning):
            # start generating orders once the kitchen was configured
            threading.Thread(target=app_dh.start_dinning_workers, daemon=True).start()
            return app_dh.get_restaurant_data()

        # POST /rating         : exposed for Client Service
        @app.route('/rating', methods=['POST'])
        def rating(app_dh=dinning):
            data = request.get_json()
            return app_dh.update_rating(data)

        threading.Thread(target=lambda: app.run(host=consts.HOST, port=dinning.config['dinning_port'], debug=False, use_reloader=False, threaded=True), name=f'{dinning.name}', daemon=True).start()


def main():
    open("dinning.log", "w").close()

    simulation()

    while True:
        pass


if __name__ == '__main__':
    main()
