import os
import sys

dirnames = ["0128\ brown\ line/", "0128\ yellow\ line\/", "0128\ band\ locking/"]

for dirname in dirnames:
    cell_names = ["xm1\ \(3231\ 3232\)\/", "xm2\ \(3233\ 3234\)\/", "xm3\ \(3235\ 3236\)\/"]
   
        
    for cell_name in cell_names:
        cell_dir = dirname + cell_name
        print(cell_dir)
        os.system("python3 cell_info_csv_processing.py " + cell_dir)
    
    
    for cell_name in cell_names:
        diag_dir = dirname + cell_name + "diag_txt\/"
        print(diag_dir)
        os.system("python3 offline-analysis.py "+ diag_dir)
    
    
    for cell_name in cell_names:
        diag_dir = dirname + cell_name + "diag_txt\/"
        print(diag_dir)
        os.system("python3 xml_mi.py "+ diag_dir)
