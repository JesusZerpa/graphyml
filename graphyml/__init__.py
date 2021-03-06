
from pydantic.main import ModelMetaclass
from dataclasses import dataclass
from .utils.serialize import serialize
import datetime
privates={}
public={}
requests={}
schema=None

@dataclass
class Model:
    def __init__(self,**fields):
        super(Model).__init__()
    
        for elem in self.__annotations__:
            if elem in fields:
                 setattr(self,elem,fields[elem])
            else:
                if callable(self.__annotations__[elem]):
                    setattr(self,elem,self.__annotations__[elem]())
              
        self.emit("pre_create",self)
    def on_pre_create(self,ctx):
        #schema.mutations
        pass   
    def on(self,name):
        def wrapper(callback):
            setattr(self,"on_"+name,callback)
        return wrapper

    def emit(self,event,data):
        if "on_"+event in dir(self):
            getattr(self,"on_"+event)(data)



    

class Repository:

    def __init__(self,instance:Model):
        self.instance=instance

        self.save=lambda:self.__class__.save(self.instance)

    @classmethod
    def _update(cls,query,data,table,many=True):
        if cls.Meta.private:
            private[cls.Meta.model.__name__]={}
        else:
            public[cls.Meta.model.__name__]={}
        fields=list(self.Meta.model.__annotations__)
        for elem in query:
            i=fields.index(elem)
            _field=table[i]
            if elem in cls.Meta.vectors:
                v=cls.Meta.vectors[elem].index(query[elem])
                ixs=[ fields.index(elem) for elem in data]
                if many:
                    table[_field == v ][ixs] = [cls.Meta.vectors[elem].index(data[elem]) for elem in data ]
                else:
                    table[_field == v ][ixs][0] = [cls.Meta.vectors[elem].index(data[elem]) for elem in data ]
    @classmethod
    def _find(cls,query,table,many=True):
        if cls.Meta.private:
            private[cls.Meta.model.__name__]={}
        else:
            public[cls.Meta.model.__name__]={}
        fields=list(cls.Meta.model.__annotations__)
        l=[]
        for elem in query:
            i=fields.index(elem)
            _field=table[i]
            if elem in cls.Meta.vectors:
                v=cls.Meta.vectors[elem].index(query[elem])
                if many:
                    l.append(table[_field == v ])
                else:
                    return table[_field == v ]
        return l 

    @classmethod
    def find(cls,**query):
        global public,private
        if cls.Meta.private:
            private[cls.Meta.model.__name__]={}
        else:
            public[cls.Meta.model.__name__]={}
        if cls.Meta.private:
            if cls.Meta.model.__name__ not in privates:
                return None
            if cls.Meta.to_array:
                return cls._find(query,privates[cls.Meta.model.__name__])
        else:
            if cls.Meta.model.__name__ not in public:
                return None
            if cls.Meta.to_array:
                return cls._find(query,public[cls.Meta.model.__name__])
            else:
                for elem in public[cls.Meta.model.__name__]:
                    for field in query:
                        if elem[field]!=query[field]:
                            break
                    else:
                        yield elem
    @classmethod
    def find_one(cls,**query):
        global public,private
        if "private" not in dir(cls.Meta):
            cls.Meta.private=False

        if cls.Meta.private:
            if cls.Meta.model.__name__ not in privates:
                return None
            if cls.Meta.to_array:
                return cls._find(query,privates[cls.Meta.model.__name__],False)
            else:
                
                for elem in public[cls.Meta.model.__name__]:
                    for field in query:
                        if elem[field]!=query[field]:
                            break
                    else:
                        return elem
        else:
            if cls.Meta.model.__name__ not in public:
                return None
            if cls.Meta.to_array:
                return cls._find(query,public[cls.Meta.model.__name__],False)
            else:
               
                for item in public[cls.Meta.model.__name__].values():
                    for field in query:
                        if getattr(item,field)!=query[field]:
                            break
                    else:
                       
                        return item

    @classmethod
    def update_one(cls,query,data):
        if cls.Meta.private:
            if cls.Meta.model.__name__ not in private:
                raise Exception(f"No inicreate collection '{cls.Meta.model.__name__}'")
            private[cls.Meta.model.__name__]={}
        else:
            if cls.Meta.model.__name__ not in public:
                raise Exception(f"No inicreate collection '{cls.Meta.model.__name__}'")
            public[cls.Meta.model.__name__]={}
        if cls.Meta.private:
            if cls.Meta.model.__name__ not in privates:
                raise Exception(f"No existen registros en la colleccion '{cls.Meta.model.__name__}'")
            if cls.Meta.to_array:
                cls._update(query,data,privates[cls.Meta.model.__name__],False)
        else:
            if cls.Meta.model.__name__ not in privates:
                raise Exception(f"No existen registros en la colleccion '{cls.Meta.model.__name__}'")
            if cls.Meta.to_array:
                cls._update(query,data,public[cls.Meta.model.__name__],False)
        
    @classmethod
    def update(cls,query,data):
        """
        {id:5},{"kind":"Animal"}
        """
        if cls.Meta.private:
            private[cls.Meta.model.__name__]={}
        else:
            public[cls.Meta.model.__name__]={}
        
        if cls.Meta.private:
            if cls.Meta.model.__name__ not in privates:
                raise Exception(f"No existen registros en la colleccion '{cls.Meta.model.__name__}'")
            if cls.Meta.to_array:
                cls._update(query,data,privates[cls.Meta.model.__name__])

        else:
            if cls.Meta.model.__name__ not in privates:
                raise Exception(f"No existen registros en la colleccion '{cls.Meta.model.__name__}'")
            if cls.Meta.to_array:
                cls._update(query,data,public[cls.Meta.model.__name__])
                
    @classmethod
    def save(cls,instance):
        import numpy as np
        global public,private
        if "private" not in dir(cls.Meta):
            cls.Meta.private=False
        if "to_array" not in dir(cls.Meta):
            cls.Meta.to_array=True
      
        if cls.Meta.private:
            if cls.Meta.to_array:
                private[cls.Meta.model.__name__]=np.asarray([])
            else:
                private[cls.Meta.model.__name__]={}
        else:
            if cls.Meta.to_array:
                public[cls.Meta.model.__name__]=np.asarray([])
            else:
                public[cls.Meta.model.__name__]={}
        if "id" in dir(instance):
      
            if cls.Meta.private:
                if cls.Meta.to_array:
                    l=[]
                    for x in instance.__annotations__:
                        if instance.__annotations__[x]==int:
                            l.append(getattr(instance,x))
                    privates[cls.Meta.model.__name__][instance.id]=np.asarray(l)
                else:
                    privates[cls.Meta.model.__name__][instance.id]=instance
            else:
                if cls.Meta.to_array:
                    l=[]
                    for x in instance.__annotations__:
                        if instance.__annotations__[x]==int:
                            l.append(getattr(instance,x))
     
                    public[cls.Meta.model.__name__][instance.id]=np.asarray(l)
                else:
                    public[cls.Meta.model.__name__][instance.id]=instance
                 
        else:
            if cls.Meta.private:
            
                if cls.Meta.to_array:
                    l=[]
                    for x in instance.__annotations__:
                        if instance.__annotations__[x]==int:
                            l.append(getattr(instance,x))
                    
                    privates[cls.Meta.model.__name__]= np.append(
                        privates[cls.Meta.model.__name__],
                        [l]
                        )
                else:
                    id=len(privates[cls.Meta.model.__name__])
                    privates[cls.Meta.model.__name__][id]=instance
            else:
               
                if cls.Meta.to_array:
                    l=[]
                    for x in instance.__annotations__:
                        if instance.__annotations__[x]==int:
                            l.append(getattr(instance,x))
                    
                    public[cls.Meta.model.__name__]= np.append(
                        public[cls.Meta.model.__name__],
                        [l]
                        )
                else:

                    id=len(public[cls.Meta.model.__name__])
                    public[cls.Meta.model.__name__][id]=instance
                   


                 

class GraphymlMutation:
    pass
class GraphymlQuery:
    pass

def need_login(fn):
    fn.need_login=True
    return fn

def Auth(request):
    request.user=None
    if 'Authorization' in request.headers:

        import base64
        from .mongo import verify_password
        from uuid import uuid4
        from quart import jsonify
  
        token = request.headers['Authorization'].split(" ")[-1]
   
        user,password=base64.b64decode(token).decode("utf-8").split(":") 
        
        user=schema.user_manager.find_one(username=user)
      
        if verify_password(user.password,password):
            obj_token={"token":str(uuid4()),
                "expire":datetime.datetime.today() + datetime.timedelta(days=1),
                "perms":user.permissions,
                "id":str(user.id),
                "username":user.username,
                "email":user.email}
            tokens=user.tokens
            if len(tokens)>10:
                tokens=user.tokens[10:]
            tokens.append(obj_token)
            user.tokens=tokens
            request.user=user
          


            schema.user_manager.save(user)
            return request,jsonify(obj_token)
        else:
            return request,jsonify({"token":None,"expire":None,"perms":{}})

        
    elif 'x-access-tokens' in request.headers:
        from quart import jsonify
        token = request.headers['x-access-tokens']
    
        
        user=schema.user_manager.find_one(**{"tokens":{
            "$elemMatch":{"token":token}}
            })
       
        if user:
            request.user=user
            obj_token={"token":token,
                "expire":datetime.datetime.today() + datetime.timedelta(days=1),
                "perms":user.permissions,
                "id":str(user.id),
                "username":user.username,
                "email":user.email}
            return request,jsonify(obj_token)

        request.user=user

    return request,None

def Request(environ,sid):
    
    request=type("request",(),environ["asgi.scope"])()

    request.headers={k.decode("utf-8"):v.decode("utf-8") for k,v in request.headers}
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(request.query_string)
    request.query=parse_qs(request.query_string.decode("utf-8"))
    request.sid=sid

    request.namespace=request.query["namespace"][0]
    requests[sid]=request
    Auth(request)
            

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
      
        return self.repository.save(instance)

    def __call__(self,**query):

        item=self.model(**query)
        for key in dir(self.model.__class__):
            try:
                field=getattr(self.model.__class__,key)
            except AttributeError:
                pass
        item=self.repository.save(item)
       
        return item

def evaluate(user,perm,mutations):
    #por defecto los permisos de edicion de campos tienen que estar agregados
    #tambien es gerarquico si usa Model@modify_others equivala a Model.\w+@modify_others

    # modify=$set, rename=$rename, max=$max, remove=$unset, increment=$incr  
    import re
    if not user:
        permissions=mutations.schema.permissions
        
        re.findall(r"(\w+)@(\w+)",perm)
        for perm2 in permissions:
            print("tttttt",[perm,perm2])
            if perm==perm2:
                return True

    elif user.is_superuser:
        return True
    else:
      
        permissions=mutations.schema.permissions
        
        re.findall(r"(\w+)@(\w+)",perm)
        for perm2 in permissions:
        
            if perm==perm2:
                return True

        def check(op):
            #user
            user_others=re.findall(rf"User\.(\w+)@{op}_others",perm)
            user_own=re.findall(rf"User\.(\w+)@{op}_own",perm)
            
            #pertenencia 
            #permisologia
            
            model_others=re.findall(rf"(\w+)\.(\w+)@{op}_others",perm) #tiene accesso en el campo user.permission
            model_own=re.findall(rf"(\w+)\.(\w+)@{op}_own",perm) #tiene un campo referenciando al usuario
            
            if user_others:

                if mutations._schema.has_perm(f"User@{op}_others"):
                    return True

                are_others=False
                for field in query:
                    if getattr(user,field)!=query[field]:
                        are_others=True
                        break

                if are_others:
                    others=user.permissions["User."+user_others[0]+f"@{op}_others"]
                    if not others:
                        return True
                    else:
                        users=self.repository("user").find(query)
                        if not set([user.id for user in users]).difference(set(others)):
                            return True                            
           
            elif user_own:
                if mutations._schema.has_perm(f"User@{op}_own"):
                    return True
                elif mutations._schema.has_perm(perm):
                    return True

            elif model_others:
                if mutations._schema.has_perm(model_others[0]+f"@{op}_others"):#modelo
                    if not user.permissions[perm]:
                        return True
                    else:
                        items=self.repository(model).find(query)
                        if not set([item.id for item in items]).difference(set(user.permissions[perm])):
                            return True
                    
                elif mutations._schema.has_perm(perm):#campo
                    if not user.permissions[perm]:
                        return True
                    else:
                        items=mutations.repository(model).find(query)
                        if not set([item.id for item in items]).difference(set(user.permissions[perm])):
                            return True

            elif model_own:
                model=model_own[0].lower()
                if mutations._schema.has_perm(model_own[0]+f"@{op}_own"):
                    if not user.permissions[perm]:
                        return True
                    else:
                        items=self.repository(model).find({**query ,"user.id":user.id})
                        if not set([item.id for item in items]).difference(set(user.permissions[perm])):
                            return True
                
                elif mutations._schema.has_perm(perm):
          
                    items=mutations.repository(model).find(query)
                    if user.id in [item.user.id for item in items]:
                        return True
        
        if op=="create":
            return user.has_perm(perm)
                
        elif op=="rename":
            return check(op)
        elif op=="max":
            return check(op)
        elif op=="modify":
            return check(op)
        elif op=="delete":
            return check(op)            
        
     
    return False

class Mutation:
    """
    las mutaciones api retornan una instancia o None
    las mutaciones api son compatibles con las sockets
    las mutaciones socket solo son comatibles con socket

    en las mutaciones de socket GET pasa a ser MESSAGE
    tambien tiene TARGETS

    """
    Manager=Manager
    _repositories=[]
    _models=[]
    def __init__(self):
   
        self.manager=self.Manager(self.Meta.repository)
    def _get(self,query):
        results={}
        for elem in query:
            results[elem]=self.repository(elem.lower()).find(**query[elem])
        return results
    async def get(self,request,query,data):
        self._get(query)

    
    
    def _create(self,data):
        instances=[]
        def callback(model,data):
            _model=self.model(model)

            for elem in _model.__annotations__:
                if type(_model.__annotations__[elem])==ModelMetaclass:
                    submodel=_model.__annotations__[elem].__name__.lower()
                    #_submodel=self.model(submodel)
                    
                    if elem in data:
                
                        item=self.repository(submodel).find_one(**{"id":data[elem]})
                        d=dict(item)
                 
                        del d["tokens"]
               
                        data[elem]=item
            item=_model(**data)
      
            return self.repository(model).save(item)
        
    
        if type(data)==list:
            for model,dataset in data:
                instances.append(callback(model.lower(),dataset))
        else:
            
            for model in  data:
                instances.append(callback(model.lower(),data[model]))

       
        if len(instances)>1:
            return instances
        else:
            return instances[0]

    async def create(self,request,query,data):
        d=self._create(data)
       
        return d

    def _create_not_exists(self,data):
        
        def callback(model,data):
            _model=self.model(model)

            for elem in _model.__annotations__:
                if type(_model.__annotations__[elem])==ModelMetaclass:
                    submodel=_model.__annotations__[elem].__name__.lower()
                    #_submodel=self.model(submodel)
                    
                    if elem in data:
                        data[elem]=self.repository(submodel).find_one(**{"id":data[elem]})
        

            if "id" in data and not self.repository(model).find_one(**{"id":data["id"]}):
                self.repository(model).save(_model(**data))

        if type(data)==list:
            for model,dataset in data:
                callback(model.lower(),dataset)
        else:
            for model,dataset in data:
                callback(list(query)[0].lower(),data[model])

    
    
    def _modify(self,query,data):
        instances=[]
        def callback(model,query,data):
            _model=self.model(model)
            d=data.copy()

            for elem in _model.__annotations__:
                if type(_model.__annotations__[elem])==ModelMetaclass:
                    submodel=_model.__annotations__[elem].__name__.lower()
                    _submodel=self.repository(submodel)
                    #Esto es para simplificar agregar el id del documento y no el documento en si
           
                    if elem in data["$set"]:
                        #tambien aprovechamos de actualizar el documento en su colleccion
                        _submodel.update_one({"id":query[elem]["id"]},data)            
                        data["$set"][elem]=data["$set"][elem].id
           
            self.repository(model).update(query,data)
                    
        if type(data)==list:
            for model,dataset in data:
                instances.append(callback(model.lower(),query[model],dataset))
        elif query:
            for q in query:
                instances.append(callback(q.lower(),query[q],data[q]))

        if len(instances)>1:
            return instances
        else:
            return instances[0]
    
    async def update(self,request,query,data):

        self._modify(query,data)
        """
        for model in query:
            if query[model]:
               
                self.repository(model.lower()).update(query[model],data)
            else:
                instance=self.model(model.lower())(data)
                self.repository(model.lower()).save(instance)
        """   

    def _delete(self,query):
        for model in query:
            self.repository(model.lower()).delete(**query[model])

    
      

    async def delete(self,query,data):
        self._delete(query)

    def _event(self,request,message,target,query={},data={}):
        if query:
            self._create(data)
        else:
            self._modify(query,data)

        self.schema.emit(message,target) 




    def repository(self,name):
        for elem in self.__class__.__bases__:
            if elem.Meta.repository.__name__.replace("Repository","").lower()==name:
                return elem.Meta.repository

    def model(self,name):
        for elem in self.__class__.__bases__:
            if elem.Meta.model.__name__.lower()==name:
                return elem.Meta.model

    def has_perm(self,name,perm):
        for elem in self.__class__.__bases__:
            if elem.Meta.model.__name__.lower()==name:
                return perm in elem.Meta.permissions


class Schema:
    def __init__(self,manager,query,mutations,user_manager):
        global schema
        self.manager=manager
        self._query=query
        self.sid=None
        schema=self
        
        
        
        self.mutations=mutations
        self.mutations.schema=self
        self.user_manager=user_manager
        self.user=None
 
        if len(self.user_manager.find(**{}))==0:
            user=self.user_manager(**{
                "username":"admin",
                "password":"1234",
                "permissions":{},
                "tokens":[],
                })
    def need(self,*permissions):
        def wrapper(fn):
            def wrapper2(query,data):
                if self.user.has_perm(*permissions):
                    return fn(query,data)
                else:
                    raise Exception("No tiene los permisos")
            return wrapper2
        return wrapper


    @property
    def query(self):
        import yaml
        with open(self._query) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            return yaml.load(file, Loader=yaml.FullLoader)
    @property
    def permissions(self):
        _permissions=[]
  
        for line in self.query:
            raw=line.split(" ")
            if " " in raw:
                raw.remove(" ")
            _model,*permissions=raw
            _permissions.append(_model+"@show")
            for elem in permissions:
                _permissions.append(_model+"@"+elem)      

            for field in self.query[line]:
                name,*field_permissions=field.split(" ")
                #fields.remove(name)
                for perm in field_permissions:
                    _permissions.append(_model+"."+name+"@"+perm)

        return _permissions

    def socket(self,app):
        import socketio
  
        # wrap with ASGI application
        self.sio = socketio.AsyncServer(
            async_mode='asgi', 
            cors_allowed_origins="*")
        return self.sio


    async def _process(self,request):
        data=await request.json
 
        mutation=data["<MUTATION>"]
        post=data["<DATA>"]
        message=None
        if "<MESSAGE>" in data:
            message=data["<MESSAGE>"]
        
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

                if "<DATA>" in data:
                    

                    m=getattr(self.mutations,mutation)
                    
                    if request.user:
           
                        """
                        if data["<DATA>"] and "$set" in data["<DATA>"]:

                            for field in post["$set"]:
                                
                                valid=evaluate(
                                    request.user,
                                    "modify",
                                    list(data["<QUERY>"])[0]+"."+field+"@modify",data["<QUERY>"])
                                if not valid:
                                    raise Exception("No tienes permisos suficientes")
                        """
                        if data["<DATA>"]:
                            
                            #valid=evaluate(request.user,"create",list(data["<QUERY>"])[0]+"@create",request.query)
                            for model in data["<DATA>"]:
                                if data["<QUERY>"]:
                                    valid=evaluate(
                                            request.user,
                                            model+"@modify",
                                            self.mutations,
                                           )
                                else:
                                    valid=evaluate(
                                            request.user,
                                            model+"@create",
                                            self.mutations,
                                           )
                                if not valid:
                                    raise Exception("No tienes permisos suficientes")

                        """
                        elif  post:
                            raise Exception("Operaciones por el momento no permitidas")
                        """
                        #el primero es self
                      
                        if m.__code__.co_varnames[1]=="request":
                          
                            return await m(request,data["<QUERY>"],data["<DATA>"])
                        
                        elif "<MESSAGE>" in data:
                           
                            return await m(request,
                                message,
                                data["<TARGET>"],
                                data["<QUERY>"],
                                data["<DATA>"])
                       
                    
                
                    elif "without_login" in dir(m):

                        # Pendiente de las mutaciones que no son por usuarios
                        # ejemplo publicaciones de anonimas 
                      
                        
                        if m.__code__.co_varnames[2]=="message":
                            
                            return await m(request,
                                message,
                                data["<TARGET>"])
                    
                        else:
                            return await m(request,data["<QUERY>"],data["<DATA>"])
                        
                    elif not request.user and  data["<DATA>"]:
              

                        valid=True
                        for model in data["<DATA>"]:
                            valid=evaluate(
                                    None,
                                    model+"@create",
                                    self.mutations,
                                   )
                            if not valid:
                                raise Exception("No tienes permisos suficientes")
                        if m.__code__.co_varnames[2]=="message":
                            
                            return await m(request,
                                message,
                                data["<TARGET>"])
                    
                        else:
                            return await m(request,data["<QUERY>"],data["<DATA>"])
                    else:
                        raise Exception("Necesitas inciar sesion")
               


            except Exception as e:
         
                import traceback
                from io import  StringIO
                s=StringIO()
                traceback.print_exc(file=s)
                s.seek(0)
                msg=s.read()
                print(msg)
                e.mutation=Exception(msg)
                return e
        else:
            print("mutacion no encontrada: ",mutation)
        # import pyyaml module
    def set_user(self,user):
        self.user=user
        

        
        
    
            

            
    
    
    async def process(self,request,event=None,sid=None):
        import json
        data=await request.json

        if event:
            data["<MUTATION>"]=event
            request.target=data["<TARGET>"]
        if type(data)!=dict:
            raw=data
            data=json.loads(raw)

    
        instance=None
  
        if "<DATA>" in data:
            instance=await self._process(request)
            l=[]
     
            if "<GET>" in data:
                
                for model in data["<GET>"]:

                    
                    if model=="$self" and instance:
                        #agregar el limpiador de campos visibles en query.yml
              
                        data["<GET>"]
                        if type(instance)==tuple:
                            pass
                        else:

                            # {$self:[field1,field2]}
                            if type(data["<GET>"])==dict:

                                l.append(["self",
                                    serialize({ k:v for k,v in filter(
                                        lambda item: item[0] in data["<GET>"]["$self"] if data["<GET>"]["$self"] else True,
                                        instance.dict().items())
                                    },model=instance.__class__.__name__,
                                    user=request.user,
                                    schema=self)
                                    ])
                            else:
                                l.append(["self",serialize(instance,
                                    model=instance.__class__.__name__,
                                    user=request.user,
                                    schema=self)])

                    elif model[0].isupper():
                    
                        for mutation in self.mutations.__class__.__bases__:
                           
                            if "repository" not in dir(mutation.Meta):
                                raise Exception(f"mutation '{mutation.__name__}' not has repository")
                         
                            if "Meta" in dir(mutation.Meta.repository) and \
                                mutation.Meta.repository.Meta.model.__name__==model:

                                if has_perm(request.user,f"{model}@show",self):
                                    
                                    l.append([model,
                                        serialize(
                                            mutation.Meta.repository.find(
                                                **data["<GET>"][model]),
                                            model=model,
                                            user=request.user,
                                            schema=self)
                                        ])
                         

                                else:
                       
                                    return self.abort(503,description="Permissions denigate")

            
            response={"response":None,"error":None}
            status=200
       
            if isinstance(instance,Exception):
            
                if self.user and self.user.is_superuser:
                    response["error"]=str(instance)
                    status=500
                else:
                    response["error"]=f"Ocurrio un error en la mutacion {instance.mutation}"
                    status=500
            
            if len(l)>1:
                response["response"]=l
                
            elif len(l)==1:
                response["response"]=l[0][1]
          
            return self.jsonify(response),status
        elif "<MESSAGE>" in data:

            await self._process(request)

    async def emit(self,event,message,namespace,target=None): 

        if not target:
            await self.sio.emit(event,message)
                
        elif target:
            await self.sio.emit(event,message,namespace=namespace,room=target)
        
        

    async def run(self,request,jsonify,abort,verify_password=None,sid=None):
        import datetime
        self.jsonify=jsonify
        self.abort=abort
        

        
        if "data" in dir(request):
            return await self.process(request)

def has_perm(user,perm,schema):
    if perm.count(".")==3:
        _model,field,_perm=perm.split("@")
    else:
        field=None
 
        _model,_perm=perm.split("@") 
  
    if user:
        if user.is_superuser:
            return True
        if user.permissions and perm in user.permissions:
            return True

    for perm2 in schema.permissions:
        if perm==perm2:
            return True

        
    return False    

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