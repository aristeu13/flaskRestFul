from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import sqlite3

items = []


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()

        connection.close()
        if row:
            return {"message": {"id": row[0], "name": row[1], "price": row[2]}}, 200

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (NULL , ?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()


    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()

    @jwt_required()
    def get(self, name):
        try:
            item = self.find_by_name(name)
        except:
            return {"meessage": "erro"}, 500
        if item:
            return item
        return {"message": "items found"}, 404

    @jwt_required()
    def post(self, name):
        try:
            row = self.find_by_name(name)
        except:
            return {"meessage": "erro"}, 500

        if row:
            return {"message": "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        item = {"name": name, "price": data['price']}

        try:
            self.insert(item)
        except:
            return {"message": "erro"}, 500

        return {"message": "Item created successfully."}, 201

    @jwt_required()
    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'Item deleted'}

    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()

        item = self.find_by_name(name)
        update_item = {'name': name, 'price': data['price']}

        if item is None:
            try:
                self.insert(update_item)
            except:
                return {"message": "erro"}, 500
        else:
            try:
                self.update(update_item)
            except:
                return {"message": "erro"}, 500

        return {"message": "s"}, 201


class ItemList(Resource):
    @jwt_required()
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        table = result.fetchall()

        connection.close()

        table_obj = []
        for values in table:
            table_obj.append({"id": values[0], "name": values[1], "price": values[2]})

        return {"message": table_obj}, 201
