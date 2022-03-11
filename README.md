# Buses on Moscow map

The web application simulates Moscow buses traffic and displays it in the browser.

<img src="screenshots/buses.gif">

## Install

Clone the repository

```bash
git clone https://github.com/balancy/async-buses-on-the-map.git
```

Go inside the cloned repository, create the virtual environment and activate it.

```bash
cd async-buses-on-the-map
```

```bash
python -m venv .venv
```

```bash
. .venv
```

Install dependencies

```
pip install -r requirements-dev.txt
```

## RUN

You need to open `index.html` in the browser.

There are two scripts. You need to launch both scripts in two different shell tabs for the app to work.

#### Server

- `server.py` - Simulates a web server that listens to the incoming data and interacts with the browser.

```
python server.py
```

You you could specify arguments:

- `--bus_port` - Port to listen data on. By default it's `8080`.
- `--browser_port` - Port to communicate with browser on. By default it's `8000`.
- `--verbose` - If you need to see logging messages. By default it's `False`.

#### Client

- `fake_buses.py` - Simulates web client that sends information about buses traffic.

```
python fake_buses.py
```

By default `fake_buses.py` launches 595 different routes with 5 buses on each route.

- `--server` - Server address. By default it's `ws://127.0.0.1:8080`.
- `--routes_amount` - Amount of bus routes. By default it's `595`.
- `--buses_per_route` - Amount of buses per route. By default it's `5`.
- `--sockets_amount` - Amount of websockets. By default it's `10`.
- `--emulator_id` - Prefix for busId if you need to lauch several `fake_buses.py`. By default there is no prefix.
- `--timeout` - Timeout for the script to take before asking for new bus coordinates. By default it's `0.5` seconds.
- `--verbose` - If you need to see logging messages. By default it's `False`.


#### Tests

You could launch tests for data. For this, you'll need your `server.py` running.

```
pytest
```

## Settings

You can enable debug and specify a non-standard web socket address at the bottom right of the page.

<img src="screenshots/settings.png">

## Data Format

Frontend waits for the JSON response from the server in the following format:

```js
{
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
  ]
}
```

Frontend follows the map bounds change in the browser and sends new map bounds to the server in the following format:

```js
{
  "msgType": "newBounds",
  "data": {
    "east_lng": 37.65563964843751,
    "north_lat": 55.77367652953477,
    "south_lat": 55.72628839374007,
    "west_lng": 37.54440307617188,
  },
}
```
