"""
-------------------------------------------------
SegDB - Lookup script to search for segmentations
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from typing import List
from enum import Enum
from .classes.DB import db
import sys, re
import pandas as pd

class QConcatType(Enum):
    AND = 1
    OR = 2

class f(str, Enum):
    chead       = '\033[95m'
    cyan        = '\033[96m'
    cgray       = '\033[30m'
    cyellow     = '\033[93m'    
    cend        = '\033[0m'
    fitalics    = '\x1B[3m'
    funderline  = '\x1B[4m'
    fnormal     = '\x1B[0m'
    fbold       = '\x1B[1m'

def search_segment_by_keywords(kwds: List[str], qct: QConcatType = QConcatType.AND) -> pd.DataFrame:

    df = db.segmentations

    f = None
    for kw in kwds:
        if f is None:
            f = df["name"].str.contains(kw, flags=re.IGNORECASE)
        elif qct == QConcatType.AND:
            f = f & df["name"].str.contains(kw, flags=re.IGNORECASE)
        elif qct == QConcatType.OR:
            f = f | df["name"].str.contains(kw, flags=re.IGNORECASE)

    assert f is not None, "Provide at least one keyword"
    return db.segmentations[f].copy()

def print_df(df: pd.DataFrame):
    print(f"\n{f.chead+f.fbold}Found {len(df)} segmentations.{f.cend}\n")

    if len(df) == 0:
        return

    def style_id(id):
        return f"{f.cyellow+f.fbold}{id}{f.cend}"
    
    df.reset_index(inplace=True)
    df['id'] = df['id'].apply(style_id)
    df.rename(columns={'id': style_id('ID')}, inplace=True)

    pd.set_option("display.colheader_justify", "left")
    print(df)


if __name__ == "__main__":

    # extract keywords from command line
    kwds = [kw for kw in sys.argv[1:] if not kw.startswith('--')]
    qct = QConcatType.AND if '--or' not in sys.argv else QConcatType.OR
    
    # search
    df = search_segment_by_keywords(kwds, qct)

    # print results
    print_df(df)