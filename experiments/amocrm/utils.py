
import numpy as np
import pandas as pd
import requests

from typing import Dict, Optional
import datetime 

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
            self.contacts: Dict[int, dict] = self._create_contact_vocab()  
            # информация обо всех компаниях. Ключ - id компании в системе. Значение - вся информация о компании 
            self.companies: Dict[int, dict]  = self._create_companies_vocab() 
            # информация обо всех сделках. Ключ - id сделки. Значение - вся информация о сделки
            self.leads: Dict[int, dict]  = self._create_leads_vocab() 
            # информация обо всех воронках. Ключ - id воронки. Значение - вся информация о воронке (включая id статусов)
            self.piplines: Dict[int, dict]  =self._create_pipline_and_status_vocab()
            # информация обо всех менеджерах. Ключ - id менеджера. Значение - вся информация о менеджере
            self.users: Dict[int, dict]  = self._create_users_vocab()


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
    
class DataRepresentation: 
    """ 
    Представление данных в "человеческом" виде
    """
    def __init__(self, token_manager, secrets):
        """
        df - итоговая таблица, содержащая всю информацию о задаче 
        vocab - все словари аккаунта
        """
        self.vocab = Vocabulary(tokens.default_token_manager, secrets) 
        self._processing()
        
    def _processing(self):
        """
        Подготовка словарей для мапинга в итоговую таблицу
        """
        self.entity_id = {k:v['name'] for k,v in self.vocab.leads.items()}
        self.client = {k:v['name'] for k,v in self.vocab.contacts.items()}
        self.company = {k:v['name'] for k,v in self.vocab.companies.items()}
        self.pipline = {k:v['name'] for k,v in self.vocab.piplines.items()}
        self.lead_status= {k:v['statuses'] for k,v in self.vocab.piplines.items()}
        self.users = {k:v['name'] for k,v in self.vocab.users.items()}
        
    def __call__(self, df):
        return df.assign(
                created_at = df.created_at.apply(lambda timestamp: datetime.datetime.fromtimestamp(timestamp)),
                created_by = df.responsible.apply(lambda cell: self.users.get(cell, None)),
                entity_id = df.entity_id.apply(lambda cell: self.entity_id.get(cell, None)),
                client = df.client.apply(lambda cell: self.client.get(cell, None)),
                company = df.company.apply(lambda cell: self.company.get(cell, None)),
                pipline = df.pipline.apply(lambda cell: self.pipline.get(cell, None)),
                lead_status	= df.apply(lambda row: self.lead_status[row.pipline][row.lead_status] , axis=1),
                responsible = df.responsible.apply(lambda cell: self.users.get(cell, None))
            )
    
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
                                        row.specific_data['responsible_user_id'],
                                        row.specific_data['pipeline'],
                                        row.specific_data['lead_status'])
        
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
            self.sale, self.responsible, self.pipline, self.lead_status = self.initial_func(row)
        
        # если установили/изменили sale
        elif row.type == 'sale_field_changed':
           self.sale =  self.sale_field_changed_func(row)
           
        # если добавили/изменили сущности: company, contact
        elif row.type=='entity_linked':
            if row.specific_data['after'][0]['link']['entity']['type']=='contact':
                 self.contact = self.entity_linked_func(row)
            elif row.specific_data['after'][0]['link']['entity']['type']=='company':
                self.company = self.entity_linked_func(row)
                
        # если изменился статус/пайплайн задачи задачи
        elif row.type=='lead_status_changed':
            self.lead_status = self.lead_status_func(row)
            self.pipline = self.pipline_func(row)

        return pd.Series([self.contact, self.company, self.sale, self.lead_status, self.pipline, self.responsible])