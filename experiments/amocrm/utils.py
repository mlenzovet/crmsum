import datetime
import numpy as np
import pandas as pd
import requests

from typing import Dict, Optional
import datetime 
import logging
from copy import copy 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Vocabulary:
    def __init__(self, token_manager, secrets):
            """ 
            Получение справочников amocrm
            
            Аргументы:
                token_manager - получение и обновление токена для доступа к данным 
                subdomain - поддомен аккаунта в autocrm 
            """
            
            self.token_manager = token_manager
            self.subdomain = secrets["subdomain"]
            
            # информация обо всех контактах. Ключ - id контакта в системе. Значение - вся информация о контакте
            self._contacts: Dict[int, dict] = self._create_contact_vocab()  
            # информация обо всех компаниях. Ключ - id компании в системе. Значение - вся информация о компании 
            self._companies: Dict[int, dict]  = self._create_companies_vocab() 
            # информация обо всех сделках. Ключ - id сделки. Значение - вся информация о сделки
            self._lead_status: Dict[int, dict]  = self._create_leads_vocab() 
            # информация обо всех воронках. Ключ - id воронки. Значение - вся информация о воронке (включая id статусов)
            self._piplines: Dict[int, dict]  =self._create_pipline_and_status_vocab()
            # информация обо всех менеджерах. Ключ - id менеджера. Значение - вся информация о менеджере
            self._users: Dict[int, dict]  = self._create_users_vocab()

        
    @property
    def contacts(self):
        return {k:v['name'] for k,v in self._contacts.items() if v['name']!=None}
    
    @property
    def companies(self):
        return  {k:v['name'] for k,v in self._companies.items()}
    
    @property
    def lead_status(self):
        return  {k:v['statuses'] for k,v in self._piplines.items()}
    
    @property
    def piplines(self):
        return{k:v['name'] for k,v in self._piplines.items()}
    
    @property
    def users(self):
        return {k:v['name'] for k,v in self._users.items()}
    
    
    def _api_call(self, endpoint, page):
        headers = {
            'Authorization': f'Bearer {self.token_manager.get_access_token()}',
            'Content-Type': 'application/json'
        }

        url = f'https://{self.subdomain}.amocrm.ru/api/v4/{endpoint}'
        params = {"page": page}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
    
    def _create_contact_vocab(self):
        """
        Создания словаря контактов, где ключом является id контакта,\
            значнием - вся информация о контакте
        """
        contacts_id_to_contacts_info = {}
        page=1 
        while True:
            response = self._api_call('contacts', page)
            if response.status_code == 204:
                break
            contacts =  response.json()['_embedded']['contacts']
            for contact in contacts:
                id = contact['id']
                contacts_id_to_contacts_info[id] = contact 
            page+=1
        
        return contacts_id_to_contacts_info
        
    def _create_companies_vocab(self):
        """
        Создания словаря компаний, где ключом является id компании,\
            значнием - вся информация о компании
        """
        companies_id_to_companies_info = {}
        page=1
        while True:
            response = self._api_call('companies', page)
            if response.status_code == 204:
                break
            companies =  response.json()['_embedded']['companies']
            for company in companies:
                id = company['id']
                companies_id_to_companies_info[id] = company
            page+=1
        
        return companies_id_to_companies_info
   
    def _create_leads_vocab(self):
        """
        Создания словаря сделок, где ключом является id сделки,\
            значнием - вся информация о сделке
        """
        leads_id_to_leads_info = {}
        page=1
        while True:
            response = self._api_call('leads', page)
            if response.status_code == 204:
                break
            leads =  response.json()['_embedded']['leads']
            for lead in leads:
                id = lead['id']
                leads_id_to_leads_info[id] = lead
            page+=1
        
        return leads_id_to_leads_info
        
    def _create_users_vocab(self):
        """
        Создания словаря менеджеров, где ключом является id менеджера,\
            значнием - вся информация о менеджере
        """
        users_id_to_users_info = {}
        page=1
        while True:
            response = self._api_call('users', page)
            if response.status_code == 204:
                break
            usesrs =  response.json()['_embedded']['users']
            for user in usesrs:
                id = user['id']
                users_id_to_users_info[id] = user
            page+=1
        
        return  users_id_to_users_info   
        
        
    def _create_pipline_and_status_vocab(self):
        """
        Создания словаря воронок, где ключом является id воронки,\
            значнием - вся информация о воронке (например, статус сделки)
        """
        pipe_id_to_pipe_info = {}
        response = self._api_call('leads/pipelines', None)
        piplines = response.json()['_embedded']['pipelines']
        for pipline in piplines:
            pipline_id = pipline['id']
            pipe_id_to_pipe_info[pipline_id] = {'name':pipline['name'],
                                                'statuses': dict([(status_dict['id'], status_dict['name']) \
                                                    for status_dict in pipline['_embedded']['statuses']])
                                            }
        return  pipe_id_to_pipe_info
    
    
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
        # self.entity_responsible_changed_func = lambda row: row.specific_data['after'][0]['responsible_user']['id']
        
        # {'after': [{'responsible_user': {'id': 1531225}}]
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
    
    
class AmoCRM:
    def __init__(self, token_manager, secrets):
        """ 
        Получение и обработка джанных AmoCRM
        
        Аргументы:
            token_manager - получение и обновление токена для доступа к данным 
            subdomain - поддомен аккаунта в autocrm 
            processor - класс для обработки сквозных значений
            _general_fields - поля основных значений (одинаковые для каждого типа записи)
        """
        self.token_manager = token_manager
        self.subdomain = secrets["subdomain"]
        self.processor = SpecificDataProcessing
        self._general_fields = ['type', 'entity_id', 'created_by', 'created_at', 'specific_data']
        self.vocab = Vocabulary(token_manager, secrets)

    def _api_call(self, endpoint, entity, entity_id):
        headers = {
            'Authorization': f'Bearer {self.token_manager.get_access_token()}',
            'Content-Type': 'application/json'
        }

        url = f'https://{self.subdomain}.amocrm.ru/api/v4/{endpoint}'

        params = {
            "filter[entity]": entity,
            "filter[entity_id]": entity_id
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
    

    def _initial_processing(self, initial_df: pd.DataFrame)-> pd.DataFrame:
        ''' 
        Унификация инициализирующих данных
        '''

        initial_df['type']='initial',
        initial_df['entity_id']=initial_df['id']
        initial_df['specific_data'] = initial_df.apply(lambda row: {'sale': row.price, 
                                                                    'responsible_user_id': row.responsible_user_id, 
                                                                    'pipeline': row.pipeline_id, 
                                                                    'lead_status': row.status_id}, axis=1)
        
        return initial_df[self._general_fields]
        
    
    def _event_processing(self, event_df: pd.DataFrame) -> pd.DataFrame:
        '''
        Унификация данных по евентам
        '''
        
        event_df['specific_data'] = event_df.apply(
            lambda row: {'after':row.value_after, 'before':row.value_before}, axis=1)
        
        return event_df[self._general_fields]
    
    def _task_processing(self, task_df: pd.DataFrame) -> pd.DataFrame:
        '''
        Унификация данных по задачам
        '''
        
        task_df['type'] = 'task'
        task_df['specific_data'] = task_df.apply(
            lambda row: {'text': row.text, 
                         'is_completed': row.is_completed,
                         'result':row.result, 
                         'responsible_user_id': row.responsible_user_id,
                         'complete_till': row.complete_till}, axis=1)
        
        return  task_df[self._general_fields ]


    def _note_processing(self, note_df: pd.DataFrame) -> pd.DataFrame:
        '''
        Унификация данных по заметкам
        '''

        note_df['type'] = 'note' 
        note_df['specific_data'] = note_df.apply(
            lambda row: {
                'text': row.params.get('text', None),  # Use .get() and provide a default value of None
                'note_type': row.note_type,
                'responsible_user_id': row.responsible_user_id,
                'updated_at': row.updated_at
            }, 
            axis=1
        )

        return note_df[self._general_fields]


    def get_initial_data_lead(self, lead_id):
        """ 
        Получение начальных данных по задаче
        """
        
        headers = {
        'Authorization': f'Bearer {self.token_manager.get_access_token()}',
        'Content-Type': 'application/json'
        }

        url = f'https://{self.subdomain}.amocrm.ru/api/v4/leads/{lead_id}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            initial_df = pd.Series(response.json()).to_frame().T # 
            return  self._initial_processing(initial_df)
        
        elif response.status_code == 204:
            return pd.DataFrame()
        
        else:
            raise Exception('Error: {}'.format(response.status_code))
        

    def get_events_by_lead_id(self, lead_id):
        response = self._api_call('events', 'lead', lead_id)
        if response.status_code == 200:
            event_df_raw = pd.DataFrame(response.json()['_embedded']['events'])
            return self._event_processing(event_df_raw)
        
        elif response.status_code == 204:
            return pd.DataFrame()
        
        else:
            raise Exception('Error: {}'.format(response.status_code))


    def get_tasks_by_lead_id(self, lead_id):
        response = self._api_call('tasks', 'lead', lead_id)
        if response.status_code == 200:
            task_df_raw = pd.DataFrame(response.json()['_embedded']['tasks'])
            return self._task_processing(task_df_raw)
        
        elif response.status_code == 204:
            return pd.DataFrame()
        
        else:
            raise Exception('Error: {}'.format(response.status_code))


    def get_notes_by_lead_id(self, lead_id):
        response = self._api_call('leads/notes', 'lead', lead_id)
        if response.status_code == 200:
            note_df_raw = pd.DataFrame(response.json()['_embedded']['notes'])
            return self._note_processing(note_df_raw)
        
        elif response.status_code == 204:
            return pd.DataFrame()
        
        else:
            raise Exception('Error: {}'.format(response.status_code))
    
    # preparation all_lead_info
    def get_all_lead_info(self, lead_id):
        """
        Получение и обоработка все данных по задачам
        """
        
        processor = self.processor() # обработчик сквозных значений
        inital_df = self.get_initial_data_lead(lead_id)
        events_df = self.get_events_by_lead_id(lead_id)
        tasks_df = self.get_tasks_by_lead_id(lead_id)
        notes_df = self.get_notes_by_lead_id(lead_id)

        result = pd.concat([inital_df, events_df, tasks_df, notes_df], axis=0)\
                                                .sort_values('created_at').\
                                                reset_index(drop=True).\
                                                assign(client=None,
                                                company=None,
                                                sale=None,  
                                                lead_status=None,
                                                pipline=None,
                                                responsible=None)
        result[['client', 'company', 'sale', 'lead_status', 'pipline', 'responsible']] = result.apply(processor, axis=1)
        
        # заполнить поля с изменением статусов, ответственны и цен
        result= lead_status_changed_processing(result)  
        result= responsible_user_processing(result)
        result = sale_field_changed_processing(result)
        
        # привести дату к нужному формату
        result['created_at'] = result['created_at'].apply(datetime.datetime.fromtimestamp)
        
        # заменить индексы на названия
        for index, row in result.iterrows():
            # создатель
            result.loc[index, 'created_by'] = self.vocab .users.get(row.created_by, None)
            # клиент 
            if not pd.isna(row.client):
                result.loc[index, 'client'] = self.vocab .contacts.get(int(row.client), None)
            # компания
            if not pd.isna(row.company):
                result.loc[index, 'company'] = self.vocab .companies.get(int(row.company), None)
            # воронка и статус сделки
            pipline_id = row.pipline
            result.loc[index, 'lead_status'] = self.vocab .lead_status[pipline_id].get(int(row.lead_status), None)
            result.loc[index, 'pipline'] = self.vocab .piplines.get(int(row.pipline), None)
            # ответственный
            result.loc[index, 'responsible'] = self.vocab .users.get(int(row.responsible), None)
         
        return result   


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