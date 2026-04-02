import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Azure automatically provides these from the connection strings we set earlier
DBHOST = os.environ.get('DBHOST')
DBNAME = os.environ.get('DBNAME')
DBUSER = os.environ.get('DBUSER')
DBPASS = os.environ.get('DBPASS')

def get_db_connection():
    conn = psycopg2.connect(
        host=DBHOST,
        database=DBNAME,
        user=DBUSER,
        password=DBPASS,
        sslmode='require'
    )
    return conn

@app.route('/deposit', methods=['POST'])
def deposit_practice():
    data = request.get_json()
    
    # Farmer inputs
    name = data.get('farmer_name')
    region = data.get('region')
    practice = data.get('practice_type')
    lat = data.get('latitude')
    lon = data.get('longitude')
    notes = data.get('notes')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # The SQL uses ST_SetSRID and ST_MakePoint to turn lat/lon into a Map Object
        query = """
        INSERT INTO farm_data (farmer_name, region, practice_type, notes, geom)
        VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """
        cur.execute(query, (name, region, practice, notes, lon, lat))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Data deposited to Sweden Command"}), 201
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
