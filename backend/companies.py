"""
Aerospace suppliers / manufacturers -- seeded as the `Supplier` object (t_suppliers).
Keeps the seed's interface (COLS / build_rows / BINDINGS) so reset_all is unchanged.
"""

# (name, country, approval, materials, reach_registered, last_audit)
SUPPLIERS = [
    ("PPG Aerospace", "USA", "approved", "primers, sealants, topcoats", "yes", "2025-11"),
    ("Henkel", "Germany", "approved", "adhesives, surface treatments", "yes", "2025-09"),
    ("AkzoNobel Aerospace Coatings", "Netherlands", "approved", "topcoats, primers", "yes", "2026-01"),
    ("Solvay", "Belgium", "approved", "composites, prepregs", "yes", "2025-07"),
    ("Hexcel", "USA", "approved", "carbon prepreg, honeycomb", "yes", "2025-10"),
    ("3M Aerospace", "USA", "approved", "adhesives, tapes, sealants", "yes", "2025-12"),
    ("Sherwin-Williams Aerospace", "USA", "approved", "coatings", "yes", "2026-02"),
    ("Eastman", "USA", "conditional", "solvents, hydraulic fluids", "partial", "2025-06"),
    ("Chemetall", "Germany", "approved", "conversion coatings, cleaners", "yes", "2025-08"),
    ("Momentive", "USA", "approved", "silicones, sealants", "yes", "2025-05"),
]

COLS = ["supplier", "country", "approval_status", "materials_supplied", "reach_registered", "last_audit"]


def build_rows():
    return [tuple(s) for s in SUPPLIERS]


# object_property, source_table, source_col, transform
BINDINGS = [
    ("Supplier.name", "t_suppliers", "supplier", "-"),
    ("Supplier.country", "t_suppliers", "country", "-"),
    ("Supplier.approval_status", "t_suppliers", "approval_status", "-"),
]
