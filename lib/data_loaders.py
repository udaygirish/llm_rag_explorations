'''Functions to help  dataloading from multiple formats and sources'''
import pandas as pd 
import os
from glob import glob 
from tqdm import tqdm , trange 

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

from unstructured.cleaners.core import replace_unicode_quotes
from unstructured.documents.elements import Text
import re 
from unstructured.cleaners.core import bytes_string_to_string
from unstructured.partition.html import partition_html

from unstructured.cleaners.core import * 
# The above import imports the following specifically - Can be used for Data cleaning process 
# <clean, clean_bullets, clean_dashes, clean_non_ascii_chars, clean_ordered_bullets, clean_postfix
# clean_prefix, clean_trailing_punctuation, group_broken_paragraphs, remove_punctuation, replace_unicode_quotes >

from unstructured.cleaners.translate import translate_text

# Temporary import from parent
from lib.table_converter import template_text_formatting, language_modelled_text



data_folder = "data"
primary_subfolder = "personal"
secondary_subfolder = "."

partition_config = {
    "doc": partition_doc,
    "image": partition_image,
    "text": partition_text,
    "csv": partition_csv,
    "json": partition_json,
    "xml": partition_xml,
    "html": partition_html,
    "pdf": partition_pdf,
    "docx": partition_docx,
    "xlsx": partition_xlsx
}

# TODO: Add support for more file formats
# 1. Add Cleaning Support - Common Cleaners - Whitespaces, Trails etc
# 2. Add Translation Support
# 3. Add Multi Page Excel Sheet Support
# 4. Add Multi Page PDF Support for Image and Chart Extractions


def load_data():
    total_folder_path = os.path.join(data_folder, primary_subfolder, secondary_subfolder)

    # Get all files in the folder 
    all_files = glob(total_folder_path + "/*")
    print(all_files)

    # Extract the text from the files using unstructured.partition.auto
    all_text = []
    for file in all_files:
        filename = file 
        if filename.split(".")[-1] in partition_config.keys():
            temp_elements = partition_config[filename.split(".")[-1]](filename)
            joined_string = " ".join([str(e) for e in temp_elements])
            all_text.append(joined_string)
        else:
            print(f"File format not supported: {file}")
            
            
    all_df = []
    for file in all_files:
        if file.split(".")[-1] in ["csv", "xlsx"]:
            # If multiple pages in .xlsx or .csv select the first page
            df = pd.read_csv(file)
            # Replace all NaN with empty string
            df.fillna("", inplace=True)
            # Reset the index
            all_df.append(df)
            
    
    print("Length of all_text: ", len(all_text))
    print("Length of all_df: ", len(all_df))
    print("DataFrames: ", all_df[0].head())
    print("==================================================="*2)
    
    # Generate a template formatted text
    out_list_df = []
    for i in range(len(all_df)):
        out_list_df += template_text_formatting(all_df[i])
    
    
    #print("Template Formatted Text: ", out_list_df)
    
    print("==================================================="*2)
    print("Length of all_text: ", len(out_list_df))
    print("==================================================="*2)
    
    total_text = all_text + out_list_df
    
    # Generate total text
    out_text = " ".join([str(e) for e in total_text])
    
    return out_text
    
    

def test():
    total_folder_path = os.path.join(data_folder, primary_subfolder, secondary_subfolder)

    # Get all files in the folder 
    all_files = glob(total_folder_path + "/*")
    print(all_files)

    # Extract the text from the files using unstructured.partition.auto
    all_text = []
    for file in all_files:
        filename = file 
        if filename.split(".")[-1] in partition_config.keys():
            temp_elements = partition_config[filename.split(".")[-1]](filename)
            joined_string = " ".join([str(e) for e in temp_elements])
            all_text.append(joined_string)
        else:
            print(f"File format not supported: {file}")
            
            
    all_df = []
    for file in all_files:
        if file.split(".")[-1] in ["csv", "xlsx"]:
            # If multiple pages in .xlsx or .csv select the first page
            df = pd.read_csv(file)
            # Replace all NaN with empty string
            df.fillna("", inplace=True)
            # Reset the index
            all_df.append(df)
            
    
    print("Length of all_text: ", len(all_text))
    print("Length of all_df: ", len(all_df))
    print("DataFrames: ", all_df[0].head())
    print("==================================================="*2)
    
    # Generate a template formatted text
    out_list = template_text_formatting(all_df[0])
    
    print("Template Formatted Text: ", out_list)
    
    print("==================================================="*2)
    print("Length of all_text: ", len(out_list))
    print("==================================================="*2)
    # Generate a language modelled text
    out_list = language_modelled_text(out_list, model_name = "llama")
    
    print("Language Modelled Text: ", out_list)



if __name__ == "__main__":
    
    test() 

