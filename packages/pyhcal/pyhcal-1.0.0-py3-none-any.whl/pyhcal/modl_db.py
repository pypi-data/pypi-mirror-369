# -*- coding: utf-8 -*-
"""
Created on Thu May  1 09:51:51 2025

@author: mfratki
"""
#import sqlite3
from pathlib import Path
import geopandas as gpd
import pandas as pd
#from hspf_tools.calibrator import etlWISKI, etlSWD


#stations_wiski = gpd.read_file('C:/Users/mfratki/Documents/GitHub/pyhcal/src/pyhcal/data/stations_wiski.gpkg')


stations_wiski = gpd.read_file(str(Path(__file__).resolve().parent/'data\\stations_wiski.gpkg')).dropna(subset='opnids')[['station_id','true_opnid','opnids','comments','modeled','repository_name','wplmn_flag']]
stations_wiski['source'] = 'wiski'
stations_equis = gpd.read_file(str(Path(__file__).resolve().parent/'data\\stations_EQUIS.gpkg')).dropna(subset='opnids')[['id_code','true_opnid','opnids','comments','modeled','repository_name']]
stations_equis['source'] = 'equis'
stations_equis['wplmn_flag'] = 0
stations_equis = stations_equis.rename(columns = {'id_code':'station_id'})


MODL_DB = pd.concat([stations_wiski,stations_equis])

database  = """
    -- Stations/Locations table
    CREATE TABLE IF NOT EXISTS Station (
        stationPK INTEGER PRIMARY KEY AUTOINCREMENT,
        reachPK INTEGER REFERENCES Reach(reachPK),
        stationID TEXT NOT NULL,
        stationName TEXT,
        stationOrigin TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        stationType TEXT,
        UNIQUE(stationID, stationOrigin)
    );
    
    -- Station Associations table
    CREATE TABLE IF NOT EXISTS StationAssociations (
        stationPK INTEGER REFERENCES Station(stationPK),
        associationPK INTEGER REFERENCES Station(stationPK)
    );

    -- Station Aliases table
    CREATE TABLE IF NOT EXISTS StationAliases (
        stationPK INTEGER NOT NULL,
        aliasPK INTEGER NOT NULL,
        FOREIGN KEY (stationPK) REFERENCES Station(stationPK),
        FOREIGN KEY (aliasPK) REFERENCES Station(stationPK)
    );
    
    CREATE TABLE Reach (
        reachPK INTEGER PRIMARY KEY,
        modelName TEXT NOT NULL,
        reachID INTEGER NOT NULL,
        drainageArea FLOAT 
    );
    
    CREATE TABLE Outlet (
        outletPK INTEGER PRIMARY KEY,
        outletName TEXT
    );
    
    -- Outlet-Station Associations table
    CREATE TABLE IF NOT EXISTS StationAssociations (
        outletPK INTEGER NOT NULL REFERENCES Outlet(outletPK),
        stationPK  INTEGER NOT NULL REFERENCES Station(reachPK)
    );
    
    -- Outlet-Reach Associations table
    CREATE TABLE IF NOT EXISTS StationAssociations (
        outletPK INTEGER NOT NULL REFERENCES Outlet(outletPK),
        reachPK  INTEGER NOT NULL REFERENCES Station(reachPK)
        exclude INTEGER NOT NULL
    );"""
    
    
#row = modl_db.MODL_DB.iloc[0]

#info = etlWISKI.info(row['station_id'])

#modl_db.MODL_DB.query('source == "equis"')

# outlet_dict = {'stations': {'wiski': ['E66050001'],
#                'equis': ['S002-118']},
#                'reaches': {'Clearwater': [650]}
                      



# station_ids = ['S002-118']
# #station_ids = ['E66050001']
# reach_ids = [650]
# flow_station_ids =  ['E66050001']
