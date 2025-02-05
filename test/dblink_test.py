import unittest
import pandas as pd
import os

class DBLinkTest(unittest.TestCase):

    def setUp(self):

        # print current path
        print("Tets started from wd: ", os.getcwd())

        # load all files
        self.categories_df = pd.read_csv('segdb/data/categories.csv')
        self.modifiers_df = pd.read_csv('segdb/data/modifiers.csv')
        self.segmentations_df = pd.read_csv('segdb/data/segmentations.csv')
        self.types_df = pd.read_csv('segdb/data/types.csv')

    def test_dblink(self):

        # iterate all rows from segmentations that have the following columns id,name,category,anatomic_region,modifier,color
        for index, row in self.segmentations_df.iterrows():
            # check if the value in category is in categories
            if row['category'] not in self.categories_df['id'].values:
                raise ValueError(f"Category {row['category']} not found in categories")
            # check if the value in anatomic_region is in types
            if row['anatomic_region'] not in self.types_df['id'].values:
                raise ValueError(f"Type {row['anatomic_region']} not found in types")
            
            # check if the value in modifier is in modifiers if it's not nan
            if not pd.isna(row['modifier']) and row['modifier'] not in self.modifiers_df['id'].values:
                raise ValueError(f"Modifier {row['modifier']} not found in modifiers")
            
            # check if color is set
            if pd.isna(row['color']):
                raise ValueError("Color not set")


    def test_unique_id(self):
        
        # check that id is unique in all tables
        if self.segmentations_df['id'].duplicated().any():
            d = self.segmentations_df[self.segmentations_df['id'].duplicated()]['id'].iloc[0]
            raise ValueError(f"Duplicate id '{d}' found in segmentations.")
        
        if self.categories_df['id'].duplicated().any():
            d = self.categories_df[self.categories_df['id'].duplicated()]['id'].iloc[0]
            raise ValueError(f"Duplicate id '{d}' found in categories.")
        
        if self.modifiers_df['id'].duplicated().any():
            d = self.modifiers_df[self.modifiers_df['id'].duplicated()]['id'].iloc[0]
            raise ValueError(f"Duplicate id '{d}' found in modifiers.")
        
        if self.types_df['id'].duplicated().any():
            d = self.types_df[self.types_df['id'].duplicated()]['id'].iloc[0]
            raise ValueError(f"Duplicate id '{d}' found in types.")
        
    def test_unique_name(self):

        # check that name is unique in all tables
        if self.segmentations_df['name'].duplicated().any():
            d = self.segmentations_df[self.segmentations_df['name'].duplicated()]['name'].iloc[0]
            raise ValueError(f"Duplicate name '{d}' found")
        
    def test_report_shared_colors(self):
        # NOTE: colores are not unique but must only be shared for structures belonging to the same group 
        # (e.g. left and right kidney should share the same color in the default colot scheme.)

        # print a list of all structures sharing the same color grouped by color 
        for color, structures in self.segmentations_df.groupby('color')['name'].apply(list).items():
            if len(structures) > 1:
                print(f"Structures with color {color}: {structures}")
        
        # check color is set unique in segmentations
        # if self.segmentations_df['color'].duplicated().any():
        #    raise ValueError("Duplicate color found")

    def test_unique_code(self):

        # check CodeValue is unique in types, categories and modifiers and print out the duplicate value
        if self.types_df['CodeValue'].duplicated().any():
            d = self.types_df[self.types_df['CodeValue'].duplicated()]['CodeValue'].iloc[0]
            raise ValueError(f"Duplicate CodeValue '{d}' found in types")
        
        if self.categories_df['CodeValue'].duplicated().any():
            d = self.categories_df[self.categories_df['CodeValue'].duplicated()]['CodeValue'].iloc[0]
            raise ValueError(f"Duplicate CodeValue '{d}' found in categories")
        
        if self.modifiers_df['CodeValue'].duplicated().any():
            d = self.modifiers_df[self.modifiers_df['CodeValue'].duplicated()]['CodeValue'].iloc[0]
            raise ValueError(f"Duplicate CodeValue '{d}' found in modifiers")
        

