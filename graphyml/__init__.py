
from pydantic.main import ModelMetaclass
from dataclasses import dataclass

privates={}

public={}

@dataclass
class Model:
    pass
class Repository:
    def __init__(self):
        pass
    def save(self,instance):
        if instance.id:
            if self.Meta.private:
                if self.Meta.to_array:
                    l=[]
                    for x in instance.__annotations__:
                        if instance.__annotations__[key]==int:
                            l.append(getattr(instance,key))
                    privates[self.Meta.model.__name__][instance.id]=np.asarray(l)
                else:
                    pass
            else:
                pass
        else:
            if self.Meta.private:
                if self.Meta.model.__name__ not in privates:
                    if self.Meta.to_array:
                        l=[]
                        for x in instance.__annotations__:
                            if instance.__annotations__[key]==int:
                                l.append(getattr(instance,key))
                        
                        privates[self.Meta.model.__name__]= np.concatenate(
                            privates[self.Meta.model.__name__],
                            np.asarray(l)
                            )
                 

class GraphymlMutation:
    pass
class GraphymlQuery:
    pass

def need_login(fn):
    fn.need_login=True
    return fn

def Request(environ):
    request=type("request",(),environ["asgi.scope"])()
    request.headers={k.decode("utf-8"):v for k,v in request.headers}
    return request

class Manager(object):
    """docstring for Mongo."""
    def __init__(self,repository):
        super(Manager, self).__init__()
        self.model = repository.Meta.model
        self.repository=repository
    def find_one(self,**query):
        try:
            return self.repository.get(**query)
        except :
            return None
    def find(self,**query):
        try:
            return list(self.repository.find(**query))
        except:
            return []
    def save(self,instance):
      
        self.repository.save(instance)

    def __call__(self,**query):

        item=self.model(**query)
        for key in dir(self.model.__class__):
            try:
                field=getattr(self.model.__class__,key)
            except AttributeError:
                pass
        self.repository.save(item)
        return item


class Mutation:
    Manager=Manager
    _repositories=[]
    _models=[]
    def __init__(self):
   
        self.manager=self.Manager(self.Meta.repository)
    def _create(self,model,data):
        _model=self.model(model)
        d=data.copy()
        for elem in _model.__annotations__:
            if type(_model.__annotations__[elem])==ModelMetaclass:
                submodel=_model.__annotations__[elem].__name__.lower()
                _submodel=self.model(submodel)
                d[elem]=_submodel.find_one({"id":data[elem]})

        return _model(**d)
    def _modify(self,model,data):
        for elem in _model.__annotations__:
            if type(_model.__annotations__[elem])==ModelMetaclass:
                submodel=_model.__annotations__[elem].__name__.lower()
                _submodel=self.model(submodel)
                d[elem]=_submodel.update_one({"id":data[elem]["id"]},data[elem])
                

    def _delete(self,model,data):
        self.mode(submodel).delete_one({"id":data["id"]})


    def repository(self,name):
        for elem in self.__class__.__bases__:
            if elem.Meta.repository.__name__.replace("Repository","").lower()==name:
                return elem.Meta.repository

    def model(self,name):
        for elem in self.__class__.__bases__:
            if elem.Meta.model.__name__.lower()==name:
                return elem.Meta.model


class Schema:
    def __init__(self,manager,query,mutations,user_manager):
        

        self.manager=manager
        self._query=query
        
        
        
        self.mutations=mutations
        self.user_manager=user_manager
        self.user=None
 
        if len(self.user_manager.find(**{}))==0:
            user=self.user_manager(**{
                "username":"admin",
                "password":"1234",
                "permissions":{},
                })
    @property
    def query(self):
        import yaml
        with open(self._query) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            return yaml.load(file, Loader=yaml.FullLoader)
    def socket(self,app):
        import socketio
  
        # wrap with ASGI application
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
        return self.sio


    async def _process(self,user,mutation,query=None,post=None):
        """
        {
            {
            "<MUTATION>":"create_user",
            "<GET>":{
                "$User.name":{"$op":"lower"},
                "$User.email":{"$op":"upper"}
            },
            "<POST>":{
                "username":"yorvy",
                "email":"yorvy@gmail.com",
                "password":"123456789"
            }
        }
        """

        if  mutation in dir(self.mutations):
            try:
                m=getattr(self.mutations,mutation)
                if "need_login" in dir(m) and m.need_login and self.user:
                    return await m(query,post)
                elif "need_login" not in dir(m):
                    return await m(query,post)


            except Exception as e:
                e.mutation=mutation
                return e
        # import pyyaml module
    def set_user(self,user):
        self.user=user
        
    def has_perm(self,perm):
        if perm.count(".")==3:
            _model,field,_perm=perm.split(".")
        else:
            field=None
            _model,_perm=perm.split(".") 

        if self.user and self.user.permissions and perm in self.user.permissions:
            return True
        return False
        
        
    def clear(self,data,model):
        if self.user.is_superuser:
            return data
        fields=list(data.keys())
        for line in self.query:
            
            
            raw=line.split(" ")
       
            if " " in raw:
                raw.remove(" ")
            _model,*permissions=raw
            
            if model==_model:
                for perm in permissions:
                    if perm not in user.permissions:
                        return None
                #El modelo es visible
          
                for field in self.query[line]:
                    name,*field_permissions=field.split(" ")
                    fields.remove(name)
                    for perm in field_permissions:
                        if perm not in user.permissions:
                            data.pop(name)
 
        for field in fields:
            data.pop(field)
        return data
            

            
    
    def serialize(self,data,model=None,user=None):
        from bson.json_util import dumps
        import json
        l=[]
        def generator():
            yield None
        if type(data)==type(generator() ):
            items=json.loads(dumps(list(data)))
            for item in items:
                d={}
                for elem in item:
                    d[elem[0]]=elem[1]
                l.append(self.clear(d,model))

            return l
        else:
            return self.clear(data.dict(),model)
    async def process(self,data,event=None):
        import json
        if event:
            data["<MUTATION>"]=event
        if type(data)!=dict:
            raw=await data
            data=json.loads(raw)
        
        instance=None
        if "<POST>" in data:
            instance=await self._process(
                user=self.user,
                mutation=data["<MUTATION>"],
                query=data["<QUERY>"] if "<QUERY>" in data else None, 
                post=data["<POST>"],
                )
            l=[]
        
            if "<GET>" in data:
                for model in data["<GET>"]:

                    if model=="$self" and instance:
             
                        l.append(["self",
                            { k:v for k,v in filter(
                                lambda item: item[0] in data["<GET>"]["$self"],
                                instance.dict().items())
                            }
                            ])

                    elif model[0].isupper():
                  
                        for mutation in self.mutations.__class__.__bases__:
                       

                            if "repository" not in dir(mutation.Meta):
                                raise Exception(f"mutation '{mutation.__name__}' not has repository")
                         
                            if "Meta" in dir(mutation.Meta.repository) and \
                                mutation.Meta.repository.Meta.model.__name__==model:

                                if self.has_perm(f"{model}.show"):
                                    

                                    l.append([model,
                                        self.serialize(
                                            mutation.Meta.repository.find(
                                                **data["<GET>"][model]),
                                            model)
                                        ])

                                else:
                                    return self.abort(503,description="Permissions denigate")
   
            if len(l)>1:
                return self.jsonify({"response":l,"error":None})
            elif len(l)==1:
           
                if isinstance(instance,Exception):
            
                    if self.user.is_superuser:
                        return self.jsonify({"response":l[0][1],"error":str(instance)}),500
                    else:
                        return self.jsonify({"response":l[0][1],
                            "error":f"Ocurrio un error en la mutacion {instance.mutation}"},
                            ),500

                return self.jsonify({"response":l[0][1],"error":None})
               
               
            else:
                return self.jsonify({"response":None,"error":None})

    async def run(self,request,jsonify,abort,verify_password=None):
        import datetime
        self.jsonify=jsonify
        self.abort=abort


        if 'Authorization' in request.headers:
            import base64
   
            from uuid import uuid4
      
            token = request.headers['Authorization'].split(" ")[-1]
       
            user,password=base64.b64decode(token).decode("utf-8").split(":") 
            
            user=self.user_manager.find_one(username=user)

            if verify_password(user.password,password):
                obj_token={"token":str(uuid4()),"expire":datetime.datetime.today() + datetime.timedelta(days=1)}
                tokens=user.tokens
                tokens.append(obj_token)
                user.tokens=tokens

                self.set_user(user)

                self.user_manager.save(user)
                return jsonify(obj_token)

            return abort(404)
        elif 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
            user=self.user_manager.find_one(**{"tokens":{
                "$elemMatch":{"token":token}}
                })
            request.user=user

            self.set_user(user)
            if "data" in dir(request):
                return await self.process(request.data)

     
            
class  Permission:
    def __init__(self,user,permission):
        self.user=user
        self.permission=permission
    def __call__(self,*permissions):
        for perm in permissions:
            model,permission=perm.split(".")
            
            if not self.permission.find_one(**{"model":model,"permission":permission}):
                self.permission(**{"model":model,"permission":permission})

        def wrapper(fn):

            return fn
        return wrapper

def connect(host,password):
    from mongomantic import BaseRepository, MongoDBModel, connect
    connect(host,password)