import parking.db.parking


def initialize_db():
    parking.db.parking.drop_db()
    parking.db.parking.metadata.create_all()
    parking.db.parking.initialize()


if __name__ == '__main__':
    initialize_db()
