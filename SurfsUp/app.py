# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
last_date = session.query(func.max(Measurement.date)).scalar()
year_ago = (dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)).date()

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; -Date format should be like YYYY-MM-DD<br/>"   
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; -Date format should be like YYYY-MM-DD<br/><br/>"           
    )



@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return a list of all precipitation in the last year"""
    # Query all precipitation in the past year
    results = (
    session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    order_by(Measurement.date).all()
    )
    session.close()

    # Convert list of tuples into normal list
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)



@app.route("/api/v1.0/stations")
def stations():

    """Return a list of all stations"""
    # Query all stations 
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert stations to a normal list
    all_stations = []
    for id, name in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():

    """Return a list of all tobs in the last year"""
    # Query tobs for the most active station
    most_active = (
    session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()
    )
    most_active_id = most_active[0]
    results = (
    session.query(
        Measurement.date, Measurement.tobs
    ).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == most_active_id).all()
    )
    session.close()

    # Convert list of tuples into normal list
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)



@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    """Return min, avg, and max temperatures from the start date."""
    
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()

    # Query min, avg, and max temperatures from start date
    results = (
        session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
        .filter(Measurement.date >= start_date)
        .all()
    )
    session.close()

    # Convert to list and prepare JSON response
    temp_min, temp_avg, temp_max = results[0]
    temperature_data = {
        "Start Date": start,
        "TEMP_MIN": temp_min,
        "TEMP_AVG": temp_avg,
        "TEMP_MAX": temp_max
    }

    return jsonify(temperature_data)



@app.route("/api/v1.0/<start>/<end>")
def temperatures_start_end(start, end):
    """Return min, avg, and max temperatures for a specified start to end date range."""
    
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()

    # Query min, avg, and max temperatures for the date range
    results = (
        session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )
    session.close()

    # Convert to list and prepare JSON response
    temp_min, temp_avg, temp_max = results[0]
    temperature_data = {
        "Start Date": start,
        "End Date": end,
        "TEMP_MIN": temp_min,
        "TEMP_AVG": temp_avg,
        "TEMP_MAX": temp_max
    }

    return jsonify(temperature_data)




if __name__ == '__main__':
    app.run(debug=True)