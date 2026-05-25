import datetime
import traceback
from fastapi import FastAPI, Response, Request, APIRouter, HTTPException
from typing import Union
from fastapi.responses import HTMLResponse
import uvicorn
from .package import StatsRow, StatsTable, StatsColumn, StatsSerializer
import time
from contextlib import asynccontextmanager
from battlenode import NewProcess
from .schemes import StatsScheme, RoundPlayers, RoundPlayerStats
from .services import StatsService
from plugins.fesl.services import ProfileService
from .ea_decoder import decode
from .stats_decoder import StatsDecoderV1
from .teams import Teams
from .game_modes import GameModes

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

@router.get("/getplayerinfo.aspx", response_class=HTMLResponse)
async def read_2(auth, mode, gsa, pToken = None, lkey = None):
    try:
        auth = decode(auth)
        pid = auth["pid"]
        profile = await ProfileService.get(pid)

        data = await StatsService.read(pid)

        result = StatsRow([
            profile["id"],
            profile["name"],
            0, #tid
            data.gsco,
            data.crpt,
            data.rnk,
            data.rnkcg,
            data.tt,
            data.pdt,
            data.pdtc,
            data.kdr,
            data.ent_1,
            data.ent_2,
            data.ent_3,
            data.bp_1,
            data.unavl,
            data.klls,
        ])

    except Exception as error:
        data = StatsScheme()

        result = StatsRow([
            0,
            "",
            0, #tid
            data.gsco,
            data.crpt,
            data.rnk,
            data.rnkcg,
            data.tt,
            data.pdt,
            data.pdtc,
            data.kdr,
            data.ent_1,
            data.ent_2,
            data.ent_3,
            data.bp_1,
            data.unavl,
            data.klls,
        ])

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
            StatsColumn("tid"), # = 0
            StatsColumn("gsco"), # Global Score
            StatsColumn("crpt"), # Career Points
            StatsColumn("rnk"), # Rank
            StatsColumn("rnkcg"), # RankUp
            StatsColumn("tt"), # Time Played
            StatsColumn("pdt"), # Unique Dog Tags Collected
            StatsColumn("pdtc"), # Dog Tags Collected
            StatsColumn("kdr"),
            StatsColumn("ent-1"), # ?
            StatsColumn("ent-2"), # ?
            StatsColumn("ent-3"), # ?
            StatsColumn("bp-1"), # ?
            StatsColumn("unavl"), # Unlooks available
            StatsColumn("klls"),
        ],
        rows=[result]
    )

    return StatsSerializer.serialize(tables=[asof_table, pid_table])

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

'''
b'BF2142\\minsk\\mapstart\\1775031089.12\\mapend\\1775031153.94\\win\\1\\gm\\0\\m\\3\\v\\bf2142\\pc\\1\\rwa\\1\\ban_0\\0\\c_0\\1\\capa_0\\0\\cpt_0\\0\\crpt_0\\0\\cs_0\\0.0\\dass_0\\0\\dcpt_0\\0\\dstrk_0\\0\\dths_0\\0\\gsco_0\\0\\hls_0\\0\\kick_0\\0\\klla_0\\0\\klls_0\\0\\klstrk_0\\0\\kluav_0\\0\\nick_0\\ Grey4545455\\ncpt_0\\0\\pdt_0\\{}\\pdtc_0\\0\\pid_0\\1400023249\\resp_0\\0\\rnk_0\\31\\rnkcg_0\\0\\rps_0\\0\\rvs_0\\0\\slbspn_0\\0\\sluav_0\\0\\suic_0\\0\\tac_0\\0\\talw_0\\51\\tas_0\\0\\tasl_0\\0\\tasm_0\\0\\tcd_0\\0\\tcrd_0\\0\\tdmg_0\\0\\tdrps_0\\0\\tds_0\\0\\tgd_0\\0\\tgr_0\\0\\tkls_0\\0\\toth_0\\0\\tots_0\\5\\tt_0\\51\\tvdmg_0\\0\\twsc_0\\0\\t_0\\2\\medalerg_0\\1\\vtp-0_0\\8\\vbf-0_0\\5\\vbh-0_0\\0\\vdstry-0_0\\0\\vrkls-0_0\\0\\vdths-0_0\\0\\vkls-0_0\\0\\kdths-0_0\\0\\kdths-1_0\\0\\kdths-2_0\\0\\kdths-3_0\\0\\kkls-0_0\\0\\kkls-1_0\\0\\kkls-2_0\\0\\kkls-3_0\\0\\ktt-0_0\\0\\ktt-1_0\\51\\ktt-2_0\\0\\ktt-3_0\\0\\waccu-7_0\\0\\wdths-7_0\\0\\wbf-7_0\\5\\wkls-7_0\\0\\wbh-7_0\\0\\wtp-7_0\\42\\EOF\\1'
b'BF2142\\minsk\\mapstart\\1775156120.01\\mapend\\1775156185.04\\win\\1\\gm\\0\\m\\3\\v\\bf2142\\pc\\2\\rwa\\1\\ban_0\\0\\c_0\\1\\capa_0\\0\\cpt_0\\0\\crpt_0\\0\\cs_0\\0.0\\dass_0\\0\\dcpt_0\\0\\dstrk_0\\0\\dths_0\\0\\gsco_0\\0\\hls_0\\0\\kick_0\\0\\klla_0\\0\\klls_0\\0\\klstrk_0\\0\\kluav_0\\0\\nick_0\\ Admin\\ncpt_0\\0\\pdt_0\\{}\\pdtc_0\\0\\pid_0\\6\\resp_0\\0\\rnk_0\\2\\rnkcg_0\\0\\rps_0\\0\\rvs_0\\0\\slbspn_0\\0\\sluav_0\\0\\suic_0\\0\\tac_0\\0\\talw_0\\50\\tas_0\\0\\tasl_0\\0\\tasm_0\\0\\tcd_0\\0\\tcrd_0\\0\\tdmg_0\\0\\tdrps_0\\0\\tds_0\\0\\tgd_0\\0\\tgr_0\\0\\tkls_0\\0\\toth_0\\0\\tots_0\\0\\tt_0\\50\\tvdmg_0\\0\\twsc_0\\0\\t_0\\2\\medalers_0\\1\\kdths-0_0\\0\\kdths-1_0\\0\\kdths-2_0\\0\\kdths-3_0\\0\\kkls-0_0\\0\\kkls-1_0\\0\\kkls-2_0\\0\\kkls-3_0\\0\\ktt-0_0\\0\\ktt-1_0\\50\\ktt-2_0\\0\\ktt-3_0\\0\\waccu-7_0\\0\\wdths-7_0\\0\\wbf-7_0\\0\\wkls-7_0\\0\\wbh-7_0\\0\\wtp-7_0\\50\\ban_1\\0\\c_1\\1\\capa_1\\0\\cpt_1\\0\\crpt_1\\0\\cs_1\\0.0\\dass_1\\0\\dcpt_1\\0\\dstrk_1\\0\\dths_1\\0\\gsco_1\\0\\hls_1\\0\\kick_1\\0\\klla_1\\0\\klls_1\\0\\klstrk_1\\0\\kluav_1\\0\\nick_1\\ user1\\ncpt_1\\0\\pdt_1\\{}\\pdtc_1\\0\\pid_1\\22\\resp_1\\0\\rnk_1\\0\\rnkcg_1\\0\\rps_1\\0\\rvs_1\\0\\slbspn_1\\0\\sluav_1\\0\\suic_1\\0\\tac_1\\0\\talw_1\\56\\tas_1\\0\\tasl_1\\0\\tasm_1\\0\\tcd_1\\0\\tcrd_1\\0\\tdmg_1\\0\\tdrps_1\\0\\tds_1\\0\\tgd_1\\0\\tgr_1\\0\\tkls_1\\0\\toth_1\\0\\tots_1\\0\\tt_1\\56\\tvdmg_1\\0\\twsc_1\\0\\t_1\\1\\medalerg_1\\1\\kdths-0_1\\0\\kdths-1_1\\0\\kdths-2_1\\0\\kdths-3_1\\0\\kkls-0_1\\0\\kkls-1_1\\0\\kkls-2_1\\0\\kkls-3_1\\0\\ktt-0_1\\0\\ktt-1_1\\56\\ktt-2_1\\0\\ktt-3_1\\0\\wdths-1_1\\0\\waccu-1_1\\0\\wbf-1_1\\0\\wtp-1_1\\56\\wbh-1_1\\0\\wkls-1_1\\0\\EOF\\1'
'''
@router.post("/bf2142statistics.php", response_class=HTMLResponse)
async def read_5(request: Request):
    try:
        rawData = StatsDecoderV1.parse_bf2142_stats(await request.body())

        players = {}
        for ident, player in rawData["players"].items():

            players[player["pid"]] = RoundPlayerStats(
                pid=player["pid"],
                nick=player["nick"],
                gsco=player["gsco"],
                crpt=player["crpt"],
                rnk=player["rnk"],
                rnkcg=player["rnkcg"],
                tt=player["tt"],
                dths=player["dths"],
                klls=player["klls"],
                team=player["t"]
            )

        start = datetime.datetime.fromtimestamp(rawData["round"]["mapstart"])
        end = datetime.datetime.fromtimestamp(rawData["round"]["mapend"])
        duration = datetime.timedelta(seconds=rawData["round"]["mapend"] - rawData["round"]["mapstart"])
        team = Teams(rawData["round"]["win"])
        game_mode = GameModes(rawData["round"]["gm"])

        rid = await StatsService.append_round(start=start, end=end, duration=duration, winner=team, game_mode=game_mode, mode=rawData["round"]["v"], players=RoundPlayers(players=players))
        await request.app.state.np.publish("stats.received", {"rid": rid})
        return "ok"
    except Exception as error:
        request.app.state.np.error(f"Error processing stats: {error}", tb=traceback.format_exc())
        raise HTTPException(status_code=404, detail="The stats were not successfully processed")

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