> Network Programming Laboratory Work [Kitchen]
>
> FAF 192 Y3-S1
>
> Pasecinic Nichita

Each kitchen get it's configuration after a dinning hall is registered at Food Ordering service via a post request to corresponding dinning hall endpoint `/restaurant_data` . A kitchen has a single exposed POST endpoint `/order` used by mapped dinning hall in order to add new client order so the Cooks can work on it. Once a order is received is splitted into food items and added to a priority queue. A Cook is represented by more threads because it can work on multiple items at once, each of them remove the food item with highest priority and checks if they can prepare it following the lab logic with cook rank / food complexity and cooking apparatus availability , if it is not possible to cook it, the item is added back to queue, else the item is being prepared, if all of the items from a single order are prepared the cook notifies the dinning hall via `/distribution` endpoint. Cooking details for each order are also saved.

#### **Run**

Order of running the restaurant simulation:

1. Food Ordering service
2. Dinning Halls
3. Kitchens
4. Client service

```bash
$ docker build --tag kitchen . 
$ # we've previously created a new docker network (with name nt)
$ docker run -d --net nt --name kitchen kitchen
```

