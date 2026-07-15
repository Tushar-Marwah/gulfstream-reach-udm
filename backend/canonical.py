"""
The Gulfstream aerospace materials & chemical-compliance canonical dictionary --
the "menu" the ontology maps into (REACH-centred).

Any incoming file (an SDS, a material declaration, a REACH SVHC export from the
R.E.A.C.T database, a supplier master...) maps into this. The LLM mapper reads the
whole dictionary; brand-new concepts that don't fit become PROPOSED new
objects/properties (auto-grow).

Entry fields:
  object, property, level, type, unit, desc   -- always present
  aliases, value_kind, seed                    -- only on the seeded core, used by the
                                                  offline heuristic matcher.
"""

# ---- the seeded core (offline matcher uses these; value_kind drives heuristic) ----
_CORE = [
    # Chemical substance (the REACH subject)
    ("Chemical", "cas", "substance", "string", "", "CAS Registry Number",
     ["cas", "cas no", "cas number", "casrn"], "code_or_name"),
    ("Chemical", "name", "substance", "string", "", "Substance name",
     ["substance", "chemical", "name", "material name"], "free_text"),
    ("Chemical", "ec_number", "substance", "string", "", "EC / EINECS number",
     ["ec", "ec number", "einecs"], "code_or_name"),
    ("Chemical", "ghs_class", "substance", "string", "", "GHS hazard classification",
     ["ghs", "hazard class", "classification", "signal"], "free_text"),
    ("Chemical", "h_statements", "substance", "string", "", "GHS hazard (H) statements",
     ["h statements", "hazard statements", "h-codes", "hazards"], "free_text"),
    ("Chemical", "reach_status", "substance", "string", "", "REACH status (SVHC / Annex XIV / Annex XVII / compliant)",
     ["reach", "reach status", "svhc", "restriction"], "free_text"),
    ("Chemical", "flash_point_c", "substance", "number", "°C", "Flash point in degrees Celsius",
     ["flash", "flash point", "fp"], "integer"),
    ("Chemical", "exposure_limit_ppm", "substance", "number", "ppm", "Occupational exposure limit",
     ["oel", "exposure limit", "pel", "tlv", "wel"], "number"),

    # Material / product (a formulated aerospace product)
    ("Material", "material_id", "material", "string", "", "Material / product part id",
     ["material", "material id", "product code", "id"], "code_or_name"),
    ("Material", "name", "material", "string", "", "Material / product name",
     ["name", "product", "description"], "free_text"),
    ("Material", "spec", "material", "string", "", "Governing spec (AMS / MIL / internal)",
     ["spec", "specification", "ams", "mil"], "free_text"),
    ("Material", "form", "material", "enum", "", "Physical form (liquid/paste/solid/aerosol)",
     ["form", "state", "physical form"], "free_text"),
    ("Material", "base_chemical", "material", "string", "", "Key hazardous constituent (CAS)",
     ["base chemical", "constituent", "active", "hazardous ingredient"], "code_or_name"),
    ("Material", "supplier", "material", "string", "", "Supplier / manufacturer",
     ["supplier", "manufacturer", "vendor", "mfr"], "free_text"),

    # Safety Data Sheet document
    ("SafetyDataSheet", "sds_id", "sds", "string", "", "SDS document id",
     ["sds", "sds id", "msds", "document"], "code_or_name"),
    ("SafetyDataSheet", "product_name", "sds", "string", "", "Product the SDS covers",
     ["product", "product name", "trade name"], "free_text"),
    ("SafetyDataSheet", "manufacturer", "sds", "string", "", "SDS author / manufacturer",
     ["manufacturer", "supplier", "author"], "free_text"),
    ("SafetyDataSheet", "revision_date", "sds", "string", "date", "SDS revision date",
     ["revision", "revision date", "rev", "date"], "date"),
    ("SafetyDataSheet", "hazards", "sds", "string", "", "Section 2 hazard summary",
     ["hazards", "section 2", "hazard identification"], "free_text"),

    # Supplier
    ("Supplier", "name", "supplier", "string", "", "Supplier name",
     ["supplier", "name", "vendor", "manufacturer"], "free_text"),
    ("Supplier", "country", "supplier", "string", "", "Country of origin",
     ["country", "origin", "location"], "free_text"),
    ("Supplier", "approval_status", "supplier", "enum", "", "Approved / conditional / disqualified",
     ["approval", "status", "qualified"], "free_text"),

    # Part / assembly on an aircraft program
    ("Part", "part_number", "part", "string", "", "Engineering part number",
     ["part", "part number", "pn", "p/n"], "code_or_name"),
    ("Part", "name", "part", "string", "", "Part name / description",
     ["name", "description", "nomenclature"], "free_text"),
    ("Part", "program", "part", "string", "", "Aircraft program the part is used on",
     ["program", "aircraft", "model", "platform"], "free_text"),
    ("Part", "material", "part", "string", "", "Material applied / used",
     ["material", "finish", "coating", "consumable"], "code_or_name"),

    # Compliance record (one per substance × regulation)
    ("Compliance", "subject", "compliance", "string", "", "Substance / material the record is about",
     ["subject", "substance", "cas", "material"], "code_or_name"),
    ("Compliance", "regulation", "compliance", "enum", "", "Regulation (REACH / RoHS / EPA / OSHA)",
     ["regulation", "regime", "framework"], "free_text"),
    ("Compliance", "status", "compliance", "enum", "", "Compliance status / classification",
     ["status", "classification", "outcome"], "free_text"),
    ("Compliance", "svhc_flag", "compliance", "enum", "", "Whether it is a REACH SVHC",
     ["svhc", "svhc flag", "candidate"], "free_text"),
    ("Compliance", "restriction_ref", "compliance", "string", "", "Annex XIV/XVII entry or restriction ref",
     ["annex", "restriction", "entry", "authorisation"], "free_text"),
    ("Compliance", "deadline", "compliance", "string", "date", "Sunset / authorisation / phase-out date",
     ["deadline", "sunset", "phase-out", "date"], "date"),
]

# ---- extended targets (LLM mapping / auto-grow; no heuristic aliases) ----
_EXT = [
    ("Chemical", "svhc", "substance", "enum", "", "Is the substance a REACH SVHC (yes/no)"),
    ("Chemical", "annex_xiv", "substance", "enum", "", "On the REACH Authorisation List (Annex XIV)"),
    ("Chemical", "pbt", "substance", "enum", "", "PBT / vPvB classification"),
    ("Chemical", "concentration_pct", "substance", "number", "%", "Concentration in the material"),
    ("Chemical", "use", "substance", "string", "", "Function / use in the aerospace application"),

    ("Material", "hazard_category", "material", "string", "", "Overall hazard category"),
    ("Material", "voc_gpl", "material", "number", "g/L", "VOC content"),
    ("Material", "shelf_life_mo", "material", "number", "months", "Shelf life"),
    ("Material", "storage_class", "material", "string", "", "Storage / handling class"),
    ("Material", "substitute", "material", "string", "", "Approved chrome-free / compliant substitute"),

    ("Part", "quantity", "part", "number", "count", "Quantity per ship-set"),
    ("Part", "finish", "part", "string", "", "Surface finish / treatment"),

    ("Program", "name", "program", "string", "", "Aircraft program name"),
    ("Program", "model", "program", "string", "", "Model / variant"),
    ("Program", "status", "program", "enum", "", "In production / in development / legacy"),
    ("Program", "cert_basis", "program", "string", "", "Certification basis (FAR 25)"),

    ("Compliance", "risk", "compliance", "number", "1-5", "Compliance risk rating"),
    ("Compliance", "owner", "compliance", "string", "", "Responsible engineer / function"),
    ("Compliance", "action", "compliance", "string", "", "Mitigation / substitution action"),

    ("ExposureScenario", "substance", "exposure", "string", "", "Substance the scenario covers"),
    ("ExposureScenario", "task", "exposure", "string", "", "Task / process generating exposure"),
    ("ExposureScenario", "control", "exposure", "string", "", "Control measure (PPE / LEV)"),
    ("ExposureScenario", "measured_ppm", "exposure", "number", "ppm", "Measured exposure level"),
]

_DOMAIN = "Gulfstream · Materials & Chemical Compliance"
CANONICAL = []
for o, p, lv, t, u, d, al, vk in _CORE:
    CANONICAL.append({"object": o, "property": p, "level": lv, "type": t, "unit": u,
                      "desc": d, "domain": _DOMAIN, "aliases": al, "value_kind": vk, "seed": True})
for o, p, lv, t, u, d in _EXT:
    CANONICAL.append({"object": o, "property": p, "level": lv, "type": t, "unit": u,
                      "desc": d, "domain": _DOMAIN, "aliases": [], "value_kind": None, "seed": False})

# focused build: no unrelated business domains merged in
try:
    import domains
    CANONICAL.extend(domains.build_entries())
except Exception:
    pass

# the offline heuristic only considers seeded entries (with a value_kind)
HEURISTIC = [c for c in CANONICAL if c.get("value_kind")]


def canonical_for(obj, prop):
    for c in CANONICAL:
        if c["object"] == obj and c["property"] == prop:
            return c
    return None


def dictionary_text():
    """Compact, domain-grouped rendering of the whole dictionary for the LLM prompt."""
    by_dom = {}
    for c in CANONICAL:
        by_dom.setdefault(c.get("domain", "Other"), {}).setdefault(c["object"], []).append(c["property"])
    lines = []
    for dom, objs in by_dom.items():
        lines.append("# %s" % dom)
        for obj, props in objs.items():
            lines.append("%s: %s" % (obj, ", ".join(props)))
    return "\n".join(lines)
