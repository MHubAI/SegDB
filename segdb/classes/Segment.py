"""
-------------------------------------------------
SegDB - Segment class
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from typing import Optional, List, Union
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
    segmented_property_name: str
    anatomic_region_type_id: Optional[str]
    anatomic_region_modifyer_id: Optional[str]
    anatomic_region_name: Optional[str]
    
    # meta
    color: Optional[str]

    @classmethod
    def getByID(cls, id: str) -> 'Segment':
        return Segment(id)
    
    @classmethod
    def getByName(cls, name: str) -> 'Segment':
        """Get a segment by its name. Raises a ValueError if no segment is found.

        Args:
            name (str): The name of the segment to look up.

        Raises:
            ValueError: If no segment with the given name is found.

        Returns:
            Segment: The segment with the given name.
        """
        
        seg = cls.findByName(name, exact_match=True)
                
        if seg is None:
            raise ValueError(f"No segment with name '{name}' found")
        
        if len(seg) > 1:
            raise ValueError(f"Multiple segments with name '{name}' found")
        
        return seg[0]
    
    @classmethod
    def findByName(cls, name: str, exact_match: bool = False, regex: bool = False, reflags: int = 0) -> Optional[List['Segment']]:
        """Returns a segment or a list of segments by name.
        
        Args:
            name (str): The name of the segment to look up.
            exact_match (bool): If true, only segments with the exact name are returned. If false, all segments containing the name are returned.
            regex (bool): If true, the name is treated as a regular expression.
            reflags (int): Flags for the regular expression search, e.g. re.IGNORECASE.
        
        Raises:
            ValueError: If multiple segments with the same name are found but exact match is requested

        Returns:
            Optional[Union[List['Segment'], 'Segment']]: A segment or a list of segments if exact_match is set to false. None if no segment is found.
        """

        # lookup
        if exact_match:
            f = db.segmentations['name'] == name
            
        elif not regex:
            f = db.segmentations['name'].str.contains(name, case=False)
            
        else:
            f = db.segmentations['name'].str.contains(name, regex=True, flags=reflags)
            
        # sanity check (name must be unique)
        if exact_match and f.sum() > 1:
            raise ValueError(f"Multiple segments with name '{name}' found")
        
        # return
        if f.sum() == 0:
            return None
        
        else:
            return [Segment(i) for i in db.segmentations[f].index]
        
    @classmethod
    def getByTriplets(cls, category: Triplet, anatomic_region: Triplet, modifier: Optional[Triplet] = None) -> 'Segment':
        
        # perform search
        segs = cls.findByTriplets(category, anatomic_region, modifier)
        
        # expext exactly one segment to be found by given triplets
        if segs is None:
            raise ValueError(f"No segment found for triplets: {category}, {anatomic_region}, {modifier}")
        
        if len(segs) > 1:
            raise ValueError(f"Multiple segments found for triplets: {category}, {anatomic_region}, {modifier}")
        
        return segs[0]
    
    @classmethod
    def findByTriplets(cls, category: Optional[Union[Triplet, str]] = None, type: Optional[Union[Triplet, str]] = None, modifier: Optional[Union[Triplet, str]] = None) -> Optional[List['Segment']]:
        
        # resolve triplets
        if isinstance(category, str):
            category = Triplet(category)
            
        if isinstance(type, str):
            type = Triplet(type)
            
        if isinstance(modifier, str):
            modifier = Triplet(modifier)
        
        # filter
        f = db.segmentations['category'] == category.id if category is not None else True
        f &= db.segmentations['anatomic_region'] == type.id if type is not None else True
        f &= db.segmentations['modifier'] == modifier.id if modifier is not None else True
        
        # apply filter
        q = db.segmentations[f].copy()
        
        # check if any segment is found
        if len(q) == 0:
            return None
        
        # return
        return [Segment(i) for i in db.segmentations[f].index]

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
        
        def ostr(s) -> Optional[str]:
            return None if s is None else str(s)

        # https://qiicr.gitbook.io/dcmqi-guide/opening/coding_schemes/existing_dicom_code
        #   if no segment property is given explicitly, we place the anatomical region code in the 
        #   segment property type as explained under the document above
        if sp is None:
            self.segmented_property_category_id = str(ar["category"])
            self.segmented_property_type_id = str(ar["anatomic_region"])
            self.segmented_property_modifyer_id = ostr(ar["modifier"])
            self.segmented_property_name = str(ar["name"])
            self.anatomic_region_type_id = None
            self.anatomic_region_modifyer_id = None
            self.anatomic_region_name = None
            self.color = ostr(ar["color"]) 
        else:
            self.segmented_property_category_id = str(sp["category"])
            self.segmented_property_type_id = str(sp["anatomic_region"])
            self.segmented_property_modifyer_id = ostr(sp["modifier"])
            self.segmented_property_name = str(sp["name"])
            self.anatomic_region_type_id = ostr(ar["anatomic_region"])
            self.anatomic_region_modifyer_id = ostr(ar["modifier"])
            self.anatomic_region_name = str(ar["name"])            
            self.color = ostr(sp["color"])

    @property
    def name(self) -> str:
        if self.segmented_property_id is not None:
            assert self.anatomic_region_name is not None
            return self.segmented_property_name + ' in ' + self.anatomic_region_name
        else:
            return self.segmented_property_name
        
    def specifyAnatomicRegion(self, anatomic_region: 'Segment'):
        """Specify the anatomic region of a segment. 

        Args:
            anatomic_region (Segment): A segment (e.g. <Anatomic-Region>+<This-Segment>)
        """

        self.id = anatomic_region.anatomic_region_id + '+' + self.anatomic_region_id
        self.segmented_property_id = self.anatomic_region_id
        self.anatomic_region_id = anatomic_region.anatomic_region_id
        self.anatomic_region_type_id = anatomic_region.anatomic_region_type_id if anatomic_region.anatomic_region_type_id is not None else anatomic_region.segmented_property_type_id
        self.anatomic_region_modifyer_id = anatomic_region.anatomic_region_modifyer_id if anatomic_region.anatomic_region_modifyer_id is not None else anatomic_region.segmented_property_modifyer_id
        self.anatomic_region_name = anatomic_region.anatomic_region_name if anatomic_region.anatomic_region_name is not None else anatomic_region.segmented_property_name
    
    def specifySegmentedProperty(self, segmented_property: 'Segment'):
        """Specify the segmented property of a segment. 
        This will take the 

        Args:
            segmented_property (Segment): A segment (e.g. <This-Segment>+<Segmented-Property>)
        """

        self.id = self.anatomic_region_id + '+' + (segmented_property.anatomic_region_id if segmented_property.anatomic_region_id is not None else segmented_property.segmented_property_id)
        self.segmented_property_id = segmented_property.id
        self.anatomic_region_type_id = self.segmented_property_type_id
        self.anatomic_region_modifyer_id = self.segmented_property_modifyer_id
        self.anatomic_region_name = self.segmented_property_name
        self.segmented_property_category_id = segmented_property.segmented_property_category_id
        self.segmented_property_type_id = segmented_property.segmented_property_type_id
        self.segmented_property_modifyer_id = segmented_property.segmented_property_modifyer_id
        self.segmented_property_name = segmented_property.segmented_property_name
        self.color = segmented_property.color

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

    @classmethod
    def fromJSON(cls, json: dict) -> 'Segment':
        
        segmented_property_category_code = int(json['SegmentedPropertyCategoryCodeSequence']['CodeValue'])
        segmented_property_category_scheme = json['SegmentedPropertyCategoryCodeSequence']['CodingSchemeDesignator']
        segmented_property_category_triplet = Triplet.getByCode(segmented_property_category_code, segmented_property_category_scheme)
        
        segmented_property_type_code = int(json['SegmentedPropertyTypeCodeSequence']['CodeValue'])
        segmented_property_type_scheme = json['SegmentedPropertyTypeCodeSequence']['CodingSchemeDesignator']
        segmented_property_type_triplet = Triplet.getByCode(segmented_property_type_code, segmented_property_type_scheme)
        
        if segmented_property_modifier := json.get('SegmentedPropertyTypeModifierCodeSequence', None):
            segmented_property_modifier_code = int(segmented_property_modifier['CodeValue'] )
            segmented_property_modifier_scheme = segmented_property_modifier['CodingSchemeDesignator'] 
            segmented_property_modifier_tiplet = Triplet.getByCode(segmented_property_modifier_code, segmented_property_modifier_scheme) 
        else:
            segmented_property_modifier_tiplet = None
        
        if anatomic_region_type := json.get('AnatomicRegionSequence', None):
            anatomic_region_type_code = int(anatomic_region_type['CodeValue'])
            anatomic_region_type_scheme = anatomic_region_type['CodingSchemeDesignator']
            anatomic_region_type_tiplet = Triplet.getByCode(anatomic_region_type_code, anatomic_region_type_scheme)
        else:
            anatomic_region_type_tiplet = None
            
        if anatomic_region_modifier := json.get('AnatomicRegionModifierSequence', None):
            anatomic_region_modifier_code = int(anatomic_region_modifier['CodeValue'])
            anatomic_region_modifier_scheme = anatomic_region_modifier['CodingSchemeDesignator']
            anatomic_region_modifier_tiplet = Triplet.getByCode(anatomic_region_modifier_code, anatomic_region_modifier_scheme)
        else:
            anatomic_region_modifier_tiplet = None
            
        # create segment
        segment = Segment.getByTriplets(segmented_property_category_triplet, segmented_property_type_triplet, segmented_property_modifier_tiplet)
        
        # if anatomic region is specified, extract a segment from it
        if anatomic_region_type_tiplet is not None:
            ar_segments = Segment.findByTriplets(None, anatomic_region_type_tiplet, anatomic_region_modifier_tiplet)
            assert ar_segments is not None, "anatomic region not found"
            assert len(ar_segments) == 1, "anatomical region is unambiguous"
            segment.specifyAnatomicRegion(ar_segments[0])
        
        # return segment
        return segment        

    def __str__(self) -> str:
        return self.id