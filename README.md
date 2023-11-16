# MHub SegDB

DISCLAIMER: **NOT FOR CLINICAL USE**

This package contains tools to facilitate the creation of standardized definitions for automatically generated segmentations in medical imaging.

## Why do we need a standard

When we train a Deep Learning model to describe a structure, we need to define and describe what the algorithm is trained on and what structure we can expect as a result.
In medical imaging, this is particularly important and complex. The delineation of anatomical structures depends on the context, which requires a detailed description. At the same time, for further analysis, we need to know exactly what is delineated and what isn't, so that there is no room for interpretation.
Let's take the case of an AI model describing the lungs as an example. This may sound straight foreward at first, but in the medical field there are many different applications for representing the lungs, so models can specialize in different ways. For example, one model may represent the lung as a whole organ, another model represents each wing or all the lung lobes individually, and still another model represents pulmonary nodules or tumorous tissue throughout the lung or in specific parts. This incomplete example gives an idea of how diverse a simple task can be when used in different scenarios and research areas. This is why it's so important to describe exactly what an algorithm represents and in what context.

Fortunately, there are standards that solve exactly this problem. One of them is the dicom standard, which solves the above problem with a [DICOM Segmentation Image (DICOM SEG)](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.51.html) object that gives us standardized descriptors for segmentations in medical images. Since simple text or a defined list of attributes is hardly sufficient to describe the complex nature and inherent relationships of the virtually identified objects on a medical image, these fields refer to objects embedded in an ontology, e.g. SNOMED CT.

The DCMQI library provides the conversion tool `itkimage2segimage` ([which is documented here](https://qiicr.gitbook.io/dcmqi-guide/opening/cmd_tools/seg/itkimage2segimage)) that produces a DICOM SEG file with the correct metadata based on NRRD or NIFTI files, which are more conventional outputs of AI pipelines but lack the required standardization.

While it's great to have such a powerful tool, we're aware of the burden it brings, as it can quickly become overwhelming. Sure, no effort, no results. So, to create a standardized DICOM SEG file, you need to look up each structure, identify the correct codes, and compile this information into a metafile to provide the DCMQI converter with the information it needs. This isn't a trivial task and requires careful selection and additional knowledge of anatomical concepts and terms. Nevertheless, it's extremely important to provide this information and the benefits are enormous.

With MHub, we want to encourage everyone to become familiar with these standards and use them for every project. This is key to creating meaningful models and driving further research based on them. Therefore, we try to simplify the process where we can. To this end, we have created a database in which we define the structures we have carefully selected.

## Installation

```bash
pip install git+https://github.com/MHubAI/segdb.git
```

## Lookup segmentations

Use the `segdb.lookup` tool to search for segmentations by specifying space-separated keywords as arguments.
By default, it searches for segmentations that contain all the specified keywords. To search for segmentations containing at least one of the keywords, add the argument `--or`.

```python
# search for lung
python -m segdb.lookup lung

# search for left lung
python -m segdb.lookup left lung

# search for lung and heart
python -m segdb.lookup --or lung heart 
```

## Generate a DCMQI json config file

In the following example, `My Model` is an AI model that segments the whole heart. It reads a CT scan as a DICOM image from `path/to/dicom` and creates a NIFTI file at `path/to/segmentation.nii.gz` that contains the binary heart segmentation.
To generate the DCMQI meta JSON, we use the `DcmqiDsegConfigGenerator` class from the `segdb.tools` module.
Then we add an element for each segmentation file and specify a list of comma-separated segment IDs next to the model name.
In this example, there is only one file that contains a single segment: the heart. So we look for the segment ID for the heart (e.g., by running `python -m segdb.lookup heart`), which is `HEART`, and set it accordingly.
To create the JSON file, we use the `save(file_name: str)` method of the generator instance.

```python

from segdb.tools import DcmqiDsegConfigGenerator

# generate json meta generator instance
generator = DcmqiDsegConfigGenerator(
    model_name = 'My Model',
    body_part_examined = 'CHEST'
)

# add segmentation
generator.addItem(
    file = 'path/to/segmentation.nii.gz',
    segment_ids = 'HEART',
    model_name = 'My Model'
)

# save json
generator.save('path/to/meta.json')
```

We can then run the `itkimage2segimage` tool with the generated JSON file to create a DICOM SEG file.

```bash
itkimage2segimage 
 --inputImageList path/to/segmentation.nii.gz
 --inputDICOMDirectory path/to/dicom
 --outputDICOM my/standardized/heart_seg.dcm
 --inputMetadata path/to/meta.json
```

## Definition of embedded structures

Some structures that we can segment are embedded in an anatomical structure, such as tissue abnormalities like tumors or cardiac calcifications.

For example, a primary tumor (malignant neoplasm) in the liver is defined by the delineated structure (the tumor) with the ID `NEOPLASM_MALIGNANT_PRIMARY` and is embedded in a context organ (the liver) with the ID `LIVER`. To annotate such a structure, combine both IDs with a `+` sign, with the ID of the anatomical structure before and the ID of the embedded structure after the plus sign: `LIVER+NEOPLASM_MALIGNANT_PRIMARY`.
