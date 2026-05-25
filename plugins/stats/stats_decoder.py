import ast
import re
from typing import Any, Dict, Union

class StatsDecoderV1:

    PLAYER_KEY_RE = re.compile(r"^(?P<name>.+)_(?P<idx>\d+)$")

    @staticmethod
    def _coerce_value(value: str) -> Any:
        value = value.strip()

        if value == "":
            return ""

        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return int(value)

        try:
            # float("0") тоже работает, поэтому int проверяем выше
            if re.fullmatch(r"-?\d+\.\d+", value):
                return float(value)
        except ValueError:
            pass

        if (value.startswith("{") and value.endswith("}")) or (
            value.startswith("[") and value.endswith("]")
        ):
            try:
                return ast.literal_eval(value)
            except Exception:
                return value

        return value

    @staticmethod
    def parse_bf2142_stats(data: Union[bytes, str]) -> Dict[str, Any]:
        if isinstance(data, str):
            s = data.strip()
            if s.startswith("b'") or s.startswith('b"'):
                try:
                    data = ast.literal_eval(s)
                except Exception:
                    data = s.encode("utf-8", errors="replace")
            else:
                data = s.encode("utf-8", errors="replace")

        if isinstance(data, bytes):
            text = data.decode("utf-8", errors="replace")
        else:
            text = str(data)

        text = text.strip()

        if text.startswith("b'") and text.endswith("'"):
            try:
                raw = ast.literal_eval(text)
                if isinstance(raw, bytes):
                    text = raw.decode("utf-8", errors="replace")
            except Exception:
                pass

        parts = text.split("\\")
        if len(parts) < 4:
            raise ValueError("Слишком короткий пакет статистики")

        result: Dict[str, Any] = {
            "round": {
                "game": StatsDecoderV1._coerce_value(parts[0]),
                "server": StatsDecoderV1._coerce_value(parts[1]),
            },
            "players": {}
        }

        payload = parts[2:]
        i = 0

        while i + 1 < len(payload):
            key = payload[i]
            value = payload[i + 1]
            i += 2

            if key == "EOF":
                result["round"]["EOF"] = StatsDecoderV1._coerce_value(value)
                continue

            m = StatsDecoderV1.PLAYER_KEY_RE.match(key)
            if m:
                base_name = m.group("name")
                idx = int(m.group("idx"))
                player = result["players"].setdefault(idx, {})
                player[base_name] = StatsDecoderV1._coerce_value(value)
            else:
                result["round"][key] = StatsDecoderV1._coerce_value(value)

        if i < len(payload):
            result["round"]["_dangling"] = payload[i]

        return result