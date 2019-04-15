#!/usr/bin/env python
import csv
from collections import defaultdict

import config
from rail.models import Map
from rail.models import Station
from rail.models import Line
from rail.models import Scorer
from rail.models import Weight

class FileLoader(object):

  def load(self, _file):
    junctions = defaultdict(list)
    lines = {}
    _map = Map()
    with open(_file) as _file:
      csv_reader = csv.reader(_file, delimiter=',')
      self._populate_lines(csv_reader, _map, lines, junctions)

    for _, line in lines.items():
      self._add_connection(_map, line.get_stations())
    
    for _, junction in junctions.items():
      self._add_connection(_map, junction, is_junction = True)

    return _map

  def _populate_lines(self, csv_reader, _map, lines, junctions):
    for line, row in enumerate(csv_reader):
      code, name, _date = row
      if line:
        station = Station(code, name, _date)
        if name not in _map.stations:
          _map.stations[name] = station
        else:
          #TODO: choose nearest junction. now randomly choosing one
          pass

        if station.is_open():
          line = Line(station.colour)
          lines.setdefault(station.colour, line).add(station)
          junctions[station.name].append(station)
        else:
          #TODO: consider loading un opened stations
          pass

  def _add_connection(self, _map, stations, is_junction = False):
    if len(stations) <= 1:
      return
    prev_station = stations[0]
    prev_station.is_junction = is_junction
    #_map.connections[prev_station]
    for station in stations[1:]:
        station.is_junction = is_junction
        _map.connections[station][prev_station] = self.get_score(station)
        _map.connections[prev_station][station] = self.get_score(station)
        prev_station = station

  def get_weights(self, time_shift, station):
     
    distance = 1
    transit = config.WEIGHT_CONFIG[time_shift][config.TRANSIT_TIME]
    if transit.get(station.colour, None) is None:
      transit = transit["default"]
    else:
      transit = transit[station.colour]

    if station.is_junction:
      change_line = config.WEIGHT_CONFIG[time_shift][config.CHANGE_LANE_TIME]
      if change_line.get(station.colour, None) is None:
        change_line = change_line["default"]
      else:
        change_line = change_line[station.colour]
    else:
      change_line = 0

    return (transit, change_line, distance)
    
  def get_score(self, station):

    transit, change_line, distance = self.get_weights(config.PEAK, station)
    peak_weights = Weight(transit, change_line, distance)

    transit, change_line, distance = self.get_weights(config.NIGHT, station)
    night_weights = Weight(transit, change_line, distance)

    transit, change_line, distance = self.get_weights(config.NONPEAK, station)
    non_peak_weights = Weight(transit, change_line, distance)

    transit, change_line, distance = 0, 0, 1
    default_weights = Weight(transit, change_line, distance)

    return Scorer(peak_weights=peak_weights,
                  night_weights=night_weights,
                  non_peak_weights=non_peak_weights,
                  default_weights=default_weights)

if __name__ == "__main__":

  import sys
  file_name = sys.argv[1]
  _map = FileLoader().load(file_name)