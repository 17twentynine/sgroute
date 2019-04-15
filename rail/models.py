#!/usr/bin/env python

import pprint
import datetime
from collections import defaultdict

import dateparser

class Station(object):
  def __init__(self, code, name, _date, is_junction=False):
    self.code = code
    self.colour = code[:2]
    self.id = int(code[2:])
    self.name = name
    self._date = dateparser.parse(_date)
    self.is_junction = is_junction

  def is_open(self):
    return self._date <= datetime.datetime.now()

  def __repr__(self):
    return pprint.pformat((self.colour, self.id, self.name, self.is_junction, id(self)))

class Line(object):

  def __init__(self, colour):
    self.colour = colour
    self._stations = []
    self.max_id = 0

  def add(self, station):
    self._stations.append(station)
    self.max_id = max(self.max_id, station.id)

  def get_stations(self):
    return sorted(self._stations, key=lambda x: x.id)

  def __repr__(self):
    return pprint.pformat((self.colour, self.max_id, self.stations[:5]))

class Map(object):
  def __init__(self):
    self.stations = {}
    self.connections = defaultdict(dict)

  def __repr__(self):
    return pprint.pformat(dict(self.connections)).replace("\\n", "\n")

if __name__ == "__main__":
  pass

class Scorer(object):
  def __init__(self, peak_weights, night_weights, non_peak_weights, default_weights):
    self.peak_weights = peak_weights
    self.night_weights = night_weights
    self.default_weights = default_weights
    self.non_peak_weights = non_peak_weights

  def __repr__(self):
    return pprint.pformat("""Peak: (%s)\nNight: (%s)\nNon Peak: (%s)\nDefault: (%s)""" % (self.peak_weights, self.night_weights, self.non_peak_weights, self.default_weights))

class Weight(object):
  def __init__(self, transit=1, change_line=1, distance=1):
    self.transit = transit
    self.change_line = change_line
    self.distance = distance

  def __repr__(self):
    return pprint.pformat("""Transit: %s, Change: %s, Distance: %s""" % (self.transit, self.change_line, self.distance))