import pandas as pd
import numpy as np
import sqlite3
import datetime as dt


def generate_2d_tec_map(cdate, mlat_min = 15., mlon_west = 250,
                        mlon_east = 34.,
                        inpDir = "/sd-data/med_filt_tec/"):

    """Generates data for 2D TEC map
    """

    # Read the median filtered TEC data
    inpColList = [ "dateStr", "timeStr", "Mlat",\
                   "Mlon", "med_tec", "dlat", "dlon" ]

    inpFile = inpDir + "tec-medFilt-" + cdate.strftime("%Y%m%d") + ".txt"
    print("reading data for " + cdate.strftime("%m/%d/%Y"))
    df = pd.read_csv(inpFile, delim_whitespace=True,
		     header=None, names=inpColList)

    # Change Mlon range from 0 to 360 to -180 to 180
    df.loc[:, "Mlon"] = df.Mlon.apply(lambda x: x if x<=180 else x-360)
    mlon_west = mlon_west - 360

    data_dict = {}
    if not df.empty:
	dateStr = str(df.dateStr[0])
        # Loop through each 5-min frame
	for time, group in df.groupby("timeStr"):

	    # Construct a datetime for current frame
	    timeStr = "00" + str(time)
	    dtmStr = dateStr + timeStr[-4:]
	    dtm = dt.datetime.strptime(dtmStr, "%Y%m%d%H%M")

            grb = group.loc[(group.Mlat >= mlat_min) & (group.Mlon >= mlon_west) & (group.Mlon <= mlon_east)]
            tec_map = grb.pivot(index="Mlat", columns="Mlon", values="med_tec").as_matrix()
            data_dict[dtm] = tec_map

            print("Extracted 2D matrix for " + str(dtm))

    return data_dict

def create_tec_map_table(sdate, edate, tec_resolution=5,
                         table_name="tec_map", 
                         db_name="tec_map.sqlite", 
                         db_dir="../data/sqlite3/"):
    """Creats a table in SQLite db to store datetimes of tec maps and their file paths"""

    # Make a db connection
    conn = sqlite3.connect(db_dir + db_name)

    # Create a table
    schema = "Create Table IF NOT EXISTS {tbl} (" +\
	     "datetime TIMESTAMP, "+\
             "file_path TEXT, " +\
             "PRIMARY KEY datetime)"
    schema = schema.format(tbl=table_name)

    # Create a dataframe
    nmaps = int(round((edate - sdate).total_seconds() / 60. / tec_resolution))
    dtms = [sdate + dt.timedelta(minutes=tec_resolution*i) for i in range(nmaps)] 
    df = pd.DataFrame(data={"datetime":dtms, "file_paths":"NaN"})

    # Write data to db
    df.to_sql(table_name, conn, schema=schema, if_exists="append", index=False)

    return



if __name__ == "__main__":


    # initialize parameters
    sdate = dt.datetime(2015, 1, 1)
    edate = dt.datetime(2016, 1, 1)

    tec_resolution = 5

    # Create a table for storing tec map datetimes and file paths
    create_tec_map_table(sdate, edate, tec_resolution=tec_resolution,
                         table_name="tec_map", 
                         db_name="tec_map.sqlite", 
                         db_dir="../data/sqlite3/")


#    #cdates = [sdate + dt.timedelta(days=i) for i in range((edate-sdate).days + 1)]
#
#    inpDir = "/sd-data/med_filt_tec/"
#    cdate = dt.datetime(2015, 1, 7)
#    mlat_min = 15.
#    mlon_west = 250
#    mlon_east = 34
#
#    data_dict = gen_2d_tec_map(cdate, mlat_min=mlat_min, mlon_west=mlon_west,
#                               mlon_east=mlon_east, inpDir=inpDir)
#
#    #closeness is sampled 12 times every 5 mins, lookback = (12*5min = 1 hour)
#    #freq 1 is 5mins
#    closeness_freq = 1
#    #size corresponds to the sample size
#    closeness_size = 12
#    #period is sampled 24 times every 1 hour (every 12th index), lookback = (24*12*5min = 1440min = 1day)
#    period_freq = 12
#    period_size = 24
#    #trend is sampled 24 times every 3 hours (every 36th index), lookback = (8*36*5min = 1440min = 1day)
#    trend_freq = 36
#    trend_size = 8

#    # Plot a TEC map
#    import matplotlib.pyplot as plt
#    fig, ax = plt.subplots()
#    ax.pcolormesh(data_dict[data_dict.keys()[0]])
#    plt.show()
    

