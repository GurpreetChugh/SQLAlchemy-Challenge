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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns the day wise precipitation values of last 12 months from the last date in database."""
    session = Session(bind=engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_before_date = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_before_date).all()
    session.close()
    return jsonify(prcp_results) 
   
@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(bind=engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_before_date = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
    active_stations = session.query(Measurement.station, func.count(Measurement.station))\
                             .group_by(Measurement.station)\
                             .order_by(func.count(Measurement.station).desc()).all()
    temp_results = session.query(Measurement.date, Measurement.tobs)\
                          .filter(Measurement.station == active_stations[0][0], Measurement.date >= one_year_before_date).all()
    session.close()
    return jsonify(temp_results)

@app.route("/api/v1.0/<start>") 
def start_date(start):
    session = Session(bind=engine)
    start_result = session.query(func.Min(Measurement.tobs), func.Max(Measurement.tobs), func.avg(Measurement.tobs))\
           .filter(Measurement.date >= 'start').first()
    session.close()
    return jsonify(start_result)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(bind=engine)
    start_end_result = session.query(func.Min(Measurement.tobs), func.Max(Measurement.tobs), func.avg(Measurement.tobs))\
           .filter(Measurement.date >= 'start', Measurement.date <= 'end').first()
    session.close()
    return jsonify(start_end_result)

if __name__ == "__main__":
    app.run(debug=True)
         
#################################################
