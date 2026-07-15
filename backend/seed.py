"""
Seed the demo database for the Gulfstream aerospace materials & chemical-compliance
UDM (REACH-centred): a raw layer (chemicals, materials, SDSs, suppliers, parts,
programs, compliance) plus the ontology (registry + bindings) that points at it.

Deterministic (hash-based), stable and re-runnable. POST /api/reset calls reset_all().
"""
import hashlib
import os

from db import get_conn, init_schema, DB_PATH
from canonical import CANONICAL
import rag
import docs
import catalog
import companies
import plat

SEED_DATE = "2026-06-20"

# ---- aerospace substances (REACH-relevant) ----
# (cas, name, ec, ghs_class, h_statements, reach_status, flash_c, oel_ppm, svhc, use)
CHEMICALS = [
    ("1333-82-0", "Chromium trioxide", "215-607-8", "Carc. 1A; Muta. 1B", "H350;H340;H317",
     "Annex XIV (Authorisation)", "", "0.005", "yes", "chromate conversion / hard chrome"),
    ("7789-06-2", "Strontium chromate", "232-142-6", "Carc. 1B", "H350;H373",
     "SVHC (Candidate List)", "", "0.0005", "yes", "corrosion-inhibiting primer"),
    ("7440-43-9", "Cadmium", "231-152-8", "Carc. 1B; Repr. 2", "H350;H341;H361",
     "SVHC / RoHS restricted", "", "0.002", "yes", "sacrificial plating"),
    ("302-01-2", "Hydrazine", "206-114-9", "Carc. 1B; Acute Tox. 2", "H350;H314;H317",
     "SVHC (Candidate List)", "38", "0.01", "yes", "EPU emergency-power fuel"),
    ("117-81-7", "Bis(2-ethylhexyl) phthalate (DEHP)", "204-211-0", "Repr. 1B", "H360",
     "Annex XIV (Authorisation)", "", "", "yes", "plasticiser in sealants"),
    ("79-01-6", "Trichloroethylene", "201-167-4", "Carc. 1B", "H350;H319",
     "Annex XIV (Authorisation)", "", "10", "yes", "vapour degreasing"),
    ("872-50-4", "N-Methyl-2-pyrrolidone (NMP)", "212-828-1", "Repr. 1B", "H360;H315",
     "Annex XVII (Restriction)", "86", "10", "yes", "paint stripper / solvent"),
    ("78-93-3", "Methyl ethyl ketone (MEK)", "201-159-0", "Flam. Liq. 2", "H225;H319;H336",
     "Registered (compliant)", "-9", "200", "no", "solvent / cleaner"),
    ("108-88-3", "Toluene", "203-625-9", "Flam. Liq. 2; Repr. 2", "H225;H361;H336",
     "Annex XVII (Restriction)", "4", "50", "no", "solvent"),
    ("822-06-0", "Hexamethylene diisocyanate (HDI)", "212-485-8", "Resp. Sens. 1", "H334;H317;H331",
     "Registered (compliant)", "140", "0.005", "no", "polyurethane topcoat hardener"),
    ("335-67-1", "Perfluorooctanoic acid (PFOA)", "206-397-9", "Carc. 2; Repr. 1B", "H350;H360;H372",
     "Annex XVII / POP", "", "", "yes", "fluoropolymer processing"),
    ("10043-35-3", "Boric acid", "233-139-2", "Repr. 1B", "H360", "SVHC (Candidate List)",
     "", "", "yes", "anodising bath"),
]

# (material_id, name, spec, form, base_cas, supplier)
MATERIALS = [
    ("44GN098", "44GN098 epoxy corrosion-inhibiting primer", "MIL-PRF-23377", "liquid", "7789-06-2", "PPG Aerospace"),
    ("A1200S", "Alodine 1200S chromate conversion coating", "MIL-DTL-5541", "liquid", "1333-82-0", "Chemetall"),
    ("PR1440", "PR-1440 fuel-tank sealant", "AMS 3277", "paste", "117-81-7", "PPG Aerospace"),
    ("EA9394", "EA 9394 structural epoxy adhesive", "AMS 3689", "paste", "", "Henkel"),
    ("A3001", "Aerodur 3001 polyurethane topcoat", "AMS-C-83286", "liquid", "822-06-0", "AkzoNobel Aerospace Coatings"),
    ("SKYLD4", "Skydrol LD-4 hydraulic fluid", "SAE AS1241", "liquid", "", "Eastman"),
    ("M21", "HexPly M21 carbon-fibre prepreg", "BMS 8-276", "solid", "", "Hexcel"),
    ("CADPL", "Cadmium electroplate", "AMS-QQ-P-416", "solid", "7440-43-9", "3M Aerospace"),
    ("TCEDEG", "Trichloroethylene vapour degreaser", "O-T-634", "liquid", "79-01-6", "Eastman"),
    ("STRIP7", "NMP-based paint stripper", "MIL-R-81294", "liquid", "872-50-4", "Chemetall"),
    ("HYDEPU", "Hydrazine EPU fuel (H-70)", "MIL-PRF-27404", "liquid", "302-01-2", "Eastman"),
]

# (name, model, status)
PROGRAMS = [
    ("G700", "Ultra-long-range", "in production"), ("G800", "Ultra-long-range", "in development"),
    ("G650ER", "Long-range", "in production"), ("G600", "Long-range", "in production"),
    ("G500", "Long-range", "in production"), ("G280", "Super-mid-size", "in production"),
]

# (part_number, name, program, material_id)
PARTS = [
    ("W-5501-01", "Wing skin panel", "G700", "44GN098"),
    ("F-2210-03", "Center-wing fuel tank", "G700", "PR1440"),
    ("FS-1120", "Fuselage frame", "G800", "A1200S"),
    ("LG-8830", "Main landing-gear strut", "G650ER", "CADPL"),
    ("EP-7702", "Engine pylon fairing", "G600", "A3001"),
    ("HYD-4410", "Flight-control hydraulic actuator", "G500", "SKYLD4"),
    ("CS-9901", "Empennage composite skin", "G280", "M21"),
    ("EPU-3300", "Emergency power unit", "G650ER", "HYDEPU"),
    ("W-5502-07", "Wing spar", "G800", "44GN098"),
    ("DR-1140", "Cabin door structure", "G600", "A1200S"),
    ("EX-2201", "Exterior topcoat (fuselage)", "G700", "A3001"),
    ("BR-3310", "Brake assembly plating", "G500", "CADPL"),
]


def _h(*parts):
    return int(hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest(), 16)


def _svhc_deadline(status, cas):
    if status.startswith("Annex XIV"):
        return ["2026-01-21", "2026-09-01", "2027-01-22"][_h(cas) % 3]
    return ""


def build_raw():
    raw = {}

    raw["t_chemicals"] = {
        "label": "R.E.A.C.T substance register (REACH export)",
        "cols": ["cas", "name", "ec", "ghs_class", "h_statements", "reach_status", "flash_c", "oel", "svhc", "use"],
        "rows": [tuple(c) for c in CHEMICALS]}

    raw["t_materials"] = {
        "label": "Approved materials / consumables master",
        "cols": ["material_id", "name", "spec", "form", "base_cas", "supplier"],
        "rows": [tuple(m) for m in MATERIALS]}

    # one SDS per material
    sds = []
    for mid, name, spec, form, base, supp in MATERIALS:
        rev = "%d-%02d-15" % (2024 + _h(mid) % 2, 1 + _h(mid, "m") % 12)
        chem = next((c for c in CHEMICALS if c[0] == base), None)
        hz = chem[3] if chem else "See Section 2"
        sds.append(("SDS-%s" % mid, name, supp, rev, hz))
    raw["t_sds"] = {"label": "Safety Data Sheet library",
                    "cols": ["sds_id", "product_name", "manufacturer", "revision_date", "hazards"], "rows": sds}

    raw["t_suppliers"] = {"label": "Supplier / manufacturer master",
                          "cols": companies.COLS, "rows": companies.build_rows()}

    raw["t_parts"] = {"label": "Engineering parts → materials (BOM)",
                      "cols": ["part_number", "name", "program", "material"],
                      "rows": [tuple(p) for p in PARTS]}

    raw["t_programs"] = {"label": "Aircraft program master",
                         "cols": ["program", "model", "status"], "rows": [tuple(p) for p in PROGRAMS]}

    # one compliance record per substance × REACH (+ RoHS where relevant)
    comp = []
    for cas, name, ec, ghs, h, status, fp, oel, svhc, use in CHEMICALS:
        ref = ("Annex XIV" if "Annex XIV" in status else ("Annex XVII" if "Annex XVII" in status else "-"))
        comp.append((cas, cas, "REACH", status, svhc, ref, _svhc_deadline(status, cas)))
        if "RoHS" in status:
            comp.append((cas, cas, "RoHS", "restricted (Pb/Cd)", "no", "Annex II", ""))
    raw["t_compliance"] = {"label": "Compliance status register",
                           "cols": ["subject", "cas", "regulation", "status", "svhc_flag", "restriction_ref", "deadline"],
                           "rows": comp}
    return raw


# object_property, source_table, source_col, transform
BINDINGS = [
    ("Chemical.cas", "t_chemicals", "cas", "-"),
    ("Chemical.name", "t_chemicals", "name", "-"),
    ("Chemical.ec_number", "t_chemicals", "ec", "-"),
    ("Chemical.ghs_class", "t_chemicals", "ghs_class", "-"),
    ("Chemical.h_statements", "t_chemicals", "h_statements", "-"),
    ("Chemical.reach_status", "t_chemicals", "reach_status", "-"),
    ("Chemical.flash_point_c", "t_chemicals", "flash_c", "to_int"),
    ("Chemical.exposure_limit_ppm", "t_chemicals", "oel", "-"),
    ("Chemical.svhc", "t_chemicals", "svhc", "-"),
    ("Chemical.use", "t_chemicals", "use", "-"),

    ("Material.material_id", "t_materials", "material_id", "-"),
    ("Material.name", "t_materials", "name", "-"),
    ("Material.spec", "t_materials", "spec", "-"),
    ("Material.form", "t_materials", "form", "-"),
    ("Material.base_chemical", "t_materials", "base_cas", "-"),
    ("Material.supplier", "t_materials", "supplier", "-"),

    ("SafetyDataSheet.sds_id", "t_sds", "sds_id", "-"),
    ("SafetyDataSheet.product_name", "t_sds", "product_name", "-"),
    ("SafetyDataSheet.manufacturer", "t_sds", "manufacturer", "-"),
    ("SafetyDataSheet.revision_date", "t_sds", "revision_date", "-"),
    ("SafetyDataSheet.hazards", "t_sds", "hazards", "-"),

    ("Part.part_number", "t_parts", "part_number", "-"),
    ("Part.name", "t_parts", "name", "-"),
    ("Part.program", "t_parts", "program", "-"),
    ("Part.material", "t_parts", "material", "-"),

    ("Program.name", "t_programs", "program", "-"),
    ("Program.model", "t_programs", "model", "-"),
    ("Program.status", "t_programs", "status", "-"),

    ("Compliance.subject", "t_compliance", "subject", "-"),
    ("Compliance.regulation", "t_compliance", "regulation", "-"),
    ("Compliance.status", "t_compliance", "status", "-"),
    ("Compliance.svhc_flag", "t_compliance", "svhc_flag", "-"),
    ("Compliance.restriction_ref", "t_compliance", "restriction_ref", "-"),
    ("Compliance.deadline", "t_compliance", "deadline", "-"),
]


def _edges():
    edges = []
    for mid, name, spec, form, base, supp in MATERIALS:
        if base:
            edges.append(("Material", mid, "containsChemical", "Chemical", base))
    for pn, name, prog, mid in PARTS:
        edges.append(("Part", pn, "madeOf", "Material", mid))
        edges.append(("Part", pn, "usedOn", "Program", prog))
    for cas, *_ in CHEMICALS:
        edges.append(("Compliance", cas, "appliesTo", "Chemical", cas))
    return edges


def seed_narrative(conn):
    """REACH status notes, substitution guidance and program commentary."""
    for cas, name, ec, ghs, h, status, fp, oel, svhc, use in CHEMICALS:
        if svhc == "yes":
            txt = ("%s (CAS %s) is a REACH substance of concern — status: %s. It is used in %s. "
                   "GHS: %s. Substitution/authorisation is tracked; where used on in-production "
                   "programs, an authorised use or a qualified substitute is required." %
                   (name, cas, status, use, ghs))
            rag.add(conn, "Chemical:%s" % name, "reach_status", txt, "seed", "2026")

    subs = [
        ("Material:44GN098 epoxy corrosion-inhibiting primer",
         "44GN098 contains strontium chromate (SVHC). A chrome-free primer (e.g. PreKote / "
         "non-chromate epoxy) has been qualified on the G700 exterior; retrofit to G650ER is in work."),
        ("Chemical:Chromium trioxide",
         "Chromium trioxide (Cr VI) is on REACH Annex XIV — continued use needs an authorisation with a "
         "defined sunset date. Trivalent-chrome and IVD-aluminium alternatives are being qualified for "
         "conversion coating and plating."),
        ("Chemical:Cadmium",
         "Cadmium plating is being phased down under REACH/RoHS pressure; zinc-nickel is the primary "
         "substitute for landing-gear and fastener plating, subject to hydrogen-embrittlement re-qual."),
    ]
    for ent, txt in subs:
        rag.add(conn, ent, "substitution", txt, "seed", "2026")

    program = [
        "REACH exposure to Gulfstream is concentrated in surface finishing — chromate primers and "
        "conversion coatings, cadmium plating, and hydrazine EPU fuel — plus solvents used in cleaning "
        "and paint stripping.",
        "The compliance strategy is authorisation-plus-substitution: hold Annex XIV authorisations to "
        "protect in-service fleets while qualifying chrome-free and cadmium-free alternatives on new "
        "programs (G700, G800) first.",
        "SDS revision currency and supplier REACH-registration status are audited annually; a lapsed "
        "registration or an SVHC newly added to the Candidate List triggers a material review.",
    ]
    for m in program:
        rag.add(conn, "Program:REACH compliance", "commentary", m, "seed", "2026")
    conn.commit()


def reset_all():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = get_conn()
    init_schema(conn)
    cur = conn.cursor()

    raw = build_raw()
    for name, spec in raw.items():
        cols_sql = ", ".join('"%s"' % c for c in spec["cols"])
        cur.execute('CREATE TABLE "%s" (%s)' % (name, cols_sql))
        ph = ", ".join("?" for _ in spec["cols"])
        cur.executemany('INSERT INTO "%s" VALUES (%s)' % (name, ph), spec["rows"])
        cur.execute("INSERT INTO raw_catalog (name, source_label, source_file, landed_on, row_count) "
                    "VALUES (?,?,?,?,?)", (name, spec["label"], "seed", SEED_DATE, len(spec["rows"])))

    # registry = the full dictionary (the whole menu is visible)
    seen, reg = set(), []
    for c in CANONICAL:
        k = (c["object"], c["property"])
        if k in seen:
            continue
        seen.add(k)
        reg.append((c["object"], c["property"], c["type"], c["unit"], "approved"))
    cur.executemany("INSERT INTO object_registry (object, property, type, unit, status) "
                    "VALUES (?,?,?,?,?)", reg)
    cur.executemany("INSERT INTO bindings (object_property, source_table, source_col, transform, "
                    "confidence, source_file, status) VALUES (?,?,?,?,1.0,'seed','approved')",
                    BINDINGS + companies.BINDINGS)
    cur.executemany("INSERT INTO edges (from_obj, from_key, link, to_obj, to_key) VALUES (?,?,?,?,?)",
                    _edges())
    conn.commit()

    seed_narrative(conn)

    # ---- control plane: tenancy / security / actions / branching ----
    plat.CTX.update({"actor": "Admin", "role": "Admin", "workspace": "Global", "branch": "main"})
    for ws in ("Global", "Environmental Compliance", "Materials Engineering"):
        cur.execute("INSERT OR IGNORE INTO workspaces (name,created_at) VALUES (?,?)", (ws, SEED_DATE))
    cur.execute("INSERT OR IGNORE INTO branches (name,base,created_by,created_at,status) "
                "VALUES ('main','','system',?, 'open')", (SEED_DATE,))
    for op, lvl in [("Compliance.status", "confidential"), ("Compliance.deadline", "confidential"),
                    ("Compliance.restriction_ref", "confidential"), ("Supplier.approval_status", "confidential"),
                    ("Chemical.exposure_limit_ppm", "internal"), ("Material.supplier", "internal"),
                    ("ExposureScenario.measured_ppm", "restricted")]:
        cur.execute("INSERT OR IGNORE INTO classifications (object_property,level) VALUES (?,?)", (op, lvl))
    conn.commit()
    # demo write-back + a branch (as a Data Steward), then back to Admin/main
    plat.set_context(actor="Data Steward")
    plat.add_edit(conn, "Compliance", "subject", "7789-06-2", "status",
                  "SVHC (Candidate List)", "Annex XIV recommendation (RAC)", "Updated per ECHA RAC opinion")
    plat.create_branch(conn, "reach-2027-sunset")
    plat.add_edit(conn, "Material", "material_id", "44GN098", "reach_status",
                  "chromate", "chrome-free substitute qualified (G700)", "Substitution qualified on G700")
    plat.set_context(actor="Admin", workspace="Global", branch="main")

    # document registry (SDSs + the raw sources)
    all_binds = BINDINGS + companies.BINDINGS
    src_objects = {}
    for op, tbl, col, tf in all_binds:
        src_objects.setdefault(tbl, set()).add(op.split(".")[0])
    dom = ("Aerospace · Materials & Chemical Compliance", "REACH Compliance", "Materials engineering")
    op_docs = []
    for name, spec in raw.items():
        op_docs.append({
            "filename": name, "label": spec["label"], "industry": dom[0], "scenario": dom[1],
            "use_case": dom[2], "doctype": "seed", "source": "seed", "kind": "table",
            "rows": len(spec["rows"]), "status": "committed", "staging_table": name,
            "objects": ", ".join(sorted(src_objects.get(name, []))),
            "bindings": sum(1 for b in all_binds if b[1] == name)})
    docs.seed_samples(op_docs)
    docs.seed_samples(catalog.build())
    conn.close()


if __name__ == "__main__":
    reset_all()
    print("seeded aerospace REACH-compliance model")
