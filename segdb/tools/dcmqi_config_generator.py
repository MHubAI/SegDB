"""
-------------------------------------------------
SegDB - Generator for dcmqi config files
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""


from typing import List, Optional
from ..classes.Segment import Segment
import os, json

class Item:

    file: str
    segment_ids: List[str]
    model_name: str

    malformed_segment_ids: Optional[List[str]] = None

    def __init__(self, file: str, segments_ids: List[str], model_name: str) -> None:
        self.file = file
        self.segment_ids = segments_ids
        self.model_name = model_name

    def validate(self) -> bool:
        if self.malformed_segment_ids is None:
            self.malformed_segment_ids = []
            for segment_id in self.segment_ids:
                try:
                    Segment(segment_id)
                except Exception as e:
                    self.malformed_segment_ids.append(segment_id)
        return len(self.malformed_segment_ids) == 0


class DcmqiDsegConfigGenerator:
    
    items: List[Item]
    item_fchk: List[str]

    model_name: str = 'MODEL NAME'
    body_part_examined: str = 'WHOLEBODY'

    def __init__(self, model_name: str, body_part_examined: str) -> None:
        self.items = []
        self.item_fchk = []
        self.model_name = model_name
        self.body_part_examined = body_part_examined

    def addItem(self, file: str, segment_ids: List[str], model_name: str, validate: bool = True):
        item = Item(file, segment_ids, model_name)

        if validate and not item.validate():
            raise Exception("Invalid segment ids: " + ', '.join(item.malformed_segment_ids or []))

        fchk = str(hash(file))
        if fchk in self.item_fchk:
            raise Exception("Duplicate file name: " + file)
        
        self.items.append(item)
        self.item_fchk.append(fchk)

    def generate(self):
        
        # header data
        json_meta = {
            'BodyPartExamined': self.body_part_examined,
            'ClinicalTrialCoordinatingCenterName': 'dcmqi',
            'ClinicalTrialSeriesID': '0',
            'ClinicalTrialTimePointID': '1',
            'ContentCreatorName': 'MHub',
            'ContentDescription': 'Image segmentation',
            'ContentLabel': 'SEGMENTATION',
            'InstanceNumber': '1',
            'SeriesDescription': self.model_name,
            'SeriesNumber': '42',
            'segmentAttributes': []
        }

        # segment attributes
        for item in self.items:
            item_segments_json = []
            for labelID, segment_id in enumerate(item.segment_ids):
                segment = Segment(segment_id)
                segment_json = segment.asJSON(
                    labelID = labelID + 1, 
                    algorithm_name = item.model_name or self.model_name
                )
                item_segments_json.append(segment_json)
            json_meta['segmentAttributes'].append(item_segments_json)

        # return json
        return json_meta
    
    def getFileList(self) -> List[str]:
        return [item.file for item in self.items]
    
    def save(self, config_file: str, overwrite: bool = False):
        if os.path.exists(config_file) and not overwrite:
            raise Exception("File already exists: " + config_file)
        
        with open(config_file, 'w') as f:
            json.dump(self.generate(), f, indent=4)

