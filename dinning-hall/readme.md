> Network Programming Laboratory Work [Dinning-Hall]
>
> FAF 192 Y3-S1
>
> Pasecinic Nichita

In `restaurants_data/data.json` is the configuration for the simulation. First of all it is instantiated 4 Dinning Halls with corresponding config from `data.json` after that all of them are registered on Food Ordering service (`/register`). Dinning hall endpoints are: 

* `GET /menu`  (used by Client service to get the menu of a restaurant)
* `GET /v2/order/<id>` (used by Client service to confirm if the order is done)
* `GET /restaurant_data` (used by Kitchen to get the kitchen configuration)
* `POST /v2/order` (used by Food Ordering to register new order)
* `POST /distribution` (used by Kitchen to notify that a order is prepared)
* `POST /rating` (used by Client service to update the rating of a restaurant)

It respects the order generation from previous implementation and can work independent without Client Service as Tables generates orders and the Waiters pick up or server them.

#### **Run**

Order of running the restaurant simulation:

1. Food Ordering service
2. Dinning Halls
3. Kitchens
4. Client service

```bash
$ docker build --tag dinning_hall . 
$ # we've previously created a new docker network (with name nt)
$ docker run -d --net nt --name dinning_hall dinning_hall
```

