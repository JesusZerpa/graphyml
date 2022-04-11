
from pydantic.main import ModelMetaclass

class GraphymlMutation:
    pass
class GraphymlQuery:
    pass

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
            field=getattr(self.model.__class__,key)
            
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
                "permissions":None,
                })
    @property
    def query(self):
        import yaml
        with open(self._query) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            return yaml.load(file, Loader=yaml.FullLoader)


    def process(self,user,mutation,query=None,post=None):
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
                return getattr(self.mutations,mutation)(query,post)
            except Exception as e:
                e.mutation=mutation
                return e
        # import pyyaml module
    def set_user(self,user):
        self.user=user

        
    def has_perm(self,perm,user):
        if perm.count(".")==3:
            _model,field,_perm=perm.split(".")
        else:
            field=None
            _model,_perm=perm.split(".") 

        if user.permissions and perm in user.permissions:
            return True
        
        
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
