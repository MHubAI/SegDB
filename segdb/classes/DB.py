"""
-------------------------------------------------
SegDB - Database class and singleton
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

import os, pandas as pd

# global ressource path (./data)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

class DB:

    categories: pd.DataFrame
    types: pd.DataFrame
    modifiers: pd.DataFrame
    segmentations: pd.DataFrame

    def __init__(self) -> None:

        # load ressources
        self.categories = pd.read_csv(os.path.join(DATA_DIR, 'categories.csv')).set_index('id')
        self.types = pd.read_csv(os.path.join(DATA_DIR, 'types.csv')).set_index('id')
        self.modifiers = pd.read_csv(os.path.join(DATA_DIR, 'modifiers.csv')).set_index('id')
        self.segmentations = pd.read_csv(os.path.join(DATA_DIR, 'segmentations.csv')).set_index('id') 

# global db singleton
db = DB()