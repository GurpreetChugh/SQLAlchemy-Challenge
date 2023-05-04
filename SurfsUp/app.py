# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement =  Base.classes.measurement
Station =  Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(bind=engine)
#################################################
# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""

    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/station<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/startdate    (Date format in YYYY-MM-DD)<br/>"
            f"/api/v1.0/startdate/enddate    (Date format in YYYY-MM-DD)"
    )
  
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns the day wise precipitation values of last 12 months from the last date in database."""
    session = Session(bind=engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_before_date = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_before_date).all()
    session.close()
    prcp_results_dict = dict(prcp_results)
    return jsonify(prcp_results_dict)

@app.route("/api/v1.0/station")
def station():
    session = Session(bind=engine)
    station_list = session.query(Station.station, Station.name).all()
    session.close()
    station_dict = dict(station_list)
    return jsonify(station_dict)
   
@app.route("/api/v1.0/tobs") 
def tobs():
    """Returns the day wise temperature reading of most active station in terms of number of records."""
    session = Session(bind=engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_before_date = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
    active_stations = session.query(Measurement.station, func.count(Measurement.station))\
                             .group_by(Measurement.station)\
                             .order_by(func.count(Measurement.station).desc()).all()
    temp_results = session.query(Measurement.date, Measurement.tobs)\
                          .filter(Measurement.station == active_stations[0][0], Measurement.date >= one_year_before_date).all()
    session.close()
    temp_results_dict = dict(temp_results)
    return jsonify(temp_results_dict)

@app.route("/api/v1.0/<start>") 
def start_date(start):
    """Returns the  minimum, maximum and average temerature from the given start date."""
    session = Session(bind=engine)
    begin_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    start_result = session.query(func.Min(Measurement.tobs), func.Max(Measurement.tobs), func.avg(Measurement.tobs))\
           .filter(Measurement.date >= begin_date).first()
    session.close()
    start_result_dict = {'Min_temp': start_result[0], 'Max_temp': start_result[1], 'Avg_temp': start_result[2]}
    print(start)
    print(begin_date)
    print(start_result)
    return jsonify(start_result_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Returns the  minimum, maximum and average temerature between start and end date."""
    session = Session(bind=engine)
    begin_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    start_end_result = session.query(func.Min(Measurement.tobs), func.Max(Measurement.tobs), func.avg(Measurement.tobs))\
           .filter(Measurement.date >= begin_date, Measurement.date <= end_date).first()
    session.close()
    start_end_result_dict = {'Min_temp': start_end_result[0], 'Max_temp': start_end_result[1], 'Avg_temp': start_end_result[2]}
    return jsonify(start_end_result_dict)

if __name__ == "__main__":
    app.run(debug=True)
         
#################################################
