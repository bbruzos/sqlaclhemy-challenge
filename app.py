Import numpy as np 
import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request
import pandas as import pd

# Setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect existing database into a new model
Base = automap()
# Reflect tables
Base.prepare(engine, reflect=True)

# Save table reference
Measurement = Base.classes.Measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)


# Flask Routes
@app.route("/")
def homepage():

    print("You've arrived at the Main Page")
    # List api routes
    return (
        f"Available Routes for API: <br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation Data</a>"
        f"</br>"
        f"<a href='/api/v1.0/stations'< Compilation of stations and their names</a>"
        f"<br/>"
        f"<a href='/api/v1.0/tobs'> Compilation of year up to 2017 temperature data from the stations</a>"
        f"<br/>"
        f"<a href= '/api/v1.0/2016-08-13'> Serve max temp, min temp, amd avg temp from a given date</a>"
        f"</br>"
        f"<a href= '/api/v1.0/2016-08-13/2017-08-13'> Serve max temp, min temp, amd avg temp from a start date to an end date</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Turn queried results to a date and precipitation dictionary
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_data = []

    # Separate list of dicts using date and precipitation as keys w/ values
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)

    # Turn dictionary into JSON object
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations(): 
    session = Session(engine)
    results = session.query(Station.station, Station.name).distinct().all()
    session.close()
    # Dataframe creation and return as JSON representation
    station_df = pd.DataFrame(results)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query dates and temp data from most active station from the past year (2017)
    most_active_station= session.query(Measurement.station,func.count(Measurement.station)\
                    ).group_by(Measurement.station)\
                    .filter(Measurement.date>= datetime.datetime.strptime("2017-01-01", '%Y-%m-%d').date())\
                    .filter(Measurement.date<= datetime.datetime.strptime("2017-12-31", '%Y-%m-%d').date())\
                    .order_by(func.count(Measurement.station).desc()).all()
    # Grab date and temp data from most active station in 2017
    results= session.query(Measurement.tobs, Measurement.date\
                    ).filter(Measurement.date>= datetime.datetime.strptime("2017-01-01", '%Y-%m-%d').date())\
                    .filter(Measurement.date<= datetime.datetime.strptime("2017-12-31", '%Y-%m-%d').date())\
                    .filter(Measurement.station==most_active_station[0][0]).all()

    session.close()

    date_tobs_data = []
    # List of dicts with data and precipitation as keys w/ values
    for tobs, date in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = tobs
        date_tobs_data.append(temp_dict)

    station_dict = {}
    station_dict["Station"] = most_active_station[0][0]
    station_dict["tob"] = date_tobs_data = []

    # Grab temp observtions from tobs for previous year and represent as JSON
    return jsonify([station_dict])

@app.route("/api/v1.0/<start>")
def startDate(start):
    session = Session(engine)

    # From start date and beyond, calc Temp min, Temp max, and Temp avg 
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)\
                    ).filter(Measurement.date >= start_date).all()
    
    session.close()
    
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def startDate_endDate(start, end):

    session = Session(engine)

    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    # Between & including start date to end date, calc Temp min, Temp max, and Temp avg 
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)\
                    ).filter(Measurement.date >= start_date.date())\
                    .filter(Measurement.date <= end_date.date()).all()
    session.close()

    results jsonify(results)

    
if __name__ == "__main__":
    app.run(debug=True)






