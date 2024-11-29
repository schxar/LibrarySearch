from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

app = Flask(__name__)
api = Api(app)

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '13380008373',
    'database': 'library'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def serialize_datetime(data):
    """Recursively serialize datetime objects in nested data structures."""
    if isinstance(data, list):
        return [serialize_datetime(item) for item in data]
    if isinstance(data, dict):
        return {
            key: serialize_datetime(value) for key, value in data.items()
        }
    if isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to string
    if isinstance(data, Decimal):
        return float(data)  # Convert Decimal to float
    return data

class Search(Resource):
    def get(self):
        """Retrieve cached search results for a query."""
        query = request.args.get('query', '')
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Check if the query exists and if it's outdated
            cursor.execute("SELECT * FROM search_results WHERE query = %s", (query,))
            results = cursor.fetchall()
            
            if results:
                created_at = results[0].get('created_at')  # Assuming all rows for a query have the same timestamp
                if created_at:
                    time_difference = datetime.now() - created_at
                    if time_difference > timedelta(days=30):  # Example: 30 days as outdated threshold
                        # Clear outdated rows and return empty results
                        cursor.execute("DELETE FROM search_results WHERE query = %s", (query,))
                        connection.commit()
                        return {'results': []}, 200
            
            # Serialize datetime objects
            results = serialize_datetime(results)
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
            query = """
                INSERT INTO search_results (id, query, title, author, isbn, publisher, language, year, extension, filesize, rating, quality, cover_url, book_url, audio_exists, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            
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
                    int(item.get('audioExists', 0))  # Convert to integer
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
