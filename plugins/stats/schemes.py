import pydantic

class StatsFieldsScheme(pydantic.BaseModel):
    gsco: int = 0
    crpt: int = 0
    rnk: int = 0
    rnkcg: int = 0
    tt: int = 0
    pdt: int = 0
    pdtc: int = 0
    kdr: float = 0.0
    ent_1: int = 0
    ent_2: int = 0
    ent_3: int = 0
    bp_1: int = 0
    unavl: int = 0
    klls: int = 0