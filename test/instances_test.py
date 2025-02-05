import unittest
from segdb.classes.Segment import Segment, Triplet
import copy

class DBLinkTest(unittest.TestCase):

    def test_segemnt(self):

        # test a coronary calcification segment
        print("\n\nCoronary Calcification")
        Segment("CORONARY_ARTERY+PATHOLOGIC_CALCIFICATION").print()

        # test the prostate
        print("\n\nProstate")
        Segment("PROSTATE").print()

        # test a kidney tumor
        print("\n\nKidney Tumor")
        Segment("LEFT_KIDNEY+NEOPLASM_MALIGNANT_PRIMARY").print()

    def test_set_segment_anatomic_region(self):
        
        # instantiate a segment
        seg_ar = Segment("CORONARY_ARTERY")
        seg_prop = Segment("PATHOLOGIC_CALCIFICATION")
        
        print("\n\nCoronary Artery")
        seg_ar.print()
        
        print("\n\nPathologic Calcification")
        seg_prop.print()
        
        # set the anatomic region
        seg_ctx0 = Segment("CORONARY_ARTERY+PATHOLOGIC_CALCIFICATION")
        seg_ctx1 = copy.deepcopy(seg_prop)
        seg_ctx2 = copy.deepcopy(seg_ar)
        seg_ctx1.specifyAnatomicRegion(seg_ar)
        seg_ctx2.specifySegmentedProperty(seg_prop)
        
        # print the segment
        print("\n\nCoronary Artery + Pathologic Calcification")
        seg_ctx0.print()
        print("---")
        seg_ctx1.print()
        print("---")
        seg_ctx2.print()
        
        print("====")
        
        print(seg_ctx0.asJSON())
        print("---")
        print(seg_ctx1.asJSON())
        print("---")
        print(seg_ctx2.asJSON())
        
        
        # assert all are equal
        self.assertDictEqual(seg_ctx0.asJSON(), seg_ctx1.asJSON())
        self.assertDictEqual(seg_ctx0.asJSON(), seg_ctx2.asJSON())

        ##### test with modifyer
        
        seg = Segment("LEFT_KIDNEY")
        seg.specifySegmentedProperty(Segment("NEOPLASM_MALIGNANT_PRIMARY"))
        self.assertDictEqual(seg.asJSON(), Segment("LEFT_KIDNEY+NEOPLASM_MALIGNANT_PRIMARY").asJSON())
        
        seg = Segment("NEOPLASM_MALIGNANT_PRIMARY")
        seg.specifyAnatomicRegion(Segment("LEFT_KIDNEY"))
        self.assertDictEqual(seg.asJSON(), Segment("LEFT_KIDNEY+NEOPLASM_MALIGNANT_PRIMARY").asJSON())

        ###### test with modifyer on both (this example makes no sense only technically)
        seg = Segment("LEFT_KIDNEY")
        seg.specifySegmentedProperty(Segment("RIGHT_SCAPULA"))
        self.assertDictEqual(seg.asJSON(), Segment("LEFT_KIDNEY+RIGHT_SCAPULA").asJSON())
        
        seg = Segment("LEFT_KIDNEY")
        seg.specifyAnatomicRegion(Segment("RIGHT_SCAPULA"))
        self.assertDictEqual(seg.asJSON(), Segment("RIGHT_SCAPULA+LEFT_KIDNEY").asJSON())


    def test_segment_json_output(self):
        
        # test a coronary calcification segment
        print("\n\nCoronary Calcification")
        json = Segment("CORONARY_ARTERY+PATHOLOGIC_CALCIFICATION").asJSON()
        print(json)
        self.assertDictEqual(json, {'labelID': 1, 'SegmentDescription': 'Pathologic calcification in Coronary Artery', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '49755003', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Morphologically abnormal structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '18115005', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Pathologic calcification, calcified structure (morphologic abnormality)'}, 'AnatomicRegionSequence': {'CodeValue': '41801008', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Coronary artery structure (body structure)'}, 'recommendedDisplayRGBValue': [255, 255, 255]})

        # test the prostate
        print("\n\nProstate")
        json = Segment("PROSTATE").asJSON()
        print(json)
        self.assertDictEqual(json, {'labelID': 1, 'SegmentDescription': 'Prostate', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '123037004', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Body structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '41216001', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Prostatic structure'}, 'recommendedDisplayRGBValue': [230, 158, 140]})

        # test a kidney tumor
        print("\n\nKidney Tumor")
        json = Segment("LEFT_KIDNEY+NEOPLASM_MALIGNANT_PRIMARY").asJSON()
        print(json)
        self.assertDictEqual(json, {'labelID': 1, 'SegmentDescription': 'Primary malignant neoplasm in Left kidney', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '49755003', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Morphologically abnormal structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '86049000', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Malignant neoplasm, primary (morphologic abnormality)'}, 'AnatomicRegionSequence': {'CodeValue': '64033007', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Kidney structure'}, 'AnatomicRegionModifierSequence': {'CodeValue': '7771000', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Left'}, 'recommendedDisplayRGBValue': [255, 0, 0]})
        

    def test_segment_lookup_by_name(self):
        
        # find a segment by exact name
        print("\n\nFind by exact name")
        seg = Segment.getByName("Prostate")
        self.assertIsNotNone(seg)
        self.assertIsInstance(seg, Segment)
        assert seg is not None and isinstance(seg, Segment)
        seg.print()
        
        # find segments containing the name
        print("\n\nFind by name containing")
        segs = Segment.findByName("Kidney", exact_match=False)
        self.assertIsNotNone(segs)
        self.assertIsInstance(segs, list)
        assert segs is not None and isinstance(segs, list)
        self.assertEqual(len(segs), 3)
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
        # find segments by regular expression
        print("\n\nFind by regular expression")
        segs = Segment.findByName(".*ili.*", exact_match=False, regex=True)
        self.assertIsNotNone(segs)
        self.assertIsInstance(segs, list)
        assert segs is not None and isinstance(segs, list)
        self.assertEqual(len(segs), 6)
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
        # find segments by regular expression
        print("\n\nFind by regular expression")
        segs = Segment.findByName(".*rib\\s[1,3]+$", exact_match=False, regex=True)
        self.assertIsNotNone(segs)
        self.assertIsInstance(segs, list)
        assert segs is not None and isinstance(segs, list)
        self.assertEqual(len(segs), 6)
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
    def test_segment_lookup_by_triplet(self):
        
        # define triplets
        category = Triplet("C_BODY_STRUCTURE")
        anatomic_region = Triplet("T_AORTIC_STRUCTURE")
        mofiier = None
        
        # lookup
        segs = Segment.findByTriplets(category, anatomic_region, mofiier)
        
        self.assertIsNotNone(segs)
        assert segs is not None
        self.assertEqual(len(segs), 1)
        
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
        # lookup 2
        segs = Segment.findByTriplets(type='T_ADRENAL_STRUCTURE')
        
        self.assertIsNotNone(segs)
        assert segs is not None
        self.assertEqual(len(segs), 2)
        
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
            
        # lookup 3
        segs = Segment.findByTriplets(category='C_BODY_STRUCTURE', modifier='M_LEFT')
        
        self.assertIsNotNone(segs)
        assert segs is not None
        self.assertEqual(len(segs), 13)
        
        for i, seg in enumerate(segs):
            print(f"-- Segment {i+1}({len(segs)}) -----------------")
            seg.print()
            
         # lookup 4
        t1 = Triplet("C_BODY_STRUCTURE")
        t2 = Triplet.getByCode('123037004')
        self.assertEqual(t1.id, t2.id)
        
    def test_segment_from_json(self):
        
        json_data = {'labelID': 1, 'SegmentDescription': 'Pathologic calcification in Coronary Artery', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '49755003', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Morphologically abnormal structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '18115005', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Pathologic calcification, calcified structure (morphologic abnormality)'}, 'AnatomicRegionSequence': {'CodeValue': '41801008', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Coronary artery structure (body structure)'}, 'recommendedDisplayRGBValue': [255, 255, 255]}
        
        seg1 = Segment.fromJSON(json_data)
        seg2 = Segment("CORONARY_ARTERY+PATHOLOGIC_CALCIFICATION")
        
        self.assertDictEqual(seg1.asJSON(), seg2.asJSON())
        
        ###
        
        json_data = {'labelID': 1, 'SegmentDescription': 'Left kidney', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '123037004', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Body structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '64033007', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Kidney structure'}, 'SegmentedPropertyTypeModifierCodeSequence': {'CodeValue': '7771000', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Left'}, 'recommendedDisplayRGBValue': [212, 126, 151]}
        seg1 = Segment.fromJSON(json_data)
        seg2 = Segment("LEFT_KIDNEY")
        
        self.assertDictEqual(seg1.asJSON(), seg2.asJSON())
        
        ###
        
        json_data = {'labelID': 1, 'SegmentDescription': 'Primary malignant neoplasm', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '49755003', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Morphologically abnormal structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': '86049000', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Malignant neoplasm, primary (morphologic abnormality)'}, 'recommendedDisplayRGBValue': [255, 0, 0]}
        seg1 = Segment.fromJSON(json_data)
        seg2 = Segment("NEOPLASM_MALIGNANT_PRIMARY")
        self.assertDictEqual(seg1.asJSON(), seg2.asJSON())

    def test_custom_triplet(self):
        
        # register
        Triplet.register("M_CUSTOM_MODIFIER", code="MYMOD", meaning="My CUstom Modifier")
        
        # instantiate custom triplet
        triplet = Triplet("M_CUSTOM_MODIFIER")
        
        # check
        self.assertEqual(triplet.id, "M_CUSTOM_MODIFIER")
        self.assertEqual(triplet.code, "MYMOD")
        self.assertEqual(triplet.meaning, "My CUstom Modifier")
        self.assertEqual(triplet.scheme_designator, "99SEGDB")

    def test_unknown_triplet(self):
        
        # instantiate unknown triplet
        triplet = Triplet("UNKNOWN")
        
        # check
        self.assertEqual(triplet.id, "UNKNOWN")
        self.assertEqual(triplet.code, "UNKNOWN")
        self.assertEqual(triplet.meaning, "UNKNOWN")
        self.assertEqual(triplet.scheme_designator, "99SEGDB")

    def test_custom_segment(self):
        
        # register
        Segment.register("CUSTOM_SEGMENT", name="Custom Segment", category="C_MORPHOLOGICALLY_ABNORMAL_STRUCTURE", modifier="M_LEFT")

        # instantiate custom segment
        seg = Segment("CUSTOM_SEGMENT")
        
        # print
        print("\n\nCustom Segment")
        seg.print()
        
        # check
        self.assertDictEqual(seg.asJSON(), {'labelID': 1, 'SegmentDescription': 'Custom Segment', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': '49755003', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Morphologically abnormal structure'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': 'UNKNOWN', 'CodingSchemeDesignator': '99SEGDB', 'CodeMeaning': 'UNKNOWN'}, 'SegmentedPropertyTypeModifierCodeSequence': {'CodeValue': '7771000', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Left'}, 'recommendedDisplayRGBValue': [255, 255, 255]})

    def test_custom_segment_usage(self):
        
        # register
        Triplet.register("C_CUSTOM_CATEGORY", code="MYCAT", meaning="My Custom Category")
        Segment.register("CUSTOM_SEGMENT2", name="Custom Segment N2", category="C_CUSTOM_CATEGORY")
        
        # create a custom segment
        seg = Segment("HEART+CUSTOM_SEGMENT2")
        
        # debug
        print("\n\nCustom Segment")
        seg.print()
        
        # check
        self.assertDictEqual(seg.asJSON(), {'labelID': 1, 'SegmentDescription': 'Custom Segment N2 in Heart', 'SegmentAlgorithmType': 'AUTOMATIC', 'SegmentAlgorithmName': '', 'SegmentedPropertyCategoryCodeSequence': {'CodeValue': 'MYCAT', 'CodingSchemeDesignator': '99SEGDB', 'CodeMeaning': 'My Custom Category'}, 'SegmentedPropertyTypeCodeSequence': {'CodeValue': 'UNKNOWN', 'CodingSchemeDesignator': '99SEGDB', 'CodeMeaning': 'UNKNOWN'}, 'AnatomicRegionSequence': {'CodeValue': '80891009', 'CodingSchemeDesignator': 'SCT', 'CodeMeaning': 'Heart structure'}, 'recommendedDisplayRGBValue': [255, 255, 255]})