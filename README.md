> Table of contents
>
> [API](#markdown-header-api)
>    * [Server](#markdown-header-server)
>    * [Endpoints for clients](#markdown-header-endpoints-for-clients)
>    *    * [Get list of venues](#markdown-header-get-list-of-venues)
>    *    * [Get menu](#markdown-header-get-menu)
>    *    * [Get promo info](#markdown-header-get-promo-info)
>    *    * [Get ID for new order](#markdown-header-get-id-for-new-order)
>    *    * [Post order](#markdown-header-post-order)
>    *    * [Get status of orders](#markdown-header-get-status-of-orders)
>    *    * [Cancel order](#markdown-header-cancel-order)
>    * [Endpoints for admins](#markdown-header-endpoints-for-admins)
>    *    * [Get current orders](#markdown-header-get-current-orders)
>    *    * [Get updates](#markdown-header-get-updates)
>    *    * [Get returns](#markdown-header-get-returns)
>    *    * [Get history](#markdown-header-get-history)
>    *    * [Cancel order](#markdown-header-cancel-order)
>    *    * [Postpone order](#markdown-header-postpone-order)
>    *    * [Close order](#markdown-header-close-order)
>    * [Constants](#markdown-header-constants)
>    *    * [Device types](#markdown-header-device-types)
>    *    * [Payment types](#markdown-header-payment-types)
>    *    * [Order statuses](#markdown-header-order-statuses)
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
    },
    "client_id": client_id                            // int
}
```

If `client_id` is not specified by the client, it is generated by the server.

### Get promo info

GET `/api/promo_info`

Parameters:

* `client_id`: int

```
#!js
{
    "promo_enabled": promo_enabled,                      // boolean
    "promo_mastercard_only": promo_mastercard_only,      // boolean
    "points_per_cup": points_per_cup,                    // int
    "has_mastercard_orders": client_has_mastercard_only, // boolean
    "bonus_points": client_bonus_points                  // int
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
    * `coordinates`: string with format `"lat,lng"`
    * `comment`: string
    * `device_type`: int, optional (0 for iOS, 1 for Android)
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
* `mastercard`: boolean

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

## Endpoints for admins

### Get current orders

GET `/api/admin/orders/current`

No parameters

```
#!js
{
    "orders": [
        {
            "order_id": order_id,                     // int
            "delivery_time": order_delivery_time,     // int, timestamp
            "payment_type_id": order_payment_type_id, // int
            "pan": order_pan,                         // string
            "comment": order_comment,                 // string
            "client": {
                "name": client_name,       // string
                "surname": client_surname, // string
                "phone": client_phone      // string
            },
            "items": [
                {
                    "title": item_title,      // string
                    "price": item_price,      // int
                    "quantity": item_quantity // int
                },
                ...
            ]
        },
        ...
    ]
}
```

### Get updates

GET `/api/admin/orders/updates`

Parameters:

* `timestamp`: int

```
#!js
{
    "new": new_orders,        // list of objects, as above
    "updated": updated_orders // list of objects, as above
}
```

### Get returns

GET `/api/admin/orders/returns`

Parameters:

* `date`: int (timestamp, time part is ignored)

```
#!js
{
    "orders": orders // list of objects, as above
}
```

### Get history

GET `/api/admin/orders/history`

Parameters:

* `start`: int (timestamp)
* `end`: int (timestamp)
* `search` (optional): string

```
#!js
{
    "orders": orders // list of objects, as above
}
```

### Cancel order

POST `/api/admin/orders/<order_id>/cancel`

Parameters:

* `comment`: string

On failure, status code is 400

```
#!js
{
}
```

### Postpone order

POST `/api/admin/orders/<order_id>/postpone`

Parameters:

* `mins`: int

```
#!js
{
}
```

### Close order

POST `/api/admin/orders/<order_id>/close` 

No parameters

```
#!js
{
}
```

## Constants

### Device types

* `0`: iOS (default)
* `1`: Android

### Payment types

* `0`: cash
* `1`: card
* `2`: bonus

### Order statuses

* `0`: new
* `1`: ready
* `2`: canceled by client
* `3`: canceled by barista
