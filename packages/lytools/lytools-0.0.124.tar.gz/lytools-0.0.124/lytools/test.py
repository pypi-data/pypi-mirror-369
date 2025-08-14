# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np

from _lytools import *


def resample_majority(tif_path,out_path, new_res):
    arr, originX, originY, pixelWidth, pixelHeight = ToRaster().raster2array(tif_path)
    col_num,row_num = np.shape(arr)
    print('origin shape:',col_num,row_num)
    new_col_num = abs(round(col_num * (pixelWidth/new_res))) + 1
    new_row_num = abs(round(row_num * (pixelHeight/new_res))) + 1

    print('new shape:',new_col_num-1,new_row_num-1)
    new_col_range = np.linspace(0,col_num,new_col_num)
    new_col_range_int = [int(round(i)) for i in new_col_range]

    new_row_range = np.linspace(0,row_num,new_row_num)
    new_row_range_int = [int(round(i)) for i in new_row_range]

    arr_new = np.ones((new_col_num-1,new_row_num-1)) * np.nan
    for i in tqdm(range(len(new_col_range_int))):
        if i == len(new_col_range_int)-1:
            break
        col_i_left = new_col_range_int[i]
        col_i_right = new_col_range_int[i+1]
        col_vals = arr[col_i_left:col_i_right]
        for j in range(len(new_row_range_int)):
            if j == len(new_row_range_int)-1:
                break
            col_j_left = new_row_range_int[j]
            col_j_right = new_row_range_int[j+1]
            col_vals_T = col_vals.T
            col_j_vals = col_vals_T[col_j_left:col_j_right]
            values, counts = np.unique(col_j_vals, return_counts=True)
            ind = np.argmax(counts)
            new_val = values[ind]

            arr_new[i,j] = new_val

    ToRaster().array2raster(arr_new, originX, originY, new_res, -new_res, out_path)