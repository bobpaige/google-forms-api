import yaml
import json
import hashlib
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/forms.body']

class FormsManager:
    def __init__(self, input_file):
        self.input_file = input_file
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        self.pickle_file = f'{base_name}.pickle'
        self.state_file = f'{base_name}_state.json'
        self.service = self._get_service()
        self.state = self._load_state()
    
    def _get_service(self):
        creds = None
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.pickle_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('forms', 'v1', credentials=creds)
    
    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _compute_hash(self, form_config):
        content = json.dumps(form_config, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _build_form_body(self, config):
        items = []
        for idx, q in enumerate(config['questions']):
            item = {
                'title': q['text'],
                'questionItem': {
                    'question': {
                        'required': q.get('required', False)
                    }
                }
            }
            
            if q['type'] == 'short_answer':
                item['questionItem']['question']['textQuestion'] = {'paragraph': False}
            elif q['type'] == 'paragraph':
                item['questionItem']['question']['textQuestion'] = {'paragraph': True}
            elif q['type'] == 'multiple_choice':
                item['questionItem']['question']['choiceQuestion'] = {
                    'type': 'RADIO',
                    'options': [{'value': opt} for opt in q['options']]
                }
            
            items.append(item)
        
        return {
            'info': {
                'title': config['title'],
                'documentTitle': config['title']
            }
        }
    
    def _create_form(self, config):
        form_body = self._build_form_body(config)
        form = self.service.forms().create(body=form_body).execute()
        form_id = form['formId']
        
        # Add description and questions
        requests = [
            {
                'updateFormInfo': {
                    'info': {
                        'description': config['description']
                    },
                    'updateMask': 'description'
                }
            }
        ]
        
        for idx, q in enumerate(config['questions']):
            item = {'title': q['text'], 'questionItem': {'question': {'required': q.get('required', False)}}}
            
            if q['type'] == 'short_answer':
                item['questionItem']['question']['textQuestion'] = {'paragraph': False}
            elif q['type'] == 'paragraph':
                item['questionItem']['question']['textQuestion'] = {'paragraph': True}
            elif q['type'] == 'multiple_choice':
                item['questionItem']['question']['choiceQuestion'] = {
                    'type': 'RADIO',
                    'options': [{'value': opt} for opt in q['options']]
                }
            
            requests.append({
                'createItem': {
                    'item': item,
                    'location': {'index': idx}
                }
            })
        
        # Add response message
        requests.append({
            'updateSettings': {
                'settings': {
                    'quizSettings': {
                        'isQuiz': False
                    }
                },
                'updateMask': 'quizSettings'
            }
        })
        
        self.service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        

        
        return form_id
    
    def _update_form(self, form_id, config):
        # Get current form
        form = self.service.forms().get(formId=form_id).execute()
        requests = []
        
        # Update title and description
        requests.append({
            'updateFormInfo': {
                'info': {
                    'title': config['title'],
                    'description': config['description']
                },
                'updateMask': 'title,description'
            }
        })
        
        # Delete existing questions
        if 'items' in form:
            for item in reversed(form['items']):
                if 'questionItem' in item:
                    requests.append({'deleteItem': {'location': {'index': form['items'].index(item)}}})
        
        self.service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        # Add new questions
        requests = []
        for idx, q in enumerate(config['questions']):
            item = {'title': q['text'], 'questionItem': {'question': {'required': q.get('required', False)}}}
            
            if q['type'] == 'short_answer':
                item['questionItem']['question']['textQuestion'] = {'paragraph': False}
            elif q['type'] == 'paragraph':
                item['questionItem']['question']['textQuestion'] = {'paragraph': True}
            elif q['type'] == 'multiple_choice':
                item['questionItem']['question']['choiceQuestion'] = {
                    'type': 'RADIO',
                    'options': [{'value': opt} for opt in q['options']]
                }
            
            requests.append({'createItem': {'item': item, 'location': {'index': idx}}})
        

        
        self.service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
    
    def sync_forms(self):
        with open(self.input_file, 'r') as f:
            config = yaml.safe_load(f)
        
        for form_config in config['forms']:
            form_id_key = form_config['id']
            config_hash = self._compute_hash(form_config)
            
            if form_id_key in self.state:
                stored = self.state[form_id_key]
                if stored['hash'] != config_hash:
                    print(f"Updating form: {form_config['title']}")
                    self._update_form(stored['form_id'], form_config)
                    self.state[form_id_key]['hash'] = config_hash
                else:
                    print(f"No changes for form: {form_config['title']}")
            else:
                print(f"Creating form: {form_config['title']}")
                form_id = self._create_form(form_config)
                self.state[form_id_key] = {
                    'form_id': form_id,
                    'hash': config_hash,
                    'url': f"https://docs.google.com/forms/d/{form_id}/edit"
                }
                print(f"Form URL: {self.state[form_id_key]['url']}")
        
        self._save_state()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Google Forms from YAML configuration')
    parser.add_argument('--input-file', required=True, help='Path to YAML configuration file')
    args = parser.parse_args()
    
    manager = FormsManager(args.input_file)
    manager.sync_forms()
