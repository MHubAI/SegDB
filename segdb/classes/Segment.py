"""
-------------------------------------------------
SegDB - Segment class
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from typing import Optional
from .DB import db
from .Triplet import Triplet
from .Color import Color
import pandas as pd

class Segment:

    # segment id
    id: str
    anatomic_region_id: str
    segmented_property_id: Optional[str]

    # triplet id
    segmented_property_category_id: str
    segmented_property_type_id: str
    segmented_property_modifyer_id: Optional[str]
    anatomic_region_type_id: Optional[str]
    anatomic_region_modifyer_id: Optional[str]

    # meta
    color: Optional[str]
    name: str


    def __init__(self, id: str) -> None:

        # solit id
        self.id = id
        id_split = id.split("+")
        self.anatomic_region_id = id_split[0]
        self.segmented_property_id = id_split[1] if len(id_split) > 1 else None

        # lookup
        ar = db.segmentations.loc[self.anatomic_region_id]
        sp = db.segmentations.loc[self.segmented_property_id] if self.segmented_property_id is not None else None

        # replace NaN with None
        ar = ar.where(pd.notnull(ar), None)
        sp = sp.where(pd.notnull(sp), None) if sp is not None else None

        # https://qiicr.gitbook.io/dcmqi-guide/opening/coding_schemes/existing_dicom_code
        #   if no segment property is given explicitly, we place the anatomical region code in the 
        #   segment property type as explained under the document above
        if sp is None:
            self.segmented_property_category_id = ar["category"]
            self.segmented_property_type_id = ar["anatomic_region"]
            self.segmented_property_modifyer_id = ar["modifier"]
            self.anatomic_region_type_id = None
            self.anatomic_region_modifyer_id = None
            self.color = ar["color"]
            self.name = ar["name"]
        else:
            self.segmented_property_category_id = sp["category"]
            self.segmented_property_type_id = sp["anatomic_region"]
            self.segmented_property_modifyer_id = sp["modifier"] 
            self.anatomic_region_type_id = ar["anatomic_region"]
            self.anatomic_region_modifyer_id = ar["modifier"] 
            self.name = sp["name"] + ' in ' + ar["name"]
            self.color = sp["color"]

    def getID(self) -> str:
        return self.id
    
    def getName(self) -> str:
        return self.name

    def getColor(self) -> Optional['Color']:
        try:
            assert self.color is not None
            rgb = self.color.split(",")
            assert len(rgb) == 3
        except:
            return None

        return Color(*map(int, rgb))

    def getAnatomicRegionID(self) -> str:
        return self.anatomic_region_id
    
    def getSegmentedPropertyID(self) -> Optional[str]:
        return self.segmented_property_id

    def getSegmentedPropertyCategory(self) -> Triplet:
        return Triplet(self.segmented_property_category_id)

    def getSegmentedPropertyType(self) -> Triplet:
        return Triplet(self.segmented_property_type_id)

    def getSegmentedPropertyModifyer(self) -> Optional[Triplet]:
        if self.segmented_property_modifyer_id is None:
            return None
        return Triplet(self.segmented_property_modifyer_id)
    
    def getAnatomicRegionSequence(self) -> Optional[Triplet]:
        if self.anatomic_region_type_id is None:
            return None
        return Triplet(self.anatomic_region_type_id)
    
    def getAnatomicRegionModifierSequence(self) -> Optional[Triplet]:
        if self.anatomic_region_modifyer_id is None:
            return None
        return Triplet(self.anatomic_region_modifyer_id)

    def print(self):
        print("Segment ID........................... ", self.id)
        print("Segment Name......................... ", self.name)
        print("Segment Color........................ ", self.color)
        print("Anatomic Region ID................... ", self.anatomic_region_id)
        print("Segmented Property ID................ ", str(self.segmented_property_id))
        print("Segmented Property Category.......... ", str(self.getSegmentedPropertyCategory()))
        print("Segmented Property Type.............. ", str(self.getSegmentedPropertyType()))
        print("Segmented Property Modifyer.......... ", str(self.getSegmentedPropertyModifyer()))
        print("Anatomic Region Sequence............. ", str(self.getAnatomicRegionSequence()))
        print("Anatomic Region Modifier Sequence.... ", str(self.getAnatomicRegionModifierSequence()))

    def asJSON(self, labelID: int = 1, algorithm_name: str = ''):
                    
        # mandatory
        json = {
            'labelID': labelID,
            'SegmentDescription': self.getName(),
            'SegmentAlgorithmType': 'AUTOMATIC',
            'SegmentAlgorithmName': algorithm_name,
            'SegmentedPropertyCategoryCodeSequence': {
                'CodeValue': self.getSegmentedPropertyCategory().code,
                'CodingSchemeDesignator': self.getSegmentedPropertyCategory().scheme_designator,
                'CodeMeaning': self.getSegmentedPropertyCategory().meaning
            },
            'SegmentedPropertyTypeCodeSequence': {
                'CodeValue': self.getSegmentedPropertyType().code,
                'CodingSchemeDesignator': self.getSegmentedPropertyType().scheme_designator,
                'CodeMeaning': self.getSegmentedPropertyType().meaning
            }
        }

        if modifier := self.getSegmentedPropertyModifyer():
            json['SegmentedPropertyTypeModifierCodeSequence'] = {
                'CodeValue': modifier.code,
                'CodingSchemeDesignator': modifier.scheme_designator,
                'CodeMeaning': modifier.meaning
            }

        if anatomic_region := self.getAnatomicRegionSequence():
            json['AnatomicRegionSequence'] = {
                'CodeValue': anatomic_region.code,
                'CodingSchemeDesignator': anatomic_region.scheme_designator,
                'CodeMeaning': anatomic_region.meaning
            }

        if modifier := self.getAnatomicRegionModifierSequence():
            json['AnatomicRegionModifierSequence'] = {
                'CodeValue': modifier.code,
                'CodingSchemeDesignator': modifier.scheme_designator,
                'CodeMeaning': modifier.meaning
            }


        if color := self.getColor():
            json['recommendedDisplayRGBValue'] = color.getComponents()
            
        # return
        return json

    def __str__(self) -> str:
        return self.id