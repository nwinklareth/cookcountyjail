#
# Model for sumarized Daily Population Changes
#

from flask.json import dumps, dump, load
from os.path import isfile
from os import environ


class DailyPopulationChanges:

    def __init__(self):
        self._path = self.choose_file()
        self.initialize_file()

    def choose_file(self):
        if not app.config['DEBUG'] and not app.config['TESTING']:
            # production
            return '/home/ubuntu/website/2.0/db_backups'
        elif app.config['TESTING']:
            # testing
            return '/tmp/test.json'
        else:
            # local
            return '/tmp/dpc.json'

    def _expand_entry(self, entry):
        """ Takes a tuple of (date, booked_male_as) and 
            turns it into a dict of the form expected 
            by the API. """
        return {
            'Date': entry['date'],
            'Booked': {
                'Male': {'AS': entry['booked_male_as']}
            }
        }

    def _load(self, f):
        try:
            return load(f)
        except ValueError as e:
            raise Exception(
                "Your JSON file at '{0}' may be empty or "
                'corrupted.'.format(self._path))


    def initialize_file(self):
        """ Make sure the file exists. If it doesn't, first create it,
            then initialize it with an empty JSON array inside. """
        # make sure the file exists
        if not isfile(self._path):
            # If not, create a file and 
            # put an empty list inside it
            self.clear()

    def clear(self):
        """ Write an empty JSON array to the file, 
            creating it if it doesn't already exist. """
        # lock here
        with open(self._path, 'w') as f:
            f.write('[]')

    def pop(self):
        """ Pop the last item in the list from our file."""
        # lock here
        with open(self._path, 'r+') as f:
            try:
                data = self._load(f)
                data.pop()
                f.seek(0)
                dump(data, f)
                f.truncate()
            except IndexError:
                # if empty list, do nothing
                pass

    def store(self, entry):
        """ Append the entry to our file. """
        assert isinstance(entry, dict)
        # lock here
        with open(self._path, 'r+') as f:
            # read the data
            data = self._load(f)
            # append to the data
            data.append(entry)
            # overwrite the old data
            f.seek(0)
            dump(data, f)
            f.truncate()

    def query(self):
        """ Return the data stored in our file as 
            Python objects. """
        #lock here
        with open(self._path) as f:
            data = self._load(f)
        return map(self._expand_entry, data)

    def to_json(self):
        """ Return the data stored in our file as JSON. """
        return dumps(self.query())


##########
#
# imports that dependencies are also dependent on
#
###############


from ccj.app import app