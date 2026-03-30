from fastapi import FastAPI, Response, Request, APIRouter
from typing import Union
from fastapi.responses import HTMLResponse
import uvicorn
from .package import StatsRow, StatsTable, StatsColumn, StatsSerializer
import time
from contextlib import asynccontextmanager
from battlenode import NewProcess

router = APIRouter()

@router.get("/getbackendinfo.aspx", response_class=HTMLResponse)
async def read_root(request: Request, auth: Union[str, None]):
    asof_table = StatsTable(
        columns=[
            StatsColumn("asof"),
            StatsColumn("tid"),
            StatsColumn("serverip"),
            StatsColumn("cb"),
        ],
        rows=[
            StatsRow([
                int(time.time()),
                "0",
                "127.0.0.1",
                "client",
            ])
        ]
    )

    config_table = StatsTable(
        columns=[
            StatsColumn("config")
        ],
        rows=[
            StatsRow(["swiffHost.setLatestGameVersion 1.7.94.0"])
        ]
    )

    options = []
    c_ranks = request.app.state.np.config.get("ranks", {})
    for ident, points in c_ranks.items():
        options.append({"rankSettings.setRank": [int(ident), int(points)]})

    options.append({"rankSettings.save": []})

    c_awards = request.app.state.np.config.get("awards", {})
    for ident, args in c_awards.items():
        _ident = (ident,) if "_" in ident else int(ident)
        options.append({"awards.setData": [_ident, *args]})

    wire = StatsSerializer.serialize(tables=[asof_table, config_table], options=options)
    return wire

    '''wire = StatsSerializer.serialize([
        asof_table,
        config_table,
    ], options=[
        {"rankSettings.setRank": [0, 0]},
        {"rankSettings.setRank": [1, 60]},
        {"rankSettings.setRank": [2, 80]},
        {"rankSettings.setRank": [3, 120]},
        {"rankSettings.setRank": [4, 200]},
        {"rankSettings.setRank": [5, 330]},
        {"rankSettings.setRank": [6, 520]},
        {"rankSettings.setRank": [7, 750]},
        {"rankSettings.setRank": [8, 1050]},
        {"rankSettings.setRank": [9, 1400]},
        {"rankSettings.setRank": [10, 1800]},
        {"rankSettings.setRank": [11, 2250]},
        {"rankSettings.setRank": [12, 2850]},
        {"rankSettings.setRank": [13, 3550]},
        {"rankSettings.setRank": [14, 4400]},
        {"rankSettings.setRank": [15, 5300]},
        {"rankSettings.setRank": [16, 6250]},
        {"rankSettings.setRank": [17, 7250]},
        {"rankSettings.setRank": [18, 8250]},
        {"rankSettings.setRank": [19, 9300]},
        {"rankSettings.setRank": [20, 10400]},
        {"rankSettings.setRank": [21, 11550]},
        {"rankSettings.setRank": [22, 12700]},
        {"rankSettings.setRank": [23, 14000]},
        {"rankSettings.setRank": [24, 15300]},
        {"rankSettings.setRank": [25, 16700]},
        {"rankSettings.setRank": [26, 18300]},
        {"rankSettings.setRank": [27, 20100]},
        {"rankSettings.setRank": [28, 22100]},
        {"rankSettings.setRank": [29, 24200]},
        {"rankSettings.setRank": [30, 26400]},
        {"rankSettings.setRank": [31, 28800]},
        {"rankSettings.setRank": [32, 31670]},
        {"rankSettings.setRank": [33, 34200]},
        {"rankSettings.setRank": [34, 37100]},
        {"rankSettings.setRank": [35, 40200]},
        {"rankSettings.setRank": [36, 43300]},
        {"rankSettings.setRank": [37, 46900]},
        {"rankSettings.setRank": [38, 50500]},
        {"rankSettings.setRank": [39, 54100]},
        {"rankSettings.setRank": [40, 57700]},
        {"rankSettings.setRank": [41, 0]},
        {"rankSettings.setRank": [42, 0]},
        {"rankSettings.setRank": [43, 0]},
        {"rankSettings.save": []},
        {"awards.setData": [("100_1",), "6,1, ,12"]},
        {"awards.setData": [("100_2",), "6,1, ,20", "9,23,ktt-3,54000"]},
        {"awards.setData": [("100_3",), "6,1, ,30", "9,23,ktt-3,180000"]},
        {"awards.setData": [("101_1",), "6,2, ,12"]},
        {"awards.setData": [("101_2",), "6,2, ,20", "9,20,ktt-0,54000"]},
        {"awards.setData": [("101_3",), "6,2, ,30", "9,20,ktt-0,180000"]},
        {"awards.setData": [("102_1",), "6,3, ,12"]},
        {"awards.setData": [("102_2",), "6,3, ,20", "9,21,ktt-1,54000"]},
        {"awards.setData": [("102_3",), "6,3, ,30", "9,21,ktt-1,180000"]},
        {"awards.setData": [("103_1",), "6,4, ,12"]},
        {"awards.setData": [("103_2",), "6,4, ,20", "9,22,ktt-2,54000"]},
        {"awards.setData": [("103_3",), "6,4, ,30", "9,22,ktt-2,180000"]},
        {"awards.setData": [("104_1",), "6,50, ,10"]},
        {"awards.setData": [("104_2",), "6,50, ,20", "1,113,slpts,300"]},
        {"awards.setData": [("104_3",), "6,50, ,30", "1,113,slpts,600"]},
        {"awards.setData": [("105_1",), "6,5, ,7"]},
        {"awards.setData": [("105_2",), "6,5, ,10", "1,5,wkls-12,50"]},
        {"awards.setData": [("105_3",), "6,5, ,17", "1,5,wkls-12,150"]},
        {"awards.setData": [("106_1",), "6,7, ,5"]},
        {"awards.setData": [("106_2",), "6,7, ,7", "1,7,wkls-5;wkls-11,50"]},
        {"awards.setData": [("106_3",), "6,7, ,18", "1,7,wkls-5;wkls-11,300"]},
        {"awards.setData": [("107_1",), "6,8, ,10"]},
        {"awards.setData": [("107_2",), "6,8, ,15", "1,8,klse,50"]},
        {"awards.setData": [("107_3",), "6,8, ,20", "1,8,klse,300"]},
        {"awards.setData": [("108_1",), "10,18, ,180"]},
        {"awards.setData": [("108_2",), "6,9, ,15", "9,148,vtp-12;vtp-3;wtp-30,72000"]},
        {"awards.setData": [("108_3",), "6,9, ,30", "9,148,vtp-12;vtp-3;wtp-30,180000"]},
        {"awards.setData": [("109_1",), "6,40, ,30"]},
        {"awards.setData": [("109_2",), "10,150, ,1200", "1,40,csgpm-0,1000"]},
        {"awards.setData": [("109_3",), "10,150, ,1500", "1,40,csgpm-0,4000"]},
        {"awards.setData": [("110_1",), "6,39, ,30"]},
        {"awards.setData": [("110_2",), "10,149, ,1200", "1,39,csgpm-1,1000"]},
        {"awards.setData": [("110_3",), "10,149, ,1500", "1,39,csgpm-1,4000"]},
        {"awards.setData": [("111_1",), "6,42, ,8"]},
        {"awards.setData": [("111_2",), "6,42, ,10", "9,128,etpk-1,36000"]},
        {"awards.setData": [("111_3",), "6,42, ,15", "9,128,etpk-1,216000", "1,42,rps,200"]},
        {"awards.setData": [("112_1",), "6,43, ,8"]},
        {"awards.setData": [("112_2",), "6,43, ,10", "9,129,etpk-5,36000"]},
        {"awards.setData": [("112_3",), "6,43, ,15", "9,129,etpk-5,216000", "1,43,hls,400"]},
        {"awards.setData": [("113_1",), "6,45, ,8"]},
        {"awards.setData": [("113_2",), "6,45, ,10", "9,130,etpk-6,36000"]},
        {"awards.setData": [("113_3",), "6,45, ,15", "9,130,etpk-6,180000", "1,45,resp,400"]},
        {"awards.setData": [("114_1",), "10,141, ,900"]},
        {"awards.setData": [("114_2",), "6,11, ,15", "9,114,atp,90000"]},
        {"awards.setData": [("114_3",), "6,11, ,35", "9,114,atp,180000"]},
        {"awards.setData": [("115_1",), "10,142, ,900"]},
        {"awards.setData": [("115_2",), "6,12, ,15", "9,25,vtp-10;vtp-4,90000"]},
        {"awards.setData": [("115_3",), "6,12, ,35", "9,25,vtp-10;vtp-4,180000"]},
        {"awards.setData": [("116_1",), "10,151, ,600"]},
        {"awards.setData": [("116_2",), "6,116, ,5", "9,115,vtp-1;vtp-4;vtp-6,90000"]},
        {"awards.setData": [("116_3",), "6,116, ,12", "9,115,vtp-1;vtp-4;vtp-6,144000"]},
        {"awards.setData": [("117_1",), "6,46, ,8"]},
        {"awards.setData": [("117_2",), "6,46, ,15", "9,27,tgpm-1,108000"]},
        {"awards.setData": [("117_3",), "6,46, ,30", "9,27,tgpm-1,216000"]},
        {"awards.setData": [("118_1",), "6,47, ,8"]},
        {"awards.setData": [("118_2",), "6,47, ,15", "9,27,tgpm-1,108000"]},
        {"awards.setData": [("118_3",), "6,47, ,30", "9,27,tgpm-1,216000"]},
        {"awards.setData": [("119_1",), "6,48, ,2"]},
        {"awards.setData": [("119_2",), "6,49, ,1", "1,48,tcd,10"]},
        {"awards.setData": [("119_3",), "6,48, ,3", "6,49, ,1", "1,48,tcd,40"]},
        {"awards.setData": [200, "6,127, ,"]},
        {"awards.setData": [201, "6,126, ,"]},
        {"awards.setData": [202, "6,125, ,"]},
        {"awards.setData": [203, "6,41, ,30", "9,19,tac,180000", "9,28,tasl,180000", "9,29,tasm,180000"]},
        {"awards.setData": [204, "6,59, ,1", "5,62,100_1,1", "5,63,101_1,1", "5,64,102_1,1", "5,65,103_1,1", "5,66,105_1,1", "5,67,106_1,1", "5,68,107_1,1"]},
        {"awards.setData": [205, "6,59, ,1", "5,69,100_2,1", "5,70,101_2,1", "5,71,102_2,1", "5,72,103_2,1", "5,73,105_2,1", "5,74,106_2,1", "5,75,107_2,1"]},
        {"awards.setData": [206, "6,59, ,1", "5,76,100_3,1", "5,77,101_3,1", "5,78,102_3,1", "5,79,103_3,1", "5,80,105_3,1", "5,81,106_3,1", "5,82,107_3,1"]},
        {"awards.setData": [207, "11,30,tt,540000", "3,51,cpt,1000", "3,52,dcpt,400", "3,41,twsc,5000"]},
        {"awards.setData": [208, "10,145, ,180", "11,31,attp-0,540000", "1,54,awin-0,300"]},
        {"awards.setData": [209, "10,146, ,180", "11,32,attp-1,540000", "1,55,awin-1,300"]},
        {"awards.setData": [210, "6,60, ,1", "11,26,tgpm-0,288000", "1,13,kgpm-0,8000", "1,15,bksgpm-0,25"]},
        {"awards.setData": [211, "6,61, ,1", "11,27,tgpm-1,288000", "1,14,kgpm-1,8000", "1,16,bksgpm-1,25"]},
        {"awards.setData": [212, "6,12, ,30", "9,25,vtp-10;vtp-4,360000", "1,12,vkls-10;vkls-4,8000"]},
        {"awards.setData": [213, "6,11, ,25", "9,24,vtp-0;vtp-1;vtp-2,360000", "1,11,vkls-0;vkls-1;vkls-2,8000"]},
        {"awards.setData": [214, "6,17, ,27", "6,83, ,0", "9,30,tt,648000"]},
        {"awards.setData": [215, "11,30,tt,360000", "3,43,hls,400", "3,42,rps,400", "3,45,resp,400"]},
        {"awards.setData": [216, "6,85, ,0.25"]},
        {"awards.setData": [217, "6,86, ,10", "9,33,vtp-4,90000"]},
        {"awards.setData": [218, "6,14, ,10", "11,27,tgpm-1,540000", "1,133,mbr-1-0;mbr-1-1;mbr-1-2;mbr-1-3;mbr-1-5;mbr-1-10;mbr-1-12,70"]},
        {"awards.setData": [219, "6,17, ,20", "1,51,cpt,100", "1,42,rps,70"]},
        {"awards.setData": [300, "10,18, ,300", "6,9, ,15"]},
        {"awards.setData": [301, "10,142, ,600", "6,12, ,20"]},
        {"awards.setData": [302, "6,120, ,10"]},
        {"awards.setData": [303, "10,143, ,1200", "9,28,tasl,144000"]},
        {"awards.setData": [304, "10,38, ,1200", "6,34, ,40", "9,19,tac,288000"]},
        {"awards.setData": [305, "6,41, ,15", "9,29,tasm,36000", "9,28,tasl,36000", "9,19,tac,36000"]},
        {"awards.setData": [306, "10,144, ,1080", "6,41, ,40", "9,29,tasm,72000"]},
        {"awards.setData": [307, "6,41, ,55", "9,29,tasm,90000", "9,28,tasl,180000"]},
        {"awards.setData": [308, "6,34, ,45", "9,19,tac,216000", "5,87,wlr,2"]},
        {"awards.setData": [309, "10,141, ,1200", "6,11, ,20"]},
        {"awards.setData": [310, "6,110, ,10", "9,121,vtp-0;vtp-1;vtp-2;vtp-6,36000"]},
        {"awards.setData": [311, "9,99,mtt-0-0;mtt-1-0,0", "9,101,mtt-0-2;mtt-1-2,0", "9,103,mtt-0-4,0", "9,104,mtt-0-5;mtt-1-5,0", "9,108,mtt-0-9,0", "9,32,attp-1,432000"]},
        {"awards.setData": [312, "9,100,mtt-0-1;mtt-1-1,0", "9,102,mtt-0-3;mtt-1-3,0", "9,105,mtt-0-6,0", "9,106,mtt-0-7,0", "9,107,mtt-0-8,0", "9,31,attp-0,432000"]},
        {"awards.setData": [313, "6,17, ,20", "1,88,bksgpm-0;bksgpm-1,10"]},
        {"awards.setData": [314, "6,17, ,10", "6,83, ,", "11,30,tt,180000"]},
        {"awards.setData": [315, "6,17, ,10", "11,30,tt,432000", "1,88,bksgpm-0;bksgpm-1,10"]},
        {"awards.setData": [316, "3,10,vkls-7,200"]},
        {"awards.setData": [317, "6,86, ,15", "9,33,vtp-4,90000"]},
        {"awards.setData": [318, "6,138, ,15", "9,137,vtp-12,36000"]},
        {"awards.setData": [319, "6,39, ,10", "11,36,ctgpm-1,90000"]},
        {"awards.setData": [400, "6,89, ,5"]},
        {"awards.setData": [401, "6,89, ,10"]},
        {"awards.setData": [402, "6,48, ,4"]},
        {"awards.setData": [403, "6,109, ,4"]},
        {"awards.setData": [404, "6,86, ,10"]},
        {"awards.setData": [406, "6,47, ,7"]},
        {"awards.setData": [407, "6,139, ,5"]},
        {"awards.setData": [408, "6,110, ,5"]},
        {"awards.setData": [409, "6,93, ,8"]},
        {"awards.setData": [410, "6,8, ,8"]},
        {"awards.setData": [411, "6,44, ,8"]},
        {"awards.setData": [412, "6,124, ,"]},
        {"awards.setData": [413, "6,7, ,4"]},
        {"awards.setData": [414, "6,9, ,10"]},
        {"awards.setData": [415, "6,6, ,10"]},
        {"awards.setData": [("120_1",), "6,152, ,6"]},
        {"awards.setData": [("120_2",), "6,152, ,10", "9,153,mtt-1-10;mtt-2-10;mtt-2-11;mtt-1-12;mtt-2-12,7200"]},
        {"awards.setData": [("120_3",), "6,152, ,14", "9,153,mtt-1-10;mtt-2-10;mtt-2-11;mtt-1-12;mtt-2-12,18000"]},
        {"awards.setData": [("121_1",), "10,154, ,300"]},
        {"awards.setData": [("121_2",), "6,156, ,8", "9,155,vtp-14;vtp-15,3600"]},
        {"awards.setData": [("121_3",), "6,156, ,12", "9,155,vtp-14;vtp-15,14400"]},
        {"awards.setData": [320, "6,157, ,5", "5,158,vkls-15,40"]},
        {"awards.setData": [321, "6,152, ,15", "5,159,mwin-1-12;mwin-2-12,2", "5,160,mwin-1-10;mwin-2-10,2", "5,161,mwin-2-11,2"]},
        {"awards.setData": [322, "6,162, ,9", "9,163,vtp-14,7200"]},
        {"awards.setData": [323, "7,164,vdstry-15,4", "7,165,vdstry-14,2", "7,166,vdths-15,5", "7,167,vdths-14,5"]},
        {"awards.setData": [416, "6,168, ,"]}
    ])
    return wire'''

'''@app.get("/getbackendinfo.aspx", response_class=HTMLResponse)
async def read_root(auth: Union[str, None]):
    return """O
H	asof	tid	serverip	cb
D	1728996060	0	127.0.0.1	client
H	config
D	swiffHost.setLatestGameVersion 1.7.94.0
rankSettings.setRank 0 0
rankSettings.setRank 1 40
rankSettings.setRank 2 80
rankSettings.setRank 3 120
rankSettings.setRank 4 200
rankSettings.setRank 5 330
rankSettings.setRank 6 520
rankSettings.setRank 7 750
rankSettings.setRank 8 1050
rankSettings.setRank 9 1400
rankSettings.setRank 10 1800
rankSettings.setRank 11 2250
rankSettings.setRank 12 2850
rankSettings.setRank 13 3550
rankSettings.setRank 14 4400
rankSettings.setRank 15 5300
rankSettings.setRank 16 6250
rankSettings.setRank 17 7250
rankSettings.setRank 18 8250
rankSettings.setRank 19 9300
rankSettings.setRank 20 10400
rankSettings.setRank 21 11550
rankSettings.setRank 22 12700
rankSettings.setRank 23 14000
rankSettings.setRank 24 15300
rankSettings.setRank 25 16700
rankSettings.setRank 26 18300
rankSettings.setRank 27 20100
rankSettings.setRank 28 22100
rankSettings.setRank 29 24200
rankSettings.setRank 30 26400
rankSettings.setRank 31 28800
rankSettings.setRank 32 31500
rankSettings.setRank 33 34200
rankSettings.setRank 34 37100
rankSettings.setRank 35 40200
rankSettings.setRank 36 43300
rankSettings.setRank 37 46900
rankSettings.setRank 38 50500
rankSettings.setRank 39 54100
rankSettings.setRank 40 57700
rankSettings.setRank 41 0
rankSettings.setRank 42 0
rankSettings.setRank 43 0
rankSettings.save
awards.setData 100_1 "6,1, ,12"
awards.setData 100_2 "6,1, ,20" "9,23,ktt-3,54000"
awards.setData 100_3 "6,1, ,30" "9,23,ktt-3,180000"
awards.setData 101_1 "6,2, ,12"
awards.setData 101_2 "6,2, ,20" "9,20,ktt-0,54000"
awards.setData 101_3 "6,2, ,30" "9,20,ktt-0,180000"
awards.setData 102_1 "6,3, ,12"
awards.setData 102_2 "6,3, ,20" "9,21,ktt-1,54000"
awards.setData 102_3 "6,3, ,30" "9,21,ktt-1,180000"
awards.setData 103_1 "6,4, ,12"
awards.setData 103_2 "6,4, ,20" "9,22,ktt-2,54000"
awards.setData 103_3 "6,4, ,30" "9,22,ktt-2,180000"
awards.setData 104_1 "6,50, ,10"
awards.setData 104_2 "6,50, ,20" "1,113,slpts,300"
awards.setData 104_3 "6,50, ,30" "1,113,slpts,600"
awards.setData 105_1 "6,5, ,7"
awards.setData 105_2 "6,5, ,10" "1,5,wkls-12,50"
awards.setData 105_3 "6,5, ,17" "1,5,wkls-12,150"
awards.setData 106_1 "6,7, ,5"
awards.setData 106_2 "6,7, ,7" "1,7,wkls-5;wkls-11,50"
awards.setData 106_3 "6,7, ,18" "1,7,wkls-5;wkls-11,300"
awards.setData 107_1 "6,8, ,10"
awards.setData 107_2 "6,8, ,15" "1,8,klse,50"
awards.setData 107_3 "6,8, ,20" "1,8,klse,300"
awards.setData 108_1 "10,18, ,180"
awards.setData 108_2 "6,9, ,15" "9,148,vtp-12;vtp-3;wtp-30,72000"
awards.setData 108_3 "6,9, ,30" "9,148,vtp-12;vtp-3;wtp-30,180000"
awards.setData 109_1 "6,40, ,30"
awards.setData 109_2 "10,150, ,1200" "1,40,csgpm-0,1000"
awards.setData 109_3 "10,150, ,1500" "1,40,csgpm-0,4000"
awards.setData 110_1 "6,39, ,30"
awards.setData 110_2 "10,149, ,1200" "1,39,csgpm-1,1000"
awards.setData 110_3 "10,149, ,1500" "1,39,csgpm-1,4000"
awards.setData 111_1 "6,42, ,8"
awards.setData 111_2 "6,42, ,10" "9,128,etpk-1,36000"
awards.setData 111_3 "6,42, ,15" "9,128,etpk-1,216000" "1,42,rps,200"
awards.setData 112_1 "6,43, ,8"
awards.setData 112_2 "6,43, ,10" "9,129,etpk-5,36000"
awards.setData 112_3 "6,43, ,15" "9,129,etpk-5,216000" "1,43,hls,400"
awards.setData 113_1 "6,45, ,8"
awards.setData 113_2 "6,45, ,10" "9,130,etpk-6,36000"
awards.setData 113_3 "6,45, ,15" "9,130,etpk-6,180000" "1,45,resp,400"
awards.setData 114_1 "10,141, ,900"
awards.setData 114_2 "6,11, ,15" "9,114,atp,90000"
awards.setData 114_3 "6,11, ,35" "9,114,atp,180000"
awards.setData 115_1 "10,142, ,900"
awards.setData 115_2 "6,12, ,15" "9,25,vtp-10;vtp-4,90000"
awards.setData 115_3 "6,12, ,35" "9,25,vtp-10;vtp-4,180000"
awards.setData 116_1 "10,151, ,600"
awards.setData 116_2 "6,116, ,5" "9,115,vtp-1;vtp-4;vtp-6,90000"
awards.setData 116_3 "6,116, ,12" "9,115,vtp-1;vtp-4;vtp-6,144000"
awards.setData 117_1 "6,46, ,8"
awards.setData 117_2 "6,46, ,15" "9,27,tgpm-1,108000"
awards.setData 117_3 "6,46, ,30" "9,27,tgpm-1,216000"
awards.setData 118_1 "6,47, ,8"
awards.setData 118_2 "6,47, ,15" "9,27,tgpm-1,108000"
awards.setData 118_3 "6,47, ,30" "9,27,tgpm-1,216000"
awards.setData 119_1 "6,48, ,2"
awards.setData 119_2 "6,49, ,1" "1,48,tcd,10"
awards.setData 119_3 "6,48, ,3" "6,49, ,1" "1,48,tcd,40"
awards.setData 200 "6,127, ,"
awards.setData 201 "6,126, ,"
awards.setData 202 "6,125, ,"
awards.setData 203 "6,41, ,30" "9,19,tac,180000" "9,28,tasl,180000" "9,29,tasm,180000"
awards.setData 204 "6,59, ,1" "5,62,100_1,1" "5,63,101_1,1" "5,64,102_1,1" "5,65,103_1,1" "5,66,105_1,1" "5,67,106_1,1" "5,68,107_1,1"
awards.setData 205 "6,59, ,1" "5,69,100_2,1" "5,70,101_2,1" "5,71,102_2,1" "5,72,103_2,1" "5,73,105_2,1" "5,74,106_2,1" "5,75,107_2,1"
awards.setData 206 "6,59, ,1" "5,76,100_3,1" "5,77,101_3,1" "5,78,102_3,1" "5,79,103_3,1" "5,80,105_3,1" "5,81,106_3,1" "5,82,107_3,1"
awards.setData 207 "11,30,tt,540000" "3,51,cpt,1000" "3,52,dcpt,400" "3,41,twsc,5000"
awards.setData 208 "10,145, ,180" "11,31,attp-0,540000" "1,54,awin-0,300"
awards.setData 209 "10,146, ,180" "11,32,attp-1,540000" "1,55,awin-1,300"
awards.setData 210 "6,60, ,1" "11,26,tgpm-0,288000" "1,13,kgpm-0,8000" "1,15,bksgpm-0,25"
awards.setData 211 "6,61, ,1" "11,27,tgpm-1,288000" "1,14,kgpm-1,8000" "1,16,bksgpm-1,25"
awards.setData 212 "6,12, ,30" "9,25,vtp-10;vtp-4,360000" "1,12,vkls-10;vkls-4,8000"
awards.setData 213 "6,11, ,25" "9,24,vtp-0;vtp-1;vtp-2,360000" "1,11,vkls-0;vkls-1;vkls-2,8000"
awards.setData 214 "6,17, ,27" "6,83, ,0" "9,30,tt,648000"
awards.setData 215 "11,30,tt,360000" "3,43,hls,400" "3,42,rps,400" "3,45,resp,400"
awards.setData 216 "6,85, ,0.25"
awards.setData 217 "6,86, ,10" "9,33,vtp-4,90000"
awards.setData 218 "6,14, ,10" "11,27,tgpm-1,540000" "1,133,mbr-1-0;mbr-1-1;mbr-1-2;mbr-1-3;mbr-1-5;mbr-1-10;mbr-1-12,70"
awards.setData 219 "6,17, ,20" "1,51,cpt,100" "1,42,rps,70"
awards.setData 300 "10,18, ,300" "6,9, ,15"
awards.setData 301 "10,142, ,600" "6,12, ,20"
awards.setData 302 "6,120, ,10"
awards.setData 303 "10,143, ,1200" "9,28,tasl,144000"
awards.setData 304 "10,38, ,1200" "6,34, ,40" "9,19,tac,288000"
awards.setData 305 "6,41, ,15" "9,29,tasm,36000" "9,28,tasl,36000" "9,19,tac,36000"
awards.setData 306 "10,144, ,1080" "6,41, ,40" "9,29,tasm,72000"
awards.setData 307 "6,41, ,55" "9,29,tasm,90000" "9,28,tasl,180000"
awards.setData 308 "6,34, ,45" "9,19,tac,216000" "5,87,wlr,2"
awards.setData 309 "10,141, ,1200" "6,11, ,20"
awards.setData 310 "6,110, ,10" "9,121,vtp-0;vtp-1;vtp-2;vtp-6,36000"
awards.setData 311 "9,99,mtt-0-0;mtt-1-0,0" "9,101,mtt-0-2;mtt-1-2,0" "9,103,mtt-0-4,0" "9,104,mtt-0-5;mtt-1-5,0" "9,108,mtt-0-9,0" "9,32,attp-1,432000"
awards.setData 312 "9,100,mtt-0-1;mtt-1-1,0" "9,102,mtt-0-3;mtt-1-3,0" "9,105,mtt-0-6,0" "9,106,mtt-0-7,0" "9,107,mtt-0-8,0" "9,31,attp-0,432000"
awards.setData 313 "6,17, ,20" "1,88,bksgpm-0;bksgpm-1,10"
awards.setData 314 "6,17, ,10" "6,83, ," "11,30,tt,180000"
awards.setData 315 "6,17, ,10" "11,30,tt,432000" "1,88,bksgpm-0;bksgpm-1,10"
awards.setData 316 "3,10,vkls-7,200"
awards.setData 317 "6,86, ,15" "9,33,vtp-4,90000"
awards.setData 318 "6,138, ,15" "9,137,vtp-12,36000"
awards.setData 319 "6,39, ,10" "11,36,ctgpm-1,90000"
awards.setData 400 "6,89, ,5"
awards.setData 401 "6,89, ,10"
awards.setData 402 "6,48, ,4"
awards.setData 403 "6,109, ,4"
awards.setData 404 "6,86, ,10"
awards.setData 406 "6,47, ,7"
awards.setData 407 "6,139, ,5"
awards.setData 408 "6,110, ,5"
awards.setData 409 "6,93, ,8"
awards.setData 410 "6,8, ,8"
awards.setData 411 "6,44, ,8"
awards.setData 412 "6,124, ,"
awards.setData 413 "6,7, ,4"
awards.setData 414 "6,9, ,10"
awards.setData 415 "6,6, ,10"
awards.setData 120_1 "6,152, ,6"
awards.setData 120_2 "6,152, ,10" "9,153,mtt-1-10;mtt-2-10;mtt-2-11;mtt-1-12;mtt-2-12,7200"
awards.setData 120_3 "6,152, ,14" "9,153,mtt-1-10;mtt-2-10;mtt-2-11;mtt-1-12;mtt-2-12,18000"
awards.setData 121_1 "10,154, ,300"
awards.setData 121_2 "6,156, ,8" "9,155,vtp-14;vtp-15,3600"
awards.setData 121_3 "6,156, ,12" "9,155,vtp-14;vtp-15,14400"
awards.setData 320 "6,157, ,5" "5,158,vkls-15,40"
awards.setData 321 "6,152, ,15" "5,159,mwin-1-12;mwin-2-12,2" "5,160,mwin-1-10;mwin-2-10,2" "5,161,mwin-2-11,2"
awards.setData 322 "6,162, ,9" "9,163,vtp-14,7200"
awards.setData 323 "7,164,vdstry-15,4" "7,165,vdstry-14,2" "7,166,vdths-15,5" "7,167,vdths-14,5"
awards.setData 416 "6,168, ,"

$	8163	$
"""'''


'''@app.get("/getplayerinfo.aspx", response_class=HTMLResponse)
def read_6(auth, mode, gsa):
	return """O
H asof cb
D 1728926207 client
H pid nick tid gsco crpt rnk rnkcg tt pdt pdtc kdr ent-1 ent-2 ent-3 bp-1 unavl klls
D 1400111649 Player 0 11405 30720 31 0 1198417 0 0 0.53 0 0 0 1 0 3997
H award level when first
D 201 18 1610732429 1497703825
D 202 7 1564939876 1497779887
D 108_1 0 1497785456 0
$ 234 $"""'''


@router.get("/getplayerinfo.aspx", response_class=HTMLResponse)
async def read_2(auth, mode, gsa, pToken = None, lkey = None):
    asof_table = StatsTable(
        columns=[
            StatsColumn("asof"),
            StatsColumn("cb"),
        ],
        rows=[
            StatsRow([
                str(int(time.time())),
                "client"
            ])
        ]
    )

    pid_table = StatsTable(
        columns=[
            StatsColumn("pid"),
            StatsColumn("nick"),
            StatsColumn("tid"),
            StatsColumn("gsco"),
            StatsColumn("crpt"),
            StatsColumn("rnk"),
            StatsColumn("rnkcg"),
            StatsColumn("tt"),
            StatsColumn("pdt"),
            StatsColumn("pdtc"),
            StatsColumn("kdr"),
            StatsColumn("ent-1"),
            StatsColumn("ent-2"),
            StatsColumn("ent-3"),
            StatsColumn("bp-1"),
            StatsColumn("unavl"),
            StatsColumn("klls"),
        ],
        rows=[
            StatsRow([
                1400111649,
                "VordyV",
                0,
                11403,
                30718,
                31,
                0,
                1199802,
                0,
                0,
                0.53,
                0,
                0,
                0,
                1,
                0,
                3997,
            ])
        ]
    )

    return StatsSerializer.serialize(tables=[asof_table, pid_table])

    return """O
H	asof	cb
D	1769972192	client
H	pid	nick	tid	gsco	crpt	rnk	rnkcg	tt	pdt	pdtc	kdr	ent-1	ent-2	ent-3	bp-1	unavl	klls
D	1400111649	VordyV	0	11403	30718	31	0	1199802	0	0	0.53	0	0	0	1	0	3997
H	award	level	when	first
D	201	18	1610732429	1497703825
D	202	7	1564939876	1497779887
D	108_1	0	1497785456	0
$	234	$"""

    '''return """O
H	asof	cb
D	1728996069	client
H	p.pid	subaccount	tid	gsco	rnk	tac	cs	tt	crpt	klstrk	bnspt	dstrk	rps	resp	tasl	tasm	awybt	hls	sasl	tds	win	los	unlc	expts	cpt	dcpt	twsc	tcd	slpts	tcrd	md	ent	ent-1	ent-2	ent-3(35)	bp-1	wtp-30	htp	hkl	atp	akl	vtp-0	vtp-1	vtp-2	vtp-3	vtp-4	vtp-5	vtp-6	vtp-7	vtp-8	vtp-9	vtp-10	vtp-11	vtp-12	vtp-13	vtp-14	vtp-15	vkls-0	vkls-1	vkls-2	vkls-3	vkls-4	vkls-5	vkls-6	vkls-7	vkls-8	vkls-9	vkls-10	vkls-11	vkls-12	vkls-13	vkls-14	vkls-15	vdstry-0	vdstry-1	vdstry-2	vdstry-3	vdstry-4	vdstry-5	vdstry-6	vdstry-7	vdstry-8	vdstry-9	vdstry-10	vdstry-11	vdstry-12	vdstry-13	vdstry-14	vdstry-15	vdths-0	vdths-1	vdths-2	vdths-3	vdths-4	vdths-5	vdths-6	vdths-7	vdths-8	vdths-9	vdths-10	vdths-11	vdths-12	vdths-13	vdths-14	vdths-15	ktt-0	ktt-1	ktt-2	ktt-3	wkls-0	wkls-1	wkls-2	wkls-3	wkls-4	wkls-5	wkls-6	wkls-7	wkls-8	wkls-9	wkls-10	wkls-11	wkls-12	wkls-13	wkls-14	wkls-15	wkls-16	wkls-17	wkls-18	wkls-19	wkls-20	wkls-21	wkls-22	wkls-23	wkls-24	wkls-25	wkls-26	wkls-27	wkls-28	wkls-29	wkls-30	wkls-31	klsk	klse	etp-0	etp-1	etp-2	etp-3	etp-4	etp-5	etp-6	etp-7	etp-8	etp-9	etp-10	etp-11	etp-12	etp-13	etp-14	etp-15	etp-16	etpk-0	etpk-1	etpk-2	etpk-3	etpk-4	etpk-5	etpk-6	etpk-7	etpk-8	etpk-9	etpk-10	etpk-11	etpk-12	etpk-13	etpk-14	etpk-15	etpk-16	attp-0	attp-1	awin-0	awin-1	tgpm-0	tgpm-1	tgpm-2	kgpm-0	kgpm-1	kgpm-2	bksgpm-0	bksgpm-1	bksgpm-2	ctgpm-0	ctgpm-1	ctgpm-2	csgpm-0	csgpm-1	csgpm-2	trpm-0	trpm-1	trpm-2	klls	attp-0	attp-1	awin-0	awin-1	pdt	mtt-0-0	mtt-0-1	mtt-0-3	mtt-0-4	mtt-0-5	mtt-0-6	mtt-0-7	mtt-0-8	mtt-0-9	mwin-0-0	mwin-0-1	mwin-0-3	mwin-0-4	mwin-0-5	mwin-0-6	mwin-0-7	mwin-0-8	mwin-0-9	mbr-0-0	mbr-0-1	mbr-0-3	mbr-0-4	mbr-0-5	mbr-0-6	mbr-0-7	mbr-0-8	mbr-0-9	mkls-0-0	mkls-0-1	mkls-0-3	mkls-0-4	mkls-0-5	mkls-0-6	mkls-0-7	mkls-0-8	mkls-0-9	mtt-1-0	mtt-1-1	mtt-1-2	mtt-1-3	mtt-1-5	mwin-1-0	mwin-1-1	mwin-1-2	mwin-1-3	mwin-1-5	mlos-1-0	mlos-1-1	mlos-1-2	mlos-1-3	mlos-1-5	mbr-1-0	mbr-1-1	mbr-1-2	mbr-1-3	mbr-1-5	msc-1-0	msc-1-1	msc-1-2	msc-1-3	msc-1-5	mkls-1-0	mkls-1-1	mkls-1-2	mkls-1-3	mkls-1-5	id	profileid	subaccount	pid	acdt	lgdt	nick	rnk	rnkcg	gsco	crpt	awaybonus	brs	cpt	capa	cts	cs	ban	ovaccu	pdt	pdtc	csgpm-0	csgpm-1	csgpm-2	dass	dcpt	kpm	dpm	spm	kdr	dstrk	dths	kkls-0	kkls-1	kkls-2	kkls-3	ktt-0	ktt-1	ktt-2	ktt-3	klla	klls	klstrk	kluav	fe	fgm	fk	fm	fv	fw	cotime	sltime	smtime	lwtime	captures	assist	defend	waccu	ate	wins	los	twsc	hls	rps	rvs	resp	sasl	slbcn	slbspn	slpts	sluav	suic	tac	talw	tas	tasl	tasm	tcd	tcrd	tdmg	tdrps	tds	tgd	tgr	tid	tkls	toth	tots	trp	tt	tvdmg	unavl	unlc	kick	ncpt	kdths-0	kdths-1	kdths-2	kdths-3	vet	etp-0	etp-1	etp-2	etp-3	etp-4	etp-5	etp-6	etp-7	etp-8	etp-9	etp-10	etp-11	etpk-0	etpk-1	etpk-2	etpk-3	etpk-4	etpk-5	etpk-6	etpk-7	etpk-8	etpk-9	etpk-10	etpk-11	gm	mapid	mbr	mwin	mlos	msc	mtt	vdstry-0	vdstry-1	vdstry-2	vdstry-3	vdstry-4	vdstry-5	vdstry-6	vdstry-7	vdstry-8	vdstry-9	vdstry-10	vdstry-11	vdstry-12	vdstry-13	vdths-0	vdths-1	vdths-2	vdths-3	vdths-4	vdths-5	vdths-6	vdths-7	vdths-8	vdths-9	vdths-10	vdths-11	vdths-12	vdths-13	vkdr-0	vkdr-1	vkdr-2	vkdr-3	vkdr-4	vkdr-5	vkdr-6	vkdr-7	vkdr-8	vkdr-9	vkdr-10	vkdr-11	vkdr-12	vkdr-13	vkls-0	vkls-1	vkls-2	vkls-3	vkls-4	vkls-5	vkls-6	vkls-7	vkls-8	vkls-9	vkls-10	vkls-11	vkls-12	vkls-13	vrkls-0	vrkls-1	vrkls-2	vrkls-3	vrkls-4	vrkls-5	vrkls-6	vrkls-7	vrkls-8	vrkls-9	vrkls-10	vrkls-11	vrkls-12	vrkls-13	vtp-0	vtp-1	vtp-2	vtp-3	vtp-4	vtp-5	vtp-6	vtp-7	vtp-8	vtp-9	vtp-10	vtp-11	vtp-12	vtp-13	vbf-0	vbf-1	vbf-2	vbf-3	vbf-4	vbf-5	vbf-6	vbf-7	vbf-8	vbf-9	vbf-10	vbf-11	vbf-12	vbf-13	vbh-0	vbh-1	vbh-2	vbh-3	vbh-4	vbh-5	vbh-6	vbh-7	vbh-8	vbh-9	vbh-10	vbh-11	vbh-12	vbh-13	vaccu-0	vaccu-1	vaccu-2	vaccu-3	vaccu-4	vaccu-5	vaccu-6	vaccu-7	vaccu-8	vaccu-9	vaccu-10	vaccu-11	vaccu-12	vaccu-13	waccu-0	waccu-1	waccu-2	waccu-3	waccu-4	waccu-5	waccu-6	waccu-7	waccu-8	waccu-9	waccu-10	waccu-11	waccu-12	waccu-13	waccu-14	waccu-15	waccu-16	waccu-17	waccu-18	waccu-19	waccu-20	waccu-21	waccu-22	waccu-23	waccu-24	waccu-25	waccu-26	waccu-27	waccu-28	waccu-29	waccu-30	waccu-31	waccu-32	waccu-33	waccu-34	waccu-35	waccu-36	waccu-37	waccu-38	waccu-39	waccu-40	waccu-41	waccu-42	wdths-0	wdths-1	wdths-2	wdths-3	wdths-4	wdths-5	wdths-6	wdths-7	wdths-8	wdths-9	wdths-10	wdths-11	wdths-12	wdths-13	wdths-14	wdths-15	wdths-16	wdths-17	wdths-18	wdths-19	wdths-20	wdths-21	wdths-22	wdths-23	wdths-24	wdths-25	wdths-26	wdths-27	wdths-28	wdths-29	wdths-30	wdths-31	wdths-32	wdths-33	wdths-34	wdths-35	wdths-36	wdths-37	wdths-38	wdths-39	wdths-40	wdths-41	wdths-42	whts-0	whts-1	whts-2	whts-3	whts-4	whts-5	whts-6	whts-7	whts-8	whts-9	whts-10	whts-11	whts-12	whts-13	whts-14	whts-15	whts-16	whts-17	whts-18	whts-19	whts-20	whts-21	whts-22	whts-23	whts-24	whts-25	whts-26	whts-27	whts-28	whts-29	whts-30	whts-31	whts-32	whts-33	whts-34	whts-35	whts-36	whts-37	whts-38	whts-39	whts-40	whts-41	whts-42	wkdr-0	wkdr-1	wkdr-2	wkdr-3	wkdr-4	wkdr-5	wkdr-6	wkdr-7	wkdr-8	wkdr-9	wkdr-10	wkdr-11	wkdr-12	wkdr-13	wkdr-14	wkdr-15	wkdr-16	wkdr-17	wkdr-18	wkdr-19	wkdr-20	wkdr-21	wkdr-22	wkdr-23	wkdr-24	wkdr-25	wkdr-26	wkdr-27	wkdr-28	wkdr-29	wkdr-30	wkdr-31	wkdr-32	wkdr-33	wkdr-34	wkdr-35	wkdr-36	wkdr-37	wkdr-38	wkdr-39	wkdr-40	wkdr-41	wkdr-42	wkls-0	wkls-1	wkls-2	wkls-3	wkls-4	wkls-5	wkls-6	wkls-7	wkls-8	wkls-9	wkls-10	wkls-11	wkls-12	wkls-13	wkls-14	wkls-15	wkls-16	wkls-17	wkls-18	wkls-19	wkls-20	wkls-21	wkls-22	wkls-23	wkls-24	wkls-25	wkls-26	wkls-27	wkls-28	wkls-29	wkls-30	wkls-31	wkls-32	wkls-33	wkls-34	wkls-35	wkls-36	wkls-37	wkls-38	wkls-39	wkls-40	wkls-41	wkls-42	wshts-0	wshts-1	wshts-2	wshts-3	wshts-4	wshts-5	wshts-6	wshts-7	wshts-8	wshts-9	wshts-10	wshts-11	wshts-12	wshts-13	wshts-14	wshts-15	wshts-16	wshts-17	wshts-18	wshts-19	wshts-20	wshts-21	wshts-22	wshts-23	wshts-24	wshts-25	wshts-26	wshts-27	wshts-28	wshts-29	wshts-30	wshts-31	wshts-32	wshts-33	wshts-34	wshts-35	wshts-36	wshts-37	wshts-38	wshts-39	wshts-40	wshts-41	wshts-42	wtp-0	wtp-1	wtp-2	wtp-3	wtp-4	wtp-5	wtp-6	wtp-7	wtp-8	wtp-9	wtp-10	wtp-11	wtp-12	wtp-13	wtp-14	wtp-15	wtp-16	wtp-17	wtp-18	wtp-19	wtp-20	wtp-21	wtp-22	wtp-23	wtp-24	wtp-25	wtp-26	wtp-27	wtp-28	wtp-29	wtp-30	wtp-31	wtp-32	wtp-33	wtp-34	wtp-35	wtp-36	wtp-37	wtp-38	wtp-39	wtp-40	wtp-41	wtp-42	wtpk-0	wtpk-1	wtpk-2	wtpk-3	wtpk-4	wtpk-5	wtpk-6	wtpk-7	wtpk-8	wtpk-9	wtpk-10	wtpk-11	wtpk-12	wtpk-13	wtpk-14	wtpk-15	wtpk-16	wtpk-17	wtpk-18	wtpk-19	wtpk-20	wtpk-21	wtpk-22	wtpk-23	wtpk-24	wtpk-25	wtpk-26	wtpk-27	wtpk-28	wtpk-29	wtpk-30	wtpk-31	wtpk-32	wtpk-33	wtpk-34	wtpk-35	wtpk-36	wtpk-37	wtpk-38	wtpk-39	wtpk-40	wtpk-41	wtpk-42	wbf-0	wbf-1	wbf-2	wbf-3	wbf-4	wbf-5	wbf-6	wbf-7	wbf-8	wbf-9	wbf-10	wbf-11	wbf-12	wbf-13	wbf-14	wbf-15	wbf-16	wbf-17	wbf-18	wbf-19	wbf-20	wbf-21	wbf-22	wbf-23	wbf-24	wbf-25	wbf-26	wbf-27	wbf-28	wbf-29	wbf-30	wbf-31	wbf-32	wbf-33	wbf-34	wbf-35	wbf-36	wbf-37	wbf-38	wbf-39	wbf-40	wbf-41	wbf-42	wbh-0	wbh-1	wbh-2	wbh-3	wbh-4	wbh-5	wbh-6	wbh-7	wbh-8	wbh-9	wbh-10	wbh-11	wbh-12	wbh-13	wbh-14	wbh-15	wbh-16	wbh-17	wbh-18	wbh-19	wbh-20	wbh-21	wbh-22	wbh-23	wbh-24	wbh-25	wbh-26	wbh-27	wbh-28	wbh-29	wbh-30	wbh-31	wbh-32	wbh-33	wbh-34	wbh-35	wbh-36	wbh-37	wbh-38	wbh-39	wbh-40	wbh-41	wbh-42	adpr	wlr	vaccu-14	vaccu-15	bp-1
D	0	ServerAdmin	0	168	5	221	0	2974	0	41	0	6	0	2	0	0	0	7	0	0	0	0	1	0	9	2	42	4	0	0	0	0	0	0	1	1	3	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	390	1518	752	277	0	24	0	0	31	0	0	15	0	0	0	0	1	0	0	11	0	2	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	123	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	27	1	ServerAdmin	1	1538223418	1538226794	 ServerAdmin	5	0	168	343	0	101	9	0	0	0	0	0.0041723136495644	0	0	0	0	0	3	2	0.024815063887021	0.0044384667114997	0.03	0.055909090909091	6	22	1	75	14	33	390	1518	752	277	11	123	41	0	0	0	1	5	0	4	0	0	0	0	0	0	0	0	0	3	0	42	7	0	0	2	0	0	0	0	0	1	221	2753	0	0	0	4	0	0	0	0	0	0	0	0	862	2066	0	2974	0	4	1	0	6	1	14	6	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	5	24	1	0	24	952																																																																																																																	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0.35185185185185	0	0	0.31512605042017	0	0	1.2391304347826	0	0	0	0	0.5	0.94904458598726	0	0.4695652173913	0	0.4	0	0	0	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	2	0	1	0	0	0	4	0	1	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	1	1	24	0	0	31	0	0	15	0	0	0	0	1	0	0	11	0	2	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	184	2	10	269	3	34	146	1	11	0	0	3	89	0	269	0	17	1	0	0	0	21	118	0	0	0	0	0	0	3	0	0	4	0	0	0	49	8	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	324	0	0	714	0	0	46	0	0	0	0	2	314	0	115	0	5	0	0	0	0	4	14	0	0	0	0	0	0	0	0	0	10	0	0	0	6	1	0	0	0	0	0	114	0	0	225	0	0	57	0	0	0	0	1	298	0	54	0	2	0	0	0	0	4	14	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	1
H	UnlockID
D	121
$	7267	$
"""'''


@router.get("/getunlocksinfo.aspx", response_class=HTMLResponse)
async def read_3(auth):
    return """O
H	pid	nick	asof
D	1	ServerAdmin	1728996071
H	Avcred
D	4
H	UnlockID
D	121
$	58	$
"""


@router.get("/getawardsinfo.aspx", response_class=HTMLResponse)
async def read_4(auth):
    return """O
H	pid	nick	asof
D	1	ServerAdmin	1728996071
H	award	level	when	first
D	202	3	1538226794	1538223413
D	102_1	0	1538223413	0
D	400	20	1538226794	1538223413
D	401	4	1538223413	1538223413
D	100_1	0	1538223413	0
D	402	1	1538226794	1538226794
D	119_1	0	1538226794	0
$	211	$
"""


@router.get("/BF2142ticker/English.xml", response_class=HTMLResponse)
async def read_5():
    i = """

<?xml version="1.0" encoding="UTF-8"?>
<newsticker>
    <newsitem>
	[2026.03.06] No news!
	</newsitem>
    <newsitem>
	[2026.03.21] Advertising placement by phone +79876543212.
	</newsitem>
</newsticker>"""
    return Response(content=i, media_type="application/xml")


async def handler(np: NewProcess):
    # manually specify only what is necessary for work

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.np = np
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    config = uvicorn.Config(app, host=np.config.get("server_address"), port=np.config.get("server_port"), log_level=np.config.get("log_level_uvicorn"))
    server = uvicorn.Server(config)
    await server.serve()

def main(queue, config, app_config):
    np = NewProcess(queue=queue, config=config, app_config=app_config, app_name="stats", db_apps={"stats": ["plugins.stats.models"], "fesl": ["plugins.fesl.models"]})
    np.start(handler)