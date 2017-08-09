import parking.db.parking


def initialize_db():
    """Remove database if it exists, then create the database schema and initialize the tables.

    """

    parking.db.parking.drop_db()
    parking.db.parking.metadata.create_all()
    parking.db.parking.initialize()


if __name__ == '__main__':
    initialize_db()
