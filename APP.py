from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# References to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_before_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_before_date).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations_list = [result[0] for result in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_before_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_before_date).all()
    session.close()

    tobs_list = [tobs for date, tobs in tobs_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    session = Session(engine)
    if not end:
        end = session.query(func.max(Measurement.date)).scalar()
    
temperature_data = session.query(
func.min(Measurement.tobs),
func.avg(Measurement.tobs),
func.max(Measurement.tobs)
).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

session.close()

    temperature_list = list(temperature_data[0])
    return jsonify(temperature_list)

if __name__ == "__main__":
    app.run(debug=True)
