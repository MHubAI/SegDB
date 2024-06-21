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
import pandas as pd
from typing import Optional

class Triplet:

    _custom_triplets = {}
    # code: str
    # scheme_designator: str
    # meaning: str
    
    @classmethod
    def _getLookupTable(cls, id: str) -> pd.DataFrame:
        
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

        return lookup_db

    def __init__(self, id: str) -> None:
        
        # check if custom triplet    
        if id in self._custom_triplets:
            # load custom triplet
            data = self._custom_triplets[id]
        else:       
            # get loopup table
            lookup_db = self._getLookupTable(id)

            # lookup by id
            data = lookup_db.loc[id]

        # assign properties
        self.id = id
        self.code = str(data['CodeValue'])
        self.scheme_designator = str(data['CodingSchemeDesignator'])
        self.meaning = str(data['CodeMeaning'])

    @classmethod
    def register(cls, id: str, code: str = "", meaning: Optional[str] = None, scheme_designator: str = "99SEGDB",  overwrite: bool = False):
        #('SADC123','99SMITH','Smith Diffusion Model')
        if id in cls._custom_triplets and not overwrite:
            raise ValueError(f"Triplet with id '{id}' already exists.")
        
        if meaning is None:
            meaning = id

        cls._custom_triplets[id] = {
            'id': id,
            "CodeValue": code,
            "CodingSchemeDesignator": scheme_designator,
            "CodeMeaning": meaning
        }

    @classmethod
    def getByCode(cls, code: str, coding_scheme_designator: str = "SCT") -> 'Triplet':
        triplet = cls.findByCode(code, coding_scheme_designator)
        if triplet is None:
            raise ValueError(f"Triplet with code '{code}' and coding scheme designator '{coding_scheme_designator}' not found.")
        return triplet

    @classmethod
    def findByCode(cls, code: str, coding_scheme_designator: str = "SCT") -> Optional['Triplet']:
        
        # look into each table for code and coding scheme designator
        for table in [db.types, db.categories, db.modifiers]:
            for id, row in table.iterrows():
                if row['CodeValue'] == code and row['CodingSchemeDesignator'] == coding_scheme_designator:
                    return cls(str(id))
                
        raise ValueError(f"Triplet with code '{code}' and coding scheme designator '{coding_scheme_designator}' not found.")
        

    def __str__(self) -> str:
        return f"{self.id}:{self.scheme_designator}:{self.code}:{self.meaning}"
    
    
Triplet.register("UNKNOWN", code="UNKNOWN")