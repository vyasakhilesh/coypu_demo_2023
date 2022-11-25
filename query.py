import requests
from .credentials import *
from .functions import *
import pandas as pd
from io import StringIO
print(__package__)
from os.path import join
from functools import reduce


class SPARQLRequest():
    def __init__(self, url, id_or_user=None, pass_or_secret=None,\
                 auth_type:str=None, is_fdq=False, is_fdq_serive=False):
        self.url = url
        self.id_or_user = id_or_user
        self.pass_or_secret = pass_or_secret
        self.auth_type = auth_type
        self.is_fdq = is_fdq
        self.is_fdq_serive = is_fdq_serive
    
    @auth
    def __set_params(self, accept_type='text/csv', *args, **kwargs):
        if self.auth_type:
            self.headers = {'Content-Type': 'application/sparql-query', 'Accept': accept_type,
                       'Authorization':self.auth}
        else:
            self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
    def __set_query(self, query):
        if self.is_fdq and self.is_service:
                self.query="query="+query+"&sparql1_1=True"
        elif self.is_fdq:
                self.query="""query="""+query
        
    @timer                    
    def execute(self, query, accept_type='text/csv'):
        self.__set_params()
        self.__set_query(query)
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=query, stream=True)
            if response.status_code == 200:
                print("Passed Query Description: {}".format(response.status_code))
                self.response = response
            else:
                print("Failed Query: {}".format(response.content))
        except Exception as e:
            print("Failed Query: {}".format(str(e)))
            
    @timer
    def save(self, save_path, filename:str):
        filename = '_'.join(filename.split(' '))
        if self.response.headers['Content-Type']=='text/csv':
            with open(join(save_path, filename+'.csv'), 'wb') as fd:
                for chunk in self.response.iter_content(chunk_size=128):
                    fd.write(chunk)
        elif self.response.headers['Content-Type']=='application/json':
            with open(join(save_path, filename+'.json'), 'wb') as fd:
                for chunk in self.response.iter_content(chunk_size=128):
                    fd.write(chunk)
            json_to_csv(self.response.json()['results']['bindings'], save_path, \
                filename, columns=[var+'.value' for var in self.response.json()['head']['vars']])    
        else:
            raise TypeError("Unknown response content-type")
        
        del self.response
        # return pd.read_csv(StringIO(str(response.content, 'utf-8')))
        

def main(client_url='', client_id='', client_secret='',
         query="""SELECT DISTINCT ?s ?o WHERE{?s a ?o.} LIMIT 10"""):
    
    cmemc_query = SPARQLRequest(client_url, client_id, client_secret)
    print(cmemc_query.get_response(query))
    
    
#    fuseki_query = Query(fuseki_endpoint, fuseki_user_infai, fuseki_pw_infai)
#    print (fuseki_query.get_response(query))
    

if __name__ == "__main__":
    
    query = """PREFIX  rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?s ?o WHERE{?s a ?o.} LIMIT 10"""
        
    main(client_url_tib, client_id_tib,
         client_secret_tib, query)
    main (client_url_imp, client_id_imp,
         client_secret_imp, query)
    main(client_url_infai, client_id_infai,
         client_secret_infai, query)
