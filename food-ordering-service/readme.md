> Network Programming Laboratory Work [Food Ordering service]
>
> FAF 192 Y3-S1
>
> Pasecinic Nichita

A Food Ordering service have exposed following endpoints:

* `GET /menu` (used by Client service to get the menu from all of the registered restaurants)
* `POST /register` (used by Dinning Halls to register its restaurant configuration)
* `POST /order` (used by Client service to register a order, it aggregates the response from all of the restaurants from a order)
* `POST /rating` (used by Client service to update the rating of a restaurant)



**Run**

Order of running the restaurant simulation:

1. Food Ordering service
2. Dinning Halls
3. Kitchens
4. Client service

```bash
$ docker build --tag food_ordering .
$ # create a network to run all of the simulation components / containers
$ docker network create nt
$ docker run -d --net nt --name food_ordering food_ordering
```

