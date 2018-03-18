# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:21:22 2018

@author: 颜
"""
import numpy as np
from GPU_explore import generate_map
from GPU_explore import search_path
from GPU_explore import write_csv

if __name__ == "__main__":
    __spec__=None
    start=np.array([142,328])
    end_list=np.array([[84,203],[199,371],[140,234],[236,241],[315,281],[358,207],[363,237],[423,266],[125,375],[189,274]])
    #generate_map("map//LR.csv",14.5)
    for t in range(10):
        search_path([start[0],start[1],t*5],end_list,min_prob=True)
    write_csv("AAA.csv")
    #[1,8,11,18,21,31,38,41,48],not_in=False

