#!/usr/bin/env python

import re
import pprint
import dateparser

import config
from rail.parser import FileLoader


class Route(object):
  def __init__(self, _map):
    self.map = _map
    self.connections = _map.connections
    self.stations = _map.stations
    self.paths = {}

  def query(self, request):
    stations = re.findall("Travel from (.+?) to (.+?) during (.+?) hours$", request)
    _from, _to = None, None
    if stations:
      (_from, _to, scorer), = stations
      _scorer = getattr(config, scorer.upper(), None)
      if _scorer is None:
        travel_time = dateparser.parse(scorer)
        if travel_time is not None:
          for (((start_time, end_time), (start_day, end_day)), _scorer) in config.TIME_CONFIG.items():
            if start_time <= travel_time.time() < end_time and start_day <= travel_time.weekday() <= end_day:
              scorer = _scorer
              break
          else:
            scorer = config.NONPEAK
      else:
        scorer = _scorer
    else:
      stations = re.findall("Travel from (.+?) to (.+?)$", request)
      if stations: (_from, _to), = stations 
      scorer = config.DISTANCE
  
    if _from not in self.stations:
      raise Exception("Unknown source")
    if _to not in self.stations:
      raise Exception("Unknown destination")

    if stations:
      if (_from, _to, scorer) in self.paths:
        path = self.paths[(_from, _to, scorer)]
      else:
        from_station = self.stations[_from]
        to_station = self.stations[_to]
        path = self.path(from_station, to_station, scorer)
        self.paths[(_from, _to, scorer)] = path
      return path
    else:
      return "Sorry, Unfortunately I am not able to understand your query. Please rephrase it"

  def get_weight(self, node, is_line_change, scorer):
    weight = None
    if scorer == config.DISTANCE:
      weight = node.default_weights.distance
    else:      
      if scorer == config.PEAK:
        weight = 'peak_weights'
      elif scorer == config.NONPEAK:
        weight = 'non_peak_weights'
      elif scorer == config.NIGHT:
        weight = 'night_weights'
      else:
        raise Exception("Invalid scorer")
      
      if is_line_change:
        weight = getattr(node, weight).change_line
      else:
        weight = getattr(node, weight).transit

    return weight

  def path(self, _from, _to, scorer=config.DISTANCE):
    shortest_paths = {_from: (None, 0)}
    current_node = _from
    visited = set()
    while current_node != _to:
      visited.add(current_node)
      destinations = self.connections[current_node]
      weight_to_current_node = shortest_paths[current_node][1]
      for next_node in destinations:
        is_line_change = current_node.name == next_node.name and next_node.is_junction
        weight = self.get_weight(self.connections[current_node][next_node], is_line_change, scorer) + weight_to_current_node
        if next_node not in shortest_paths:
          shortest_paths[next_node] = (current_node, weight)
        else:
          current_shortest_weight = shortest_paths[next_node][1]
          if current_shortest_weight > weight:
            shortest_paths[next_node] = (current_node, weight)
      next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
      if not next_destinations:
        return None
      current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    path = []
    while current_node is not None:
      path.append(current_node)
      next_node = shortest_paths[current_node][0]
      current_node = next_node
    path = path[::-1]
    path = self.get_readable_path(path, scorer)
    return path
  
  def get_readable_path(self, path, scorer):
    previous_station = None
    readable_full_path = []
    suggested_path = []
    direction = [path[0]]
    time_taken = 0
    if len(path) >= 2:
      if path[0].name == path[1].name:
        path = path[1:]
      if path[-1].name == path[-2].name:
        path = path[:-1]

    stations = []
    for station in path:
      is_line_change = False
      if previous_station is not None and station.colour != previous_station.colour:
        readable_full_path.append("Change from %s line to %s line" % (previous_station.colour, station.colour))
        suggested_path.append("Travel on %s line from %s to %s" % (previous_station.colour, direction[-1].name, previous_station.name))
        suggested_path.append("Change from %s line to %s line" % (previous_station.colour, station.colour))
        direction.append(previous_station)
        direction.append(station)
        is_line_change = True
      elif previous_station is not None:
        readable_full_path.append("Take %s line from %s to %s" % (station.colour, previous_station.name, station.name))
      if previous_station is not None:
        connection = self.connections[previous_station][station]
        time_taken += self.get_weight(connection, is_line_change, scorer)
        #stations.append("--%s-->" % (time_taken))
      stations.append(station.code)
      previous_station = station
    else:
      suggested_path.append("Travel on %s line from %s to %s" % (previous_station.colour, direction[-1].name, station.name))
      direction.append(station)

    output = []
    output.append("Stations Travelled: %s" % (len(stations) - 1))
    output.append("Scorer : %s" % (scorer))
    output.append("Stations: %s" % str(tuple(stations)) )
    if scorer != config.DISTANCE:
      output.append("Time Taken: %s minutes" % time_taken)
    output.append("---")

    if time_taken == float('inf'):
      return ["No Route Exists"]

    return output + suggested_path

if __name__ == "__main__":
  
  import sys
  file_name = sys.argv[1]
  _map = FileLoader().load(file_name)
  route = Route(_map)
  while True:
    request = raw_input()
    try:
      print ("\n".join(route.query(request)))
    except Exception as e:
      print (e.message)
