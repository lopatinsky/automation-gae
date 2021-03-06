> __Table of contents__
>
>   * [API](#markdown-header-api)
>       * [Server](#markdown-header-server)
>       * [Card binding](#markdown-header-card-binding)
>           * [Step 1](#markdown-header-step-1)
>           * [Step 2](#markdown-header-step-2)
>           * [Step 3](#markdown-header-step-3)
>           * [Step 4](#markdown-header-step-4)
>       * [Endpoints for clients](#markdown-header-endpoints-for-clients)
>           * [Get list of venues](#markdown-header-get-list-of-venues)
>           * [Get menu](#markdown-header-get-menu)
>           * [Get promo info](#markdown-header-get-promo-info)
>           * [Save or update (by phone or emails) client info](#markdown-header-save-or-update-(by-phone-or-emails)-client-info)
>           * [Get ID for new order](#markdown-header-get-id-for-new-order)
>           * [Validate order and get active promos](#markdown-header-validate-order-and-get-active-promos)
>           * [Post order](#markdown-header-post-order)
>           * [Confirm the order is received](#markdown-header-confirm-the-order-is-received)
>           * [Get status of orders](#markdown-header-get-status-of-orders)
>           * [Get orders history](#markdown-header-get-orders-history)
>           * [Cancel order](#markdown-header-cancel-order)
>           * [Get wallet balance](#markdown-header-get-wallet-balance)
>           * [Deposit money from card to wallet](#markdown-header-deposit-money-from-card-to-wallet)
>           * [Add return comment to canceled order](#markdown-header-add-return-comment-to-canceled-order)
>           * [Get shared info](#markdown-header-get-shared-info)
>       * [Endpoints for admins](#markdown-header-endpoints-for-admins)
>           * [Login](#markdown-header-login)
>           * [Logout](#markdown-header-logout)
>           * [Ping](#markdown-header-ping)
>           * [Get current orders](#markdown-header-get-current-orders)
>           * [Get updates](#markdown-header-get-updates)
>           * [Get returns](#markdown-header-get-returns)
>           * [Get history](#markdown-header-get-history)
>           * [Cancel order](#markdown-header-cancel-order)
>           * [Postpone order](#markdown-header-postpone-order)
>           * [Close order](#markdown-header-close-order)
>       * [Constants](#markdown-header-constants)
>           * [Device types](#markdown-header-device-types)
>           * [Payment types](#markdown-header-payment-types)
>           * [Order statuses](#markdown-header-order-statuses)
>   * [Documents](#markdown-header-documents)

# API

## Server

Server is currently located at http://empatika-doubleb.appspot.com/.

## Card binding

### Step 1

POST `/api/payment/register.php`

Parameters:

* `clientId`
* `orderNumber`: any alphanumeric string (eg current timestamp)
* `amount`: number 100
* `returnUrl`: url to redirect in web view

Response:

On failure, contains nonzero `errorCode`.  
On success, contains `orderId` and `formUrl`.

### Step 2

Open `formUrl` in web view and wait for it to navigate to `returnUrl`.

### Step 3

POST `/api/payment/status.php`

Parameters:

* `orderId`

Response:

```
#!js
{
    "ErrorCode": error_code,     // numeric string
    "OrderStatus": order_status, // int
    "bindingId": binding_id,     // GUID string
    "Pan": card_pan              // string in format 123456**1234
}
```

On success, `ErrorCode` is `0` and `OrderStatus` is `1`, then the client should save the `bindingId` and last four digits of the `Pan`.  
Any other values of `ErrorCode` and `OrderStatus` indicate a failure.

### Step 4

POST `/api/payment/reverse.php`

Parameters:

* `orderId`

On success, `errorCode` of response is `0`.

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
            "is_open": venue_is_open_now,        // boolean
            "takeout_only": venue_takeout_only,  // boolean
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
* `device_phone` (optional): string

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
    "client_id": client_id,                           // int
    "client_name": client_name,                       // string, if exists
    "client_phone": client_phone,                     // string, if exists
    "demo": is_card_binding_required,                 // boolean
}
```

The client_id is issued according to the following table.

`client_id` |`device_phone`|Rule
:-----------|:-------------|:--------
Not provided|Not provided  |Generates new `client_id`
Not provided|Provided      |If a client exists with this `device_phone`, it is returned, otherwise new is generated
Provided    |Not provided  |If the given ID exists, it is returned
Provided    |Provided      |Same as above, and `device_phone` is updated

### Get promo info

GET `/api/promo_info`

Parameters:

* `client_id`: int

```
#!js
{
    "geopush": {
        "id": geopush_id,            // string
        "send": should_send_geopush, // boolean
        "expires": expiry_timestamp, // int
        "radius": radius_to_send,    // int, in meters
        "text": geopush_text         // string
    },

    "promo_enabled": promo_enabled,                        // boolean
    "promo_end_date": promo_end_date,                      // int, timestamp
    "promo_mastercard_only": promo_mastercard_only,        // boolean
    "points_per_cup": points_per_cup,                      // int
    "has_mastercard_orders": client_has_mastercard_orders, // boolean
    "bonus_points": client_bonus_points,                   // int
    "news": [
        {
            "id": news_id,                                 // int
            "text": news_text,                             // string (html, may contain <b> tags)
            "image_url": news_image_url,                   // string
            "created_at": news_timestamp                   // int
        },
        ...
    ]
}
```

### Save or update (by phone or emails) client info

POST `/api/client.php`

Parameters:

* `client_id`: int
* `client_name`: string
* `client_phone` (optional):  string
* `client_email` (optional):  string

```
#!js
{
    "id": client id     // int
    "name": name        // string
    "surname": surname  // string
    "tel": phone        // string
    "email": email      // string
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

### Validate order and get active promos

POST `/api/check_order`

Parameters:

* `client_id`: int
* `venue_id` (optional): int
* `items`: JSON string: array of objects with the following fields:
    * `id`: int|string
    * `quantity`: int
* `payment` (optional): JSON string: object with the following fields:
    * `type_id`: int, see constants
    * `mastercard`: bool
* `delivery_time`(optional): int
    
```
#!js
{
    "valid": is_order_valid,      // boolean
    "total_sum": order_total_sum, // int
    "items": [
        {
            "id": item_id,              // int
            "quantity": item_quantity,  // int
            "errors": item_errors,      // array of strings, item-specific error messages
            "promos": applied_promo_ids // array of strings, eg ["master","other_promo"]
        },
        ...
    ],
    "errors": order_errors, // order-wide error messages
    "promos": [             // applied promos 
        {
            "id": promo_id,    // string
            "text": promo_text // string
        },
        ...
    ]
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
    * `total_sum`: int
    * `client`: object
        * `id`: int|string
        * `name`: string
        * `phone`: string
        * `email`: string
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
    "order_id": order_id                              // int
    "shared_info": {
        "text_share_new_order": sharing text          // string
        "text_share_about_app": text about doubleb    // string
        "app_url_ios": url                            // string
        "app_url_android" url                         // string
    }
}
```

### Confirm the order is received

POST `/api/set_order_success`

Parameters:

* `order_id`: int

Response:

```
#!js
{
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

### Get orders history

GET `/api/history`

Parameters:

* `client_id`: string

```
#!js
{
    "orders": [
        {
            "order_id": order_id,                     // int
            "status": order_status,                   // int, see constants
            "delivery_time": order_delivery_time,     // int, timestamp
            "payment_type_id": order_payment_type_id, // int
            "total": order_total_sum,                 // int
            "venue_id": order_venue_id,               // int
            "items": [
                {
                    "id": item_id,            // int
                    "title": item_title,      // string
                    "price": item_price,      // int
                    "quantity": item_quantity // int
                },
                ...
            ]
        },
        ...
    }
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

### Get wallet balance

POST `/api/wallet/balance`

Parameters:

* `client_id`: string

```
#!js
{
    "balance": client_new_balance // int
}
```

### Deposit money from card to wallet

POST `/api/wallet/deposit`

Parameters:

* `client_id`: string
* `binding_id`: string
* `amount`: int (in rubles)

Success response:

```
#!js
{
    "balance": client_new_balance // int
}
```

Error response:

```
#!js
{
    "description": error_description // string
}
```

### Add return comment to canceled order

POST `/api/add_return_comment`

Parameters:

* `order_id`: int
* `text`: string

```
#!js
{
}
```

### Get shared info

No Parameters

```
#!js
{
    "image_url": image url                                   // string
    "fb_android_image_url" image url for android facebook    // string
    "text_share_new_order": text about me                    // string
    "text_share_about_app": text about app                   // string
    "app_url": app url                                       // string
    "screen_title": title for screen                         // string
    "screen_text": text for screen                           // string
}
```


## Endpoints for admins

### Login

POST `/api/admin/login`

Parameters:

* `email`: string
* `password`: string
* `lat`: float
* `lon`: float

```
#!js
{
    "token": access_token // string
}
```

### Logout

POST `/api/admin/logout`

Parameters:

* `token`: string
* `password`: string

```
#!js
{
}
```

### Ping

POST `/api/admin/ping`

Parameters: 

* `token`: string
* `lat`: float
* `lon`: float
* `error_number`(optional): int
* `sound_level_general`(optional): int
* `sound_level_system`(optional): int
* `is_in_charging`(optional): bool
* `battery_level`(optional): int
* `is_turned_on`(optional): bool
* `app_version`(optional): string

```
#!js
{
}
```

### Get current orders

GET `/api/admin/orders/current`

Parameters:

* `token`: string

```
#!js
{
    "orders": [
        {
            "order_id": order_id,                               // int
            "status": order_status,                             // int, see constants
            "delivery_time": order_delivery_time,               // int, timestamp
            "actual_delivery_time": order_actual_delivery_time, // int|null
            "payment_type_id": order_payment_type_id,           // int
            "pan": order_pan,                                   // string
            "comment": order_comment,                           // string
            "return_comment": barista_return_comment,           // string|null
            "venue": {
                "id": venue_id,          // string
                "title": venue_title,    // string
                "address": venue_address // string
            },
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
    ],
    "timestamp": current_server_timestamp // int
}
```

### Get updates

GET `/api/admin/orders/updates`

Parameters:

* `token`: string
* `timestamp`: int

```
#!js
{
    "new": new_orders,             // list of objects, as above
    "new_orders": new_orders,      // same as new 
    "updated": updated_orders,     // list of objects, as above
    "timestamp": current_timestamp // int
}
```

### Get returns

GET `/api/admin/orders/returns`

Parameters:

* `token`: string
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

* `token`: string
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

* `token`: string
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

* `token`: string
* `mins`: int

```
#!js
{
}
```

### Close order

POST `/api/admin/orders/<order_id>/close` 

Parameters:

* `token`: string

```
#!js
{
    "delivery_time": requested_delivery_time,    // int, timestamp
    "actual_delivery_time": actual_delivery_time // int, timestamp
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

# Documents

List of documents:

* About: `/docs/about.html`
* License agreement: `/docs/license_agreement.html`
* NDA: `/docs/nda.html`
* Payment rules: `/docs/payment_rules.html`
