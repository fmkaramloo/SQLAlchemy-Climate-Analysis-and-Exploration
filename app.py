from datetime import datetime
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate API! <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/calc_temps/&lt;start&gt;<br/>"
        f"/api/v1.0/calc_temps/&lt;start&gt;&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return prcp data for previous year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23)).all()

    # Create dict with date as key and prcp as the value.
    prcp = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    station_results = session.query(Station.station, Station.name).group_by(Station.station).all()

    station = list(np.ravel(station_results))
    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_results = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()
    
    tobs_list = list(np.ravel(tobs_results))
    # tobs_list=[]
    # for tobs in tobs_results:
    #     tobs_dict = {}
    #     tobs_dict["station"] = tobs[0]
    #     tobs_dict["tobs"] = float(tobs[1])
       
    #     tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/calc_temps/<start>")
def calc_temps(start='start_date'):
    start_date = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    start_results = session.query(func.max(Measurement.tobs), \
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date) 
    
    start_tobs = []
    for tobs in start_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])
        
        start_tobs.append(tobs_dict)

    return jsonify(start_tobs)
@app.route("/api/v1.0/calc_temps/<start>/<end>")

def calc_temps_2(start='start_date', end='end_date'):      
    start_date = datetime.strptime('2017-01-02', '%Y-%m-%d').date()
    end_date = datetime.strptime('2017-01-09', '%Y-%m-%d').date()

    start_end_results=session.query(func.max(Measurement.tobs).label("max_tobs"), \
                      func.min(Measurement.tobs).label("min_tobs"),\
                      func.avg(Measurement.tobs).label("avg_tobs")).\
                      filter(Measurement.date.between(start_date , end_date))   

    start_end_tobs = []
    for tobs in start_end_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_end_tobs.append(tobs_dict)
    
    return jsonify(start_end_tobs)



if __name__ == '__main__':
    app.run(debug=True)


