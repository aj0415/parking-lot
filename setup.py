from setuptools import setup, find_packages

setup(name='parking', version='0.1', packages=find_packages(),
      scripts=['bin/initialize-db'],
      entry_points={'console_scripts': ['parking-serve=parking.app:app.run',
                                        'parking-remove-db=parking.db.parking:drop_db']})
