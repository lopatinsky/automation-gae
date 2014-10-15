# API

## Server

Server is currently located at http://empatika-doubleb.appspot.com/.

## Endpoints for clients

### Get list of venues

GET `/api/venues.php`

Parameters:

* `ll` (optional): string with format `"lat,lng"`, e.g. `"1.23456,-1.23456"`

```
#!js
{
    "venues": [
        {
            "id": venue_id,                      // numeric string
            "title": venue_title,                // string
            "address": venue_address,            // string
            "pic": venue_pic,                    // string
            "lat": venue_latitude,               // float
            "lon": venue_longitude,              // float
            "coordinates": venue_coordinates,    // string with format "lat,lng"
            "schedule": [
                {
                    "days": schedule_item_days,  // array of ints
                    "hours": schedule_item_hours // string
                },
                {
                    "days": [1, 2, 3, 4, 5],     // example
                    "hours": "9-23"
                },
                ...
            ],
            "distance": distance_to_location     // float, 0 if location not specified
        },
        ...
    ]
}
```

If `ll` is specified, venues are sorted by distance to this location.

### Get menu

GET `/api/menu.php`

Parameters:

* `client_id` (optional): int

```
#!js
{
    "menu": {
        category1_title: [                            // keys are category titles
            {
                "id": menu_item_id,                   // numeric string
                "title": menu_item_title,             // string
                "description": menu_item_description, // string
                "price": menu_item_price,             // int
                "kal": menu_item_calories,            // int
                "pic": menu_item_pic                  // string
            }
        ],
        ...
    }
}
```

### Get ID for new order

GET `/api/order_register.php`

No parameters

```
#!js
{
    "order_id": new_order_id // int
}
```

### Post order

POST `/api/orders.php`

Parameters:

* `order`: JSON string: object with the following fields:
    * `order_id`: int|string
    * `venue_id`: int|string
    * `total_sum`: int
    * `coordinates`: string with format `"lat,lng"`
    * `comment`: string
    * `device_type`: int
    * `delivery_time`: int (interval in minutes)
    * `client`: object
        * `id`: int|string
        * `name`: string
        * `phone`: string
    * `payment`: object
        * `type_id`: int
        * see below
    * `items`: array of objects
        * `item_id`: int|string
        * `quantity`: int

For payment by card from client (DEPRECATED), `payment` must contain the following fields:

* `payment_id`: string

For payment by card from server, `payment` must contain the following fields:

* `binding_id`: string
* `client_id`: string
* `return_url`: string

Response:

```
#!js
{
    "order_id": order_id // int
}
```

### Get status of orders

POST `/api/status.php`

Parameters:

* `orders`: JSON string: array of order IDs (int)

Response:

```
#!js
{
    "status": [
        {
            "order_id": order_id,  // int
            "status": order.status // int
        },
        ...
    ]
}
```

### Cancel order

POST `/api/return.php`

Parameters:

* `order_id`: int

Response on success:

```
#!js
{
    "error": 0,
    "order_id": order_id // int
}
```

Response on failure:

```
#!js
{
    "error": 1,
    "description": error_description // string
}
```
