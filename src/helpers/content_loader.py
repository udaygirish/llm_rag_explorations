'''
Functions to help direct text loading from
different formats of files and sources 

This Code needs more optimization its a bit raw as
this is developed with Continuous Incremental Issue Fixes
'''

# Import common libaries 
import pandas as pd 
import os 
from glob import glob 
from tqdm import tqdm, trange 
import re 

# Import Loggers 
from utilities.logger import logger

# Import Unstructured Library components for loading text from different documents
from unstructured.partition.auto import partition 
from unstructured.partition.doc import partition_doc
from unstructured.partition.image import partition_image
from unstructured.partition.text import partition_text
from unstructured.partition.csv import partition_csv
from unstructured.partition.json import partition_json
from unstructured.partition.xml import partition_xml
from unstructured.partition.html import partition_html
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.xlsx import partition_xlsx


# Load Unstructured Library components for cleaning the files and content 
from unstructured.documents.elements import Text
from unstructured.cleaners.core import * 
# Used compoenents - replace_unicode_quotes , bytes_string_to_string 
# clean, clean_bullets, clean_dashes, clean_non_ascii_chars, 
# clean_ordered_bullets, clean_postfix, clean_prefix,
# clean_trailing_punctuation, group_broken_paragraphs, 
# remove_punctuation, translate_text 


# Current File types in Scope: .DOC, .DOCX, .PDF, .XLSX, .CSV, .JSON, .XML, .HTML, .TXT. .JPEG, .PNG, .GIF, .TIFF, .BMP, .SVG
# This function only handles some content currently 
# For full modified functionality of unstrcutured see docs
# Unstructured Docs: https://docs.unstructured.io/open-source/core-functionality/partitioning 



class ContentLoader:
    def __init__(self):
        self.description = "Content Loader for Different Type of Input files"
        self.partition_config = {
            'text': partition_text,
            'doc': partition_doc,
            'image': partition_image,
            'csv': partition_csv,
            'json': partition_json,
            'xml': partition_xml,
            'html': partition_html,
            'pdf': partition_pdf,
            'docx': partition_docx,
            'xlsx': partition_xlsx
        }
        self.load_tables = True
        self.load_db = True 
        self.load_tables_as_text = False # IF this is true above should be set to False (load_tables and load_db)
        # else they are forced to Set to False
    
    def get_partition_type(self, path):
        extension = path.split('.')[-1]
        if extension in self.partition_config:
            return extension
        else:
            return None
        
    def load_text(self, path, partition_type = None):
        if partition_type is None:
            print("Partition Type not provided, trying to infer from file extension")
            partition_type = self.get_partition_type(path)
        
        if partition_type not in ["csv", "xlsx"]:
                temp_elements = self.partition_config[partition_type](path)
                return temp_elements
        elif partition_type == "csv":
            temp_elements = partition_csv(path)
            return temp_elements
        elif partition_type == "xlsx":
            temp_elements = partition_xlsx(path)
            return temp_elements
        else:
            logger.error("Partition Type not supported")
            return None
    
    def load_df(self, csv_path):
        return pd.read_csv(csv_path)
        
    def load_all_files(self, folder_path):
        all_files = glob(folder_path + "/*")
        all_text = []
        for file in tqdm(all_files):
            if self.load_tables_as_text:
                temp_elements = self.load_text(file)
                all_text += [str(e) for e in temp_elements]
            elif file.split(".")[-1]  not in ["csv", "xlsx"]:
                temp_elements = self.load_text(file)
                all_text += [str(e) for e in temp_elements]
            else:
                logger.error("File format not supported")
        return all_text 
    
    def load_all_df(self, folder_path):
        all_files = glob(folder_path + "/*")
        all_df = []
        for file in all_files:
            if file.split(".")[-1] in ["csv", "xlsx"]:
                if file.split(".")[-1] == "csv":
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                df.fillna("", inplace=True)
                all_df.append(df)
        # Remove parent directory from the path and also the extension
        all_files = [re.sub(r".*/", "", file) for file in all_files]
        return all_df, all_files
    
    
        