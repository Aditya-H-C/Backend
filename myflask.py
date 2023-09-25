from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Enable CORS by adding the appropriate headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    return response

db = mysql.connector.connect(
    host="DESKTOP-S594G9A",  # Use localhost if MySQL is on the same machine
    user="Aditya",
    password="Aditya1!",
    database="book_management2"
)
cursor = db.cursor()

# Create a book
@app.route('/books', methods=['POST'])
def create_book():
    try:
        data = request.json
        print("Received JSON data:", data)  # Debugging
        title = data['title']
        author = data.get('author', '')
        genre = data.get('genre', '')
        publication_date = data.get('publication_date', None)
        ##is_free = data.get('is_free', False)
        cost = data.get('cost',0)
        image_url = data.get('image_url','')
        description = data.get('description','')

        insert_query = "INSERT INTO books (title, author, genre, publication_date,cost,image_url,description) VALUES (%s, %s, %s, %s, %s,%s,%s)"
        cursor.execute(insert_query, (title, author, genre, publication_date,cost,image_url,description))
        db.commit()

        return jsonify({"message": "Book created successfully"}), 201

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"error": "Internal Server Error"}), 500

# Modify the 'fetch_books' endpoint to return key-value pairs
@app.route('/books', methods=['GET'])
def fetch_books():
    page = request.args.get('page', 1, type=int)
    items_per_page = 10
    offset = (page - 1) * items_per_page

    sort_order = request.args.get('sort_order', 'asc')
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'

    sort_by = request.args.get('sort_by', 'publication_date')
    if sort_by not in ['title', 'author', 'genre', 'publication_date', 'cost']:
        sort_by = 'publication_date'

    genre = request.args.get('genre')
    publication_date = request.args.get('publication_date')
    cost = request.args.get('cost')

    filters = []
    filter_values = []

    if genre:
        filters.append("genre = %s")
        filter_values.append(genre)

    if publication_date:
        filters.append("publication_date = %s")
        filter_values.append(publication_date)

    if cost is not None:
        filters.append("cost = %s")
        filter_values.append(int(cost))

    if filters:
        filter_query = "WHERE " + " AND ".join(filters)
        filter_values = tuple(filter_values)
    else:
        filter_query = ""
        filter_values = ()

    count_query = f"SELECT COUNT(*) FROM books {filter_query}"
    cursor.execute(count_query, filter_values)
    total_count = cursor.fetchone()[0]

    fetch_query = f"SELECT * FROM books {filter_query} ORDER BY {sort_by} {sort_order} LIMIT %s OFFSET %s"
    cursor.execute(fetch_query, filter_values + (items_per_page, offset))
    books = cursor.fetchall()

    # Create a custom response format
    response_data = {
        "page": page,
        "total_pages": (total_count + items_per_page - 1) // items_per_page,
        "total_items": total_count,
        "items": []
    }

    for book in books:
        book_data = {
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "genre": book[3],
            "publication_date": book[4].strftime('%Y-%m-%d') if book[4] else None,
            "cost": book[5],
            "image_url":book[6],
            "description":book[7]
        }
        response_data["items"].append(book_data)

    return jsonify(response_data), 200

# Fetch a book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def fetch_book_by_id(book_id):
    fetch_query = "SELECT * FROM books WHERE id = %s"
    cursor.execute(fetch_query, (book_id,))
    book = cursor.fetchone()

    if not book:
        return jsonify({"message": "Book not found"}), 404

    book_data = {
        "id": book[0],
        "title": book[1],
        "author": book[2],
        "genre": book[3],
        "publication_date": book[4].strftime('%Y-%m-%d') if book[4] else None,
        "cost": book[5],
        "image_url":book[6],
        "description":book[7]
    }

    return jsonify(book_data), 200

# Update a book by ID
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    publication_date = data.get('publication_date')
    cost = data.get('cost')
    image_url=data.get('image_url')
    description=data.get('description')

    update_query = "UPDATE books SET title = %s, author = %s, genre = %s, publication_date = %s, cost = %s,image_url=%s ,description=%s WHERE id = %s"
    cursor.execute(update_query, (title, author, genre, publication_date,cost,image_url,description, book_id))
    db.commit()

    return jsonify({"message": "Book updated successfully"}), 200

# Delete a book by ID
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    delete_query = "DELETE FROM books WHERE id = %s"
    cursor.execute(delete_query, (book_id,))
    db.commit()

    return jsonify({"message": "Book deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0",port='8080',ssl_context=("cert.pem","key.pem"))
