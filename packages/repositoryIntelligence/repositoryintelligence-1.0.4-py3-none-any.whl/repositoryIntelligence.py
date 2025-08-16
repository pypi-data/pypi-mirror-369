#
# define a simple DataCiteRepository class to hold information about repositories
#
import  datetime
import  os
import  re                                           # the python regular expression library
import  requests                                     # used to make requests for data on the web using APIs
import  pandas as pd                                 # a python tool for data analysis and visualization in dataframes
from    collections import Counter
from    IPython.display import display, Markdown
from    tabulate import tabulate                     # makes pretty tables in many formats from dataframes
from    IPython.display import display, Markdown     # allows computation results to be displayed in markdown
from    matplotlib import pyplot as plt              # a python tool for creating plots of many kinds
import  ipywidgets as widgets                        # interactive widgets

from    jsonpath_ng.ext import parse                # a python tool for parsing json data, must be version 1.7.0

import  textwrap

import  datetime                                                  # the python datetime library, used to create a timestamp
timestamp = datetime.datetime.now().isoformat(timespec='hours')   # create an ISO timestamp with resolution of hours whenever this notebook is run

class DataCiteRepository:
    '''
        Define a simple DataCite Repository, a collection of metadata records associated with a particular client_id,
        to hold data and spiral scores.
    '''
    def __init__(self,
                 **kwargs):
        '''
            Arguments:
                rep_id: str                             # DataCite repository id
        '''
        self.source             = None                  # source of the repository metadata set during the data input.
                                                        # simple repositories have source = 'DataCite'
        self.name               = None                  # name of the repository
        self.provider           = None                  # argument is the path of the data
        self.client_id          = kwargs.get('rep_id')  # id of the repository
        self.numberOfRecords    = None                  # total numberOfRecords in repository (meta.total)
        self.recordsRetrieved   = None
        self.timestamp          = None                  # the time that the repository object is created
        self.json               = None                  # the json for the repository
        self.meta               = None
        self.metadata           = None
        self.query              = None
        self.URL                = None
        self.URL_l              = None
        self.notes_l            = None                  # a list of notes for the repository

        if 'rep_id' in kwargs.keys():
            self.source             = 'DataCite'                          # set the source of the repository
            self.client_id          = kwargs['rep_id']
            self.name               = self.getRepositoryName()            # set the name of the repository
            self.timestamp          = datetime.datetime.now().isoformat(timespec='minutes')
            self.query  = kwargs.get('query')
            self.URL_l  = self.makeURL(combineQueries=False, pageSize=1)
            if self.URL_l is not None:
                self.URL = self.URL_l[0]                                  # set the URL to the first URL in the list
            else:
                self.URL = None

            numberOfRecords         = self.getNumberOfRecords()           # get the number of records in the repository
            self.numberOfRecords    = numberOfRecords
       
        return
    

    def makeURL(self, pageSize: int = 1000, combineQueries: bool = True, **kwargs):
        '''
            Create a URL for the DataCite API query that includes the client-id, parameters, and queries.
            The arguments are:
                parameters: list of parameters to include in the URL (list of (parameter, [value]) tuples)
                queries:    list of queries to include in the URL (list of (query, value) tuples)
                target:     number of records to retrieve
        '''
        base_url = 'https://api.datacite.org/dois?'             # base DataCite URL

        URL     = f'{base_url}'
        if self.client_id != 'datacite.all':                    # if the client id is not datacite.all, add it to the URL
            URL    += f'&client-id={self.client_id}'
        URL        += '&affiliation=true&publisher=true'
        URL        += f'&page[size]={str(pageSize)}'            # create  URL with client id, affiliation, and publisher

        if 'fields' in kwargs.keys():
            URL += f"&fields[dois]={kwargs['fields']}"          # the fields parameter controls the metadata that is returned by the query
                                                                # it can be used to restrict the return to elements that are being updated
                                                                # for example, fields[dois]=publisher returns DOIs and publisher

        if combineQueries:                                      # combine queries
            p_l_l = []                                          # create a list of URL parameters from the parameters dictionary (name=value)
            if 'parameters' in kwargs.keys():                   # the parameters argument is a dictionary with the form {'name': parameterName, 'values': [value1, value2, ...]}                    
                for p in kwargs['parameters']:                  # loop parameters where p is a dictionary
                    p_l = []                                    # create a list of URL parameters from the parameters dictionary (name=value)
                    for v in p['values']:
                            p_l.append(p['name'] + '=' + v)              #
                    p_l_l.append(p_l)                           # add parameter list to list of parameter lists

            if 'queries' in kwargs.keys():                      # add queries to URL
                q_l = []
                for q in kwargs['queries']:
                    for v in q[1]:
                        q_l.append(q[0] + ':' + v)

            self.URL_l = []
            for u in list(itertools.product(*p_l_l)):              # create list of all combinations of items in url_parameter_lists
                self.URL_l.append(URL + '&'.join(u))

            return self.URL_l
        else:
            if 'parameters' in kwargs.keys():                       # add parameters to URL
                p = kwargs['parameters']
                URL += '&' + p['name'] + '=' + p['values'][0]
                self.description = p['name'] + ':' + p['values'][0]

            if self.query:                                           # add queries to URL
                if (' ' in self.query) or ("%20" in self.query) :
                    if self.query.startswith('"'):
                        self.query = self.query[1:]                  # remove leading quote if it exists
                    self.query = self.query.replace(' ', '%20')      # replace spaces with %20 for URL encoding
                    self.query = self.query.replace(':', ':"')       # insert quote at start of query value (after :)
                    self.query = self.query.replace('""', '"')       # insert quote at start of query value (after :)
                    if not self.query.endswith('"'):
                        self.query += '"'

                    self.query = self.query.replace(':"(', ':(')    # adjust queries with ( for grouping
                    self.query = self.query.replace('))"', '))')

                    if 'https:"' in self.query:                     # queries with RORs and fundref IDs include http: remove " after the :
                        self.query = self.query.replace('https:"', 'https:')

                    self.query = self.query.replace('https:"', 'https:')    # queries with RORs and fundref IDs include http: remove " after the :

                if '=' in self.query:                                    # if query contains '=', it is a parameter
                    URL += '&' + self.query                             # add query to URL
                elif ':' in self.query:                                  # if query contains ':', it is a query
                    URL += f'&query={self.query}'

        self.URL_l          = [URL]

        return self.URL_l


    def getNumberOfRecords(self):
        '''
            Get the number of records in the repository.
            If the repository is empty, return 0.

            Args:
                self (dataCiteRepository): The repository object.
                self.client_id (str): The client id for the repository (must be defined in repository)
                self.numberOfRecords (int): Assumed to be None at the start of the function, 
                                            if already defined, return value.
            Attributes:
                self.meta (dict): The metadata for the repository from the DataCite response
                self.numberOfRecords (int): The number of records in the repository
                self.URL (str): The URL for the repository used to retrieve numberOfRecords

            Returns:
                numberOfRecords (int): The number of records in the repository (defined as meta.total)

            Notes:
                This function does not set the repository data (metadata). It just retrieves the number of records.

        '''
        if self.numberOfRecords is None:                            # retrieve one record to get metadata
            if self.URL is None:                                    # if URL is not defined, create it
                self.URL = 'https://api.datacite.org/dois?'                  # base DataCite URL
                self.URL += 'client-id=' + self.client_id                    # add repository id to URL
                self.URL += '&affiliation=true&publisher=true'               # add affiliation and publisher to URL
                self.URL += '&page[size]=1'                                  # just get one record

            response = requests.get(self.URL)                            # retrieve one record

            if response.status_code != 200:
                print(f'Problem retrieving metadata from {self.URL}: {response.status_code}')
                print(f'Error message: {response.text}')
                self.numberOfRecords = 0
            else:
                self.meta            = response.json()['meta']             # retrieve metadata
                self.numberOfRecords = self.meta.get('total')              # retrieve the total number of records from meta
                return self.numberOfRecords
        else:                                                               # if the number of records is already defined, 
            return self.numberOfRecords                                     # just return it


    def getRepositoryName(self):
        '''
            Get the name of the repository.

            Args:
                self (dataCiteRepository): The repository object.

            Attributes:
                self.meta (dict): The metadata for the repository from the DataCite response
                self.name (str): Sets the name of the repository

            Returns:
                name (str): The name of the repository

            Notes:
                
        '''
        URL = f'https://api.datacite.org/clients?id={self.client_id}'         # create client search URL
        response = requests.get(URL)                                          # retrieve matching client data

        if response.status_code != 200:                                       # if there is a problem
            self.name = self.client_id
        else:
            retrieved_json = response.json()                                   # retrieve json data
            if len(response.json()['data']) > 0:                               # if there is data in the response
                self.name = response.json()['data'][0]['attributes']['name']
        
        return self.name                                                       # return the name of the repository
    

    def get_metadataPaging(self,
                recordLimit:    int = 2000,                 # maximum number of records to retrieve
                recordsPerPage: int = 1000,                 # number of records per page  
                randomSelection:bool = False):              # True => make random selection of records
        '''
            The DataCite API offers two ways to retrieve large sets of metadata: pages and cursors.
            This function uses the paging approach to retrieve up to recordLimit records for a repository

            Args:
                self (dataCiteRepository): The repository object.
                self.client_id (str): The client id for the repository (must be defined in repository)
                recordLimit:    int = 2000,                 # maximum number of records to retrieve
                recordsPerPage: int = 1000,                 # number of records per page  
                randomSelection:bool = False):              # True => make random selection of records (using DataCite random parameter)

            Attributes:
                self.meta (dict): The metadata for the repository from the DataCite response
                self.numberOfRecords (int): The number of records in the repository must be set before calling this function
                self.recordsRetrieved (int): The number of records retrieved from the repository
                self.metadata (list): The metadata for the repository from the DataCite response
                self.meta (dict):     The metadata for the retrieval from the DataCite response

            Returns:
                This function does not return anything. 
                It sets the metadata and meta attributes of the repository object.  

            Notes:
                
        '''
        #recordLimit = 2000

        if self.numberOfRecords > recordLimit:                              # if the number of records is greater than the record limit 
            recordsToRetrieve   = recordLimit                               # set the number of records to retrieve to the record limit
            pagesToRetrieve     = int(recordsToRetrieve / recordsPerPage)   # calculate the number of pages to retrieve
            randomSelection     = True                                      # set random selection to True
            print(f'Making random selection of {recordLimit} records from {self.numberOfRecords} records')
        else:
            pagesToRetrieve = int(self.numberOfRecords / recordsPerPage + 1)

        self.metadata   = []                 # initialize empty metadata list
        self.meta       = {}                 # initialize empty meta dictionary

        for page in range(1, pagesToRetrieve + 1):                      # loop through retrieval pages
                                                                        # retrieve page number (page) from repository
                                                                        
            if self.URL is None:
                self.URL     = 'https://api.datacite.org/dois?'                  # base DataCite URL
                self.URL     += 'client-id=' + self.client_id                    # add repository id to URL
                self.URL     += '&affiliation=true&publisher=true'               # add affiliation and publisher to URL
                self.URL     += '&disable-facets=true'                           # disable facet calculation to speed up retrieval

            if randomSelection:
                self.URL     += '&random=true'                               # add random selection to URL

            self.URL     += '&page[number]=' + str(page) + '&page[size]=' + str(recordsPerPage)      # add page number and size to URL

            print(f'Retrieving metadata: Page {page} of {pagesToRetrieve} URL: {self.URL}')

            response = requests.get(self.URL)

            if response.status_code != 200:                             # if the response is not 200, 
                                                                        # there was a problem retrieving the metadata
                print(f'Problem retrieving metadata from {self.URL}: {response.status_code}')
                print(f'Error message: {response.text}')
                self.numberOfRecords = 0
                return
            else:
                retrieved_json = response.json()
                if page == 1:                                   # retrieved_json['meta'] should be the same for all samples
                                                                # so copy retrieved_json['meta'] from first sample.
                    self.meta       = retrieved_json['meta']
                    self.metadata   = retrieved_json['data']            # copy metadata records to repository
                else:
                    self.metadata.extend(retrieved_json['data'])        # add metadata to repository
                    self.meta['total'] = len(self.metadata)             # increase count of records in data

                self.recordsRetrieved = len(self.metadata)
                if randomSelection:
                    duplicateCount = self.checkUniqueRecords()                # check for unique records
                    print(f'Page {page} of {pagesToRetrieve} retrieved: {len(self.metadata)} records with {duplicateCount} duplicates')
                    if duplicateCount > 0:                                 # if duplicates exist
                        self.removeDuplicates()                            # remove duplicate metadata records
                        self.recordsRetrieved = len(self.metadata)         # correct recordsRetrieved for dropped duplicates
                        print(f'Page {page} of {pagesToRetrieve} retrieved: {len(self.metadata)} records with {duplicateCount} duplicates removed')
                else:
                    print(f'Page {page} of {pagesToRetrieve} retrieved: {len(self.metadata)} records')

        return

    def checkUniqueRecords(self):
        '''
            Check for unique records in the metadata.
            return True if all records are unique, false if duplicates exist
        '''
        if self.metadata is None:
            print('No metadata to check')
            return

        if 'id' in self.metadata[0].keys():
            id_l = [r['id'] for r in self.metadata]
            return len(id_l) - len(set(id_l))
        else:
            print('No id field in metadata')


    def removeDuplicates(self):
        '''
            Remove duplicate records in the metadata.
            Return the number of duplicates removed.
        '''
        if self.metadata is None:
            print('Repository has no metadata to check for duplicates')
            return

        if 'id' in self.metadata[0].keys():
            id_l = [r['id'] for r in self.metadata]
            duplicates = len(id_l) - len(set(id_l))             # determine number of duplicates
            if duplicates > 0:                                  # if duplicates exist
                self.metadata = [m for i, m in enumerate(self.metadata) if m['id'] not in id_l[:i]]                     
            return duplicates
        else:
            print('No id field in metadata')
            return -1

    def createFacetsDictionary(self,
                               facetList:      list,      # list of facets e.g. ['states','resourceTypes','created'] see full list below
                               )-> dict:                  # json retrieved for item
      '''
          Read DataCite json response and create a summary dictionary for facets in a list.

          The DataCite json response is a dictionary with two items: 'data' is the metadata and 'meta' is a
          dictionary with metadata about the query results. The facets are in the meta section.

          For the facet f, the dictionary includes the query item, the timetamp, the numberOfRecords and
          the following statistics:
              f_number: the number of facet values
              f_max: the maximum facet value
              f_common: the name of the facet with the largest value
              f_total: the total of all of the facet values
              f_HI: the homogeneity index (f_max / f_total)
              f_coverage: f_total / NumberOfRecords
              f: the facet names and values written as a name (value) string
      '''
      #
      # initialize results dictionary
      #
      d_dict = {}                                                                    # initialize dictionary of results
      d_dict.update({'Repository_id': self.client_id, 'DateTime': self.timestamp})   # add client_id and timestamp to dictionary
      numberOfFacets = 0                                      # initialize numberOfFacets
      facet_l = []                                            # initialize facet list

      for f in facetList:                                     # loop facets (f), defult list of facets defined above.
          try:
              numberOfFacets = len(self.meta[f])              # determine the number of values for this facet (the length of the list of facet values)
          except:
              print(f'No facet {f}')
          finally:
              if numberOfFacets > 0:                                                         # populate dictionary for facet
                  d_dict[f + '_number']   = numberOfFacets                                   # add count (number of facet values) for facet
                  d_dict[f + '_max']      = max([d['count'] for d in self.meta[f]])          # add max count, the number of occurrences of the most common value for facet
                  d_dict[f + '_common']   = ', '.join([d['id'] for d in self.meta[f] \
                                              if d['count'] == d_dict[f + '_max']])          # add the most common value for the facet, the value with the maxCount.
                  d_dict[f + '_total']    = sum([d['count'] for d in self.meta[f]])          # add total for facet. The sum of the facet values (remember there are only ten values given)
                  d_dict[f + '_HI']       = d_dict[f + '_max'] /  self.numberOfRecords       # The homogeneity index (maxCount / total) for the facet. added 20220708
                  d_dict[f + '_coverage'] = d_dict[f + '_total'] / self.numberOfRecords      # %coverage, i.e. % of records) of top 10 values for facet. If coverage is 100%, all values are counted.
                                                                                             # If coverage is < 100% there are more than ten values for the facet element, facet is incomplete.
                  output = createCountStringFromListOfDictionaries(self.meta[f], False)      # Make a string that gives facet values and count: value1 (count1), value2 (count2), ..., valueN (countN)
                  d_dict[f] = output # add count string to dictionary                        # add the count string to the dictionary as a value with the name of the facet
                  facet_l.append({'repository_id':self.client_id,                            # add a dictionary with the facet data into the list of facets.
                                  'facet':    f,
                                  'number':   d_dict[f + '_number'],
                                  'total':    d_dict[f + '_total'],
                                  'common':   d_dict[f + '_common'],
                                  'max':      d_dict[f + '_max'],
                                  'HI':       d_dict[f + '_HI'],
                                  'coverage': d_dict[f + '_coverage'],
                                  'values':   d_dict[f]})

      return d_dict, pd.DataFrame(facet_l)      # return facet dictionary and facet dataframe for item

    def showRepositoryFacets(self,**kwargs):
        '''
            Display facet values for the repository in a markdown table.

            Args:
                self (dataCiteRepository): The repository object.
                type:    str,                               # facet or type of facet to display
                verbose: bool = False                       # True => display facet details

            Attributes:
                self.meta (dict): The metadata for the repository from the DataCite response
                self.facets_df (pd.DataFrame): The facets dataframe for the repository must exist
                self.notes_l (list): A list of notes for the repository

            Returns:
                This function creates a display for a notebook but does not return anything. 

            Notes:
                
        '''
        if self.notes_l == None:                                   # if notes list does not exist, create it
            self.notes_l = []
      
        if 'type' not in kwargs.keys():                            # if type is not in kwargs, display all facets'
            pd.set_option('display.max_colwidth', None)
            display(Markdown(f'# Repository Facet Report: {self.name} ({self.client_id}): {self.timestamp}, {self.numberOfRecords} records.'))
            display(Markdown(tabulate(self.facets_df.sort_values(by=['number', 'total'], ascending=[True, False]), 
                                        headers=list(self.facets_df.columns), tablefmt='pipe', floatfmt=".0%", maxcolwidths=500, showindex=False)))
            display(Markdown(f'These facets were retrieved using URL: {self.URL}'))
            return
        else:
            facetType = kwargs['type']          # get the facet type from kwargs

        if facetType == 'missing':              # missing facets are those that are in the list of facets (facet_names)
                                                # but not defined for the repository

            missing_facet_l = [x for x in facet_names if x not in list(self.facets_df.facet.values)]                           # compare found facets to list of all facets

            #display(Markdown(f'## Missing Facets'))
            display(Markdown(f'Missing facets are related to metadata elements that do not exist in the repository.'))

            if len(missing_facet_l) > 0:
                display(Markdown(f'Repository {self.client_id} is missing the following facets: {", ".join(missing_facet_l)}'))
                self.notes_l.append({'order': 1, 'repository': self.client_id, 'facet': 'missing facets', 'type':'Missing Facets', 'note': f'{", ".join(missing_facet_l)}'})
            else:
                display(Markdown(f'Repository {self.client_id} has no missing facets.'))
                self.notes_l.append({'repository': self.client_id, 'facet': 'missing facets', 'note': f'No Missing Facets'})

            return

        elif facetType == 'single':
            #display(Markdown(f'## Single Value Facets'))                        # find single value facets
            display(Markdown(f'Single Value Facets are typically set by the DataCite System and have a single value, Completeness = Coverage.'))
            df = self.facets_df[self.facets_df['number'] == 1]

        elif facetType == '2to9':
            #display(Markdown(f'## 2 <= Facet Number <= 9'))
            display(Markdown(f'Facets with 2 <= number <= 9 provide completeness information, Completeness = Coverage.'))
            df = self.facets_df[self.facets_df['number'].between(2, 9, inclusive='both')]

        elif facetType == '10':
            #display(Markdown(f'## Facet Number = 10'))
            display(Markdown(f'Facets with number = 10 do not provide completeness information, Completeness = Unknown.'))
            df = self.facets_df[self.facets_df['number'] == 10]

        elif facetType == '10+':
            #display(Markdown(f'## Facet Number > 10'))
            display(Markdown(f'Only two facets (published and resourceType) can have number > 10, Completeness = Coverage.'))
            df = self.facets_df[self.facets_df['number'] > 10]

        if len(df) > 0:
            display(Markdown(tabulate(df, headers=list(df.columns), tablefmt='pipe', floatfmt=".0%", showindex=False)))
            n_l = list(df[df['total'] < self.numberOfRecords].facet)               # list incomplete single value facets
            if len(n_l) > 0:
                self.notes_l.append({'order': 2, 'repository': self.client_id, 'facet': 'single value facets', 'type':'Incomplete Facets', 'note': f'{", ".join(n_l)}'})
        else:
            display(Markdown(f'Repository {self.client_id} has no facets in this category.'))
            self.notes_l.append({'repository': self.client_id, 'facet': facetType, 'note': f'No Facets in this category'})


    def saveFacets(self, outputDirectory: str):
      '''
          Save the facets dataframe to a file in the output directory.
      '''
      if self.facets_df is not None:
          facetFile = f'{outputDirectory}/facets__{self.timestamp}.csv'
          self.facets_df.to_csv(facetFile, index=False)
          display(Markdown(f'Facets saved to {facetFile}'))
      else:
          print('No facets to save')


    def get_spiral_data(self,
                        spiralCode_l: list,          # list of spiralCodes
                        save: bool = False,          # save the spiral data to a file
    ):
        '''
            Get repository spiral scores for a list of spiralCodes

            Each spiral includes metadata, a list of concepts, concept name and a list of paths:
                'title'         : 'DataCite Mandatory Fields in mdJSON',
                'code'          : 'DataCiteMandatorymdJSON',
                'description'   : 'mdJson Paths to DataCite Mandatory Fields',
                'items'         : [
                    concept:    The name of the concept
                    paths:      A list of paths for the concept (container and attribute), e.g. for dataCite.title:
                        {'concept': 'Resource Title',
                         'paths':
                            [
                                {'container': 'data[*].attributes.titles[*]', 'attribute': 'title'}
                            ]
                        }
                    ]
        '''
        global outputDirectory

        if not 'data' in self.metadata:                             # if metadata is not in a 'data' dictionary, wrap it in a 'data' dictionary
            self.metadata = {'data':self.metadata}                  # because paths are defined for 'data' dictionaries in spiral.py

        repository_score_d = {  'Repository_ID': self.client_id,                # initialize repository score dictionary with repository metadata
                                'FileName': self.name,
                                'DateTime': self.timestamp,
#                                'Number of Records': self.numberOfRecords}
                                'Number of Records': self.recordsRetrieved}     # for larger reporitories only a sample is retrieved.

        repository_content_d    = {}
        repository_score_l      = []

        spiral_l = []
        spiral_l = list(filter(lambda d: d['code'] in spiralCode_l, spiral_d))             # filter spirals to those with codes in spiralCode_l

        allConcepts = list(spiral_l[0]['items'])            # create list of concepts in all spirals starting with those in the first spiral
        for i in range(1, len(spiral_l)):                   # loop through remaining spirals and add items
            allConcepts.extend(spiral_l[i]['items'])        # add concepts from subsequent spirals to allConcepts list

        contentValue_df = pd.DataFrame()                    # create empty dataframe for values
        for concept in allConcepts:                         # loop through concepts in all spirals in spiral_l
            valueList = []                                  # initialize a list of values found for the concept
            value_l   = []                                  # initialize a list of values found for the concept to create concept dictionary
            doiList = []                                    # initialize a list of DOIs for the records with values

            for path in concept['paths']:                   # concepts can have multiple paths - loop all paths
                #
                # a path includes a container and an attribute
                # check the container for a variable identified as {{varibleName}}
                #
                m = re.search('\{\{(.*)\}\}',path['container'])
                if m is not None:                                       # path contains variable
                    variableName    = m.group(1)
                    variable_d      = next((item for item in allVariables if item['name'] == variableName), None)
                    variableValue   = variable_d['value']
                    pc              = path['container'].replace('{{' + variableName + '}}',variableValue)
                else:
                    pc = path['container']

                parsedPath = parse(pc).find(self.metadata)              # parse the path (jsonPaths) and find the metadata in the repository
                for match in parsedPath:                                # loop all matches for the path
                    conceptFound = False
                    if match.value is None:                             # no match for this path
                        valueCount = 0
                        recordCount = 0

                    elif isinstance(match.value, dict) and path['attribute'] in match.value:
                        #
                        # if the value is a list then it must be split into strings before adding to the valueList
                        #
                        if isinstance(match.value[path['attribute']],list):
                            #
                            # remove newlines and tabs from list items add to valuelist
                            #
                            for i in match.value[path['attribute']]:
                                #
                                # if the lit item is a dictionary (like affiliation can be), skip it
                                # as the element being searched for should be picked up with a path that
                                # includes the specific item in the dictionary, like affiliation['name']
                                # this was added to deal with files that have creator.affiliation as a list
                                # of strings in some cases and as a list of dictionaries in others
                                #
                                if isinstance(i, dict):
                                    continue
                                valueList.append((self.name + '\t' + concept['concept'] + '\t' + str(i).replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()))
                                value_l.append({'fileName': self.name,
                                                'concept': concept['concept'],
                                                'value': str(i).replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()})
                                conceptFound = True

                        elif isinstance(match.value[path['attribute']],(str,int,float,dict)) and match.value[path['attribute']] is not None:
                            #
                            # remove newlines and tabs from matched attribute and add to valuelist
                            #
                            valueList.append((self.name + '\t' + concept['concept'] + '\t' + str(match.value[path['attribute']]).replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()))
                            value_l.append({'fileName': self.name,
                                            'concept': concept['concept'],
                                            'value': str(match.value[path['attribute']]).replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()})

                            if len(str(match.value[path['attribute']]).replace('\n',' ').replace('\t',' ').strip().split('\n')) > 1:
                                print(f'newlines in value string')
                            conceptFound = True

                        if conceptFound:
                            recordIdentifier = None
                            if  match is not None and 'doi' in match.value:
                                recordIdentifier = match.value['doi']
                            elif match is not None and 'id' in match.value:
                                recordIdentifier = match.value['id']
                            elif match is not None and 'identifier' in match.value:                   # Dryad native
                                recordIdentifier = match.value['identifier']
                            elif match is not None and '_id' in match.value:                          # USGS ScienceBase JSON
                                recordIdentifier = match.value['_id']
                            elif match.context is not None and 'doi' in match.context.value:
                                recordIdentifier = match.context.value['doi']
                            elif match.context is not None and '_id' in match.context.value:          # USGS ScienceBase JSON
                                recordIdentifier = match.context.value['_id']
                            elif match.context is not None and 'identifier' in match.context.value:          # Dryad
                                recordIdentifier = match.context.value['identifier']
                            elif match.context.context is not None and 'doi' in match.context.context.value:
                                recordIdentifier = match.context.context.value['doi']
                            elif match.context.context is not None and 'identifier' in match.context.context.value:                 # Dryad Native metadata, doi is identifier
                                recordIdentifier = match.context.context.value['identifier']
                            elif match.context.context is not None and '_id' in match.context.context.value:          # USGS ScienceBase JSON
                                recordIdentifier = match.context.context.value['_id']
                            elif match.context.context is not None and \
                                    match.context.context.context is not None and 'doi' in match.context.context.context.value:
                                recordIdentifier = match.context.context.context.value['doi']
                            elif match.context.context is not None and \
                                    match.context.context.context is not None and \
                                    match.context.context.context.context is not None and \
                                'doi' in match.context.context.context.context.value:
                                recordIdentifier = match.context.context.context.context.value['doi']

                            doiList.append(recordIdentifier)

                # end of match processing
            # end of path processing (for path in concept['paths'])
            #
            # now count the values in valueList after filtering empty lines.
            # In order to do this with counter the items must be strings, not lists
            #
            valueCounter = Counter(valueList)               # valueList is a list of strings: filename\tconcept\tvalue and valueCounter
                                                            # is a dictionary with the string as the key and the count as the value
            valueCount = len(list(filter(None,valueList)))  # the number of times a value exists for this concept. This = len(value_l)
            valueCount = len(value_l)                       # the number of times a value exists for this concept. This = len(value_l)
            #
            # count unique DOIs
            #
            recordCounter   = Counter(doiList)
            recordCount     = len(list(filter(None,recordCounter.keys())))  # the number of records that have a value
            record_count    = len(doiList)

            repository_score_d.update({concept['concept'] + '_exist':   valueCount})    # add the number of times this path exists (valueCount) to the repository_score_d dictionary
            repository_score_d.update({concept['concept'] + '_records': recordCount})   # add the number of records that have a value for this concept to the repository_score_d dictionary

            repository_content_d.update(valueCounter)                                   # valueCounter is the dictionary of values for this concept

            contentValue_df = pd.concat([contentValue_df, pd.DataFrame(value_l)], ignore_index=True)    # add this concept to contentValue_df

        repository_score_l.append(repository_score_d)
        #
        # after all data files in the dataDirectory are analyzed, create results data frames
        #
        self.conceptCounts_df = pd.DataFrame(repository_score_l)
        #
        # output metadata content to file named 'collectionContent__timestamp.csv' in outputDirectory
        #
        contentFileName = outputDirectory + '/collectionContent__' + self.timestamp + '.csv'
        contentValue_l = []
        for h,c in repository_content_d.items():
            file, concept, value = h.split('\t')
            contentValue_l.append({'File': file, 'Concept': concept, 'Value': value, 'Count': c})
        self.contentValue_df = pd.DataFrame(contentValue_l)
        self.contentValue_df.to_csv(contentFileName,sep='\t', index=False)
        print(f'{len(self.contentValue_df)} lines of content written to {contentFileName}')

        self.spiralScores_d = {}

        for spiral in spiral_l:                             # loop spirals and create output files
            #
            # create header
            #
            concept_header = []
            concept_header = createConceptHeader(spiral)
            print(f"{spiral['code']} {len(concept_header) - 7} concepts")
            #
            # initialize a spiral dataframe with concept_header
            #
            spiral_df = pd.DataFrame(columns=concept_header)
            #
            # initialize the first 4 fields of the spiral_df
            # Repository_ID, FileName, DateTime, Number of Records
            #
            for i in range(0,4):
                spiral_df[concept_header[i]] = self.conceptCounts_df[concept_header[i]]
            #
            # calulate % columns, the number of records / the number retrieved.
            #
            for concept in concept_header[7:]:
                spiral_df[concept] = self.conceptCounts_df[concept + '_records']/self.conceptCounts_df['Number of Records']
            #
            # calculate summary columns
            #
            spiral_df['Average'] = (spiral_df.iloc[ : , 7: ].apply(trimLargeCounts).sum(axis=1))/len(spiral['items'])
            spiral_df['Exist'] = spiral_df.iloc[ : , 7: ].apply(conceptExists).sum(axis=1).astype('int')
            spiral_df['Complete'] = spiral_df.iloc[ : , 7: ].apply(trimLargeCounts).apply(conceptComplete).sum(axis=1).astype('int')
            #
            # merge in provider and repository names
            #
            self.spiralScores_d[spiral['code']] = spiral_df
            #
            # output spiral result
            #
            outputFileName = outputDirectory + '/' + spiral['title'] + '__' + self.timestamp + '.csv'
            output_df = spiral_df

            print(f'OutputFile: {outputFileName}\n')
            output_df.to_csv(outputFileName,sep=',',index=False)

        self.metadata = self.metadata['data']                  # unwrap the metadata from the 'data' dictionary


    def get_spiral_summary(self):
        '''
            Make a summary dataframe of the spirals for the repository
        '''
        #
        # make a series of all unique data file names by combining the FileName
        # columns of all dataframes and then selecting unique values
        #
        global outputDirectory                                                  # define output directory

        allDataFiles = pd.Series(dtype = 'object')

        spiralCode_l = list(self.spiralScores_d.keys())                         # get spiralCodeList from spiralScores_d
        for sc in spiralCode_l:
            allDataFiles = allDataFiles._append(self.spiralScores_d[sc]['FileName'])           # append is deprecated for series
        #
        # pick the first spiral for number of records
        #
        spiral = next((s for s in spiral_d if s['code'] == spiralCode_l[0]), None)

        allTotals = []

        for f in allDataFiles.unique(): # loop the data files
            if f == 'Average':  # skip Average
                continue

            if not(isinstance(f, str)):
                continue

            f_dict = {}                 # create dataframe for datafile
            f_dict['FileName'] = f
            f_dict['Repository_ID'] = '.'.join(f.split('.')[0:2])
            #
            # get the number of records for repository by defining s, the rows in the first data dataframe with
            # FileName == f
            #
            s = self.spiralScores_d[spiralCode_l[0]].loc[self.spiralScores_d[spiralCode_l[0]]['FileName'] == f]['Number of Records']
            f_dict['Number of Records'] = int(s.iloc[0])
            for sc in spiralCode_l:
                dframe = self.spiralScores_d[sc]                        # retrieve data for spiral sc
                s = dframe.loc[dframe['FileName'] == f]['Average']      # find Total for FileName in data[sc]
                spiralTitle = next((s for s in spiral_d if s['code'] == sc), None)['title']
                f_dict[spiralTitle] = s.iloc[0]                         # add score for spiral sc to dictionary
            allTotals.append(f_dict)                                    # add file dictionary to list
        #
        # Add summary to spiralScores_d
        #
        self.spiralScores_d['Total'] = pd.DataFrame(allTotals) # create dataframe from list of file dictionaries
        self.spiralScores_d['Total']['Total'] = self.spiralScores_d['Total'].apply(lambda row: self.getDataFileTotal(), axis=1)
        self.spiralScores_d['Total'].sort_values(by=['Total'],inplace=True,ascending=False)

        outputFileName = outputDirectory + '/spiralSummary__' + self.timestamp + '.csv'
        print(f'OutputFile: {outputFileName}\n')
        self.spiralScores_d['Total'].to_csv(outputFileName,sep=',',index=False)


    def getUniqueValueAndOccurrenceCounts(self, contentCounts):
        """
            This function takes a repository object and a contentCounts DataFrame, and 
            adds a DataFrame with the number of unique values and occurrences for each documentation 
            concept in the metadata.
            
            Args:
                self (repositoryIntelligence.DataCiteRepository): The repository object.
                contentCounts:      a dataframe with concepts as the index and two columns: 
                                    numberOfOccurrences and perRecord
            Attributes:
                self.meta (dict): The metadata for the repository from the DataCite response
                self.contentValue_df (dataFrame): Must be defined
                self.uniqueValueAndOccurrenceCounts_df (dataFrame): A dataframe with the number of unique values and occurrences for each documentation concept in the metadata.

            Returns:
                This function returns the uniqueValueAndOccurrenceCounts_df dataFrame which contains 
                the number of unique values and occurrences for each documentation concept in the 
                spirals metadata.

            Notes:

        """
        self.uniqueValueAndOccurrenceCounts_df = pd.DataFrame()  # Initialize the DataFrame to store unique value and occurrence counts

        # Get the unique values and their counts
        value_counts_series = self.contentValue_df.Concept.value_counts()
        
        # Convert to DataFrame using reset_index()
        df = value_counts_series.reset_index()
        df['Concept'] = df['Concept'].astype(str)
        
        # Merge with contentCounts DataFrame
        self.uniqueValueAndOccurrenceCounts_df = contentCounts.merge(df, on='Concept', how='left')
        self.uniqueValueAndOccurrenceCounts_df.rename(columns={'count': 'Number of Unique Values'}, inplace=True)
        columns = ['Concept', 'Number of Unique Values', 'Number of Occurrences', 'perRecord']
        self.uniqueValueAndOccurrenceCounts_df = self.uniqueValueAndOccurrenceCounts_df[columns]

        return self.uniqueValueAndOccurrenceCounts_df


    def getDataFileTotal(self):
        #
        # loop dataframes in self.spiralScores_d and calculate the total index for a data file
        #
        total = 0.0
        totalScore = 0.0
        totalCount = 0
        for sc in list(self.spiralScores_d.keys()):                             # get spiralCodeList from spiralScores_d

            if sc == 'Total':                                                   # skip Total dataframe
                continue

            spiral_df = self.spiralScores_d[sc]                                 # select data spiral for spiral sc
            spiralPercent = spiral_df[spiral_df['FileName'] == self.name]['Average'].values[0]

            spiral = next((s for s in spiral_d if s['code'] == sc), None)      # look up spiral in spiral_d to get number of items
            spiralConceptCount = len(spiral['items'])

            totalScore += spiralPercent * spiralConceptCount
            totalCount += spiralConceptCount

        return totalScore / totalCount  # return total score as a %
#
# End of DataCiteRepository Class
#
# Utility functions:
#   These functions are used to create plots and tables for the repository insights
#   and to create the output directory for the repository insights

def findDataDirectory(repository_id: str):
    '''
        Define the location of the directory for outputs and plots. If this notebook is running locally
        the output directory can be defined by the environment variable DATACITE_DATA. This keeps all
        of the repository insights output in one location.

        If the notebook is running in Google collab, the output directory is set to a sub-directory of
        the current working directory with the reposiroty id as the name.
    '''
    global outputDirectory
    
    try:  
        dataCiteData = os.environ['DATACITE_DATA']
        if dataCiteData[-1] != '/': dataCiteData += '/'  # make sure there is a trailing slash
        outputDirectory = dataCiteData + repository_id
        outputDirectory = os.path.expanduser(outputDirectory)
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory, exist_ok=True)
    except:
        print('DATACITE_DATA environment variable not set. Using current directory for output.')
        outputDirectory = os.getcwd() + '/' + repository_id
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory, exist_ok=True)

    print(f'Output data and plots are in  {outputDirectory}')
    return outputDirectory


def makeRadarPlot(title, df, row, startColumn):
    '''
      This function uses matplotlib to make a radar plot of the results
    '''
    pi = 3.1415926535897932384  # pi

    ax = plt.subplot(polar="True")
    #
    # define categories, angles, values
    #
    categories = df.iloc[row,startColumn:].index.tolist()               # get the categories from the dataframe after the header columns
    N = len(categories)                                                 # number of categories

    values = df.iloc[row,startColumn:].values.tolist()                  # trim the values that are > 1 to 1
    values += values[:1]
    for i in range(len(values)):
        values[i] = min(1.0,values[i])

    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    plt.polar(angles, values)
    plt.fill(angles, values, alpha=0.3)
    plt.xticks(angles[:-1], categories, size=8)                        # was 16
    for label,i in zip(ax.get_xticklabels(),range(0,len(angles))):
        if angles[i] == 0:
            label.set_horizontalalignment('center')
        elif angles[i] < pi:
            label.set_horizontalalignment('left')
        elif angles[i] == pi:
            label.set_horizontalalignment('center')
        else:
            label.set_horizontalalignment('right')

    wrap_labels(ax, 20)                             # trying to stop label overlap

    ax.set_rlabel_position(0)
    ax.set_theta_offset(pi/2)
    ax.set_theta_direction(-1)
    title = f"{title} ({df.at[row,'Average']:.0%})"
    ax.set_title(title,size=18,y=1.1)

    plt.yticks([.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0], color='grey',size=9)
    plt.ylim(0,1)


def wrap_labels(ax, width, break_long_words=False):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text().replace('Identifier','ID')          # Replace Identifier with ID
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=0)


def createConceptHeader(spiral)-> list:
    '''
        This function creates a header for the spiral dataframe.
        It includes eight header columns and a columm for each item.concept
        in the spiral (in alphabetical order).
    '''
    concept_header = ['Repository_ID','FileName','DateTime','Number of Records','Exist','Complete','Average']
    concepts = []
    for item in spiral['items']:
        concepts.append(item['concept'])

    concept_header.extend(sorted(list(set(concepts))))
    return concept_header

#
# These functions are used to filter dataframes to compute summary statistics
#
def trimLargeCounts(x):
    return x.mask(x>1.0, 1.0)


def conceptExists(x):
    return x.mask(x>0, 1.0)

def conceptComplete(x):
    return x.mask(x<1, 0)

def makeSquishedTable(df, numberOfSets=2):
    '''
        This function takes a dataframe and returns a dataframe with long rows 
        compressed into columns. This is used to convert a spiral results table
        with 25 columns in two rows intof a table with seven rows and eight columns
        (numberOfSets = 4). The squishing makes it possible to include the table 
        in a report with portrait orientation
        
        Args:
            df (dataframe): The dataframe to be squished
            numberOfSets (int, default = 2): The number of sets of columns

        Attributes:

        Returns:
            table_df (dataframe): The squished dataframe

        Notes:
    '''

    df_t    = df.transpose()                                       # transpose the dataframe so that concepts are rows instead of columns

    for i in range(len(df_t)):                                     # convert floats to % in Scores
        if isinstance(df_t.iloc[i,0], float):
                df_t.iloc[i,0] = f'{df_t.iloc[i,0]:.0%}'

    if len(df.columns) / numberOfSets == int(len(df.columns) / numberOfSets):   # calculate the number of rows per set, rounding up if necessary
        rowsPerSet = int(len(df.columns) / numberOfSets)
    else:
        rowsPerSet = int(len(df.columns) / numberOfSets) + 1

    table_df = pd.DataFrame()
    i = 0
    col = []

    while i < len(df_t):
        j = i + rowsPerSet
        df_i = df_t.iloc[i:j]
        df_i.reset_index(inplace=True)
        table_df = pd.concat([table_df, df_i], axis=1, ignore_index=True)
        col.extend(['Concept', 'Score'])
        i += rowsPerSet

    table_df.columns = col
    return table_df.fillna('')


def makeItemDisplay(p_l: list):
    '''
        This function takes a dictionary and returns a string that can be displayed in markdown.
    '''
    d_l = []
    for p in p_l:
        c = re.sub(r'.*attributes[\[\]\*\.]*','',p['container'])
        c = c.replace('*','\*')
        if c:
            d_l.append(f"{c}.{p['attribute']}")
        else:
            d_l.append(p['attribute'])
    return ', '.join(d_l)


def displayConceptMapping(spiralCodeList, rep):
    '''
        This function takes a list of spiral codes and a repository object and returns a dictionary with 
        the mapping of concepts in the spirals to DataCite metadata.
        It also displays the mapping in a markdown table.

        Args:
            spiralCodeList (list): A list of the spiral codes to display.
            rep: (repositoryIntelligence.DataCiteRepository): The repository object.

        Attributes:

        Returns:

        Notes:
    '''
    for sc in spiralCodeList:                                           # loop through the spiral codes

        spiral_l = list(filter(lambda d: d['code'] == sc, spiral_d))    # filter spirals to those with codes in spiralCodeList
        spiral = spiral_l[0]                                            # we expect there to be only one spiral with this code
                                                                        # this could be a problem in the future if we add spirals    

        display(Markdown(f"### Spiral {spiral.get('title')} ({spiral.get('code')})"))
        display(Markdown(f"{spiral.get('description')}"))
        display_df = pd.DataFrame(spiral.get('items'))
        display_df['Paths'] = display_df['paths'].apply(makeItemDisplay)
        display(Markdown(tabulate(display_df[['concept','Paths']], headers=['Concept','Paths (after data[\*].attributes)'], tablefmt='pipe', showindex=False)))


#
# this cell has data about dataCite facets that are used later in this notebook.
#
outputDirectory = None                      # define the directory for output data and plots. 
                                            # Use local variable DATACITE_DATA if available
                                            # or use the current working directory if not.

facet_description_d = {             # a dictionary with facet names (as keys) and descriptions.
	'affiliations':
		{'description':'''The **affiliations** facet might better be named affiliationIdentifiers as it gives data about RORs used as affiliation identifiers.'''
		},
	'citations':
		{'description':'''The **citations** column shows the number of citations to items in the repository each year.'''
		},
	'certificates':
		{'description':'The **certificates** facet gives the repository certificates (i.e. CoreTrustSeal).'
		},
	'clients':
		{'description':'''The **clients** facet shows the number of clients included in the query result. Clients are essentially repositories managed by a provider. The repository id combines the provider and the client separated by a '.', i.e. id = provider.client. The queries used to create these facet reports are repository queries so they only have one client.'''
		},
	'created':
		{'description':'''The **created** facet shows the number of DOIs created each year.'''
		},
	'fieldsOfScience':
		{'description':'''The [Fields of Science](https://interoperable-europe.ec.europa.eu/collection/eu-semantic-interoperability-catalogue/solution/field-science-and-technology-classification) are a standard list of high-level scientific domains or fields developed by UNESCO. They are used by DataCite to provide some standardization in the subject fields (which are free text). FOS keywords are written as Fos:value in order to identify them and include them in this facet.'''
		},
	'licenses':
		{'description':'''The **licenses** facet shows the licenses used in the repository and the number of occurrences of each.'''
		},
	'linkChecksStatus':
		{'description':'''The **linkChecksStatus** facet shows the status of the landing pages of DOIs in the search (when and if last checked) with counts.'''
		},
	'providers':
		{'description':'''The **providers** facet shows the number of providers included in the query result. Providers are DataCite members and may have more than one repository. The first part of the repository id, i.e. before the '.' is an abbreviation for the provider. The queries used to create these facet reports are repository queries so they only have one provider.'''
		},
	'prefixes':
		{'description':'''DOI **prefixes** are the numbers, startng with '10.' that occur before the first slash in a DOI.Most repositories include DOIs with the same predix, although there are some large repositories that use prefixes to group DOIs within the repository. These have more than one prefix.'''
		},
	'published':
		{'description':'''The **published** facet shows the number of resources published each year. Resource publication dates can be different than DOI creation or registration dates so it is not unusual for the published date to have more facets (years) than the created or registered facets.'''
		},
	'resourceTypes':
		{
			'description':'''The DataCite metadata schema supports DOIs for many types of resources. The resourceType facet shows the number of occurrences of each resource type. The **common** column shows the most common resource type in the repository. It is not unusual for a repository to focus on a small number of resource types, even a single resource type. In these cases the **number** column is 1 and the **values** column shows only one value with a count that matches the number of records in the repository.'''
		},
	'registered':
		{'description':'''The **registered** facet shows the number of DOIs registered each year.'''
		},
	'schemaVersions':
		{'description':'''The DataCite metadata schema has a number of versions with 4.6 being the most recent version. The **schemaVersions** colum lists schema versions present in the repository. All versions earlier than 4 are deprecated, so if one of those is present, it is flagged as a warning.'''
   	},
	'states':
		{
			'description':'''DataCite DOIs can exist in several different states: findable, and all records have a state. Most records are in the findable state, i.e. they are available through the API and can be found. In those cases, the number of states is 1 and the total is the number of records in the repository.'''
		},
	'subjects':
		{'description':'''The DataCite metadata schema defines **subjects** as free text keywords describing topics relevant to DOIs. The subjects for a repository provide and overview of the domains covered by the repository.'''
		},
	'views':
		{'description':'''The **views** facet shows the number of views of items in the repository each year.'''
		},
	'downloads':
		{'description':'''The **downloads** facet shows the number of downloads of items in the repository each year.'''
		}
}

facet_names = list(facet_description_d.keys())                      # create a list of facet names from the keys of the description dictionary

facets_l = []                                                       # organize the facet descriptions into a list of dictionarys to create a dataframe for displaying the descriptions
for k,v in facet_description_d.items():                             # loop the items (keys and values) in the dictionary
  facets_l.append({'Facet':k, 'Description':v['description']})      # add a dictionary for each facet to the list.

notes_l = []

facetStatistics_d = {                                               # these are the definitions of the columne in the facets table
    'facet':      'The name of the facet',
    'number':     'The number of unique values of the facet metadata element, <= 10 for all but published and resourceTypes',
    'total':      'The total number of records with the top 10 facet metadata element values, i.e. the total listed in the facets.',
    'common':     'The most common facet id (meant for machines), equals value in some cases.',
    'max':        'The number of occurrences of the most common facet value, listed first in the values column.',
    'homogeneity (HI)': 'An indicator of homogeneity of the facet: maximum count / total count (0.1 = uniform, 1.0 = single item)',
    'coverage':   'The % of all records covered by the top 10 facet values (numbers close to 100% mean the 10 facet values cover most of the repository).',
    'values':     'The facet values and their counts, e.g. value1 (count1), value2 (count2), ..., valueN (countN).'
}

def showFacetColumnDefinitions():
    display(Markdown('### Column definitions:'))
    display(Markdown("Facets have id's for machines and values for humans, e.g. id='sjyq.oozvia' and value='Metadata Game Changers'."))
    fs_s = '| Name  | Description|\n|:-------- |:------|\n'
    for k,v in facetStatistics_d.items():
        fs_s += f'| {k} | {v} |' + '\n'
    display(Markdown('\n' + fs_s))
    display(Markdown('*Keep in mind that for most facets dataCite provides just the top ten values.*'))


def makeFacetTable():
    '''
        Make a markdown table with the facet descriptions.

        Parameters:
        facet_d: the dictionary with facet names as keys and descriptions.
    '''
    global facet_description_d
    s = '| Facet  | Description|\n|:-------- |:------|\n'
    nl = '\n'
    for k,v_d in list(sorted(facet_description_d.items())):
        s += f'| {k} | {v_d["description"].replace(nl,"")} |' + '\n'
    display(Markdown('\n' + s))


#
# Repository facet functions
#   These functions are related to repository facets and are used to read, store, and display facet data
#
def createFacetsDictionary(self,
							facetList:      list,      # list of facets e.g. ['states','resourceTypes','created'] see full list below
							)-> dict:                  # json retrieved for item
	'''
		Read DataCite json response and create a summary dictionary for facets in a list.

		The DataCite json response is a dictionary with two items: 'data' is the metadata and 'meta' is a
		dictionary with metadata about the query results. The facets are in the meta section.

		For the facet f, the dictionary includes the query item, the timetamp, the numberOfRecords and
		the following statistics:
			f_number: the number of facet values
			f_max: the maximum facet value
			f_common: the name of the facet with the largest value
			f_total: the total of all of the facet values
			f_HI: the homogeneity index (f_max / f_total)
			f_coverage: f_total / NumberOfRecords
			f: the facet names and values written as a name (value) string
	'''
	#
	# initialize results dictionary
	#
	d_dict = {}                                                                    # initialize dictionary of results
	d_dict.update({'Repository_id': self.client_id, 'DateTime': self.timestamp})   # add client_id and timestamp to dictionary
	numberOfFacets = 0                                      # initialize numberOfFacets
	facet_l = []                                            # initialize facet list

	for f in facetList:                                     # loop facets (f), defult list of facets defined above.
		try:
			numberOfFacets = len(self.meta[f])              # determine the number of values for this facet (the length of the list of facet values)
		except:
			print(f'No facet {f}')
		finally:
			if numberOfFacets > 0:                                                         # populate dictionary for facet
				d_dict[f + '_number']   = numberOfFacets                                   # add count (number of facet values) for facet
				d_dict[f + '_max']      = max([d['count'] for d in self.meta[f]])          # add max count, the number of occurrences of the most common value for facet
				d_dict[f + '_common']   = ', '.join([d['id'] for d in self.meta[f] \
											if d['count'] == d_dict[f + '_max']])          # add the most common value for the facet, the value with the maxCount.
				d_dict[f + '_total']    = sum([d['count'] for d in self.meta[f]])          # add total for facet. The sum of the facet values (remember there are only ten values given)
				d_dict[f + '_HI']       = d_dict[f + '_max'] /  self.numberOfRecords       # The homogeneity index (maxCount / total) for the facet. added 20220708
				d_dict[f + '_coverage'] = d_dict[f + '_total'] / self.numberOfRecords      # %coverage, i.e. % of records) of top 10 values for facet. If coverage is 100%, all values are counted.
																							# If coverage is < 100% there are more than ten values for the facet element, facet is incomplete.
				output = createCountStringFromListOfDictionaries(self.meta[f], False)      # Make a string that gives facet values and count: value1 (count1), value2 (count2), ..., valueN (countN)
				d_dict[f] = output # add count string to dictionary                        # add the count string to the dictionary as a value with the name of the facet
				facet_l.append({'repository_id':self.client_id,                            # add a dictionary with the facet data into the list of facets.
								'facet':    f,
								'number':   d_dict[f + '_number'],
								'total':    d_dict[f + '_total'],
								'common':   d_dict[f + '_common'],
								'max':      d_dict[f + '_max'],
								'HI':       d_dict[f + '_HI'],
								'coverage': d_dict[f + '_coverage'],
								'values':   d_dict[f]})

	return d_dict, pd.DataFrame(facet_l)      # return facet dictionary and facet dataframe for item


def showRepositoryFacets(self):
	pd.set_option('display.max_colwidth', None)
	display(Markdown(f'# Repository Facet Report: {self.client_id}: {self.timestamp}, {self.numberOfRecords} records.'))
	display(Markdown(tabulate(self.facets_df.sort_values(by=['number', 'total'], ascending=[True, False]), 
							headers=list(self.facets_df.columns), tablefmt='pipe', floatfmt=".0%", maxcolwidths=500, showindex=False)))
	display(Markdown(f'These facets were retrieved using URL: {self.URL}'))


def saveFacets(self, outputDirectory: str):
	'''
		Save the facets dataframe to a file in the output directory.
	'''
	if self.facets_df is not None:
		facetFile = f'{outputDirectory}/facets__{self.timestamp}.csv'
		self.facets_df.to_csv(facetFile, index=False)
		display(Markdown(f'Facets saved to {facetFile}'))
	else:
		print('No facets to save')

def createCountStringFromListOfDictionaries(l:list,                 # list of property dictionaries ({})
                                            useID:bool              # use repository id instead of name as title
                                            )->str:
    '''
        Make a list of counts from DataCite list of property dictionaries (l)

        The list has the form title1 (count1), title2 (count2), ...
    '''
    s = ''

    if useID:                           # use repository id as column title
        s = ", ".join([d['id'] + ' (' + str(d['count']) + ')' for d in l])
    else:                               # use repository name as column title (default)
        s = ", ".join([d['title'].replace(',',';') + ' (' + str(d['count']) + ')' for d in l])


    return s


def createDictionaryFromCountString(s: str)-> dict:
    '''
        Convert a count string like Aalto University (69), University of Lapland (8)
        into a dictionary like {'Aalto University':69, 'University of Lapland':8}
    '''
    if not isinstance(s,str):
        return

    d_ = {}
    pc = re.compile('^(?P<value>.*?)\((?P<count>[0-9]+?)\)$')

    items = s.replace(' ','').split(',')
    for i in items:
        m = re.match(pc, i)
        if m is None:
            print(f'No match: {i}')
            continue
        md = m.groupdict()
        if md['value'] is not None:
            d_[md['value']] = int(md['count'])
        else:
            d_[md['None']] = int(md['count'])

    return d_


def gatherInsights(f, r, df):
    '''
        Gather insights from the facet data, create a string of markdown text with insights.
    '''
    insights_d = {
        'states':
        {
            'insights':
            [
                {
                    'name':'Records Are Findable',
                    'condition': "int(df.loc[(r, f),'number']) > 0",
                    'statements': {
                        'True': 	f"Repository {r} has {df.loc[(r, f),'total']} Findable records.",
                        'False': 	"Some records in the repository are findable."
                    }
                }
            ],
        },
        'resourceTypes':
        {
            'insights':
            [
                {
                    'name':'Resource Types Exist',
                    'condition': "df.loc[(r, f),'number'] > 0",
                    'statements': {
						'True': 	f"Repository {r} has {df.loc[(r, f),'number']} resourceTypes. The most common ({df.loc[(r,f),'HI']:.0%}) is {df.loc[(r, f),'common']}",
                        'False': 	"No resource types were found in the repository."
                    }
                },
                {
                    'name':'All Records Have Resource Types',
                    'condition': "df.loc[(r, f),'coverage'] >= 1.00",
                    'statements': {
                        'True': 	f"All records have resourceTypes.",
                        'False': 	f'Repository has a low resourceType coverage of {df.loc[(r, f),"coverage"]:.2%}.'
                    }
                },
            ]
        },
    	'schemaVersions':
        {
            'insights':
            [
                {
                    'name':'Multiple Schema Versions',
                    'condition': "df.loc[(r, f),'number'] == 1",
                    'statements': {
                        'True': 	"Only one schema version exists in the repository.",
                        'False': 	"Multiple schema version exists in the repository."
                    }
                },
                {
                    'name':'Schema Version 3 Exists',
                    'condition': "'Schema 3' not in df.loc[(r, f),'values']",
                    'statements': {
                        'True': 	"Schema version 3 does not exist in the repository.",
                        'False': 	"Schema 3, deprecated on January 1, 2025, exist in the repository."
                    }
                }
            ]
        }
    }

    if f not in insights_d:
        return None, None

    s = ''
    warn_l = []

    for i in insights_d[f]['insights']:
        if eval(i.get('condition')):
            pass
            #display(Markdown(i.get('statements').get('True')))
        else:
            s += f'<font color="red" size="6">{i.get("statements").get("False")}</font>\n\n'
            warn_l.append({'repository': r, 'facet': f, 'warning':i.get('name'), 'note': ''})
            #display(Markdown(s))

    return s, warn_l

def makeFacetBarGraph(facet, rep_id, rep):
    '''
        Make a bar graph of the facet data for the repository.
        The graph is a horizontal bar graph with the facet values on the y-axis and the counts on the x-axis.
        The graph is created using matplotlib and is saved to the output directory.
    '''
    global outputDirectory
    if facet in list(rep.facets_df.facet.values):
        df = facetListRowToDataframe(rep.facets_df, facet)
        cnt_df = df.iloc[0,7:].astype(int)
        facet_plot = cnt_df.plot.barh(title=f'{rep_id} {facet}')                                # plot the summary data for the repository
        return facet_plot
    else:
        display(Markdown(f'Repository {rep_id} has no {facet} data'))
        return None
    
def facetListRowToDataframe(df, facet):
    '''
        convert row of facet dataframe to dataframe with header and values
    '''
    h = df[df['facet'] == facet].iloc[0,:7]                                     # get the header information for the facet
    #p   = ' ?(?P<facet>[A-Za-z 0-9]*?) \((?P<cnt>[0-9]*?)\)'                   # initial regular expression to extract the facet and count
    p   = ' ?(?P<facet>[A-Za-z 0-9\.;:-]*?) \((?P<cnt>[0-9]*?)\)'               # regular expression with punctuation to extract the facet and count
    m   = re.findall(p, df.loc[df['facet'] == facet]['values'].values[0])       # extract the facets and counts from the values to list of tuples
    idx, values = zip(*m)                                                       # unzip the list of tuples into two lists
    a = pd.Series(values, idx).sort_index()                                     # create a series from the values and index
    return pd.DataFrame(pd.concat([h,a],axis=0)).transpose()                    # create a dataframe from the header and series
#
# End of Facet Code - Beginning of useCase Code
#
# This code is used tomeasure repositories for various use cases.
# 
#@title Define Spiral Data (run this cell to define spiral data)
#
# this cell has data about metadata spirals that are used later in this notebook.
#
# Metadata exist in many dialects and communities that use these dialects share many needs.
# The spirals used here are defined in terms of dialect independent concepts so that they spirals
# can be shared across multiple dialects. For example, the concepts "Abstract", "Title", and "author"
# exist in nearly all dialects, but they have different names. In the DataCite dialect, the focus of
# this notebook, these concepts are called description, title, and creator. Mappings between the
# concepts and the DataCite metadata dialect are shown at the bottom of the notebook.
#
# Data for the spirals is in the sprial_d dictionary. Each spiral has metadata (title, code, dialect, description)
# and a list ot items which are concepts and json paths paths to those concepts in the DataCite metadata schema.
#
spiral_d = [
    {
        'title': 'FAIR Text',
        'code': 'FAIR_Text',
        'dialect':  'DataCite',
        'description': 'Documentation concepts used to support many types of data discovery using text searches, i.e. title, author, funder name, publisher, etc. This spiral includes six mandatory concepts that exist in all records so the minimum completeness for this spiral is 40%. The average for this spiral for all DataCite repositories during May 2025 is 53%.',
        'items': [
            {'concept': 'Abstract',
             'paths': [
                 {'container': 'data[*].attributes.descriptions[?(@.descriptionType="Abstract")]',
                  'attribute': 'description'}
             ]
             },
            {'concept': 'Date Created',
             'paths': [
                 {'container': 'data[*].attributes.dates[?(@.dateType="Created")]','attribute': 'date'}
             ]
             },
            {'concept': 'Keyword',
             'paths': [
                 {'container': 'data[*].attributes.subjects[*]',
                     'attribute': 'subject'}
             ]
             },
            {'concept': 'Keyword Vocabulary',
             'paths': [
                 {'container': 'data[*].attributes.subjects[*]',
                     'attribute': 'subjectScheme'}
             ]
             },
             {'concept': 'Resource Author Affiliation',
              'paths': [
                {'container': 'data[*].attributes.creators[*].affiliation[*]','attribute': 'name'}
            ]},
            {'concept': 'Resource Author',
             'paths': [
                 {'container': 'data[*].attributes.creators[*]', 'attribute': 'name'}
             ]
             },
            {'concept': 'Resource Identifier',
             'paths': [
                 {'container': 'data[*].attributes', 'attribute': 'doi'},
                 {'container': 'data[*].attributes.identifiers[*]',
                     'attribute': 'identifier'}
             ]
             },
            {'concept': 'Resource Publication Date',
             'paths': [
                 {'container': 'data[*].attributes',
                     'attribute': 'publicationYear'}
             ]
             },
            {'concept': 'Resource Publisher',
             'paths': [
                 {'container': 'data[*].attributes.publisher', 'attribute': 'name'},
                 #{'container': 'data[*].attributes', 'attribute': 'publisher'}             # deprecated in V4.5
             ]
             },
            {'concept': 'Resource Title',
             'paths': [{'container': 'data[*].attributes.titles[*]', 'attribute': 'title'}
                       ]
             },
            {'concept': 'Resource Type General',
             'paths': [{'container': 'data[*].attributes.types', 'attribute': 'resourceTypeGeneral'}
                       ]
             },
            {'concept': 'Project Funder',
             'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderName'}
                       ]
             },
            {'concept': 'Award Title',
             'paths': [
                 {'container': 'data[*].attributes[*].fundingReferences[*]',
                     'attribute': 'awardTitle'},
             ]
             },
            {'concept': 'Temporal Extent',
             'paths': [{'container': 'data[*].attributes.dates[?(@.dateType="Collected")]', 'attribute': 'date'}
                       ]
             },
            {'concept': 'Spatial Extent',
             'paths': [
                 {'container': 'data[*].attributes.geoLocations[*]',
                     'attribute': 'geoLocationBox'},
                 {'container': 'data[*].attributes.geoLocations[*]',
                     'attribute': 'geoLocationPoint'},
                 {'container': 'data[*].attributes.geoLocations[*]',
                     'attribute': 'geoLocationPolygon'},
                 {'container': 'data[*].attributes.geoLocations[*]',
                     'attribute': 'geoLocationPlace'}
             ]
             }
        ]
    },
    {
        'title': 'FAIR Identifiers',
        'code': 'FAIR_Identifiers',
        'dialect':  'DataCite',
        'description': 'Documentation concepts that provide extra information, i.e. identifiers and references, about discovery concepts. The average for this spiral for all DataCite repositories during May 2025 is 20%.',
        'items': [
            # supports Data Created
            {'concept': 'Date Submitted',
             'paths': [
                {'container': 'data[*].attributes.dates[?(@.dateType="Submitted")]',
                 'attribute': 'date'},
             ]
             },
            # supports Keyword
            {'concept': 'Keyword Value URI',
             'paths': [
                 {'container': 'data[*].attributes.subjects[*]',
                     'attribute': 'valueURI'},
             ]
             },
            # supports Keyword Vocabulary
            {'concept': 'Keyword Vocabulary URI',
             'paths': [
                 {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeURI'},
                 {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeUri'},
             ]
             },
            # supports Resource Author
            {'concept': 'Resource Author Type',
             'paths': [
                 {'container': 'data[*].attributes.creators[*]',
                     'attribute': 'nameType'},
             ]
             },
            {'concept': 'Resource Author Identifier',
             'paths': [
                 {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]',
                     'attribute': 'nameIdentifier'},
             ]
             },
            {'concept': 'Resource Author Identifier Type',
             'paths': [
                 {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]',
                     'attribute': 'nameIdentifierScheme'},
             ]
             },
            #
            # publisher Identifier added 202502 to support V4.5 of the schema...
            # supports Resource Publisher
            #
            {'concept': 'Publisher Identifier',
             'paths': [
                 {'container': 'data[*].attributes.publisher',
                     'attribute': 'publisherIdentifier'},
             ]
             },
            {'concept': 'Publisher Identifier Type',
             'paths': [
                 {'container': 'data[*].attributes.publisher',
                     'attribute': 'publisherIdentifierScheme'},
             ]
             },
            {'concept': 'Publisher Identifier Scheme URI',
             'paths': [
                 {'container': 'data[*].attributes.publisher',
                     'attribute': 'schemeUri'},
             ]
             },
            # supports Resource Author Affiliation
            {'concept': 'Resource Author Affiliation Identifier',
             'paths': [
                 {'container': 'data[*].attributes.creators[*].affiliation[*]',
                     'attribute': 'affiliationIdentifier'}
             ]
             },
            {'concept': 'Resource Author Affiliation Identifier Type',
             'paths': [
                 {'container': 'data[*].attributes.creators[*].affiliation[*]',
                     'attribute': 'affiliationIdentifierScheme'}
             ]
             },
            {'concept': 'Resource Author Affiliation Identifier Scheme URI',
             'paths': [
                 {'container': 'data[*].attributes.creators[*].affiliation[*]',
                     'attribute': 'schemeUri'}
#                     'attribute': 'affiliationIdentifierSchemeURI'} dropped 2025-05-31
             ]
             },
            # supports Resource Identifier
            {'concept': 'Resource Identifier Type',
             'paths': [
                 {'container': 'data[*].attributes.identifiers[*]', 'attribute': 'identifierType'},
             ]
             },
            # supports resouceType General
            {'concept': 'Resource Type',
             'paths': [
                 {'container': 'data[*].attributes.types',
                     'attribute': 'resourceType'},
             ]
             },
            # supports Project Sponsor
            {'concept': 'Funder Identifier',
             'paths': [
                 {'container': 'data[*].attributes[*].fundingReferences[*]',
                     'attribute': 'funderIdentifier'},
             ]
             },
            {'concept': 'Funder Identifier Type',
             'paths': [
                 {'container': 'data[*].attributes[*].fundingReferences[*]',
                     'attribute': 'funderIdentifierType'},
             ]
             },
            {'concept': 'Award URI',
             'paths': [
                 {'container': 'data[*].attributes[*].fundingReferences[*]',
                     'attribute': 'awardURI'},
             ]
             },
            {'concept': 'Award Number',
             'paths': [
                 {'container': 'data[*].attributes[*].fundingReferences[*]',
                     'attribute': 'awardNumber'},
             ]
             }
        ]
    },
    {
        'title': 'FAIR Connections',
        'code': 'FAIR_Connections',
        'dialect':  'DataCite',
        'description': 'Documentation concepts for datasets interoperability and connections for resource documentation, understanding, and trust. This spiral includes one mandatory concept (Resource URL) so the minimum score is 6%. The average for this spiral for all DataCite repositories during May 2025 is 13%.',
        'items': [
            #
            # Accessibility Essential
            #
            {'concept': 'CitedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCitedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Date Available',
             'paths': [
                 {'container': 'data[*].attributes.dates[?(@.dateType="Available")]','attribute': 'date'}
             ]
             },
            {'concept': 'DescribedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsDescribedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Distribution Contact',
             'paths': [
                {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')]", 'attribute': 'name'},
                {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')]",
                 'attribute': 'givenName'},
                {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')]",
                 'attribute': 'familyName'}
             ]
             },
            {'concept': 'DocumentedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsDocumentedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Resource Contact',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')]", 'attribute': 'name'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')]",
                  'attribute': 'givenName'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')]",
                  'attribute': 'familyName'}
             ]
             },
            {'concept': 'HasMetadata',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasMetadata')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Resource Format', 'paths': [
                {'container': 'data[*].attributes', 'attribute': 'formats'}]},
            {'concept': 'Resource Size', 'paths': [
                {'container': 'data[*].attributes', 'attribute': 'sizes'}]},
            {'concept': 'Resource URL', 'paths': [
                {'container': 'data[*].attributes', 'attribute': 'url'}]},
            {'concept': 'Rights', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rights'}]},
            {'concept': 'RightsHolder',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')]", 'attribute': 'name'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')]",
                  'attribute': 'givenName'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')]",
                  'attribute': 'familyName'}
             ]
             },
            {'concept': 'Methods',
             'paths': [
                 {'container': 'data[*].attributes.descriptions[?(@.descriptionType="Methods")]',
                  'attribute': 'description'}
             ]
             },
            {'concept': 'Technical Information',
             'paths': [
                 {'container': 'data[*].attributes.descriptions[?(@.descriptionType="TechnicalInfo")]',
                  'attribute': 'description'}
             ]
             },
            {'concept': 'ReferencedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsReferencedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'ReviewedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsReviewedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'SourceOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSourceOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'SupplementTo',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementTo')]", 'attribute': 'relatedIdentifier'}]
             },
        ]
    },
    {
        'title': 'FAIR Contacts',
        'code': 'FAIR_Contacts',
        'dialect':  'DataCite',
        'description': 'Documentation concepts for contacts that can answer questions not addressed in the metadata or other documentation. The average for this spiral for all DataCite repositories during May 2025 is 5%.',
        'items': [
            #
            # Accessibility Support
            #
            {'concept': 'Resource Contact Identifier',
             'paths': [
                {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')].nameIdentifiers[*]",
                 'attribute': 'nameIdentifier'},
             ]
             },
            {'concept': 'Resource Contact Identifier Scheme',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')].nameIdentifiers[*]",
                  'attribute': 'nameIdentifierScheme'},
             ]
             },
            {'concept': 'Resource Contact Identifier Scheme URI',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')].nameIdentifiers[*]",
                  'attribute': 'schemeUri'},
                {'container': "data[*].attributes.contributors[?(@.contributorType='ContactPerson')].nameIdentifiers[*]",
                  'attribute': 'schemeURI'}
             ]
             },
            {'concept': 'Distribution Contact Identifier',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')].nameIdentifiers[*]",
                  'attribute': 'nameIdentifier'},
             ]
             },
            {'concept': 'Distribution Contact Identifier Scheme',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')].nameIdentifiers[*]",
                  'attribute': 'nameIdentifierScheme'},
             ]
             },
            {'concept': 'Distribution Contact Identifier Scheme URI',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')].nameIdentifiers[*]",
                  'attribute': 'schemeURI'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='Distributor')].nameIdentifiers[*]",
                  'attribute': 'schemeUri'}
             ]
             },
            #
            # RightsHolder is Essential
            # {'concept': 'Rights Holder',
            # 'paths': [
            #    {'container':"data[*].attributes.contributors[?(@.contributorType='RightsHolder')]",'attribute': 'name'},
            #    ]
            # },
            {'concept': 'Rights Holder Identifier',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')].nameIdentifiers[*]",
                  'attribute': 'nameIdentifier'},
             ]
             },
            {'concept': 'Rights Holder Identifier Scheme',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')].nameIdentifiers[*]",
                  'attribute': 'nameIdentifierScheme'},
             ]
             },
            {'concept': 'Rights Holder Identifier Scheme URI',
             'paths': [
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')].nameIdentifiers[*]",
                  'attribute': 'schemeURI'},
                 {'container': "data[*].attributes.contributors[?(@.contributorType='RightsHolder')].nameIdentifiers[*]",
                  'attribute': 'schemeUri'}
             ]
             },
            #
            # Rights is Essential
            #
            # {'concept': 'Rights',
            # 'paths': [
            #    {'container': 'data[*].attributes.rightsList[*]','attribute': 'rights'},
            #    ]
            # },
            {'concept': 'Rights URI',
             'paths': [
                 {'container': 'data[*].attributes.rightsList[*]','attribute': 'rightsUri'},
             ]
             },
            #
            # Resource Format, Size and URL are essential
            #
            # {'concept': 'Resource Format',
            # 'paths': [
            #    {'container':'data[*].attributes','attribute': 'formats'},
            #    ]
            # },
            # {'concept': 'Resource Size',
            # 'paths': [
            #    {'container':'data[*].attributes','attribute': 'sizes'},
            #    ]
            # },
            # {'concept': 'Resource URL',
            # 'paths': [
            #    {'container':'data[*].attributes','attribute': 'url'}
            #    ]
            # },
        ],
        'aggregates': []
    },
    {
        'title': 'DataCite Relations',
        'code': 'DataCite_Relations',
        'dialect':  'DataCite',
        'description': 'These are relation types supported by the DataCite Metadata Schema.',
        'items': [
            {'concept': 'Related Identifier',
             'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Related Identifier Type',
             'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifierType'}]
             },
            {'concept': 'Related Item Type',
             'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'resourceTypeGeneral'}]
             },
            {'concept': 'Cites',
             'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Cites')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'CitedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCitedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Collects',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Collects')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsCollectedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCollectedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsSupplementTo',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementTo')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsSupplementedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Continues',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Continues')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsContinuedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsContinuedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsNewVersionOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsNewVersionOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsPreviousVersionOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPreviousVersionOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsPartOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPartOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'HasPart',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasPart')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsPublishedIn',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPublishedIn')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsReferencedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsReferencedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'References',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='References')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Documents',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Documents')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsDocumentedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsDocumentedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsCompiledBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCompiledBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Compiles',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Compiles')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsVariantFormOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsVariantFormOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsOriginalFormOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsOriginalFormOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsIdenticalTo',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsIdenticalTo')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'HasMetadata',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasMetadata')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsMetadataFor',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsMetadataFor')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Reviews',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Reviews')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsReviewedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsReviewedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsDerivedFrom',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsDerivedFrom')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsSourceOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSourceOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Describes',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Describes')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsDescribedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsDescribedBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'HasVersion',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasVersion')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsVersionOf',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsVersionOf')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Requires',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Requires')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsRequiredBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsRequiredBy')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'Obsoletes',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Obsoletes')]", 'attribute': 'relatedIdentifier'}]
             },
            {'concept': 'IsObsoletedBy',
             'paths': [
                 {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsObsoletedBy')]", 'attribute': 'relatedIdentifier'}]
             },
        ]
    },
    ########## GREI Metadata Recommendations V2 ##########
    {
        'title': 'GREI Metadata Recommedation V2',
        'code': 'GREI_V2',
        'dialect':  'DataCite',
        'description': 'A metadata recommendation for DataCite created by the Generalist Repository Ecosystem Initiative (GREI).',
        'items': [
            {'concept': 'Identifier',
            'paths': [
                {'container': 'data[*].attributes', 'attribute': 'doi'},
                {'container': 'data[*].attributes.identifiers[*]',
                    'attribute': 'identifier'}
            ]
            },
            {'concept': 'Resource Title',
            'paths': [{'container': 'data[*].attributes.titles[*]', 'attribute': 'title'}
                    ]
            },
            {'concept': 'Publisher',
            'paths': [
                {'container': 'data[*].attributes.publisher', 'attribute': 'name'},
                # {'container': 'data[*].attributes', 'attribute': 'publisher'}     older version of publisher (deprecated)
            ]
            },
            {'concept': 'Publication Date',
            'paths': [
                {'container': 'data[*].attributes',
                    'attribute': 'publicationYear'}
            ]
            },

            {'concept': 'Abstract',
            'paths': [
                {'container': 'data[*].attributes.descriptions[?(@.descriptionType="Abstract")]',
                'attribute': 'description'}
            ]
            },
            {'concept': 'Description Type',
            'paths': [
                {'container': 'data[*].attributes.descriptions[*]', 'attribute': 'descriptionType'}
            ]
            },
            {'concept': 'Creator',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'name'}
            ]
            },
            {'concept': 'Creator Type',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',
                    'attribute': 'nameType'}
                ]
            },
            {'concept': 'Creator Given Name',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'givenName'}
            ]
            },
            {'concept': 'Creator Family Name',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'familyName'}
            ]
            },
            {'concept': 'Creator Identifier',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]','attribute': 'nameIdentifier'}
                ]
            },
            {'concept': 'Creator Identifier Type',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]','attribute': 'nameIdentifierScheme'}
            ]
            },
            {'concept': 'Creator Identifier Schema URI',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]', 'attribute': 'schemeUri'},
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]', 'attribute': 'schemeURI'}
            ]
            },
            {'concept': 'Creator Affiliation',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'affiliation'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'name'}
            ]
            },
            {'concept': 'Creator Affiliation Identifier',
            'paths': [
                {'container': 'data[*].attributes.creators[*]','attribute':    'affiliationIdentifier'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'affiliationIdentifier'}
            ]
            },
            {'concept': 'Creator Affiliation Identifier Scheme',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',    'attribute':    'affiliationIdentifierScheme'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]',     'attribute': 'affiliationIdentifierScheme'}
            ]
            },
            {'concept': 'Creator Affiliation Scheme URI',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'schemeUri'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'schemeUri'}
            ]
            },
            {'concept': 'Resource Title',
            'paths': [{'container': 'data[*].attributes.titles[*]', 'attribute': 'title'}
            ]
            },
            {'concept': 'Resource Publisher',
            'paths': [
                {'container': 'data[*].attributes.publisher', 'attribute': 'name'},
                # {'container': 'data[*].attributes', 'attribute': 'publisher'} older version of publisher (deprecated)
            ]
            },
            {'concept': 'Resource Publication Date',
            'paths': [
                {'container': 'data[*].attributes',
                    'attribute': 'publicationYear'}
            ]
            },
            {'concept': 'Subject',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]',
                    'attribute': 'subject'}
            ]
            },
            {'concept': 'Subject Scheme',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]',
                    'attribute': 'subjectScheme'}
            ]
            },
            {'concept': 'Subject Scheme URI',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeUri'},
            ]
            },
            {'concept': 'Subject Value URI',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'valueURI'},
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'valueUri'}
            ]
            },
            {'concept': 'Date Issued',
            'paths': [
                {'container': 'data[*].attributes.dates[?(@.dateType="Issued")]','attribute': 'date'}
            ]
            },
            {'concept': 'Date Type',
            'paths': [
                {'container': 'data[*].attributes.dates[*]','attribute': 'dateType'}
            ]
            },
            {'concept': 'Resource Type',
            'paths': [{'container': 'data[*].attributes.types', 'attribute': 'resourceType'}
            ]
            },
            {'concept': 'Resource Type General',
            'paths': [{'container': 'data[*].attributes.types', 'attribute': 'resourceTypeGeneral'}
            ]
            },
            {'concept': 'Version',
            'paths': [{'container': 'data[*].attributes', 'attribute': 'version'}
            ]
            },
            {'concept': 'Rights', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rights'}]},
            {'concept': 'Rights URI', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsUri'}]},
            {'concept': 'Rights Identifier', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsIdentifier'}]},
            {'concept': 'Rights Identifier Schema', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsIdentifierScheme'}]},
            {'concept': 'Rights Scheme URI', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'schemeUri'}]},
            {'concept': 'Abstract',
            'paths': [
                {'container': 'data[*].attributes.descriptions[?(@.descriptionType="Abstract")]',
                'attribute': 'description'}
            ]
            },
            {'concept': 'Funder Name',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderName'}]},
            {'concept': 'Funder Identifier',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderIdentifier'}]},
            {'concept': 'Funder Identifier Type',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderIdentifierType'}]},
            {'concept': 'Funder Identifier Scheme URI', 
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'schemeUri'},
                    {'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'schemeURI'}]
            },
            {'concept': 'Award Number',
            'paths':[{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardNumber'}]},            
            {'concept': 'Award URI',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardURI'}]},            
            {'concept': 'Award Title',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardTitle'}]},
            
            {'concept': 'Related Identifier',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'Related Identifier Type',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifierType'}]
            },
            {'concept': 'Relation Type',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relationType'}]
            },
            {'concept': 'Related Item Type',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'resourceTypeGeneral'}]
            },
            {'concept': 'CitedBy',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCitedBy')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'Cites',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Cites')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsSupplementTo',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementTo')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsSupplementedBy',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementedBy')]", 'attribute': 'relatedIdentifier'}]
            },
                        {'concept': 'IsPartOf',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPartOf')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'HasPart',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasPart')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsNewVersionOf',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsNewVersionOf')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsPreviousVersionOf',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPreviousVersionOf')]", 'attribute': 'relatedIdentifier'}]
            },
                        {'concept': 'HasVersion',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasVersion')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsVersionOf',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsVersionOf')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsIdenticalTo',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsIdenticalTo')]", 'attribute': 'relatedIdentifier'}]
            },
            {'concept': 'IsCollectedBy',
            'paths': [
                {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCollectedBy')]", 'attribute': 'relatedIdentifier'}]
            },
        ]
    },
    {
        'title': 'GREI Metadata Recommedation V2: Text',
        'code': 'Text_GREI_V2',
        'dialect':  'DataCite',
        'description': 'Metadata elements recommended by GREI that facilitate text discovery.',
        'items': [
            {'concept': 'Identifier',
            'paths': [
                {'container': 'data[*].attributes', 'attribute': 'doi'},
                {'container': 'data[*].attributes.identifiers[*]',
                    'attribute': 'identifier'}
            ]
            },
            {'concept': 'Resource Title',
            'paths': [{'container': 'data[*].attributes.titles[*]', 'attribute': 'title'}
                    ]
            },
            {'concept': 'Publisher',
            'paths': [
                {'container': 'data[*].attributes.publisher', 'attribute': 'name'},
                # {'container': 'data[*].attributes', 'attribute': 'publisher'}     older version of publisher (deprecated)
            ]
            },
            {'concept': 'Publication Date',
            'paths': [
                {'container': 'data[*].attributes',
                    'attribute': 'publicationYear'}
            ]
            },
            {'concept': 'Abstract',
            'paths': [
                {'container': 'data[*].attributes.descriptions[?(@.descriptionType="Abstract")]',
                'attribute': 'description'}
            ]
            },
            {'concept': 'Description Type',
            'paths': [
                {'container': 'data[*].attributes.descriptions[*]', 'attribute': 'descriptionType'}
            ]
            },
            {'concept': 'Creator',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'name'}
            ]
            },
            {'concept': 'Creator Given Name',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'givenName'}
            ]
            },
            {'concept': 'Creator Family Name',
            'paths': [
                {'container': 'data[*].attributes.creators[*]', 'attribute': 'familyName'}
            ]
            },
            {'concept': 'Creator Type',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',
                    'attribute': 'nameType'}
                ]
            },
            {'concept': 'Creator Affiliation',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'affiliation'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'name'}
            ]
            },
            {'concept': 'Subject',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]',
                    'attribute': 'subject'}
            ]
            },
            {'concept': 'Subject Scheme',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]',
                    'attribute': 'subjectScheme'}
            ]
            },
            {'concept': 'Date Issued',
            'paths': [
                {'container': 'data[*].attributes.dates[?(@.dateType="Issued")]','attribute': 'date'}
            ]
            },
            {'concept': 'Date Type',
            'paths': [
                {'container': 'data[*].attributes.dates[*]','attribute': 'dateType'}
            ]
            },
            {'concept': 'Resource Type',
            'paths': [{'container': 'data[*].attributes.types', 'attribute': 'resourceType'}
            ]
            },
            {'concept': 'Resource Type General',
            'paths': [{'container': 'data[*].attributes.types', 'attribute': 'resourceTypeGeneral'}
            ]
            },
            {'concept': 'Version',
            'paths': [{'container': 'data[*].attributes', 'attribute': 'version'}
            ]
            },
            {'concept': 'Rights', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rights'}]},
            {'concept': 'Funder Name',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderName'}]},
            {'concept': 'Award Title',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardTitle'}]},
        ]
    },
    {
        'title': 'GREI Metadata Recommedation V2: Identifiers',
        'code': 'Identifiers_GREI_V2',
        'dialect':  'DataCite',
        'description': 'Metadata elements recommended by GREI that facilitate identification of resources using presistent identifiers (PIDs).',
        'items': [
            {'concept': 'Creator Identifier',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]','attribute': 'nameIdentifier'}
                ]
            },
            {'concept': 'Creator Identifier Type',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]','attribute': 'nameIdentifierScheme'}
            ]
            },
            {'concept': 'Creator Identifier Schema URI',
            'paths': [
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]', 'attribute': 'schemeUri'},
                {'container': 'data[*].attributes.creators[*].nameIdentifiers[*]', 'attribute': 'schemeURI'}
            ]
            },
            {'concept': 'Creator Affiliation Identifier',
            'paths': [
                {'container': 'data[*].attributes.creators[*]','attribute':    'affiliationIdentifier'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'affiliationIdentifier'}
            ]
            },
            {'concept': 'Creator Affiliation Identifier Scheme',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',    'attribute':    'affiliationIdentifierScheme'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]',     'attribute': 'affiliationIdentifierScheme'}
            ]
            },
            {'concept': 'Creator Affiliation Scheme URI',
            'paths': [
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.creators[*]',                'attribute': 'schemeUri'},
                {'container': 'data[*].attributes.creators[*].affiliation[*]', 'attribute': 'schemeUri'}
            ]
            },
            {'concept': 'Subject Scheme URI',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'schemeUri'},
            ]
            },
            {'concept': 'Subject Value URI',
            'paths': [
                {'container': 'data[*].attributes.subjects[*]','attribute': 'valueURI'},
                {'container': 'data[*].attributes.subjects[*]', 'attribute': 'valueUri'}
            ]
            },
            {'concept': 'Rights URI', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsUri'}]},
            {'concept': 'Rights Identifier', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsIdentifier'}]},
            {'concept': 'Rights Identifier Schema', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'rightsIdentifierScheme'}]},
            {'concept': 'Rights Scheme URI', 'paths': [
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'schemeURI'},
                {'container': 'data[*].attributes.rightsList[*]', 'attribute': 'schemeUri'}]},
            {'concept': 'Funder Identifier',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderIdentifier'}]},
            {'concept': 'Funder Identifier Type',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'funderIdentifierType'}]},
            {'concept': 'Funder Identifier Schema URI', 
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'schemeUri'},
                    {'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'schemeURI'}
            ]
            },
            {'concept': 'Award Number',
            'paths':[{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardNumber'}]},            
            {'concept': 'Award URI',
            'paths': [{'container': 'data[*].attributes.fundingReferences[*]', 'attribute': 'awardURI'}]},            
        ]
    },
    {
                'title': 'GREI Metadata Recommedation V2: Connections',
                'code': 'Connections_GREI_V2',
                'dialect':  'DataCite',
                'description': 'Metadata elements recommended by GREI that facilitate connections between resources using DataCite relatedIdentifiers.',
                'items': [
                    {'concept': 'Related Identifier',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'Related Identifier Type',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relatedIdentifierType'}]
                    },
                    {'concept': 'Relation Type',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'relationType'}]
                    },
                    {'concept': 'Related Item Type',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[*]", 'attribute': 'resourceTypeGeneral'}]
                    },
                    {'concept': 'CitedBy',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCitedBy')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'Cites',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='Cites')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsSupplementTo',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementTo')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsSupplementedBy',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsSupplementedBy')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsPartOf',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPartOf')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'HasPart',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasPart')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsNewVersionOf',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsNewVersionOf')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsPreviousVersionOf',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsPreviousVersionOf')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'HasVersion',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='HasVersion')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsVersionOf',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsVersionOf')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsIdenticalTo',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsIdenticalTo')]", 'attribute': 'relatedIdentifier'}]
                    },
                    {'concept': 'IsCollectedBy',
                    'paths': [
                        {'container': "data[*].attributes.relatedIdentifiers[?(@.relationType='IsCollectedBy')]", 'attribute': 'relatedIdentifier'}]
                    }
                ]
            },
    ############## End of GREI V2 use cases

]
#
# define global variables
#
verbose = True
outputDirectory = None                      # define the directory for output data and plots. 
                                            # Use local variable DATACITE_DATA if available
                                            # or use the current working directory if not.

import argparse
import logging

def main():
    #
    # retrieve command line arguments
    #
    commandLine = argparse.ArgumentParser(prog='DataCite Repositories',
                                          description='Library retrieving and analyzing DataCite repositories'
                                          )
    commandLine.add_argument("-r", "--repository_l", nargs="*", type=str,
                            help='List of repository ids',
                            )
    commandLine.add_argument('--loglevel', default='info',
                             choices=['debug', 'info', 'warning'],
                             help='Logging level'
                             )
    commandLine.add_argument('--logto', metavar='FILE', nargs="*",
                             help='Log file (will append to file if exists)'
                             )

    args = commandLine.parse_args()    # parse the command line and define variables

    if args.logto:
        # Log to file
        logging.basicConfig(
            filename=args.logto, filemode='a',
            format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
            level=args.loglevel.upper(),
            datefmt='%Y-%m-%d %H:%M:%S')
    else:
        # Log to stderr
        logging.basicConfig(
            format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
            level=args.loglevel.upper(),
             datefmt='%Y-%m-%d %H:%M:%S')

    lggr = logging.getLogger('dataCiteRepositories')

    spiralCodeList = ['Text_GREI_V2','Identifiers_GREI_V2','Connections_GREI_V2']
    query_d = {'funderName': '(fundingReferences.funderName:(%22National%20Institutes%20of%20Health%22%20OR%20%22Center%20for%20Information%20Technology%22%20OR%20%22Center%20for%20Scientific%20Review%22%20OR%20%22Eunice%20Kennedy%20Shriver%20National%20Institute%20of%20Child%20Health%20and%20Human%20Development%22%20OR%20%22Fogarty%20International%20Center%22%20OR%20%22National%20Cancer%20Institute%22%20OR%20%22National%20Center%20for%20Advancing%20Translational%20Sciences%22%20OR%20%22National%20Center%20for%20Complementary%20and%20Integrative%20Health%22%20OR%20%22National%20Eye%20Institute%22%20OR%20%22National%20Heart%20Lung%20and%20Blood%20Institute%22%20OR%20%22National%20Human%20Genome%20Research%20Institute%22%20OR%20%22National%20Institute%20of%20Allergy%20and%20Infectious%20Diseases%22%20OR%20%22National%20Institute%20of%20Arthritis%20and%20Musculoskeletal%20and%20Skin%20Diseases%22%20OR%20%22National%20Institute%20of%20Biomedical%20Imaging%20and%20Bioengineering%22%20OR%20%22National%20Institute%20of%20Dental%20and%20Craniofacial%20Research%22%20OR%20%22National%20Institute%20of%20Diabetes%20and%20Digestive%20and%20Kidney%20Diseases%22%20OR%20%22National%20Institute%20of%20Environmental%20Health%20Sciences%22%20OR%20%22National%20Institute%20of%20General%20Medical%20Sciences%22%20OR%20%22National%20Institute%20of%20Mental%20Health%22%20OR%20%22National%20Institute%20of%20Neurological%20Disorders%20and%20Stroke%22%20OR%20%22National%20Institute%20of%20Nursing%20Research%22%20OR%20%22National%20Institute%20on%20Aging%22%20OR%20%22National%20Institute%20on%20Alcohol%20Abuse%20and%20Alcoholism%22%20OR%20%22National%20Institute%20on%20Deafness%20and%20Other%20Communication%20Disorders%22%20OR%20%22National%20Institute%20on%20Drug%20Abuse%22%20OR%20%22National%20Institute%20on%20Minority%20Health%20and%20Health%20Disparities%22%20OR%20%22National%20Institutes%20of%20Health%20Clinical%20Center%22%20OR%20%22Office%20of%20the%20Director%22%20OR%20%22United%20States%20National%20Library%20of%20Medicine%22%20OR%20%22Office%20of%20Research%20Infrastructure%20Programs%22%20))'}

    rep = DataCiteRepository(rep_id=args.repository_l[0], query=query_d['funderName'])
    rep.get_metadataPaging()
    rep.get_spiral_data(spiralCodeList, save=True)

if __name__ == "__main__":
    main()