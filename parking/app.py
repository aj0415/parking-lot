from flask import Flask, render_template
from werkzeug.exceptions import NotFound

from parking.db.parking import get_lot_status, get_queue_status, get_revenue_status, leave, park

app = Flask(__name__)


@app.route('/status')
def lot_status():
    try:
        return render_template('status.html', lot_data=get_lot_status(),
                               queue_data=get_queue_status(), revenue_data=get_revenue_status())
    except AttributeError:
        raise NotFound


@app.route('/park/<vehicle_name>/<parking_time_length>', methods=['POST'])
def park_vehicle(vehicle_name, parking_time_length):
    park(vehicle_name, int(parking_time_length))
    return '', 202


@app.route('/leave/<vehicle_name>', methods=['POST'])
def remove_vehicle(vehicle_name):
    leave(vehicle_name)
    return '', 202


if __name__ == '__main__':
    app.run()
