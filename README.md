# Parking Lot API
## Initial Setup
### Create Your Virtual Environment
To get started you will need to have pip and
[tox](https://tox.readthedocs.io/en/latest/) installed.

    $ pip install tox
    $ tox -e devenv

Running this command will create a new virtual environment in the `.tox/devenv` directory

### Activate Your Virtual Environment

    $ source .tox/devenv/bin/activate

### Initialize Your Database
Run this in your active virtual environment

Running this command will create a `parking.db` SQLite database file in the top level directory, which includes all
the necessary tables.

    $ initialize-db

### Start the Flask Application
Run this in your active virtual environment

    $ parking-serve

Now you can view the status of the Parking Lot, Revenue, and Parking Queue at [http://localhost:5000/status](http://localhost:5000/status)

## Usage
### POST /park/<vehicle-name>/<minutes-required-to-park>
Park a vehicle in the parking lot, or add to the queue if no spaces are available

NOTE: The vehicle-name value must be unique

Example of parking a vehicle

    $ curl -i -X POST localhost:5000/park/test_car/7333

    HTTP/1.0 202 ACCEPTED
    Content-Type: text/html; charset=utf-8
    Content-Length: 0
    Server: Werkzeug/0.12.2 Python/3.6.2
    Date: Mon, 07 Aug 2017 20:20:50 GMT

### POST /leave/<vehicle-name>
Remove a vehicle from it's space in the parking lot and park the next vehicle in the queue, if one
exists

The revenue will be adjusted to reflect the relevant rate and time parked for the vehicle being
removed

Example of removing a vehicle

    $ curl -i -X POST localhost:5000/leave/test_car

    HTTP/1.0 202 ACCEPTED
    Content-Type: text/html; charset=utf-8
    Content-Length: 0
    Server: Werkzeug/0.12.2 Python/3.6.2
    Date: Mon, 07 Aug 2017 19:22:37 GMT

## Extras
### Remove Your Database
Run this in your active virtual environment

    $ parking-remove-db

This command will delete the `parking.db` SQLite database file and all the data in the database
