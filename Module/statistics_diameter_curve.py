# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 18:41:14 2020

@author: Wei Huajing
@company: Nanjing University
@e-mail: jerryweihuajing@126.com

@title: Module-Stastics of Diameter Curve
"""

import xlrd
import copy as cp
import numpy as np
import pandas as pd

import operation_head_column as O_H_C
import operation_list as O_L
import operation_path as O_P

from o_data import data

#------------------------------------------------------------------------------
"""
Make resilience curve from one excel

Args:
    xls_path: path of excel to be processed
    num_head_rows: top rows
    num_head_columns: left columns

Returns:
    None
"""
def WorkbookDiameter(xls_path,num_head_rows,num_head_columns):
    
    print('')
    print('--Workbook Diameter')
    
    #plt.style.use('ggplot')
    
    #construct output folder path
    output_folder=xls_path.replace('.xls','').replace('input','output')+'\\粒径曲线\\'
    
    #generate output folder
    O_P.GenerateFolder(output_folder)
    
    #open the excel sheet to be operated on
    #formatting_info: keep the header format
    workbook=xlrd.open_workbook(xls_path,formatting_info=True)
    
    #construct map between sheet names and head rows
    list_sheet_names=list(workbook.sheet_names())
    
    #traverse all sheets
    for this_sheet_name in list_sheet_names[:-1]:
    
        print('')
        print('...')
        print('......')
        print('->sheet name:',this_sheet_name)
        print('')
        
        #Data Frame object
        channel=pd.read_excel(xls_path,sheet_name=this_sheet_name)
        
        final_head_columns,unit_list=O_H_C.HeadColumnsGeneration(channel,num_head_rows)
        
#        print(final_head_columns)
        
        #all info of dataframe
        value_matrix=channel.values
        
#        '''special condition'''
#        num_head_rows-=1
        
        #delete the repetition
        index_valid=O_L.ValidIndexList(value_matrix[num_head_rows:,1])  
    
        index_diameter=[]
        diameter_range=[200,20,2,0.5,0.25,0.075,0.05,0.005,0]
    
        for k in range(num_head_columns,np.shape(value_matrix)[1]):
            
            #title str
            title=final_head_columns[k] 
               
            if '颗' in title\
            and '粒' in title\
            and '分' in title\
            and '析' in title\
            and 'mm' in title:
                
                print(k,title)
                
                index_diameter.append(k)
 
        index_list=[0,1,2,3]
        
        #indoor id, hole id, start depth, end depth, 
        #pore aperture, consolidation pressure, compression index, resilience index
        list_indoor_id,\
        list_hole_id,\
        list_start_depth,\
        list_end_depth=[O_L.CustomIndexList(list(value_matrix[num_head_rows:,this_index]),index_valid) for this_index in index_list]
        
        #matrix to contain grain partition proportion
        data_diameter=np.zeros((len(index_valid),len(index_diameter)))
        
        column=0
        
        for this_index in index_diameter:
            
            data_diameter[:,column]=O_L.CustomIndexList(list(value_matrix[num_head_rows:,this_index]),index_valid)
        
            column+=1
              
        #construct data objects
        list_data=[]
        
        for i in range(np.shape(data_diameter)[0]):
            
            new_data=data()
            
            new_data.hole_id=list_hole_id[i]
            new_data.indoor_id=list_indoor_id[i]
            new_data.end_depth=list_end_depth[i]
            new_data.start_depth=list_start_depth[i]
            
            new_data.list_diameter=cp.deepcopy(diameter_range)
            new_data.list_diameter_percentage=list(data_diameter[i,:])

            list_bool=[np.isnan(this_percentage) for this_percentage in new_data.list_diameter_percentage]
            
            #expire list with all nan
            if list_bool==len(list_bool)*[True]:
                
                continue
            
            #calculate the cumulative percentage
            new_data.list_diameter_percentage_cumulative=[]
            
            for s in range(len(new_data.list_diameter_percentage)):
                
                this_cumulative_percentage=np.sum([this_percentage for this_percentage in new_data.list_diameter_percentage[s:] if not np.isnan(this_percentage)])
                
                new_data.list_diameter_percentage_cumulative.append(this_cumulative_percentage)
                
            list_data.append(new_data)
            
    the_data=list_data[-1]
    
    the_data.DiameterCurve()