import xmlrpc.client as clt
from datetime import datetime
from models import StandLine, ResultAnalysis, TripInformation, Performances, TrippingSpeedAnalysis
from pymongo import MongoClient, ASCENDING
from constants import TRIP_REASON, TRIP_TYPE, ROTARY_SYSTEM, HOLE_TYPE

URL = "http://10.171.59.90:8069"
DB = "29_10_2023"
USERNAME = 'admin'
# password = "Ext3ns1on"
PASSWORD = "TeamSpace@2023"
UID = ''
MODELS = None
DEBUG=True



def connect():
    common = clt.ServerProxy('{}/xmlrpc/2/common'.format(URL))
    UID = common.authenticate(DB, USERNAME, PASSWORD, {})
    MODELS = clt.ServerProxy('{}/xmlrpc/2/object'.format(URL))
    
    trips, rigs, wells = getAllTrips(MODELS, UID)
    print('-------------------------')
    standLines = getAllStandLines(MODELS, UID)
    # # print(len(standLines))
    print('-------------------------')
    tripAnalysis = createTrips(trips, standLines)
    print('-------------------------')

    insertToMongo(tripAnalysis, rigs, wells)

def createTrips(trips, standLines):
    for i, trip in enumerate(trips):
        not_found_for = -1
        tmp_stand_lines = []
        
        for j, stand in enumerate(standLines):
            if (trip['id'] == stand['trip_id'][0]):
                not_found_for=  0
                tmp_stand_lines.append(stand)
                
            elif not_found_for != -1:
                not_found_for += 1
            
            if not_found_for >= 5:
                break
        trips[i]['stand_lines'] = tmp_stand_lines
        

    return trips

def insertToMongo(tripAnalysis, rigs, wells):
    # mongodb_uri = 'mongodb://madji:madjimadji@10.171.59.167:27017'
    mongodb_uri = 'mongodb://localhost:27017'
    mongodb_port = 27017  
    client = MongoClient(mongodb_uri, mongodb_port)
    deliverables_db = client['DELIVERABLES']
    tripping_speed_collection = deliverables_db['TS']
    
    trips_to_insert = []

    
    tripping_speed_collection.create_index([('well', ASCENDING), ('csg_size', ASCENDING),
    ('result_analysis.start_date', ASCENDING), ('result_analysis.end_date', ASCENDING)], unique=True)

   
    for trip in tripAnalysis:
        trip_stands, perf = compute_perf(trip['stand_lines'])
        performance = Performances(trip['tripping_time'],perf['post_connection_time'], trip['connection_time']*3600, trip['tripped_distance'], trip['total_connections'],
                                                perf['abnormal_time'], trip['avg_speed'], trip['avg_connection_time'])
        
        trip_reason = TRIP_REASON[trip['trip_reason']] if trip['trip_reason'] else '' 
        tripInfo = TripInformation(TRIP_TYPE[trip['trip_type']], trip_reason, 
                                   ROTARY_SYSTEM[trip['rotary_system']], HOLE_TYPE[trip['hole_type']])

        result = ResultAnalysis(
            datetime.strptime(trip['date_start'], '%Y-%m-%d %H:%M:%S'), 
            datetime.strptime(trip['date_end'], '%Y-%m-%d %H:%M:%S'), 
            trip['md_start'], 
            trip['md_end'])
        
        
        contractor = rigs[trip['rig_id'][0]]['rig_company'][-1].split(', ')[1] if rigs[trip['rig_id'][0]] != False else ''
        ts = TrippingSpeedAnalysis(trip['rig_id'][1],trip['well_id'][1], int(trip['well_id'][0]), int(trip['trip_number']), 
                                   trip['phase_id'][1], trip['csg'], trip['drill_pipe_size'], trip['bha_name'], trip['controled_speed'], 
                                   int(trip['benchmark_speed']), int(trip['benchmark_connection_time']), trip['threshold'],
                                   tripInfo.__dict__,
                                   trip_stands,
                                   result.__dict__,
                                   performance.__dict__, 
                                   datetime.strptime(trip['create_date'], '%Y-%m-%d %H:%M:%S'), 
                                    'TS Analysis', trip['create_uid'][1],

                                    wells[trip['well_id'][0]]['pole'][1] or '', 
                                    contractor, 
                                    rigs[trip['rig_id'][0]]['crew_change_start'], 
                                    rigs[trip['rig_id'][0]]['crew_change_end']
                                   )
        trips_to_insert.append(ts.__dict__)

        # if len(trips_to_insert) >= 50:
        #     tripping_speed_collection.insert_many(trips_to_insert, False)
        #     trips_to_insert = []

    tripping_speed_collection.insert_many(trips_to_insert, False)

def compute_perf(stands):
    trip_stands = []
    abnormal_time =  0
    post_connection_time= 0.0

    for i, s in enumerate(stands):
        tripping_time = 0
        if(i < len(stands)-1):
            tripping_time = (datetime.strptime(stands[i+1]['date_time_from'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(s['date_time_to'], '%Y-%m-%d %H:%M:%S')).total_seconds()

        sequence_time = tripping_time + s['connection_time'] * 60
        connection_time = s['connection_time'] * 60
        delta_depth = round(abs(s['depth_to'] - s['depth_from']), 2)
        gross_speed =  0 if sequence_time == 0 else round(delta_depth / sequence_time * 3600, 2)
        net_speed =  0 if connection_time == 0 else round(delta_depth / connection_time * 3600, 2)

        stand = StandLine(s['stand_number'], 
                        datetime.strptime(s['date_time_from'], '%Y-%m-%d %H:%M:%S'),
                        datetime.strptime(s['date_time_to'], '%Y-%m-%d %H:%M:%S'),
                        s['depth_from'], s['depth_to'], 
                        delta_depth, int(connection_time), int(sequence_time), gross_speed, net_speed, 
                        s['abnormal'], s['comment'] or 'Description..')

        trip_stands.append(stand.__dict__)
        
        if s['abnormal'] == True:     
            abnormal_time += sequence_time
        post_connection_time += (sequence_time - connection_time)

    
    return trip_stands, {'post_connection_time':post_connection_time, 'abnormal_time':abnormal_time}

            
def getAllTrips(MODELS, UID):
    
    res = MODELS.execute_kw(DB, UID, PASSWORD,
        'tripping.speed', 'search_read',
        [['|', ('well_id', '!=', False), ('rig_id', '!=', False), ('stand_lines', '!=', False)]], 
        {
            'fields':['id', 'create_date', 'create_uid',
                'date_start', 'date_end', 'md_start', 'md_end', 'benchmark_speed', 'threshold', 'benchmark_connection_time', 'bha_name', 'controled_speed',
                'drill_pipe_wet', 'csg','trip_type', 'trip_reason', 'hole_type', 'drill_pipe_size', 'rotary_system', 'well_id', 'wellbore_id', 'rig_id', 'phase_id',
                'trip_number', 'pod_id', 'tripped_distance', 'total_time', 'tripping_time', 'connection_time', 'avg_speed', 'avg_connection_time', 'total_connections',
                'pole_id', 'project_id', 'contractor_id', 'stand_lines'
                                            ], 
            # 'limit' : 23,
            'order': 'id ASC'
        })
    
    rigs, wells = getOtherInfo(MODELS, UID)
    
    return res, rigs, wells

def getAllStandLines(MODELS, UID):
    res = MODELS.execute_kw(DB, UID, PASSWORD,
        'stand.line', 'search_read',
        [[('trip_id', '!=', False)]], 
        {
            'fields':['trip_id', 'stand_number', 'date_time_from', 'date_time_to','depth_from', 'depth_to', 'connection_time', 'connection_speed',
                                                     'abnormal', 'description', 'comment'
                                                    ],
            # 'limit' : 100,
            # 'order': 'trip_id ASC'
        })
    return res

def getOtherInfo(MODELS, UID):
    rigs = MODELS.execute_kw(DB, UID, PASSWORD,
        'rig.information', 'search_read',
        [[]], 
        {'fields':['id', 'name', 'rig_company', 'crew_change_start','crew_change_end']})
    wells =  MODELS.execute_kw(DB, UID, PASSWORD,
        'well.information', 'search_read',
        [[]], 
        {'fields':['id', 'name', 'pole']})

    rigs_dict = {}
    wells_dict = {}
    for rig in rigs:
        rigs_dict[rig['id']] = rig
    for well in wells:
        wells_dict[well['id']] = well

    return rigs_dict, wells_dict
def log(msg):
    log_file = open('log.txt', 'a')
    log_file.write(str(msg) + '\n')
    if(DEBUG):
        print(str(msg))
    log_file.close()
    return
   

connect()