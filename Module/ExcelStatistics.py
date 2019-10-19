# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 21:03:11 2019

@author: Wei Huajing
@company: Nanjing University
@e-mail: jerryweihuajing@126.com

@title：Statistics
"""

import xlrd

import copy as cp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from xlutils.copy import copy
from matplotlib.pyplot import MultipleLocator
from matplotlib.font_manager import FontProperties

import HeadColumns as HC
import PathProcessing as PP

#------------------------------------------------------------------------------
"""
Make statistics from one excel

Args:
    xls_path: path of excel to be processed
    num_head_rows: top rows
    num_head_columns: left columns
    list_num_head_columns: list of num_head_rows (default: None)
    
Returns:
    new head columns list
"""
def WorkbookStatistics(xls_path,num_head_rows,num_head_columns,list_num_head_columns=None):
    
    print('')
    print('--Workbook Statistics')
    
    plt.style.use('ggplot')
    
    #open the excel sheet to be operated on
    #formatting_info: keep the header format
    workbook=xlrd.open_workbook(xls_path,formatting_info=True)
    
    #copy former workbook
    new_workbook=copy(workbook)
        
    #construct output folder path
    tables_output_folder=xls_path.replace('.xls','').replace('input','output')+'\\'
    
    #save as
    new_workbook.save(tables_output_folder+'统计结果.xls')
    
    #construct map between sheet names and head rows
    list_sheet_names=list(workbook.sheet_names())
    
    #default
    if list_num_head_columns==None:
        
        list_num_head_columns=[num_head_columns]*len(list_sheet_names)
        
    map_sheet_names_num_head_columns=dict(zip(list_sheet_names,list_num_head_columns))    
    
    #traverse all sheets
    for this_sheet_name in workbook.sheet_names():

        print('')
        print('...')
        print('......')
        print('->sheet name:',this_sheet_name)
        print('')
        
        #construct output folder path
        figures_output_folder=xls_path.replace('.xls','').replace('input','output')+'\\Figures\\sheet '+this_sheet_name+'\\'
        
        #generate output folder
        PP.GenerateFolder(figures_output_folder)
        PP.GenerateFolder(tables_output_folder)
        
        #Data Frame object
        channel=pd.read_excel(xls_path,sheet_name=this_sheet_name)
        
        final_head_columns,unit_list=HC.HeadColumnsGeneration(channel,num_head_rows)
        
        #print(final_head_columns)
        
        #all info of dataframe
        value_matrix=channel.values
        
        title_font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=16)  
        label_font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=13)  
        
        '''complete info of statistics'''
            
        #item names of statistics
        statistic_items=['平均值','标准差','最大值','最小值']
        
        #new dataframe to store statistic data
        statistic=cp.deepcopy(channel.iloc[:len(statistic_items)])
        
        #columns to delete
        columns_to_delete=[]
        
        #no valid data
        columns_void=[]
        
        for k in range(num_head_columns,np.shape(value_matrix)[1]):
        
            #num of steps
            n_step=20
            
            #fetch the data
            data=list(value_matrix[num_head_rows:,k])
            
            #unit str
            unit=unit_list[k]
            
            #title str
            title=final_head_columns[k]
            
            #expire particular conditions
            if '分类' in title or '备' in title or '注' in title:
                
                #give the value
                statistic.iloc[0,k]=''
                statistic.iloc[1,k]=''
                statistic.iloc[2,k]=''
                statistic.iloc[3,k]=''
                
                columns_to_delete.append(title)
                
                #expire nan
                valid_str=[this_data for this_data in data if isinstance(this_data,str)]
                
                #group in x axis
                str_group=list(set(valid_str))
                
                #list of str frequency
                str_frequency=[0]*(len(str_group))
                      
                #construct a dictionary as vote machine
                map_str_frequency=dict((this_valid_str,valid_str.count(this_valid_str)) for this_valid_str in valid_str)
                
        #        print(map_str_frequency)
               
                #frequency list
                str_frequency=list(map_str_frequency.values())
                
                fig,ax=plt.subplots(figsize=(8,8))
                
                #plot histogram
                plt.bar(range(len(str_frequency)),str_frequency,tick_label=str_group)
                
                ax.yaxis.set_major_locator(MultipleLocator(int(np.ceil((max(str_frequency)-min(str_frequency))/n_step))))
                
                #set ticks
                plt.tick_params(labelsize=60/len(str_group))
        
                #y label fonts
                for this_label in ax.get_yticklabels():
                    
                    this_label.set_fontname('Times New Roman')
                    
                #x label fonts
                for this_label in ax.get_xticklabels():
                    
                    this_label.set_fontname('SimHei')
                    
                plt.title(title+' 频数分布直方图\n样本总量:'+str(int(len(valid_str))),
                          FontProperties=title_font)
                
                plt.xlabel(title+' '+unit,FontProperties=label_font)
                
                plt.savefig(figures_output_folder+title+'.png')
                plt.close()
                
                continue
            
            #expire nan
            valid_data=[float(this_data) for this_data in data if not np.isnan(float(this_data))]
            
            print(k,title)
        
            if valid_data==[]:
                
                #give the value
                statistic.iloc[0,k]=''
                statistic.iloc[1,k]=''
                statistic.iloc[2,k]=''
                statistic.iloc[3,k]=''
            
                columns_void.append(title)
                
                continue
            
            #x coordinates
            group=np.linspace(min(valid_data),max(valid_data),n_step)
        
            #whether to process
            scaled_flag=False
            
            #exception processing
            for this_tick in group:
                
                if 'e' in str(this_tick):
                    
        #            print(str(min(group)).split('e')[0])
        #            print(str(max(group)).split('e')[0])
        #            print(str(min(group)).split('e')[-1])
        #            print(str(max(group)).split('e')[-1])
        
                    factor=str(min(group)).split('e')[-1]
        
                    scaled_flag=True
                    
                    break
                
            fig,ax=plt.subplots(figsize=(8,8))
            
            if scaled_flag:
                    
                #mutiply a factor
                valid_data=np.array(valid_data)/10**(int(factor))
                        
                group=np.linspace(min(valid_data),max(valid_data),n_step)  
                
                #plot histogram
                plt.hist(valid_data, group, histtype='bar', rwidth=0.95)
                 
                plt.title(title+' 频数分布直方图\n样本总量:'+str(int(len(valid_data))),
                          FontProperties=title_font)
                
                plt.xlabel(title+' e'+factor+' '+unit,FontProperties=label_font)
            
            else:
                
                #plot histogram
                plt.hist(valid_data, group, histtype='bar', rwidth=0.95)
                 
                plt.title(title+' 频数分布直方图\n样本总量:'+str(int(len(valid_data))),
                          FontProperties=title_font)  
                
                plt.xlabel(title+' '+unit,FontProperties=label_font)
            
            #list of frequency
            frequency=[0]*(len(group)-1)
            
            #mannual histogram
            for this_valid_data in valid_data:
        
                for g in range(len(group)-1):
                    
                    if group[g]<=this_valid_data<=group[g+1]:
                        
                        frequency[g]+=1
                        
                        break
         
            ax.yaxis.set_major_locator(MultipleLocator(int(np.ceil((max(frequency)-min(frequency))/n_step))))
            
            #set ticks
            plt.tick_params(labelsize=15)
            labels = ax.get_xticklabels() + ax.get_yticklabels()
            
            #label fonts
            for this_label in labels:
                
                this_label.set_fontname('Times New Roman')
                
            #average
            data_average=np.mean(valid_data)
            
            #standard
            data_standard=np.std(valid_data,ddof=1)
            
            #maximum
            data_maximum=np.max(valid_data)
            
            #minimum
            data_minimum=np.min(valid_data)
            
        #    print(data_average,data_standard,data_maximum,data_minimum)
            
            #give the value
            statistic.iloc[0,k]=data_average
            statistic.iloc[1,k]=data_standard
            statistic.iloc[2,k]=data_maximum
            statistic.iloc[3,k]=data_minimum
            
            #valid file name
            if '<' in title:
                
                title=title.replace('<','小于')
                
            if '>' in title:
                
                title=title.replace('>','大于')    
            
            plt.savefig(figures_output_folder+title+'.png')
            plt.close()
            
        #statistics decoration
        for k in range(len(statistic_items)):
            
            statistic.iloc[k,1]=statistic_items[k]
          
        #delete one column
        statistic=statistic.drop(statistic.columns[0],axis=1,index=None)
        
        #rename column
        statistic=statistic.rename(columns = {statistic.columns[1]:'特征值'})  
        
        #index of line where info starts
        start_info_row=num_head_rows+1
          
        #open a sheet
        this_sheet=new_workbook.get_sheet(this_sheet_name)   
         
        #total lines
        num_info_rows=len(this_sheet.rows)
        
        #blank row
        one_list=['']*(len(channel.iloc[:1].columns)+2)
        
        #fill with blank lines
        for ii in range(num_info_rows):
            
            for jj in range(len(one_list)):
                
                this_sheet.write(ii+start_info_row,jj,one_list[jj])
        
        '''Data frame reads data and automatically ignores empty rows and columns'''
        for i in range(statistic.shape[0]):
            
            for j in range(statistic.shape[1]):
              
                try:
                    
                    this_sheet.write(i+start_info_row,
                                     j+map_sheet_names_num_head_columns[this_sheet_name],
                                     statistic.iloc[i,j])      
                  
                #transform int to float
                except:
                    
                    this_sheet.write(i+start_info_row,
                                     j+map_sheet_names_num_head_columns[this_sheet_name],
                                     float(statistic.iloc[i,j]))
   
        new_workbook.save(tables_output_folder+'统计结果.xls')