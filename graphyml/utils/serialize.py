from .clear import clear
from pprint import pprint
def serialize(data,model=None,user=None,schema=None):
    from bson.json_util import dumps
    import json
    l=[]
    def generator():
        yield None
    if type(data)==type(generator() ):
        for item in data:
            for elem in item:

                if callable(elem[1]):
                    setattr(item,elem[0],elem[1]())

            d={}
            for elem in json.loads(dumps(item)):
                
                if type(elem[1])==dict and list(elem[1].keys())[0] in ["$oid","$date"]:
                    d[elem[0]]=list(elem[1].values())[0]
                elif type(getattr(item,elem[0])) not in [str,dict,list,bool,int,float,type(None)]:
                    
                    d[elem[0]]=clear(user,
                        dict(elem[1]),
                        getattr(item,elem[0]),
                        schema)

                else:
                    print("*********",elem[0],)
                    d[elem[0]]=elem[1]

            l.append(clear(user,d,model,schema))

        return l
    else:
        d={}
       
        item=json.loads(dumps(data))
        for elem in item:
          
            

            if type(elem[1])==dict and list(elem[1].keys())[0] in ["$oid","$date"]:
                d[elem[0]]=list(elem[1].values())[0]
            elif type(getattr(data,elem[0])) not in [str,dict,list,bool,int,float,type(None)]:

                d[elem[0]]=clear(user,
                    dict(elem[1]),
                    getattr(data,elem[0]),
                    schema)

            else:
                d[elem[0]]=elem[1]
        
        return clear(user,d,model,schema)