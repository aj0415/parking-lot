import os
import random
from datetime import datetime, time, timedelta

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table, create_engine, insert,
                        select, update)

import parking

engine = create_engine('sqlite:///parking.db')
metadata = MetaData(bind=engine)

lot = Table('lot', metadata,
            Column('space_id', Integer, primary_key=True),
            Column('vehicle_name', String(50), unique=True),
            Column('parking_start_time', DateTime),
            Column('parking_leave_time', DateTime))

queue = Table('queue', metadata,
              Column('queue_id', Integer, primary_key=True),
              Column('vehicle_name', String(50), unique=True),
              Column('parking_time_length', Integer, nullable=False))

revenue = Table('revenue', metadata,
                Column('total_revenue', Integer, nullable=False))


def drop_db():
    try:
        os.remove('parking.db')
    except OSError:
        pass


def get_lot_status():
    lot_table = getattr(parking.db.parking, 'lot')

    lot_query = select([lot_table.c.space_id, lot_table.c.vehicle_name,
                        lot_table.c.parking_start_time,
                        lot_table.c.parking_leave_time]) \
        .order_by(lot_table.c.space_id)

    with engine.connect() as conn:
        lot_results = [row for row in conn.execute(lot_query)]

    return lot_results


def get_queue_status():
    queue_table = getattr(parking.db.parking, 'queue')

    queue_query = select([queue_table.c.queue_id, queue_table.c.vehicle_name,
                          queue_table.c.parking_time_length]) \
        .order_by(queue_table.c.queue_id)

    with engine.connect() as conn:
        queue_results = [row for row in conn.execute(queue_query)]

    return queue_results


def get_revenue_status():
    revenue_table = getattr(parking.db.parking, 'revenue')

    revenue_query = select([revenue_table.c.total_revenue])

    with engine.connect() as conn:
        revenue_results = [row for row in conn.execute(revenue_query)]

    return revenue_results


def initialize():
    lot_table = getattr(parking.db.parking, 'lot')

    insert_spaces = []

    for i in range(1, 17):
        insert_spaces.append(insert(lot_table)
                             .values(space_id=i)
                             .prefix_with("OR REPLACE"))

    with engine.connect() as conn:
        for statement in insert_spaces:
            conn.execute(statement)

    revenue_table = getattr(parking.db.parking, 'revenue')

    revenue_insert = insert(revenue_table) \
        .values(total_revenue=0) \
        .prefix_with("OR REPLACE")

    with engine.connect() as conn:
        conn.execute(revenue_insert)


def park(vehicle_name, parking_time_length):
    lot_table = getattr(parking.db.parking, 'lot')

    null_value = None
    check_lot = select([lot_table.c.space_id]) \
        .where(lot_table.c.vehicle_name == null_value)

    with engine.connect() as conn:
        open_spots = [row for (row, ) in conn.execute(check_lot)]

    current_datetime = datetime.now()
    parking_leave_time = current_datetime + timedelta(minutes=parking_time_length)

    if len(open_spots) > 0:
        spot = random.choice(open_spots)
        update_space = update(lot_table) \
            .values(vehicle_name=vehicle_name, parking_start_time=current_datetime,
                    parking_leave_time=parking_leave_time) \
            .where(lot_table.c.space_id == spot)
        with engine.connect() as conn:
            conn.execute(update_space)
    else:
        queue_table = getattr(parking.db.parking, 'queue')
        insert_queue = insert(queue_table) \
            .values(vehicle_name=vehicle_name,
                    parking_time_length=parking_time_length)
        with engine.connect() as conn:
            conn.execute(insert_queue)


def calculate_fee(day_of_week, park_time):
    rate_dict = {'weekday': {'lt_2': 5, '2_6': 10, '6_12': 15, '24': 20},
                 'weekend': {'lt_2': 10, '2_6': 20, '6_12': 30, '24': 40}}

    if park_time <= time(2, 0):
        rate = rate_dict[day_of_week]['lt_2']
    elif time(2, 0) < park_time <= time(6, 0):
        rate = rate_dict[day_of_week]['2_6']
    elif time(6, 0) < park_time <= time(12, 0):
        rate = rate_dict[day_of_week]['6_12']
    elif time(12, 0) < park_time <= time(23, 59, 59):
        rate = rate_dict[day_of_week]['24']

    return rate


def seconds_to_time(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return time(hours, minutes, seconds)


def leave(vehicle_name):
    lot_table = getattr(parking.db.parking, 'lot')
    queue_table = getattr(parking.db.parking, 'queue')
    revenue_table = getattr(parking.db.parking, 'revenue')

    vehicle_query = select([lot_table.c.space_id, lot_table.c.parking_start_time,
                            lot_table.c.parking_leave_time]) \
        .where(lot_table.c.vehicle_name == vehicle_name)

    with engine.connect() as conn:
        vehicle_info = [row for row in conn.execute(vehicle_query)]

    open_space = vehicle_info[0][0]
    start_datetime = vehicle_info[0][1]
    leave_datetime = vehicle_info[0][2]
    number_of_days = (leave_datetime.date() - start_datetime.date()).days

    parked_dates = []
    for i in range(number_of_days + 1):
        parked_dates.append(start_datetime.date() + timedelta(days=i))

    revenue_query = select([revenue_table.c.total_revenue])

    with engine.connect() as conn:
        revenue = [row for (row, ) in conn.execute(revenue_query)]

    total_revenue = revenue[0]
    for rate_date in parked_dates:
        if rate_date.weekday() < 5:
            day_of_week = 'weekday'
        else:
            day_of_week = 'weekend'

        if len(parked_dates) == 1:
            total_seconds = int((leave_datetime - start_datetime).total_seconds())
            elapsed_time_parked = seconds_to_time(total_seconds)
        elif rate_date == parked_dates[0]:
            end_datetime = datetime.combine(rate_date, time.max)
            total_seconds = int((end_datetime - start_datetime).total_seconds())
            elapsed_time_parked = seconds_to_time(total_seconds)
        elif rate_date == parked_dates[-1]:
            begin_datetime = datetime.combine(rate_date, time.min)
            total_seconds = int((leave_datetime - begin_datetime).total_seconds())
            elapsed_time_parked = seconds_to_time(total_seconds)
        else:
            elapsed_time_parked = time(23, 59, 59)

        total_revenue += calculate_fee(day_of_week, elapsed_time_parked)

    update_revenue = update(revenue_table) \
        .values(total_revenue=total_revenue)

    with engine.connect() as conn:
        conn.execute(update_revenue)

    remove_vehicle = update(lot_table) \
        .values(vehicle_name=None, parking_start_time=None, parking_leave_time=None) \
        .where(lot_table.c.vehicle_name == vehicle_name)

    with engine.connect() as conn:
        conn.execute(remove_vehicle)

    next_vehicle_query = select([queue_table.c.queue_id, queue_table.c.vehicle_name,
                                 queue_table.c.parking_time_length]) \
        .order_by(queue_table.c.queue_id) \
        .limit(1)

    with engine.connect() as conn:
        next_vehicle = [row for row in conn.execute(next_vehicle_query)]

    if len(next_vehicle) > 0:
        next_vehicle_id = next_vehicle[0][0]
        next_vehicle_name = next_vehicle[0][1]
        next_parking_time_length = next_vehicle[0][2]

        next_parking_leave_time = leave_datetime + timedelta(minutes=next_parking_time_length)

        leave_queue_query = queue_table.delete(queue_table.c.queue_id == next_vehicle_id)

        with engine.connect() as conn:
            conn.execute(leave_queue_query)

        update_space = update(lot_table) \
            .values(vehicle_name=next_vehicle_name, parking_start_time=leave_datetime,
                    parking_leave_time=next_parking_leave_time) \
            .where(lot_table.c.space_id == open_space)

        with engine.connect() as conn:
            conn.execute(update_space)
