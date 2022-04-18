
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
        item=self.repository.save(item)
       
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
                

    def _delete(self,model,query):

        self.repository(submodel).delete(query)
    def _evaluate(self,op,perm,query):
        #por defecto los permisos de edicion de campos tienen que estar agregados
        #tambien es gerarquico si usa Model@modify_others quivala a Model.\w+@modify_others

        # modify=$set, rename=$rename, max=$max, remove=$unset, increment=$incr  
        import re
        print("nnnnnnnn")
        
        def check(op):

            self._schema.has_perm(model+f"@{op}_own")
            self._schema.has_perm(model+f"@{op}_others")
            #user
            user_others=re.match(rf"User.(\w+)@{op}_others",perm)
            user_own=re.match(rf"User.(\w+)@{op}_own",perm)
            
            #pertenencia 
            #permisologia
            
            model_others=re.match(rf"(\w+).(\w+)@{op}_others",perm) #tiene accesso en el campo user.permission
            model_own=re.match(rf"(\w+).(\w+)@{op}_own",perm) #tiene un campo referenciando al usuario
            print("cccccccc",user_others,user_own,model_others,model_own)
            if user_others:

                if self._schema.has_perm(f"User@{op}_others"):
                    return True

                are_others=False
                for field in query:
                    if getattr(self.user,field)!=query[field]:
                        are_others=True
                        break

                if are_others:
                    others=self.user.permissions["User."+user_others[0]+f"@{op}_others"]
                    if not others:
                        return True
                    else:
                        users=self.repository("user").find(query)
                        if not set([user.id for user in users]).difference(set(others)):
                            return True                            
           
            elif user_own:
                if self._schema.has_perm(f"User@{op}_own"):
                    return True
                elif self._schema.has_perm(perm):
                    return True

            elif model_others:
                if self._schema.has_perm(model_others[0]+f"@{op}_others"):#modelo
                    if not self.user.permissions[perm]:
                        return True
                    else:
                        items=self.repository(model).find(query)
                        if not set([item.id for item in items]).difference(set(self.user.permissions[perm])):
                            return True
                    
                elif self._schema.has_perm(perm):#campo
                    if not self.user.permissions[perm]:
                        return True
                    else:
                        items=self.repository(model).find(query)
                        if not set([item.id for item in items]).difference(set(self.user.permissions[perm])):
                            return True

            elif model_own:
                if self._schema.has_perm(model_others[0]+f"@{op}_own"):
                    if not self.user.permissions[perm]:
                        return True
                    else:
                        items=self.repository(model).find({**query ,"user.id":self.user.id})
                        if not set([item.id for item in items]).difference(set(self.user.permissions[perm])):
                            return True
                
                elif self._schema.has_perm(perm):
                    model=model_others[0]
                    items=self.repository(model).find(query)
                    if self.schema.user.id in [item.user.id for item in items]:
                        return True
        print(">>>>>>>>>>>",op)
        if op=="create":
            print("aaaaaa",self._schema.has_perm(perm))
            return self._schema.has_perm(perm)
                
        elif op=="rename":
            return check(op)
        elif op=="max":
            return check(op)
        elif op=="modify":
            return check(op)
        elif op=="delete":
            return check(op)            


        return False
    
    async def post(self,query,data):

        for model in query:
            if query[model]:
                self.repository(model).update(query[model],data)
            else:
                instance=self.model(model)(data)
                self.repository(model).save(instance)
                


    async def get(self,query,data):
        pass
    async def delete(self,query,data):
        self.repository()


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
        self.mutations._schema=self
        self.user_manager=user_manager
        self.user=None
 
        if len(self.user_manager.find(**{}))==0:
            user=self.user_manager(**{
                "username":"admin",
                "password":"1234",
                "permissions":{},
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
            for elem in permissions:
                _permissions.append(_model+elem)          
            for field in self.query[line]:
                name,*field_permissions=field.split(" ")
                fields.remove(name)
                for perm in field_permissions:
                    _permissions.append(_model+"."+name+perm)
        return _permissions

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

                if post or query:
                  
                    m=getattr(self.mutations,mutation)

                    if self.user:
                  
                        if "$set" in post:
                            for field in post["$set"]:
                                valid=self.mutations._evaluate(
                                    "modify",
                                    query.keys()[0]+"."+field+"@modify",query)
                                if not valid:
                                    raise Exception("No tienes permisos suficientes")
                        elif post and query:
             
                            valid=self.mutations._evaluate("create",list(query)[0]+"@create",query)
                           
                            if not valid:
                                raise Exception("No tienes permisos suficientes")
                        else:
                            raise Exception("Operaciones por el momento no permitidas")
                        return await m(query,post)
                
                    elif "without_login" in dir(m):

                        # Pendiente de las mutaciones que no son por usuarios
                        # ejemplo publicaciones de anonimas 
                        
                        return await m(query,post)
                    else:
                       
                        raise Exception("Necesitas inciar sesion")
                

            except Exception as e:
                import traceback
                from io import  StringIO
                s=StringIO()
                traceback.print_exc(file=s)
                s.seek(0)
                msg=s.read()
                e.mutation=Exception(msg)
                return e
        # import pyyaml module
    def set_user(self,user):
        self.user=user
        
    def has_perm(self,perm):
        if self.user.is_superuser:
            return True
        if perm.count(".")==3:
            _model,field,_perm=perm.split("@")
        else:
            field=None
            _model,_perm=perm.split("@") 

        if self.user and self.user.permissions and perm in self.user.permissions:
            return True
        return False
        
        
    def clear(self,data,model):
        """
        permissos show
        """
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
                        #agregar el limpiador de campos visibles en query.yml
                        l.append(["self",
                            { k:v for k,v in filter(
                                lambda item: item[0] in data["<GET>"]["$self"] if data["<GET>"]["$self"] else True,
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
            
            response={"response":None,"error":None}
            status=200
            if isinstance(instance,Exception):
            
                if self.user and self.user.is_superuser:
                    response["error"]=str(instance)
                    status=500
                else:
                    response["error"]=f"Ocurrio un error en la mutacion {instance.mutation}"
                    status=500
            print("ffffff",l)
            if len(l)>1:
                response["response"]=l
                
            elif len(l)==1:
                response["response"]=l[0][1]
                
            return self.jsonify(response),status

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
                obj_token={"token":str(uuid4()),"expire":datetime.datetime.today() + datetime.timedelta(days=1),"perms":user.permissions}
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