from rich.table import Table
from rich.text import Text

MAX_ROWS = 20


def build_table(rows: list[dict], stats: dict) -> Table:
    table = Table(title=f"Flows classified : {stats['total']}", expand=True)
    table.add_column("Time", style="dim", width=8)
    table.add_column("Src IP", overflow="fold")
    table.add_column("Dst IP", overflow="fold")
    table.add_column("Src Port", justify="right", width=4)
    table.add_column("Dst Port", overflow="fold")
    table.add_column("Proto", justify="center", width=4)
    table.add_column("Label", justify="center")
    table.add_column("Conf.", justify="right", width=4)

    for r in rows[-MAX_ROWS:]:
        style = "bold red" if r["is_attack"] else "bold green"
        conf_str = f"{r['confidence']:.0%}" if r["confidence"] is not None else ""
        table.add_row(
            r["time"],
            r["src_ip"],
            r["dst_ip"],
            str(r["src_port"]),
            str(r["dst_port"]),
            r["proto"],
            Text(r["label"], style=style),
            conf_str,
        )
    return table
