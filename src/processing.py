import numpy as np
import pandas as pd
from typing import  Optional


class SpecificDataProcessing:
    """
    Обработка specific_data в зависимоси от типа входящей строки
    """
    
    def __init__(self):
        """
        entity_linked_func - получить даные о клиенте/компании
        sale_field_changed_func- поулчить данные о цене 
        lead_status_func - получить данные о статусе задачи 
        pipline_func - получить даные о pipline 
        
        sale: float - цена 
        company: int - id компании 
        client: int - id клиента
        lead_status: int - id статуса задачи 
        pipline: int - id пайплайна
        """
        
        # логика обработки для разных типов specific_data
        self.entity_linked_func = lambda row: row.specific_data['after'][0]['link']['entity']['id']                
        self.sale_field_changed_func = lambda row: row.specific_data['after'][0]['sale_field_value']['sale']
        self.lead_status_func = lambda row: row.specific_data['after'][0]['lead_status']['id']
        self.pipline_func = lambda row: row.specific_data['after'][0]['lead_status']['pipeline_id'] 

        # начальная инициализация сквозных значений (sale, responsible_user_id, pipeline, lead_status)
        self.initial_func= lambda row: (row.specific_data['sale'], 
                                        row.specific_data['pipeline'],
                                        row.specific_data['lead_status'],
                                        row.specific_data['responsible_user_id'])
        
        # сквозные поля датасета
        self.sale: Optional[float] = np.nan
        self.company: Optional[str]= np.nan 
        self.contact: Optional[str]= np.nan
        self.lead_status: Optional[str] = np.nan
        self.pipline: Optional[int]= np.nan 
        self.responsible: Optional[int]= np.nan 

        
    
    def __call__(self, row: pd.Series) -> pd.Series:
        """  
        Обработка поля specific_data для получени сквозных показателей
        
        Аргументы:
            row: строка данных 
        Возвращает:
            pd.Series для следующих полей:
                ('client', 'company', 'sale', 'lead_status', 'pipline')
        """
        
        # если это строка инициализации задачи
        if row.type == 'initial':
            self.sale, self.pipline, self.lead_status,  self.responsible = self.initial_func(row)
        
        # если установили/изменили sale
        elif row.type == 'sale_field_changed':
           self.sale =  self.sale_field_changed_func(row)
           
        # если добавили/изменили сущности: company, contact
        elif row.type=='entity_linked':
            if row.specific_data['after'][0]['link']['entity']['type']=='contact':
                 self.contact = self.entity_linked_func(row)
            elif row.specific_data['after'][0]['link']['entity']['type']=='company':
                self.company = self.entity_linked_func(row)
                
            
        return pd.Series([self.contact, self.company, self.sale, self.lead_status, self.pipline, self.responsible])
    
    
def lead_status_changed_processing(data):
    """
    Заполнить поле со статусом сделки
    """
    
    row_start = 0
    if 'lead_status_changed' in data.type.to_list():
        for index, row in data.iterrows():
            if row.type == 'lead_status_changed':
                after = row['specific_data']['after'][0]['lead_status']['id']
                before = row['specific_data']['before'][0]['lead_status']['id']
                data.loc[row_start: index-1, 'lead_status'] = before
                data.loc[index:, 'lead_status'] = after
                row_start = index
        
    return data

def responsible_user_processing(data):
    """
    Заполнить поле с ответственными
    """
    
    row_start = 0
    if 'entity_responsible_changed' in data.type.to_list():
        for index, row in data.iterrows():
            if row.type == 'entity_responsible_changed':
                after = row['specific_data']['after'][0]['responsible_user']['id']
                before = row['specific_data']['before'][0]['responsible_user']['id']
                data.loc[row_start: index-1, 'responsible'] = before
                data.loc[index:, 'responsible'] = after
                row_start = index
        
    return data


def sale_field_changed_processing(data):
    """
    Заполнить поле с ценой сделки
    """
    
    row_start = 0
    if 'sale_field_changed' in data.type.to_list():
        for index, row in data.iterrows():
            if row.type == 'sale_field_changed':
                after = row['specific_data']['after'][0]['sale_field_value']['sale']
                if len(row['specific_data']['before']) == 0:
                    before = None
                else:  
                    before = row['specific_data']['before'][0]['sale_field_value']['sale']
                data.loc[row_start: index-1, 'sale'] = before
                data.loc[index:, 'sale'] = after
                row_start = index
        
    return data