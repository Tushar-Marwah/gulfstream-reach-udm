"""
Document catalog for the Gulfstream aerospace compliance UDM: SDSs, REACH dossiers,
material declarations (IMDS-style) and supplier registration letters. Feeds the
Documents tab + entity search. Deterministic.
"""
import hashlib


def _h(*p):
    return int(hashlib.md5("|".join(str(x) for x in p).encode()).hexdigest(), 16)


def build():
    from seed import CHEMICALS, MATERIALS, PARTS, PROGRAMS
    from companies import SUPPLIERS
    docs = []

    def add(fn, label, industry, scenario, use_case, entities, project, objects, kind="doc", ext="pdf"):
        s = _h(fn) % 20
        status = "committed" if s < 17 else ("landed" if s < 19 else "processing")
        docs.append({
            "filename": fn, "label": label, "industry": industry, "scenario": scenario,
            "use_case": use_case, "entities": entities, "project": project,
            "doctype": ext, "source": "seed", "kind": kind,
            "rows": 1 + _h(fn, "r") % 6, "status": status, "staging_table": "",
            "objects": objects if status == "committed" else "",
            "bindings": (len(objects.split(",")) * (1 + _h(fn) % 3)) if status == "committed" else 0,
            "narrative": (_h(fn, "n") % 4), "cost_usd": round(0.0005 + (_h(fn, "c") % 30) / 10000.0, 5),
            "date": "2026-0%d-%02d" % (1 + _h(fn) % 6, 1 + _h(fn, "d") % 27)})

    # SDS per material (per revision year)
    for mid, name, spec, form, base, supp in MATERIALS:
        for yr in ("2024", "2025"):
            code = mid.lower()
            add("SDS_%s_%s.pdf" % (code, yr), "%s — Safety Data Sheet (%s)" % (name, yr),
                "Aerospace · SDS Library", "Safety Data Sheet", "Hazard communication",
                supp, "SDS Library %s" % yr, "SafetyDataSheet, Material, Chemical")

    # REACH dossier / SVHC assessment per substance of concern
    for cas, name, ec, ghs, h, status, fp, oel, svhc, use in CHEMICALS:
        if svhc == "yes":
            code = cas.replace("-", "")
            add("REACH_dossier_%s.pdf" % code, "%s (CAS %s) — REACH assessment" % (name, cas),
                "Aerospace · REACH Dossier", "REACH SVHC", "Regulatory assessment",
                name, "REACH SVHC Review", "Chemical, Compliance")
            add("authorisation_%s.pdf" % code, "%s — authorisation / substitution plan" % name,
                "Aerospace · REACH Dossier", "Annex XIV", "Authorisation",
                name, "Annex XIV Programme", "Compliance, Material")

    # material declarations (IMDS-style) per part × program
    for pn, name, prog, mid in PARTS:
        add("MD_%s_%s.xlsx" % (pn.replace('-', ''), prog), "Material declaration — %s (%s)" % (name, prog),
            "Aerospace · Material Declaration", "IMDS declaration", "Substance disclosure",
            prog, "%s Compliance" % prog, "Part, Material, Chemical", kind="table", ext="xlsx")

    # supplier REACH-registration letters
    for name, country, appr, mats, reg, audit in SUPPLIERS:
        add("supplier_reach_%s.pdf" % name.split()[0].lower(), "%s — REACH registration confirmation" % name,
            "Aerospace · Supplier", "Supplier compliance", "Supply-chain assurance",
            name, "Supplier Assurance", "Supplier, Chemical")
    return docs


if __name__ == "__main__":
    d = build()
    from collections import Counter
    print("docs:", len(d), "| industries:", dict(Counter(x["industry"] for x in d)))
