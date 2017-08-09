from setuptools import setup, find_packages

setup(name='parking', version='0.1', packages=find_packages(),
      entry_points={'console_scripts': ['initialize-db=parking.initialize_db:initialize_db',
                                        'parking-serve=parking.app:app.run',
                                        'parking-remove-db=parking.db.parking:drop_db']})
