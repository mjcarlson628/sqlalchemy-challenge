import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes:<br><hr>"
        f"/api/v1.0/precipitation<br><br>"
        f"Precipitation data for the final year<br><hr>"
        f"/api/v1.0/stations<br><br>"
        f"List of weather stations<br><hr>"
        f"/api/v1.0/tobs<br><br>"
        f"Dates and temperatures at the most active station for the final year<br><hr>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br><br>"
        f"Temperatures measured starting with start date<br>"
        f"or between start and end dates yyyymmdd<br><hr>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)    
# get precipitation data from the last year
    year_ago = dt.date(2016, 8, 23)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    session.close()
# convert to {date: prcp} formatted dictionary
    results_dict = {}
    for i in range(len(results)):
        results_dict[results[i][0]] = results[i][1]        
    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
# search for all stations
    results = session.query(Station.name).\
        filter(Measurement.station == Station.station).\
        group_by(Measurement.station).all()    
    session.close()
# return json list
    station_names = list(np.ravel(results))    
    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# dates and temperatures for the final year of data, ending at 8/23/2017
    year_ago = dt.date(2016, 8, 23)
# identifier for the station with the most observations
    active_station = 'USC00519281'    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_station).\
        filter(Measurement.date >= year_ago).all()    
    session.close()
# store date and temperature in dictionary
    results_dict = {}
    for i in range(len(results)):
        results_dict[results[i][0]] = results[i][1]        
    return jsonify(results_dict)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end = 20170823):
    session = Session(engine)    
# convert start and end into strings and remove any dashes if they are present
# end defaults to the final date if only start is provided
    start = str(start).replace("-", "")
    end = str(end).replace("-", "")
# convert to date using string indices
    startdate = dt.date(int(start[0:4]), int(start[4:6]), int(start[6:8]))
    enddate = dt.date(int(end[0:4]), int(end[4:6]), int(end[6:8]))
# temperature data filtered between date ranges
    results = session.query(
        Measurement.date,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).\
        group_by(Measurement.date).all()    
    session.close()
# store date and temperature info in dictionaries
    all_results = []
    for date, min_temp, avg_temp, max_temp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tmin"] = min_temp
        temp_dict["tavg"] = avg_temp
        temp_dict["tmax"] = max_temp
        all_results.append(temp_dict)    
    return jsonify(all_results)
    
    
if __name__ == "__main__":
    app.run(debug=True)