# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 16:35:23 2017

@author: 颜
"""

'''
this file load predict wind into the map, which has size [5,548,421,360,2]
'''

import numpy as np
from MAP_class import generate_map
from MAP_class import load_map
from MAP_class import search_path
from MAP_class import write_csv
from multiprocessing import Pool


if __name__ == "__main__":
    __spec__=None
    process_num=5
    output_test_file=True
    start=np.array([142,328,0])
    end=np.array([[84,203],[199,371],[140,234],[236,241],[315,281],[358,207],[363,237],[423,266],[125,375],[189,274]])
    #generate_map("map.csv")
    h_min=3
    pool=Pool(processes=process_num)
    for i in range(5):
        for j in range(10):
            pool.apply_async(search_path,(i,j,start,end[j],h_min))
    pool.close()
    pool.join()
    write_csv(output_test_file)


