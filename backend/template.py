"""
Data Templates: generate a custom structured output from everything that lives
in the model.

Two entry points, both grounded in the SAME ontology the agent uses (objects ->
resolver -> clean rows -- never a raw table name):

  * template mode -- the caller supplies column headers; the LLM populates the
                     rows from the model's data, best-effort per header.
  * query mode    -- the caller writes a plain-English retrieval query; the LLM
                     returns a structured table answering it.

Every run is logged to `template_runs` so "Query tracking" can replay it.
"""
import json

import llm
from resolver import resolve


# ---- gather the whole model as compact evidence --------------------------
def _objects(conn):
    rows = conn.execute(
        "SELECT DISTINCT object FROM object_registry WHERE status='approved' "
        "ORDER BY object").fetchall()
    return [r["object"] for r in rows]


def _context(conn, max_rows=60):
    """Resolve every object and render it as compact text the LLM can read."""
    blocks = []
    for obj in _objects(conn):
        try:
            r = resolve(conn, obj)
        except Exception:  # noqa
            continue
        cols = r["columns"]
        rows = r["rows"][:max_rows]
        if not cols:
            continue
        lines = ["## %s  (columns: %s)" % (obj, ", ".join(cols))]
        for row in rows:
            lines.append(json.dumps({c: row.get(c) for c in cols}, default=str))
        if len(r["rows"]) > max_rows:
            lines.append("...(%d more %s rows)" % (len(r["rows"]) - max_rows, obj))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def categories(conn):
    """The objects + their properties available to build a template from."""
    rows = conn.execute(
        "SELECT object, property, type, unit FROM object_registry "
        "WHERE status='approved' ORDER BY object, id").fetchall()
    by = {}
    for r in rows:
        by.setdefault(r["object"], []).append(
            {"property": r["property"], "type": r["type"], "unit": r["unit"]})
    return [{"object": o, "properties": p} for o, p in by.items()]


# ---- generation ----------------------------------------------------------
def _build_prompt(mode, headers, query, ctx):
    if mode == "template":
        task = (
            "The user uploaded a template with these column headers:\n  "
            + ", ".join(headers) + "\n\n"
            "Populate a table with those EXACT columns, one row per real entity in "
            "the data. Map each header to the closest fact in the model; if a header "
            "has no matching data, leave that cell as an empty string. Do not invent "
            "values that are not supported by the data.")
        cols_hint = headers
    else:
        task = (
            "The user's retrieval query is:\n  \"" + query + "\"\n\n"
            "Answer it as a structured table. Choose sensible, clearly-named columns, "
            "and return one row per matching entity. Ground every value in the data "
            "below -- do not fabricate.")
        cols_hint = None

    sys = ("You are a data-retrieval engine over a governed data model. You return "
           "ONLY strict JSON, no prose, no markdown fences.")
    prompt = (
        "Here is every object in the model and its rows:\n\n" + ctx + "\n\n"
        + task + "\n\n"
        "Return JSON of exactly this shape:\n"
        '{"columns": ["colA","colB", ...], "rows": [["v1","v2", ...], ...], '
        '"note": "one short sentence on how you built this"}\n'
        + ("The columns MUST be exactly: " + json.dumps(cols_hint) + "\n" if cols_hint else "")
        + "Keep values short and scalar. Numbers may be numbers; everything else a string."
    )
    return prompt, sys


def generate(conn, mode="query", headers=None, query="", name=""):
    headers = [h.strip() for h in (headers or []) if h and h.strip()]
    if mode == "template" and not headers:
        return {"ok": False, "error": "No column headers supplied."}
    if mode == "query" and not query.strip():
        return {"ok": False, "error": "No query supplied."}

    if not llm.available():
        return {"ok": False, "error": "The generation engine (LLM) is not configured "
                "on this deployment."}

    ctx = _context(conn)
    prompt, sys = _build_prompt(mode, headers, query, ctx)
    res = llm.complete(prompt, system=sys, model=llm.AGENT_MODEL, max_tokens=3000)
    data = llm.extract_json(res["text"]) or {}
    cols = data.get("columns") or (headers if mode == "template" else [])
    rows = data.get("rows") or []
    # normalise rows to lists aligned to cols
    norm = []
    for r in rows:
        if isinstance(r, dict):
            norm.append([r.get(c, "") for c in cols])
        elif isinstance(r, list):
            norm.append(r)
    out = {
        "ok": True, "mode": mode, "name": name.strip(),
        "spec": (", ".join(headers) if mode == "template" else query.strip()),
        "columns": cols, "rows": norm,
        "note": data.get("note", ""),
        "engine": "llm (%s)" % llm.AGENT_MODEL,
        "cost_usd": round(res.get("cost_usd", 0), 6),
    }
    _log(conn, out)
    return out


# ---- run log (Query tracking) --------------------------------------------
def _ensure(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS template_runs ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mode TEXT, spec TEXT, "
        "columns TEXT, rows TEXT, note TEXT, rowcount INTEGER, "
        "created_at TEXT DEFAULT CURRENT_TIMESTAMP)")


def _log(conn, out):
    _ensure(conn)
    conn.execute(
        "INSERT INTO template_runs (name, mode, spec, columns, rows, note, rowcount) "
        "VALUES (?,?,?,?,?,?,?)",
        (out["name"] or "(untitled)", out["mode"], out["spec"],
         json.dumps(out["columns"]), json.dumps(out["rows"]),
         out.get("note", ""), len(out["rows"])))
    conn.commit()


def history(conn, limit=100):
    _ensure(conn)
    rows = conn.execute(
        "SELECT id, name, mode, spec, columns, rows, note, rowcount, created_at "
        "FROM template_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "name": r["name"], "mode": r["mode"], "spec": r["spec"],
            "note": r["note"], "rowcount": r["rowcount"], "created_at": r["created_at"],
            "columns": json.loads(r["columns"] or "[]"),
            "rows": json.loads(r["rows"] or "[]"),
        })
    return out
