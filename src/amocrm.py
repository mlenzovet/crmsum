import datetime
import pandas as pd
import requests
import datetime 
import logging

from .vocabulary import Vocabulary
from .processing import (sale_field_changed_processing, 
                        lead_status_changed_processing, 
                        SpecificDataProcessing, 
                        responsible_user_processing)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
            result.loc[index, 'lead_status'] = self.vocab.lead_status[pipline_id].get(int(row.lead_status), None)
            result.loc[index, 'pipline'] = self.vocab.piplines.get(int(row.pipline), None)
            # ответственный
            result.loc[index, 'responsible'] = self.vocab .users.get(int(row.responsible), None)
         
        return result   