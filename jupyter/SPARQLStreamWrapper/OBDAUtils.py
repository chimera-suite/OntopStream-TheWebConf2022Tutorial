from SPARQLWrapper import SPARQLWrapper, JSON, CSV
from .Wrapper import SPARQLStreamWrapper, JSONL
from string import Template
import json


def leftJoinJSONResults(OntopStreamJSON,JenaJSON):
    v=OntopStreamJSON["head"]["vars"]+JenaJSON["head"]["vars"]
        
    if JenaJSON["head"]["vars"]!=[] and JenaJSON["results"]["bindings"]!=[]:
        for JenaResult in JenaJSON["results"]["bindings"]:
            b=[{**OntopStreamJSON["results"]["bindings"][0],**JenaResult}]
            yield {'head': {'vars': v }, 'results': {'bindings': b }}
    else:
        yield {'head': {'vars': v }, 'results': {'bindings': OntopStreamJSON["results"]["bindings"]}}

        
def innerJoinJSONResults(OntopStreamJSON,JenaJSON):  
    if JenaJSON["head"]["vars"]!=[] and JenaJSON["results"]["bindings"]!=[]:
        v=OntopStreamJSON["head"]["vars"]+JenaJSON["head"]["vars"]
        for JenaResult in JenaJSON["results"]["bindings"]:
            b=[{**OntopStreamJSON["results"]["bindings"][0],**JenaResult}]
            yield {'head': {'vars': v }, 'results': {'bindings': b }}
    else:
        yield OntopStreamJSON
        

def leftJoinCSVResults(ontopStreamCSV,jenaCSV):
    header = jenaCSV[0]
    data = jenaCSV[1]
    
    if data != []:
        for line in data:
            yield ontopStreamCSV.rstrip("\r\n")+","+line.rstrip("\r\n")+"\r\n"
    else:
        yield ontopStreamCSV.rstrip("\r\n") + ("," * (header.count(',')+1))+"\r\n"

        
def innerJoinCSVResults(ontopStreamJSON,jenaCSV):
    header = jenaCSV[0]
    data = jenaCSV[1]
    
    if data != []:
        for line in data:
            yield ontopStreamCSV.rstrip("\r\n")+","+line.rstrip("\r\n")+"\r\n"
    else:
        yield ""
        

def batchSparqlQueryJSON(endpoint: str, queryTemplate: Template, mapping: dict) -> dict:
    """
    Make a query over a batch triplestore (i.e. Jena-Fuseki)
    """
    
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    
    query=queryTemplate.substitute(**mapping)
    #print(query)
    sparql.setQuery(query)
    
    try :
        return sparql.query().convert()
    except:
        return {'head': {'vars': [] }, 'results': {'bindings': [] }}
    

def batchSparqlQueryCSV(endpoint: str, queryTemplate: Template, mapping: dict) -> dict:
    """
    Make a query over a batch triplestore (i.e. Jena-Fuseki)
    """
    
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(CSV)
    
    query=queryTemplate.substitute(**mapping)
    #print(query)
    sparql.setQuery(query)
    
    response=[]
    
    try :
        kgData = iter(sparql.query())
        header = next(kgData).decode('utf8')
        for kgRow in kgData:
            response.append(kgRow.decode('utf8'))
        return header,response
    except:
        return []
    
    
def streamingEnrichedSparqlQueryJSONL(endpointOBDA: str, endpointKG: str, queryOBDA: str, queryTemplateKG: Template, mapping: dict, joinStrategy: str="inner") -> dict:

    # OntopStream
    sparql = SPARQLStreamWrapper(endpointOBDA)
    sparql.setQuery(queryOBDA)
    sparql.addParameter("streaming-mode","single-element")
    #sparql.addParameter("json","jsonl")
    sparql.setReturnFormat(JSONL)
    
    # join algorithm
    if joinStrategy == 'left':
        join = leftJoinJSONResults
    elif joinStrategy == 'inner':
        join = innerJoinJSONResults
    else: #default
        join = innerJoinJSONResults

    results=sparql.query()

    for result in results:
        ontopData = json.loads(result.getRawResponse().decode('utf8'))
        substitution = {}
        for key in mapping.keys():
            substitution[mapping[key]]= ontopData["results"]["bindings"][0][key]["value"]
        #print("SUBS: "+json.dumps(substitution))
        for joinedData in join(ontopData,batchSparqlQueryJSON(endpointKG,queryTemplateKG,substitution)):
            if joinedData != {'head': {'vars': [] }, 'results': {'bindings': [] }}:
                yield json.dumps(joinedData)+"\n"
                

def streamingEnrichedSparqlQueryCSV(endpointOBDA: str, endpointKG: str, queryOBDA: str, queryTemplateKG: Template, mapping: dict, joinStrategy: str="inner") -> dict:

    # OntopStream
    sparql = SPARQLStreamWrapper(endpointOBDA)
    sparql.setQuery(queryOBDA)
    sparql.addParameter("streaming-mode","single-element")
    sparql.setReturnFormat(CSV)
    
    # join algorithm
    if joinStrategy == 'left':
        join = leftJoinCSVResults
    elif joinStrategy == 'inner':
        join = innerJoinCSVResults
    else: #default
        join = innerJoinCSVResults

    results=sparql.query(skipHeader=True)

    for result in results:
        ontopData = result.getRawResponse().decode('utf8')
        substitution = {}
        for key in mapping.keys():
            substitution[key]= ontopData.split(",")[mapping[key]]
    
        kgData = batchSparqlQueryCSV(endpointKG,queryTemplateKG,substitution)
        
        for joinedData in join(ontopData,kgData):
            if joinedData != "":
                yield joinedData