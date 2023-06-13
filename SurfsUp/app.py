# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes"""
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return last 12 months of query analysis for preciptation analysis"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Put in necessary variables
    sel = [Measurement.date, Measurement.prcp]

    # Calculate one year ago
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query results
    results = session.query(*sel).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    
    session.close()

    # create dictionary from row data
    all_data =[]
    for date, precipitation in results:
        results_dict = {}
        results_dict['date'] = date
        results_dict['precipitation'] = precipitation
        all_data.append(results_dict)
    
    return jsonify(all_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    station_activity = session.query(Measurement.station).\
        group_by(Measurement.station).all()

    session.close()
    
    # create dictionary from row data
    station_list = []
    for station in station_activity:
        station_list.append(station[0])
    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the time difference for onen year ago
    year_ago = dt.date(2017,8,18) - dt.timedelta(days=365)

    # Query results
    last_year = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').all()

    session.close()


    # Create a dictionary from row data
    all_last_year = []
    for date, tobs in last_year:
        last_year_dict = {}
        last_year_dict['date'] = date
        last_year_dict['tobs'] = tobs
        all_last_year.append(last_year_dict)

    return jsonify(all_last_year)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    sel = [func.avg(Measurement.tobs),
           func.min(Measurement.tobs),
           func.max(Measurement.tobs)]
    # Query Results
    start_date = session.query(*sel).\
        filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary from row data
    temp_list = []
    for avg, min, max in start_date:
        start_temp = {}
        start_temp['avg'] = avg
        start_temp['min'] = min
        start_temp['max'] = max
        temp_list.append(start_temp)
    
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.avg(Measurement.tobs),
       func.min(Measurement.tobs),
       func.max(Measurement.tobs)]
    
    end_date = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <=end).all()

    session.close()

    # Create a dictionary from row data
    temp_list = []
    for avg, min, max in end_date:
        end_temp = {}
        end_temp['avg'] = avg
        end_temp['min'] = min
        end_temp['max'] = max
        temp_list.append(end_temp)
    
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
    