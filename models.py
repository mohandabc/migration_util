
from typing import List
from datetime import datetime


class StandLine:
    def __init__(self, standNum, date_from, date_to, depth_from, depth_to, delta_depth, connection_time, sequence_time, gross_speed, net_speed, abnormal, description):
        self.standNum = standNum
        self.date_from = date_from
        self.date_to = date_to
        self.depth_from = depth_from
        self.depth_to = depth_to
        self.delta_depth = delta_depth
        self.connection_time = connection_time
        self.sequence_time = sequence_time
        self.gross_speed = gross_speed
        self.net_speed = net_speed
        self.abnormal = abnormal
        self.description = description

class TripInformation:
    def __init__(self, trip_type, trip_reason, rotary_system, hole_type):
        self.trip_type = trip_type
        self.trip_reason = trip_reason
        self.rotary_system = rotary_system
        self.hole_type = hole_type

class ResultAnalysis:
    def __init__(self, start_date, end_date, start_depth, end_depth):
        self.start_date = start_date
        self.end_date = end_date
        self.start_depth = start_depth
        self.end_depth = end_depth

class Performances:
    def __init__(self, tripping_time, post_connection_time, connection_time, tripping_distance, total_connections, abnormal_time, average_speed, average_connection_time):
        self.tripping_time = tripping_time
        self.post_connection_time = post_connection_time
        self.connection_time = connection_time
        self.tripping_distance = tripping_distance
        self.total_connections = total_connections
        self.abnormal_time = abnormal_time
        self.average_speed = average_speed
        self.average_connection_time = average_connection_time

class TrippingSpeedAnalysis:
    def __init__(self, rig, well, well_id, trip_number, phase, csg_size, drill_pipe_size, bha, trip_speed_controlled, benchmarkTS, benchmarkCT, 
                 threshold, trip_information, standline, result_analysis, performances, create_date, analysis_type, created_by, pole, contractor, crew_change_start, crew_change_end):
        self.rig = rig
        self.well = well
        self.well_id = well_id
        self.trip_number = trip_number
        self.phase = phase
        self.csg_size = csg_size
        self.drill_pipe_size = drill_pipe_size
        self.bha = bha
        self.trip_speed_controlled = trip_speed_controlled
        self.benchmarkTS = benchmarkTS
        self.benchmarkCT = benchmarkCT
        self.threshold = threshold
        self.trip_information = trip_information
        self.standline = standline
        self.result_analysis = result_analysis
        self.performances = performances
        self.create_date = create_date
        self.analysis_type = analysis_type
        self.created_by = created_by
        self.pole = pole
        self.contractor = contractor
        self.crew_change_start = crew_change_start
        self.crew_change_end = crew_change_end
