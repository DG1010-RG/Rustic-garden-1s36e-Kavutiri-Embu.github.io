from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/time', methods=['GET'])
def get_time():
    """Returns current server time"""
    return jsonify({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Azure uses PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
