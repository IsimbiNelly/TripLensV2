from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/triplens.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/trips', methods=['GET'])
def get_trips():
    """Get all trips with optional filtering"""
    try:
        conn = get_db_connection()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        vendor_id = request.args.get('vendor_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search', '')
        
        # Build query
        query = """
        SELECT t.*, v.name as vendor_name, l.pickup_longitude, l.pickup_latitude, 
               l.dropoff_longitude, l.dropoff_latitude
        FROM trip t
        JOIN vendor v ON t.vendor_id = v.id
        JOIN location l ON t.location_id = l.id
        WHERE 1=1
        """
        params = []
        
        if vendor_id:
            query += " AND t.vendor_id = ?"
            params.append(vendor_id)
            
        if start_date:
            query += " AND t.pickup_date >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND t.pickup_date <= ?"
            params.append(end_date)
            
        if search:
            query += " AND (t.id LIKE ? OR v.name LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        # Add pagination
        offset = (page - 1) * limit
        query += f" ORDER BY t.pickup_date DESC LIMIT {limit} OFFSET {offset}"
        
        trips = conn.execute(query, params).fetchall()
        
        # Convert to list of dictionaries
        trips_list = []
        for trip in trips:
            trip_dict = dict(trip)
            # Add status based on some logic (for demo purposes)
            if trip_dict['trip_duration'] > 30:
                trip_dict['status'] = 'completed'
            elif trip_dict['trip_duration'] < 5:
                trip_dict['status'] = 'cancelled'
            else:
                trip_dict['status'] = 'pending'
            trips_list.append(trip_dict)
        
        # Get total count for pagination
        count_query = """
        SELECT COUNT(*) as total
        FROM trip t
        JOIN vendor v ON t.vendor_id = v.id
        WHERE 1=1
        """
        count_params = []
        
        if vendor_id:
            count_query += " AND t.vendor_id = ?"
            count_params.append(vendor_id)
            
        if start_date:
            count_query += " AND t.pickup_date >= ?"
            count_params.append(start_date)
            
        if end_date:
            count_query += " AND t.pickup_date <= ?"
            count_params.append(end_date)
            
        if search:
            count_query += " AND (t.id LIKE ? OR v.name LIKE ?)"
            count_params.extend([f'%{search}%', f'%{search}%'])
        
        total = conn.execute(count_query, count_params).fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'trips': trips_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics"""
    try:
        conn = get_db_connection()
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build date filter
        date_filter = ""
        params = []
        if start_date and end_date:
            date_filter = "WHERE t.pickup_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        # Total trips
        total_trips_query = f"SELECT COUNT(*) as count FROM trip t {date_filter}"
        total_trips = conn.execute(total_trips_query, params).fetchone()['count']
        
        # Total passengers
        passengers_query = f"SELECT SUM(passenger_count) as total FROM trip t {date_filter}"
        total_passengers = conn.execute(passengers_query, params).fetchone()['total'] or 0
        
        # Average duration
        duration_query = f"SELECT AVG(trip_duration) as avg_duration FROM trip t {date_filter}"
        avg_duration = conn.execute(duration_query, params).fetchone()['avg_duration'] or 0
        
        # Estimated revenue (assuming $15 per trip)
        estimated_revenue = total_trips * 15
        
        conn.close()
        
        return jsonify({
            'total_trips': total_trips,
            'total_passengers': total_passengers,
            'avg_duration': round(avg_duration, 1),
            'estimated_revenue': estimated_revenue
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/trends', methods=['GET'])
def get_trip_trends():
    """Get trip trends data for charts"""
    try:
        conn = get_db_connection()
        
        period = request.args.get('period', 'daily')
        
        if period == 'daily':
            query = """
            SELECT DATE(pickup_date) as date, COUNT(*) as trips
            FROM trip
            WHERE pickup_date >= date('now', '-7 days')
            GROUP BY DATE(pickup_date)
            ORDER BY date
            """
        elif period == 'weekly':
            query = """
            SELECT strftime('%Y-%W', pickup_date) as week, COUNT(*) as trips
            FROM trip
            WHERE pickup_date >= date('now', '-8 weeks')
            GROUP BY strftime('%Y-%W', pickup_date)
            ORDER BY week
            """
        else:  # monthly
            query = """
            SELECT strftime('%Y-%m', pickup_date) as month, COUNT(*) as trips
            FROM trip
            WHERE pickup_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', pickup_date)
            ORDER BY month
            """
        
        trends = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify([dict(trend) for trend in trends])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/vendors', methods=['GET'])
def get_vendor_analytics():
    """Get vendor performance data"""
    try:
        conn = get_db_connection()
        
        query = """
        SELECT v.name, COUNT(t.id) as trip_count, 
               AVG(t.trip_duration) as avg_duration,
               SUM(t.passenger_count) as total_passengers
        FROM vendor v
        LEFT JOIN trip t ON v.id = t.vendor_id
        GROUP BY v.id, v.name
        ORDER BY trip_count DESC
        """
        
        vendors = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify([dict(vendor) for vendor in vendors])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
