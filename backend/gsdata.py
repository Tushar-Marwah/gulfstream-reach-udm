"""
Comprehensive Gulfstream REACH / SDS demo dataset.

Curated real REACH-relevant substances + deterministic generators that explode
them into a realistic, sizeable model: a substance register, an approved-materials
master (with grade variants), an engineering BOM of parts across programmes, an
SDS library, a supplier master and a compliance register.

Deterministic (hash-seeded) so every reset produces the same model.
"""
import hashlib

# ------------------------------------------------------------------ helpers
def _h(*parts):
    return int(hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest(), 16)


def _pick(seq, *seed):
    return seq[_h(*seed) % len(seq)]


# ------------------------------------------------------------------ substances
# (cas, name, ec, ghs_class, h_statements, reach_status, flash_c, oel_ppm, svhc, use)
CHEM_BASE = [
    ("1333-82-0", "Chromium trioxide", "215-607-8", "Carc. 1A; Muta. 1B; STOT RE 1", "H350;H340;H317;H314", "Annex XIV (Authorisation)", "", "0.005", "yes", "hard chrome / conversion coating"),
    ("7789-06-2", "Strontium chromate", "232-142-6", "Carc. 1B; STOT RE 2", "H350;H373;H317", "SVHC (Candidate List)", "", "0.0005", "yes", "corrosion-inhibiting primer"),
    ("13530-65-9", "Zinc chromate", "236-878-9", "Carc. 1B; Repr. 2", "H350;H317;H410", "SVHC (Candidate List)", "", "0.01", "yes", "corrosion-inhibiting primer"),
    ("7778-50-9", "Potassium dichromate", "231-906-6", "Carc. 1B; Muta. 1B; Repr. 1B", "H350;H340;H360", "Annex XIV (Authorisation)", "", "0.005", "yes", "conversion coating bath"),
    ("10588-01-9", "Sodium dichromate", "234-190-3", "Carc. 1B; Muta. 1B; Repr. 1B", "H350;H340;H360", "Annex XIV (Authorisation)", "", "0.005", "yes", "sealing / passivation bath"),
    ("1344-37-2", "Lead sulfochromate yellow", "215-693-7", "Carc. 1B; Repr. 1A", "H350;H360;H373", "SVHC (Candidate List)", "", "0.05", "yes", "high-visibility marking paint"),
    ("7440-43-9", "Cadmium", "231-152-8", "Carc. 1B; Muta. 2; Repr. 2; STOT RE 1", "H350;H341;H361;H372", "SVHC / RoHS restricted", "", "0.002", "yes", "sacrificial plating"),
    ("1306-19-0", "Cadmium oxide", "215-146-2", "Carc. 1B; Muta. 2; Repr. 2", "H350;H341;H361;H330", "SVHC (Candidate List)", "", "0.002", "yes", "plating anode"),
    ("7440-41-7", "Beryllium", "231-150-7", "Carc. 1B; STOT RE 1; Resp. Sens. 1", "H350;H372;H335;H317", "Registered (compliant)", "", "0.00002", "no", "copper-beryllium bushings"),
    ("7439-92-1", "Lead", "231-100-4", "Repr. 1A; STOT RE 2", "H360;H373;H410", "SVHC (Candidate List)", "", "0.05", "yes", "solder / balance weights"),
    ("1314-41-6", "Trilead tetraoxide (red lead)", "215-235-6", "Repr. 1A; STOT RE 2", "H360;H373;H410", "SVHC (Candidate List)", "", "0.05", "yes", "anticorrosive primer (legacy)"),
    ("302-01-2", "Hydrazine", "206-114-9", "Carc. 1B; Acute Tox. 2; Skin Corr. 1B", "H350;H314;H317;H330", "SVHC (Candidate List)", "38", "0.01", "yes", "EPU emergency-power fuel"),
    ("117-81-7", "Bis(2-ethylhexyl) phthalate (DEHP)", "204-211-0", "Repr. 1B", "H360", "Annex XIV (Authorisation)", "", "", "yes", "plasticiser in sealants"),
    ("84-74-2", "Dibutyl phthalate (DBP)", "201-557-4", "Repr. 1B", "H360;H411", "Annex XIV (Authorisation)", "157", "", "yes", "plasticiser / lacquer"),
    ("85-68-7", "Benzyl butyl phthalate (BBP)", "201-622-7", "Repr. 1B", "H360;H400", "Annex XIV (Authorisation)", "", "", "yes", "plasticiser in coatings"),
    ("84-69-5", "Diisobutyl phthalate (DIBP)", "201-553-2", "Repr. 1B", "H360", "Annex XIV (Authorisation)", "", "", "yes", "plasticiser"),
    ("79-01-6", "Trichloroethylene", "201-167-4", "Carc. 1B; Muta. 2", "H350;H341;H319", "Annex XIV (Authorisation)", "", "10", "yes", "vapour degreasing"),
    ("75-09-2", "Dichloromethane (DCM)", "200-838-9", "Carc. 2; STOT SE 3", "H351;H336;H373", "Annex XVII (Restriction)", "", "50", "yes", "paint stripping"),
    ("127-18-4", "Tetrachloroethylene (PERC)", "204-825-9", "Carc. 2", "H351;H411", "Registered (compliant)", "", "20", "no", "degreasing"),
    ("872-50-4", "N-Methyl-2-pyrrolidone (NMP)", "212-828-1", "Repr. 1B; STOT SE 3; Skin Irrit. 2", "H360;H335;H315", "Annex XVII (Restriction)", "86", "10", "yes", "paint stripper / solvent"),
    ("110-80-5", "2-Ethoxyethanol", "203-804-1", "Flam. Liq. 3; Repr. 1B", "H360;H226;H332", "SVHC (Candidate List)", "44", "2", "yes", "coating solvent"),
    ("109-86-4", "2-Methoxyethanol", "203-713-7", "Flam. Liq. 3; Repr. 1B", "H360;H226;H332", "SVHC (Candidate List)", "39", "0.1", "yes", "coating solvent (legacy)"),
    ("78-93-3", "Methyl ethyl ketone (MEK)", "201-159-0", "Flam. Liq. 2; Eye Irrit. 2", "H225;H319;H336", "Registered (compliant)", "-9", "200", "no", "solvent / cleaner"),
    ("108-10-1", "Methyl isobutyl ketone (MIBK)", "203-550-1", "Flam. Liq. 2; STOT SE 3", "H225;H319;H335", "Registered (compliant)", "14", "20", "no", "coating solvent"),
    ("67-64-1", "Acetone", "200-662-2", "Flam. Liq. 2; Eye Irrit. 2", "H225;H319;H336", "Registered (compliant)", "-20", "500", "no", "cleaning solvent"),
    ("108-88-3", "Toluene", "203-625-9", "Flam. Liq. 2; Repr. 2; STOT RE 2", "H225;H361;H336", "Annex XVII (Restriction)", "4", "50", "no", "solvent"),
    ("1330-20-7", "Xylene (mixed isomers)", "215-535-7", "Flam. Liq. 3; Acute Tox. 4", "H226;H332;H312;H315", "Registered (compliant)", "27", "50", "no", "solvent"),
    ("100-41-4", "Ethylbenzene", "202-849-4", "Flam. Liq. 2; Carc. 2", "H225;H351;H332", "Registered (compliant)", "18", "100", "no", "solvent carrier"),
    ("71-43-2", "Benzene", "200-753-7", "Flam. Liq. 2; Carc. 1A; Muta. 1B", "H225;H350;H340", "Annex XVII (Restriction)", "-11", "0.5", "yes", "trace solvent contaminant"),
    ("822-06-0", "Hexamethylene diisocyanate (HDI)", "212-485-8", "Resp. Sens. 1; Acute Tox. 2", "H334;H317;H330", "Registered (compliant)", "140", "0.005", "no", "polyurethane topcoat hardener"),
    ("101-68-8", "4,4'-Methylenediphenyl diisocyanate (MDI)", "202-966-0", "Resp. Sens. 1; Carc. 2", "H334;H351;H335", "Annex XVII (Restriction)", "212", "0.005", "no", "adhesive / foam hardener"),
    ("584-84-9", "Toluene-2,4-diisocyanate (TDI)", "209-544-5", "Resp. Sens. 1; Carc. 2; Acute Tox. 2", "H334;H351;H330", "Annex XVII (Restriction)", "127", "0.005", "no", "polyurethane precursor"),
    ("335-67-1", "Perfluorooctanoic acid (PFOA)", "206-397-9", "Carc. 2; Repr. 1B; STOT RE 1", "H350;H360;H372", "Annex XVII / POP", "", "", "yes", "fluoropolymer processing aid"),
    ("1763-23-1", "Perfluorooctanesulfonic acid (PFOS)", "217-179-8", "Carc. 2; Repr. 1B; Lact.", "H351;H360;H362", "POP (banned)", "", "", "yes", "chrome-mist suppressant (legacy)"),
    ("375-95-1", "Perfluorononanoic acid (PFNA)", "206-801-3", "Repr. 1B; STOT RE 1", "H360;H372;H332", "SVHC (Candidate List)", "", "", "yes", "surfactant (legacy)"),
    ("10043-35-3", "Boric acid", "233-139-2", "Repr. 1B", "H360", "SVHC (Candidate List)", "", "", "yes", "anodising / etch bath"),
    ("1303-96-4", "Disodium tetraborate decahydrate (borax)", "215-540-4", "Repr. 1B", "H360", "SVHC (Candidate List)", "", "", "yes", "flux / bath additive"),
    ("7440-48-4", "Cobalt (metallic)", "231-158-0", "Carc. 1B; Muta. 2; Repr. 1B; Resp. Sens. 1", "H350;H341;H360;H334", "SVHC (Candidate List)", "", "0.02", "yes", "hard-metal / superalloy"),
    ("10124-43-3", "Cobalt sulfate", "233-334-2", "Carc. 1B; Muta. 2; Repr. 1B", "H350;H341;H360", "Annex XIV (Authorisation)", "", "0.02", "yes", "electroplating bath"),
    ("80-05-7", "Bisphenol A (BPA)", "201-245-8", "Repr. 1B; STOT SE 3; Eye Dam. 1; Skin Sens. 1", "H360;H335;H318;H317", "SVHC (Candidate List)", "", "", "yes", "epoxy resin monomer"),
    ("25068-38-6", "Bisphenol-A epoxy resin (DGEBA)", "500-033-5", "Skin Sens. 1; Aquatic Chronic 2", "H317;H411;H319", "Registered (compliant)", "", "", "no", "structural epoxy base"),
    ("111-40-0", "Diethylenetriamine (DETA)", "203-865-4", "Skin Corr. 1B; Skin Sens. 1", "H314;H317;H302", "Registered (compliant)", "98", "1", "no", "epoxy curing agent"),
    ("90-72-2", "Tris(dimethylaminomethyl)phenol", "202-013-9", "Skin Corr. 1C; Acute Tox. 4", "H314;H302;H332", "Registered (compliant)", "110", "", "no", "epoxy accelerator"),
    ("80-62-6", "Methyl methacrylate (MMA)", "201-297-1", "Flam. Liq. 2; Skin Sens. 1; STOT SE 3", "H225;H317;H335", "Registered (compliant)", "10", "50", "no", "acrylic adhesive"),
    ("1338-23-4", "Methyl ethyl ketone peroxide (MEKP)", "215-661-2", "Org. Perox. C; Acute Tox. 4; Eye Dam. 1", "H242;H302;H318", "Registered (compliant)", "65", "0.2", "no", "resin catalyst"),
    ("7647-01-0", "Hydrochloric acid", "231-595-7", "Skin Corr. 1B; STOT SE 3", "H314;H335;H290", "Registered (compliant)", "", "2", "no", "pickling / activation"),
    ("7664-93-9", "Sulfuric acid", "231-639-5", "Skin Corr. 1A", "H314;H290", "Registered (compliant)", "", "0.1", "no", "anodising electrolyte"),
    ("7697-37-2", "Nitric acid", "231-714-2", "Ox. Liq. 3; Skin Corr. 1A", "H272;H314;H290", "Registered (compliant)", "", "2", "no", "desmutting / passivation"),
    ("1310-73-2", "Sodium hydroxide", "215-185-5", "Skin Corr. 1A", "H314;H290", "Registered (compliant)", "", "", "no", "alkaline cleaner"),
    ("76-13-1", "1,1,2-Trichlorotrifluoroethane (CFC-113)", "200-936-1", "Ozone 1", "H420", "Ozone-depleting (banned)", "", "1000", "yes", "precision cleaning (legacy)"),
    ("107-21-1", "Ethylene glycol", "203-473-3", "Acute Tox. 4; STOT RE 2", "H302;H373", "Registered (compliant)", "111", "", "no", "de-icing / coolant"),
]


def chemicals():
    return [tuple(c) for c in CHEM_BASE]


CAS = [c[0] for c in CHEM_BASE]
# CAS pools by application, for realistic material→chemical binding
_PRIMER_CAS = ["7789-06-2", "13530-65-9", "1333-82-0", "10043-35-3"]
_SEALANT_CAS = ["117-81-7", "84-74-2", "85-68-7", "84-69-5"]
_TOPCOAT_CAS = ["822-06-0", "101-68-8", "584-84-9"]
_ADHESIVE_CAS = ["25068-38-6", "80-05-7", "111-40-0", "80-62-6"]
_PLATING_CAS = ["7440-43-9", "1306-19-0", "10124-43-3", "7440-48-4"]
_SOLVENT_CAS = ["79-01-6", "872-50-4", "78-93-3", "108-88-3", "75-09-2", "110-80-5"]
_STRIP_CAS = ["872-50-4", "75-09-2", "109-86-4"]
_CONV_CAS = ["1333-82-0", "7778-50-9", "10588-01-9"]

# ------------------------------------------------------------------ materials
# (id_prefix, name, spec, form, cas_pool, supplier, n_variants)
MAT_FAMILIES = [
    ("PRM-CIP", "Chromated corrosion-inhibiting epoxy primer", "MIL-PRF-23377", "liquid", _PRIMER_CAS, "PPG Aerospace", 8),
    ("PRM-CF", "Chrome-free corrosion-inhibiting primer", "MIL-PRF-85582", "liquid", ["10043-35-3"], "AkzoNobel Aerospace Coatings", 6),
    ("PRM-WB", "Waterborne epoxy primer", "AMS 3095", "liquid", _PRIMER_CAS, "Sherwin-Williams Aerospace", 4),
    ("CVC", "Chromate conversion coating", "MIL-DTL-5541", "liquid", _CONV_CAS, "Chemetall", 6),
    ("CVC-TF", "Trivalent-chromium conversion coating", "MIL-DTL-81706", "liquid", ["1308-38-9"], "Chemetall", 4),
    ("SEA-FT", "Polysulfide fuel-tank sealant", "AMS 3277", "paste", _SEALANT_CAS, "PPG Aerospace", 8),
    ("SEA-AC", "Aerodynamic smoothing sealant", "AMS 3281", "paste", _SEALANT_CAS, "3M Aerospace", 5),
    ("SEA-FS", "Firewall / high-temp sealant", "AMS 3374", "paste", ["117-81-7"], "Momentive", 4),
    ("TOP-PU", "Polyurethane exterior topcoat", "AMS-C-83286", "liquid", _TOPCOAT_CAS, "AkzoNobel Aerospace Coatings", 8),
    ("TOP-BC", "Basecoat/clearcoat livery system", "AMS 3095", "liquid", _TOPCOAT_CAS, "Sherwin-Williams Aerospace", 6),
    ("ADH-EP", "Structural epoxy film adhesive", "AMS 3689", "solid", _ADHESIVE_CAS, "Henkel", 8),
    ("ADH-PS", "Paste epoxy adhesive", "AMS 3735", "paste", _ADHESIVE_CAS, "Henkel", 5),
    ("ADH-AC", "Acrylic structural adhesive", "AMS 3736", "paste", ["80-62-6", "1338-23-4"], "3M Aerospace", 4),
    ("CMP-PP", "Carbon-fibre epoxy prepreg", "BMS 8-276", "solid", ["25068-38-6", "80-05-7"], "Hexcel", 8),
    ("CMP-HC", "Aramid honeycomb core", "AMS 3711", "solid", [], "Hexcel", 4),
    ("CMP-GF", "Glass-fibre prepreg", "BMS 8-79", "solid", ["25068-38-6"], "Solvay", 5),
    ("PLT-CD", "Cadmium electroplate", "AMS-QQ-P-416", "solid", ["7440-43-9"], "3M Aerospace", 4),
    ("PLT-ZN", "Zinc-nickel electroplate", "AMS 2417", "solid", ["10124-43-3"], "Chemetall", 4),
    ("PLT-HC", "Hard chromium plate", "AMS 2460", "solid", ["1333-82-0"], "PPG Aerospace", 4),
    ("HYD-FL", "Phosphate-ester hydraulic fluid", "SAE AS1241", "liquid", [], "Eastman", 4),
    ("SOL-DG", "Vapour-degreasing solvent", "O-T-634", "liquid", _SOLVENT_CAS, "Eastman", 6),
    ("SOL-CL", "General cleaning solvent", "TT-C-490", "liquid", ["78-93-3", "67-64-1", "108-10-1"], "Eastman", 6),
    ("STR-PR", "Chemical paint stripper", "MIL-R-81294", "liquid", _STRIP_CAS, "Chemetall", 6),
    ("ANO-BATH", "Sulfuric / boric-sulfuric anodise bath", "MIL-A-8625", "liquid", ["7664-93-9", "10043-35-3"], "Chemetall", 4),
    ("EPU-FL", "Hydrazine EPU fuel (H-70)", "MIL-PRF-27404", "liquid", ["302-01-2"], "Eastman", 2),
    ("MRK-PT", "High-visibility marking paint", "AMS 3138", "liquid", ["1344-37-2"], "Sherwin-Williams Aerospace", 3),
    ("LUB-AS", "Anti-seize compound", "MIL-PRF-83483", "paste", ["7440-48-4"], "Momentive", 3),
    ("DEI-FL", "De-icing / anti-icing fluid", "AMS 1428", "liquid", ["107-21-1"], "Eastman", 3),
]

_FORMS_GRADE = ["Class A", "Class B", "Type I", "Type II", "Grade 1", "Grade 2", "Low-VOC", "Std"]


def materials():
    """Explode families into graded variants → the approved-materials master."""
    out = []
    for pfx, name, spec, form, pool, supp, n in MAT_FAMILIES:
        for i in range(n):
            mid = "%s-%03d" % (pfx, 100 + i)
            grade = _FORMS_GRADE[_h(mid, "g") % len(_FORMS_GRADE)]
            base = pool[_h(mid, "c") % len(pool)] if pool else ""
            vname = "%s (%s)" % (name, grade)
            out.append((mid, vname, spec, form, base, supp))
    return out


# ------------------------------------------------------------------ programmes
PROGRAMS = [
    ("G700", "Ultra-long-range", "in production"), ("G800", "Ultra-long-range", "in development"),
    ("G650ER", "Long-range", "in production"), ("G600", "Long-range", "in production"),
    ("G500", "Long-range", "in production"), ("G400", "Long-range", "in development"),
    ("G280", "Super-mid-size", "in production"),
]

# ------------------------------------------------------------------ parts (BOM)
_ZONES = [
    ("W", "Wing", ["skin panel", "spar", "rib", "stringer", "leading-edge slat", "flap track", "aileron"]),
    ("F", "Fuselage", ["frame", "skin panel", "bulkhead", "door structure", "window frame", "keel beam"]),
    ("E", "Empennage", ["horizontal stabiliser", "vertical fin", "rudder", "elevator", "trim tab"]),
    ("N", "Nacelle", ["inlet cowl", "fan cowl", "pylon fairing", "thrust reverser", "exhaust nozzle"]),
    ("L", "Landing gear", ["main strut", "drag brace", "axle", "wheel", "brake assembly", "actuator"]),
    ("S", "Systems", ["hydraulic actuator", "fuel manifold", "bleed-air duct", "avionics tray", "EPU"]),
    ("I", "Interior", ["seat track", "galley panel", "sidewall", "overhead bin", "floor beam"]),
]


def parts(mat_ids):
    """Generate a realistic engineering BOM across programmes and zones."""
    out = []
    for prog, _model, _status in PROGRAMS:
        for zc, zname, items in _ZONES:
            for item in items:
                # serialised instances per item per programme
                for seq in range(3 + _h(prog, zc, item) % 10):
                    pn = "%s-%s%04d-%02d" % (prog[:4], zc, 1000 + _h(prog, item, seq) % 9000, seq + 1)
                    mid = mat_ids[_h(pn) % len(mat_ids)]
                    name = "%s %s" % (zname, item)
                    out.append((pn, name, prog, mid))
    return out


# ------------------------------------------------------------------ suppliers
# (name, country, approval, materials, reach_registered, last_audit)
SUPPLIERS = [
    ("PPG Aerospace", "USA", "approved", "primers, sealants, hard-chrome", "yes", "2025-11"),
    ("Henkel", "Germany", "approved", "adhesives, surface treatments", "yes", "2025-09"),
    ("AkzoNobel Aerospace Coatings", "Netherlands", "approved", "topcoats, primers", "yes", "2026-01"),
    ("Solvay", "Belgium", "approved", "composites, prepregs", "yes", "2025-07"),
    ("Hexcel", "USA", "approved", "carbon prepreg, honeycomb", "yes", "2025-10"),
    ("3M Aerospace", "USA", "approved", "adhesives, sealants, plating", "yes", "2025-12"),
    ("Sherwin-Williams Aerospace", "USA", "approved", "coatings, marking paint", "yes", "2026-02"),
    ("Eastman", "USA", "conditional", "solvents, hydraulic fluids", "partial", "2025-06"),
    ("Chemetall", "Germany", "approved", "conversion coatings, cleaners, strippers", "yes", "2025-08"),
    ("Momentive", "USA", "approved", "silicones, sealants, anti-seize", "yes", "2025-05"),
    ("Socomore", "France", "approved", "surface prep, cleaners", "yes", "2025-09"),
    ("Cytec / Solvay", "USA", "approved", "adhesives, resins", "yes", "2025-04"),
    ("Mankiewicz", "Germany", "approved", "coatings", "yes", "2025-10"),
    ("Indestructible Paint", "UK", "approved", "high-temp coatings", "yes", "2025-03"),
    ("Aerocom Specialty", "USA", "conditional", "consumables", "under review", "2025-02"),
    ("Nusil / Avantor", "USA", "approved", "silicones", "yes", "2025-07"),
    ("Lord Corp / Parker", "USA", "approved", "adhesives, coatings", "yes", "2025-11"),
    ("Anticorrosive Metals Ltd", "UK", "conditional", "plating chemistry", "partial", "2024-12"),
    ("Praxair Surface Tech", "USA", "approved", "thermal-spray, plating", "yes", "2025-08"),
    ("Callington Haven", "Australia", "conditional", "cleaners, solvents", "under review", "2025-01"),
    ("Dow", "USA", "approved", "silicones, sealers", "yes", "2025-09"),
    ("Bostik / Arkema", "France", "approved", "sealants, adhesives", "yes", "2025-06"),
    ("Elantas / Altana", "Germany", "approved", "resins, potting", "yes", "2025-05"),
    ("Quaker Houghton", "USA", "conditional", "metalworking fluids", "partial", "2024-11"),
    ("Zip-Chem", "USA", "approved", "corrosion inhibitors, cleaners", "yes", "2025-10"),
    ("MacDermid", "USA", "approved", "plating, surface finishing", "yes", "2025-07"),
    ("Hentzen Coatings", "USA", "approved", "primers, topcoats", "yes", "2025-08"),
    ("PPG Industries (EU)", "France", "approved", "coatings", "yes", "2026-01"),
    ("Everlube / Curtiss-Wright", "USA", "approved", "solid-film lubricants", "yes", "2025-04"),
    ("Kluber Lubrication", "Germany", "approved", "specialty lubricants", "yes", "2025-06"),
    ("Techform / TIODIZE", "USA", "conditional", "anti-galling coatings", "partial", "2025-02"),
    ("Aremco Products", "USA", "conditional", "high-temp adhesives", "under review", "2024-10"),
    ("Aerospace Coatings Intl", "UK", "approved", "coatings", "yes", "2025-09"),
    ("Chemours", "USA", "conditional", "fluoropolymers", "partial", "2024-09"),
    ("BASF Aerospace", "Germany", "approved", "resins, additives", "yes", "2025-11"),
    ("Momentive Quartz", "USA", "approved", "sealers", "yes", "2025-03"),
    ("Poly-Scientific", "USA", "conditional", "consumables", "under review", "2024-12"),
    ("Sika Aerospace", "Switzerland", "approved", "sealants, adhesives", "yes", "2025-10"),
    ("Deft / PPG", "USA", "approved", "primers", "yes", "2025-12"),
    ("Blue Cube / Olin", "USA", "conditional", "epoxy resins", "partial", "2025-01"),
]
SUPPLIER_COLS = ["supplier", "country", "approval_status", "materials_supplied", "reach_registered", "last_audit"]


def suppliers():
    return [tuple(s) for s in SUPPLIERS]


# ------------------------------------------------------------------ SDS library
def sds(mat_rows):
    out = []
    for mid, name, spec, form, base, supp in mat_rows:
        rev = "%d-%02d-%02d" % (2023 + _h(mid) % 3, 1 + _h(mid, "m") % 12, 1 + _h(mid, "d") % 28)
        chem = next((c for c in CHEM_BASE if c[0] == base), None)
        hz = chem[3] if chem else "Not classified as hazardous"
        out.append(("SDS-%s" % mid, name, supp, rev, hz))
    return out


# ------------------------------------------------------------------ compliance
def _deadline(status, cas):
    if status.startswith("Annex XIV"):
        return ["2026-01-21", "2026-09-01", "2027-01-22", "2028-05-01"][_h(cas) % 4]
    return ""


def compliance():
    out = []
    for cas, name, ec, ghs, h, status, fp, oel, svhc, use in CHEM_BASE:
        ref = ("Annex XIV" if "Annex XIV" in status else "Annex XVII" if "Annex XVII" in status
               else "Annex I (POP)" if "POP" in status else "-")
        out.append((cas, cas, "REACH", status, svhc, ref, _deadline(status, cas)))
        if "RoHS" in status or cas in ("7439-92-1", "7440-43-9", "1306-19-0"):
            out.append((cas, cas, "RoHS", "restricted (Pb/Cd)", "no", "Annex II", ""))
        if "POP" in status or "Ozone" in status:
            out.append((cas, cas, "POPs/ODS", status, "yes", "prohibited", ""))
        if "Carc. 1" in ghs:
            out.append((cas, cas, "OSHA / CMR", "carcinogen category 1", svhc, "monitored", ""))
    return out
