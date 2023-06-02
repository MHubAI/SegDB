"""
-------------------------------------------------
SegDB - Code Sequence Triplet class
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""


from .DB import db

class Triplet:

    code: str
    scheme_designator: str
    meaning: str

    def __init__(self, id: str) -> None:
        
        # id prefix
        id_prefix = id.split("_")[0]

        # select lookup table
        lookup_db = None
        if id_prefix == "T":
            lookup_db = db.types
        elif id_prefix == "C":
            lookup_db = db.categories
        elif id_prefix == "M":
            lookup_db = db.modifiers
        else:
            raise ValueError(f"Unknown triplet id prefix: {id_prefix}")

        # lookup by id
        data = lookup_db.loc[id]

        # assign properties
        self.id = id
        self.code = str(data['CodeValue'])
        self.scheme_designator = str(data['CodingSchemeDesignator'])
        self.meaning = str(data['CodeMeaning'])


    def __str__(self) -> str:
        return f"{self.id}:{self.scheme_designator}:{self.code}:{self.meaning}"
    