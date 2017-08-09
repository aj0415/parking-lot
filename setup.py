from setuptools import os, setup, find_packages

db_command = os.path.join('bin', 'initialize-db')

setup(name='parking', version='0.1', packages=find_packages(),
      scripts=[db_command],
      entry_points={'console_scripts': ['parking-serve=parking.app:app.run',
                                        'parking-remove-db=parking.db.parking:drop_db']})
