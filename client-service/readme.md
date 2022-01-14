> Network Programming Laboratory Work [Client Service]
>
> FAF 192 Y3-S1
>
> Pasecinic Nichita

Each client thread requests all available menus from Food ordering service and generates a random order (which may contain orders from different restaurants), as a response from Food ordering it receives a estimation waiting time (for each distinct restaurant). Then client thread is waiting estimation waiting time for each suborder and makes a post request to the restaurant address (dinning hall), if order is ready the client calculates the rating stars and post them on Food ordering service, if order is not ready yet, the thread waits additional x time.

#### **Run**

Order of running the restaurant simulation:

1. Food Ordering service
2. Dinning Halls
3. Kitchens
4. Client service

```bash
$ docker build --tag client_service . 
$ # we've previously created a new docker network (with name nt)
$ docker run -d --net nt --name client_service client_service
```

