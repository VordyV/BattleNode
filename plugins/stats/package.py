from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class StatsColumn:
    name: str

@dataclass
class StatsRow:
    cells: List[str]

@dataclass
class StatsTable:
    columns: List[StatsColumn] = field(default_factory=list)
    rows: List[StatsRow] = field(default_factory=list)

class StatsSerializer:
    SEP = "\t"
    EOL = "\n"

    @classmethod
    def serialize(cls, tables: List[StatsTable], options: list[dict[str, Any]] = []) -> str:
        lines: List[str] = ["O"]

        for table in tables:
            header = ["H"]
            header.extend(col.name for col in table.columns)
            lines.append(cls.SEP.join(header))

            for row in table.rows:
                if len(row.cells) != len(table.columns):
                    raise ValueError(
                        f"Row has {len(row.cells)} cells, "
                        f"expected {len(table.columns)}"
                    )

                lines.append(cls.SEP.join(["D", *[str(r) for r in row.cells]]))

        for option in options:
            for key, value in option.items():
                values = []
                for v in value:
                    if isinstance(v, int): values.append(str(v))
                    elif isinstance(v, list): values.append(f'"{','.join([str(_v) for _v in v])}"')
                    elif isinstance(v, tuple): values.append(f'{','.join([str(_v) for _v in v])}')
                    elif not v: values.append("")
                    else: values.append(f'"{v}"')
                lines.append(f'{key} {" ".join(values)}')

        payload = "\n".join(lines)
        count = len(payload.replace("\t","").replace("\n",""))
        payload += f"\n$\t{count}\t$\n"
        return payload