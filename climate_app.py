import datetime as dt
from dateutil.relativedelta import relativedelta
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
engine = create_engine('sqlite:///hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurements
Station = Base.classes.station

# Create session from Python to the DB
session = Session(engine)

#################################################
# Set up Flask and landing page
#################################################
app = Flask(__name__)

# last 12 months variable
last_twelve_months = '2016-08-23'

@app.route("/")
def welcome():
    return (
        f"<p>Welcome to my Hawaii weather API!<br> <img src='https://ssl.quiksilver.com/static/QS/default/category-assets/marketing-landing/landing/build/img/surf/tiles/surf_featured_1.jpg'></p>"
        f"<p>Usage:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for each station for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and 8/23/17<br/><br/>."
        f"/api/v1.0/start_date/end_date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."
    )

# /api/v1.0/precipitation
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Date 12 months ago
    p_results = session.query(Measurement.date, func.avg(Measurement.prcp)).filter(Measurement.date >= last_twelve_months).group_by(Measurement.date).all()
    return jsonify(p_results)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    s_results = session.query(Station.station, Station.name).all()
    return jsonify(s_results)


# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    t_results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= last_twelve_months).all()
    return jsonify(t_results)


# /api/v1.0/<start>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<date>")
def startDateOnly(date):
    day_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    return jsonify(day_temp_results)


# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    multi_day_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(multi_day_temp_results)

if __name__ == "__main__":
    app.run(debug=True)