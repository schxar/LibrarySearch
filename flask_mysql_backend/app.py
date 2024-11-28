from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import mysql.connector

app = Flask(__name__)
api = Api(app)

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '13380008373',
    'database': 'test_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

class Search(Resource):
    def get(self):
        """Retrieve cached search results for a query."""
        query = request.args.get('query', '')
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM search_results WHERE query = %s", (query,))
            results = cursor.fetchall()
            return {'results': results}, 200
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def post(self):
        """Cache new search results."""
        data = request.get_json()
        if not isinstance(data, list):
            return {'error': 'Invalid data format'}, 400
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "INSERT INTO search_results (id, query, title, author, isbn, publisher, language, year, extension, filesize, rating, quality, cover_url, book_url, audio_exists) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            
            for item in data:
                cursor.execute(query, (
                    item.get('id'), 
                    request.args.get('query', ''),
                    item.get('title'), 
                    item.get('author'), 
                    item.get('isbn'), 
                    item.get('publisher'), 
                    item.get('language'), 
                    item.get('year'), 
                    item.get('extension'), 
                    item.get('filesize'), 
                    item.get('rating'), 
                    item.get('quality'), 
                    item.get('cover_url'), 
                    item.get('book_url'), 
                    item.get('audioExists')
                ))
            connection.commit()
            return {'message': 'Results cached successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10803, debug=True)
