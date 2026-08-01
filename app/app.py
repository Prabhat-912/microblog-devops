from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest
import redis
import psycopg2

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

# Prometheus metric
request_counter = Counter(
    "app_requests_total",
    "Total app HTTP requests"
)

@app.route("/")
def home():
    request_counter.inc()

    # Increment homepage visit count
    redis_client.incr("homepage_visits")

    # Get current visit count
    visits = redis_client.get("homepage_visits")

    return jsonify({
        "message": "Microblog DevOps Platform",
        "visits": int(visits)
    })

@app.route("/health")
def health():
    request_counter.inc()

    health = {
        "flask": "healthy",
        "redis": "healthy",
        "postgres": "healthy"
    }

    # Check Redis
    try:
        redis_client.ping()
    except Exception:
        health["redis"] = "unhealthy"

    # Check PostgreSQL
    try:
        connection = psycopg2.connect(
            host="postgres",
            database="microblog",
            user="admin",
            password="admin123"
        )
        connection.close()
    except Exception:
        health["postgres"] = "unhealthy"

    # If any dependency is unhealthy, return HTTP 500
    if "unhealthy" in health.values():
        return jsonify(health), 500

    return jsonify(health), 200

@app.route("/db-check")
def db_check():
    request_counter.inc()

    try:
        connection = psycopg2.connect(
            host="postgres",
            database="microblog",
            user="admin",
            password="admin123"
        )

        cursor = connection.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255)
            )
        """)

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "database": "connected",
            "table": "posts created successfully"
        })

    except Exception as e:
        return jsonify({
            "database": "failed",
            "error": str(e)
        }), 500

@app.route("/posts")
def posts():
    request_counter.inc()

    try:
        connection = psycopg2.connect(
            host="postgres",
            database="microblog",
            user="admin",
            password="admin123"
        )

        cursor = connection.cursor()

        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()[0]

        # Insert sample posts only if table empty
        if count == 0:
            cursor.execute("""
                INSERT INTO posts (title)
                VALUES
                ('First Post'),
                ('DevOps Project')
            """)

            connection.commit()

        # Fetch all posts
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()

        posts_list = []

        for row in rows:
            posts_list.append({
                "id": row[0],
                "title": row[1]
            })

        cursor.close()
        connection.close()

        return jsonify(posts_list)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": "text/plain"
    }

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )