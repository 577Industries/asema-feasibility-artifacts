from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "out" / "product-demo" / "aegisgraph.sqlite"
app = FastAPI(title="AegisGraph ASEMA Local Demo API")


def rows(query: str):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(query)]
    finally:
        con.close()


@app.get("/health")
def health():
    return {"ok": DB.exists(), "database": str(DB.relative_to(ROOT)) if DB.exists() else "missing"}


@app.get("/targets")
def targets():
    data = json.loads((ROOT / "site" / "local-dashboard" / "data" / "dashboard_data.json").read_text())
    return data["targets"]


@app.get("/evidence")
def evidence():
    return rows("select * from evidence order by evidence_id")


@app.get("/graph/nodes")
def graph_nodes():
    return rows("select * from graph_nodes order by target_id, node_id")


@app.get("/graph/edges")
def graph_edges():
    return rows("select * from graph_edges order by edge_id")


@app.get("/scores")
def scores():
    return rows("select * from scores order by score desc")


@app.get("/recommendations")
def recommendations():
    return rows("select * from recommendations order by recommendation_id")
