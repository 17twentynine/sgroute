#!/usr/bin/env python

import os
from datetime import time

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "StationMap.csv")
SECRET = '7d441f27d441f27567d441f2b6176a' #TODO read from environment
EXAMPLES = [
  "Travel from Holland Village to Bugis",
  "Travel from Boon Lay to Little India during peak hours",
  "Travel from Boon Lay to Little India during night hours",
  "Travel from Boon Lay to Little India during nonpeak hours",
]

# peak 6am-9am and 6pm-9pm Mon-Fri
# 10pm-6am on Mon-Sun

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

PEAK = 1
NIGHT = 2
NONPEAK = 3
DISTANCE = 4

TRANSIT_TIME = 1
CHANGE_LANE_TIME = 2

# Assuming inclusive intervals
TIME_CONFIG = {
  ( (time(6,0), time(8, 59, 59) ), (MONDAY, FRIDAY) ) : PEAK,
  ( (time(18,0), time(20, 59, 59) ), (MONDAY, FRIDAY) ) : PEAK,
  ( (time(20,0), time(23, 59, 59) ), (MONDAY, SUNDAY) ) : NIGHT,
  ( (time(0,0), time(5, 59, 59) ), (MONDAY, SUNDAY) ) : NIGHT,
  "default" : NONPEAK,
}

WEIGHT_CONFIG = {
  PEAK: {
    TRANSIT_TIME : {
      "NE": 12,
      "NS": 12,
      "default": 10,
    },
    CHANGE_LANE_TIME : {
      "default": 15
    },
  },
  NIGHT: {
    TRANSIT_TIME : {
      "DT": float('inf'),
      "CG": float('inf'),
      "CE": float('inf'),
      "TE": 8,
      "default" : 10,
    },
    CHANGE_LANE_TIME : {
      "default": 10,
    }
  },
  NONPEAK: {
    TRANSIT_TIME: {
      "DT": 8,
      "TE": 8,
      "default": 10,
    },
   CHANGE_LANE_TIME: {
      "default": 10,
    } 
  }
}

"""
Peak hours (6am-9am and 6pm-9pm on Mon-Fri)
	NS and NE lines take 12 minutes per station
	All other train lines take 10 minutes
	Every train line change adds 15 minutes of waiting time to the journey

Night hours (10pm-6am on Mon-Sun)
	DT, CG and CE lines do not operate
	TE line takes 8 minutes per stop
	All trains take 10 minutes per stop
	Every train line change adds 10 minutes of waiting time to the journey

Non-Peak hours (all other times)
	DT and TE lines take 8 minutes per stop
	All trains take 10 minutes per stop
	Every train line change adds 10 minutes of waiting time to the journey
"""