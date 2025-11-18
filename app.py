from flask import Flask, render_template, jsonify, request
import firebase_admin
from firebase_admin import credentials, db
import datetime
import random

# ---------- FLASK APP ----------
app = Flask(__name__)

# ---------- FIREBASE CONFIG ----------
# Replace with your Firebase service account key file and DB URL
try:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://project-2625a-default-rtdb.firebaseio.com/'
    })
    firebase_initialized = True
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    firebase_initialized = False


# ---------- ENHANCED WATER QUALITY FUNCTIONS ----------

def get_tds_quality_details(tds_value):
    """Get detailed quality information based on TDS level"""
    if tds_value == 0 or tds_value == '-':
        return {
            "level": "No Data",
            "class": "no-data",
            "description": "No sensor data available",
            "drinking_safety": "Cannot assess without data",
            "health_impact": "Unknown - connect sensors",
            "usage": "Not determinable",
            "risk_level": "Unknown"
        }
    elif tds_value < 50:
        return {
            "level": "Ultra Pure",
            "class": "ultra-pure",
            "description": "Extremely pure demineralized water",
            "drinking_safety": "Not ideal for regular drinking - lacks essential minerals",
            "health_impact": "May leach minerals from body with long-term consumption",
            "usage": "Laboratory use, specific medical applications, batteries",
            "risk_level": "Low"
        }
    elif tds_value < 150:
        return {
            "level": "Excellent",
            "class": "excellent",
            "description": "Ideal mineralized drinking water",
            "drinking_safety": "Perfect for drinking and cooking",
            "health_impact": "Contains beneficial minerals like calcium and magnesium",
            "usage": "Drinking, cooking, baby formula, brewing coffee/tea",
            "risk_level": "Very Low"
        }
    elif tds_value < 250:
        return {
            "level": "Good",
            "class": "good",
            "description": "Good quality potable water",
            "drinking_safety": "Safe for drinking and domestic use",
            "health_impact": "Adequate mineral content for daily consumption",
            "usage": "General drinking, cooking, bathing, gardening",
            "risk_level": "Low"
        }
    elif tds_value < 350:
        return {
            "level": "Fair",
            "class": "fair",
            "description": "Acceptable quality with some impurities",
            "drinking_safety": "Generally safe with filtration recommended",
            "health_impact": "May contain elevated levels of certain minerals",
            "usage": "Domestic use with filtration, gardening, cleaning",
            "risk_level": "Moderate"
        }
    elif tds_value < 500:
        return {
            "level": "Poor",
            "class": "poor",
            "description": "Low quality water with significant impurities",
            "drinking_safety": "Not recommended without treatment",
            "health_impact": "May cause digestive issues with prolonged consumption",
            "usage": "Limited domestic use, toilet flushing, irrigation",
            "risk_level": "High"
        }
    elif tds_value < 900:
        return {
            "level": "Unacceptable",
            "class": "unacceptable",
            "description": "Highly contaminated water",
            "drinking_safety": "Not safe for drinking - treatment required",
            "health_impact": "Risk of gastrointestinal diseases and other health issues",
            "usage": "Industrial use only, construction, firefighting",
            "risk_level": "Very High"
        }
    else:
        return {
            "level": "Hazardous",
            "class": "hazardous",
            "description": "Severely contaminated - immediate action required",
            "drinking_safety": "Dangerous to health - avoid all contact",
            "health_impact": "Serious health risks including poisoning and disease",
            "usage": "Not recommended for any use without treatment",
            "risk_level": "Critical"
        }


def get_temperature_recommendations(temperature):
    """Get recommendations based on water temperature"""
    recommendations = []

    if temperature == 0 or temperature == '-':
        recommendations.extend([
            "No temperature data available",
            "Connect temperature sensor for complete analysis"
        ])
    elif temperature < 5:
        recommendations.extend([
            "🚫 Water is very cold - may affect digestion",
            "⚠️ Consider warming to room temperature before drinking",
            "❄️ Cold water may constrict blood vessels temporarily",
            "💧 Ideal for refrigeration and cold storage"
        ])
    elif 5 <= temperature < 15:
        recommendations.extend([
            "✅ Cool water - refreshing for drinking",
            "👍 Ideal temperature for water storage",
            "⚡ Good for metabolic functions and hydration",
            "🌡️ Perfect temperature for athletic activities"
        ])
    elif 15 <= temperature < 25:
        recommendations.extend([
            "✅ Room temperature - ideal for drinking",
            "👍 Best for hydration and digestion",
            "⚡ Optimal for nutrient absorption",
            "💫 Most comfortable for daily consumption"
        ])
    elif 25 <= temperature < 35:
        recommendations.extend([
            "⚠️ Slightly warm - pleasant for drinking in cold weather",
            "🔍 Monitor water source for bacterial growth",
            "⏰ Not ideal for long-term storage",
            "🌡️ Good for digestion and metabolism"
        ])
    elif 35 <= temperature < 50:
        recommendations.extend([
            "🚨 Warm water - potential contamination risk",
            "🔍 Check water source and storage conditions",
            "⏰ Immediate consumption recommended",
            "🦠 May promote bacterial growth if stored"
        ])
    else:
        recommendations.extend([
            "🚨 CRITICAL: Hot water - high contamination risk",
            "🆘 Immediate testing and investigation required",
            "🔧 Check for equipment malfunction",
            "🚱 Avoid consumption until verified safe"
        ])

    return recommendations


def get_improvement_suggestions(tds_value, temperature):
    """Get comprehensive improvement suggestions"""
    suggestions = []

    # TDS-based suggestions
    if tds_value == 0 or tds_value == '-':
        suggestions.extend([
            "🔌 Connect water quality sensors",
            "📊 Enable data collection system",
            "🔄 Check sensor connections and power"
        ])
    elif tds_value < 50:
        suggestions.extend([
            "💎 Add mineral supplements for drinking water",
            "🔄 Consider remineralization filter system",
            "🚰 Mix with natural mineral water for drinking",
            "📈 Monitor mineral levels regularly"
        ])
    elif tds_value < 250:
        suggestions.extend([
            "✅ Maintain current filtration system",
            "📅 Regular quarterly water testing recommended",
            "👀 Monitor for sudden TDS changes",
            "💧 Continue good water storage practices"
        ])
    elif tds_value < 500:
        suggestions.extend([
            "🔄 Install RO water purification system",
            "⚡ Use activated carbon filters",
            "🔦 Consider UV purification for bacteria",
            "📋 Test for specific contaminants (lead, arsenic)",
            "💡 Improve source water protection"
        ])
    elif tds_value < 900:
        suggestions.extend([
            "🚨 IMMEDIATE: Install RO purification system",
            "🆘 Use bottled water for drinking and cooking",
            "📞 Professional water testing needed immediately",
            "🔧 Check plumbing system for contamination sources",
            "💧 Install whole-house filtration system"
        ])
    else:
        suggestions.extend([
            "🆘 CRITICAL: USE BOTTLED WATER IMMEDIATELY",
            "📞 Contact water quality authorities immediately",
            "🔧 Professional remediation required",
            "🧪 Comprehensive water testing essential",
            "🏠 Consider alternative water sources"
        ])

    # Temperature-based suggestions
    if temperature != 0 and temperature != '-':
        if temperature > 35:
            suggestions.extend([
                "🌡️ Store water in cool, dark place",
                "🧊 Use insulated water containers",
                "🔍 Monitor for bacterial growth regularly",
                "⏰ Reduce water storage time"
            ])
        elif temperature < 10:
            suggestions.extend([
                "☕ Allow water to reach room temperature before drinking",
                "🏠 Check for pipe insulation issues",
                "💧 Consider water heating options",
                "🌡️ Monitor for freezing in cold weather"
            ])

    # General suggestions
    suggestions.extend([
        "📊 Regular monitoring with this dashboard",
        "📝 Maintain water quality log",
        "🔔 Set up alerts for quality changes",
        "🌱 Consider environmental factors affecting water source"
    ])

    return suggestions


def get_additional_parameters(tds_value, temperature):
    """Generate simulated additional water parameters based on TDS and temperature"""
    if tds_value == 0 or tds_value == '-':
        return {
            "ph": "-",
            "turbidity": "-",
            "chlorine": "-",
            "hardness": "-",
            "alkalinity": "-"
        }

    # Simulate pH based on TDS (generally inverse relationship)
    if tds_value < 100:
        ph_value = round(6.8 + random.uniform(0.1, 0.4), 1)  # Slightly acidic for pure water
    elif tds_value < 300:
        ph_value = round(7.0 + random.uniform(0.1, 0.5), 1)  # Near neutral
    elif tds_value < 600:
        ph_value = round(7.2 + random.uniform(0.1, 0.6), 1)  # Slightly alkaline
    else:
        ph_value = round(7.5 + random.uniform(0.2, 0.8), 1)  # Alkaline

    # Simulate turbidity (generally correlates with TDS)
    turbidity = min(10, round(tds_value / 100 + random.uniform(0.1, 0.5), 1))

    # Simulate chlorine residual
    if tds_value < 300:
        chlorine = round(0.2 + random.uniform(0.1, 0.3), 2)
    else:
        chlorine = round(0.1 + random.uniform(0.0, 0.2), 2)

    # Simulate hardness (correlates with TDS)
    hardness = round(tds_value * 0.7 + random.uniform(-10, 10))

    # Simulate alkalinity
    alkalinity = round(tds_value * 0.5 + random.uniform(-20, 20))

    return {
        "ph": ph_value,
        "turbidity": turbidity,
        "chlorine": chlorine,
        "hardness": hardness,
        "alkalinity": alkalinity
    }


def get_water_quality_standards():
    """Provide reference to water quality standards"""
    return {
        "WHO Standards": {
            "TDS": "≤ 500 ppm (recommended)",
            "Temperature": "Cool, preferably 10-15°C for drinking",
            "pH": "6.5-8.5",
            "Turbidity": "< 5 NTU"
        },
        "EPA Standards": {
            "TDS": "500 ppm (secondary standard)",
            "Temperature": "Based on local conditions",
            "pH": "6.5-8.5",
            "Chlorine": "< 4 mg/L"
        },
        "BIS Standards (India)": {
            "TDS": "500 ppm (acceptable), 2000 ppm (permissible)",
            "Temperature": "Ambient",
            "pH": "6.5-8.5",
            "Hardness": "< 300 mg/L"
        }
    }


# ---------- ORIGINAL FUNCTIONS ----------

def get_sensor_data():
    """Fetch latest TDS and temperature data from Firebase."""
    if not firebase_initialized:
        return []

    try:
        ref = db.reference("water_data")
        data = ref.order_by_key().limit_to_last(20).get()

        readings = []
        if data:
            for key, value in data.items():
                readings.append({
                    "timestamp": key,
                    "tds": float(value.get("tds", 0)),
                    "temperature": float(value.get("temperature", 0))
                })
            # Sort by timestamp
            readings.sort(key=lambda x: x["timestamp"])
        return readings
    except Exception as e:
        print(f"Error fetching Firebase data: {e}")
        return []


def get_latest_reading():
    """Get the most recent reading from Firebase."""
    if not firebase_initialized:
        return None

    try:
        ref = db.reference("water_data")
        data = ref.order_by_key().limit_to_last(1).get()

        if data:
            for key, value in data.items():
                return {
                    "timestamp": key,
                    "tds": float(value.get("tds", 0)),
                    "temperature": float(value.get("temperature", 0))
                }
        return None
    except Exception as e:
        print(f"Error fetching latest reading: {e}")
        return None


def add_real_time_data(tds, temperature):
    """Add real-time sensor data to Firebase."""
    if not firebase_initialized:
        return False

    try:
        ref = db.reference("water_data")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        data = {
            "tds": tds,
            "temperature": temperature
        }

        ref.child(timestamp).set(data)
        print(f"Added real data to Firebase: TDS={tds}, Temp={temperature}")
        return True
    except Exception as e:
        print(f"Error adding real-time data: {e}")
        return False


# ---------- ROUTES ----------

@app.route('/')
def index():
    latest_reading = get_latest_reading()

    if latest_reading:
        latest_tds = latest_reading["tds"]
        latest_temp = latest_reading["temperature"]

        # Get enhanced quality information
        quality_info = get_tds_quality_details(latest_tds)
        temp_recommendations = get_temperature_recommendations(latest_temp)
        improvement_suggestions = get_improvement_suggestions(latest_tds, latest_temp)
        additional_params = get_additional_parameters(latest_tds, latest_temp)
        quality_standards = get_water_quality_standards()

    else:
        latest_tds = 0
        latest_temp = 0
        quality_info = get_tds_quality_details(0)
        temp_recommendations = get_temperature_recommendations(0)
        improvement_suggestions = get_improvement_suggestions(0, 0)
        additional_params = get_additional_parameters(0, 0)
        quality_standards = get_water_quality_standards()

    return render_template('index.html',
                           latest_tds=latest_tds,
                           latest_temp=latest_temp,
                           quality_info=quality_info,
                           temp_recommendations=temp_recommendations,
                           improvement_suggestions=improvement_suggestions,
                           additional_params=additional_params,
                           quality_standards=quality_standards,
                           firebase_status=firebase_initialized,
                           has_data=latest_reading is not None)


@app.route('/data')
def data_api():
    """API endpoint for live data chart"""
    readings = get_sensor_data()
    # Format for chart display
    formatted_readings = []
    for reading in readings:
        # Convert timestamp to display format (HH:MM)
        timestamp_obj = datetime.datetime.strptime(reading["timestamp"], "%Y-%m-%dT%H:%M:%S")
        display_time = timestamp_obj.strftime("%H:%M")

        formatted_readings.append({
            "timestamp": display_time,
            "tds": reading["tds"],
            "temperature": reading["temperature"]
        })
    return jsonify(formatted_readings)


@app.route('/add_real_data', methods=['POST'])
def add_real_data_route():
    """Add real sensor data to Firebase"""
    try:
        data = request.get_json()
        tds = float(data.get('tds', 0))
        temperature = float(data.get('temperature', 0))

        success = add_real_time_data(tds, temperature)
        return jsonify({
            "success": success,
            "message": "Real data added successfully" if success else "Failed to add real data"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    """Endpoint for IoT sensors to send data"""
    try:
        data = request.get_json()

        # Extract sensor readings
        tds = float(data.get('tds', 0))
        temperature = float(data.get('temperature', 0))

        # Add to Firebase
        success = add_real_time_data(tds, temperature)

        return jsonify({
            "success": success,
            "message": "Sensor data stored successfully" if success else "Failed to store sensor data"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/questionnaire', methods=['POST'])
def process_questionnaire():
    """Process water quality questionnaire"""
    try:
        data = request.get_json()
        score = calculate_questionnaire_score(data)

        # Generate recommendations based on score
        if score >= 80:
            recommendations = [
                "Your water quality practices are excellent!",
                "Continue regular maintenance and monitoring.",
                "Consider annual professional testing to maintain standards."
            ]
        elif score >= 60:
            recommendations = [
                "Your water quality is generally good.",
                "Consider more frequent filter changes (every 3-6 months).",
                "Schedule professional testing within 6 months."
            ]
        elif score >= 40:
            recommendations = [
                "Your water quality needs attention.",
                "Install or upgrade your water filtration system.",
                "Schedule immediate professional testing.",
                "Consider using bottled water temporarily."
            ]
        else:
            recommendations = [
                "Immediate action required for water quality.",
                "Use bottled water for drinking immediately.",
                "Contact water authority with concerns.",
                "Schedule comprehensive professional testing."
            ]

        return jsonify({
            "success": True,
            "score": score,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


def calculate_questionnaire_score(data):
    """Calculate score based on questionnaire responses"""
    score = 0

    # Water source scoring
    source_scores = {
        'municipal': 30,
        'filtered': 30,
        'bottled': 25,
        'well': 15
    }

    # Changes in water scoring
    change_scores = {
        'no': 40,
        'slight': 30,
        'noticeable': 15,
        'significant': 5
    }

    # Testing frequency scoring
    test_scores = {
        '3months': 30,
        '6months': 20,
        '1year': 10,
        'never': 0
    }

    # Filtration system scoring
    filter_scores = {
        'ro': 30,
        'uv': 25,
        'carbon': 20,
        'none': 5
    }

    if 'source' in data:
        score += source_scores.get(data['source'], 0)
    if 'change' in data:
        score += change_scores.get(data['change'], 0)
    if 'test' in data:
        score += test_scores.get(data['test'], 0)
    if 'filter' in data:
        score += filter_scores.get(data['filter'], 0)

    return score


# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)