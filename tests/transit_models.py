import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from tests.models import Base


class Route(Base):

    __tablename__ = 'route'

    id = Column(Integer, primary_key=True)
    route_directions = relationship('RouteDirection')
    directions = relationship('Direction', secondary='route_direction', uselist=True)
    patterns = relationship('Pattern', secondary='route_direction', uselist=True)


class Direction(Base):

    __tablename__ = 'direction'

    id = Column(Integer, primary_key=True)
    route_directions = relationship('RouteDirection')
    routes = relationship('Route', secondary='route_direction', uselist=True)
    patterns = relationship('Pattern', secondary='route_direction', uselist=True)


class RouteDirection(Base):

    __tablename__ = 'route_direction'

    id = Column(Integer, primary_key=True)
    route_id = Column(ForeignKey('route.id'))
    direction_id = Column(ForeignKey('direction.id'))
    route = relationship('Route')
    direction = relationship('Direction')
    patterns = relationship('Pattern', uselist=True)


class Pattern(Base):

    __tablename__ = 'pattern'

    id = Column(Integer, primary_key=True)
    route_direction_id = Column(ForeignKey('route_direction.id'))
    route_direction = relationship('RouteDirection')
    pattern_locations = relationship('PatternLocation', order_by='PatternLocation.order', uselist=True)
    locations = relationship('Location', secondary='pattern_location', uselist=True)


class PatternLocation(Base):

    __tablename__ = 'pattern_location'

    id = Column(Integer, primary_key=True)
    pattern_id = Column(ForeignKey('pattern.id'))
    order = Column(Integer)
    location_id = Column(ForeignKey('location.id'))
    pattern = relationship('Pattern')
    location = relationship('Location')


class Block(Base):

    __tablename__ = 'block'

    id = Column(Integer, primary_key=True)


class Trip(Base):

    __tablename__ = 'trip'

    id = Column(Integer, primary_key=True)
    pattern_id = Column(ForeignKey('pattern.id'))
    block_id = Column(ForeignKey('block.id'))
    pattern = relationship('Pattern')
    block = relationship('Block')


class TripStop(Base):

    __tablename__ = 'trip_stop'

    id = Column(Integer, primary_key=True)
    trip_id = Column(ForeignKey('trip.id'))
    trip = relationship('Trip')


class TripStopLocation(Base):

    __tablename__ = 'trip_stop_location'

    id = Column(Integer, primary_key=True)
    trip_stop_id = Column(ForeignKey('trip_stop.id'))
    location_id = Column(ForeignKey('location.id'))
    trip_stop = relationship('TripStop')
    location = relationship('Location')


class Location(Base):

    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    location_type_id = Column(ForeignKey('location_type.id'))
    pattern_locations = relationship('PatternLocation', uselist=True)
    patterns = relationship('Pattern', secondary='pattern_location', uselist=True)
    trip_stop_locations = relationship('TripStopLocation', uselist=True)
    trip_stops = relationship('TripStop', secondary='trip_stop_location', uselist=True)
    location_type = relationship('LocationType')


class LocationType(Base):

    __tablename__ = 'location_type'

    id = Column(Integer, primary_key=True)
