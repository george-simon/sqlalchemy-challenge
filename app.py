import numpy as np

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

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def HomePage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>tobs</a><br/>"
        f"<a href='/api/v1.0/2016-06-15'>start_date</a><br/>"
        f"<a href='/api/v1.0/2016-06-15,2016-06-25'>start_end_date</a><br/>"
    )
#################################################
# Flask Routes
#################################################

# query all precipitation & date data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    # Query all precipitation & date data
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the results
    # Create a dictionary from the row data and append to a list of all_results
    all_results = []
    for item in results:
        item_dict = {}
        item_dict["date"] = item[0]
        try:
            item_dict["precipitation"] = float(item[1])
        except TypeError as e:
            continue
        all_results.append(item_dict)

    return jsonify(all_results)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all countries in billing history
    results = session.query(Station.id, Station.station, Station.name).all()

    session.close()

    all_results = []
    for item in results:
        item_dict = {}
        item_dict["id"] = item[0]
        item_dict["station"] = item[1]
        item_dict["name"] = item[2]

        all_results.append(item_dict)

    return jsonify(all_results)

    # # Convert list of tuples into normal list
    # all_results = list(np.ravel(results))

    # return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > '2016-08-28').filter(Measurement.station == "USC00519281").\
    order_by(Measurement.tobs).all()

    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    print(results) #why is my query only returning one result?...

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    all_results = []
    for item in results:
        item_dict = {}
        item_dict["date"] = item[0]
        item_dict["min_temp"] = item[1]
        item_dict["max_temp"] = item[2]
        item_dict["avg_temp"] = item[3]
        all_results.append(item_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/<start>,<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end date.
    all_results = []
    for item in results:
        item_dict = {}
        item_dict["date"] = item[0]
        item_dict["min_temp"] = item[1]
        item_dict["max_temp"] = item[2]
        item_dict["avg_temp"] = item[3]
        all_results.append(item_dict)

    return jsonify(all_results)


if __name__ == '__main__':
    app.run(debug=True)