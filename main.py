from pymongo import MongoClient
# from bson.objectid import ObjectId


class DatabaseLayer(object):

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.db = None
        self.coll = None
        self.uri = 'mongodb://' + user + ':' + password + '@' + host + ':' + port
        print(self.uri)

    # open connection
    def connect(self, logging=False):
        self.connection = MongoClient(self.uri)
        if logging:
            # show dbs
            print(self.connection.list_database_names())

    # use database AAC the animals collection should be used
    def usedb(self, database, coll):
        self.db = self.connection['%s' % database]
        self.coll = self.db[coll]

    # checks to see if there is an active connection to the db

    def checkcoll(self):

        if self.coll is not None:
            return True

        else:
            print("self.coll is still none. Make sure that there is an active connection.")
            return False

    # assuming connection is already active

    def create(self, doc):

        if doc is not None:

            if self.checkcoll:
                c = self.coll

            else:
                print("self.db is still none. Make sure that there is an active connection.")
                raise Exception("no active connection")

            test = c.insert_one(doc)
            if test.inserted_id is not None:
                print("created test id is ", test.inserted_id)
                return True
            else:
                print("created test id is empty")
                return False
        else:
            print("Nothing to save, because data parameter is empty")
            return False

    # q needs to be dict  {key: pair} for query

    def read(self, q):

        if self.checkcoll:
            c = self.coll

        else:
            print("self.db is still none. Make sure that there is an active connection.")
            raise Exception("no active connection")

        # doing this is keep a list of the result for future use
        result = []
        for rec in c.find(q):
            result.append(rec)
        # print(result)

        return result

    # many is to use update_many() and create will create a record if none match
    def update(self, q, u, many=False, create=False):

        if self.checkcoll:
            c = self.coll

        else:
            print("self.db is still none. Make sure that there is an active connection.")
            raise Exception("no active connection")

        # do stuff
        # filter = { 'app': 'fan' }
        # new = { "$set": { 'quantity': 25 } }
        # self.coll.update_one(filter, new)

        # do the update

        if many:
            update = c.update_many(q, u, create)

        else:
            update = c.update_one(q, u, create)

        # after update return count
        if update.modified_count is None:
            return 0

        else:
            return update.modified_count

    def delete(self, q, many=False):

        if self.checkcoll:
            c = self.coll

        else:
            print("self.db is still none. Make sure that there is an active connection.")
            raise Exception("no active connection")

        if many:
            d = c.delete_many(q)

        else:
            d = c.delete_one(q)

        if d.deleted_count is None:
            return 0
        else:
            return d.deleted_count
