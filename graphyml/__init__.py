

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
        self.repository.save(item)

class Mutation:
    Manager=Manager
    def __init__(self):
        self.manager=self.Manager(self.Meta.repository)

class Schema:
    def __init__(self,manager,query,mutations,user_manager):
        import yaml

        self.manager=manager
        
        with open(query) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.query= yaml.load(file, Loader=yaml.FullLoader)
        
        self.mutations=mutations
        self.user_manager=user_manager
        if len(self.user_manager.find())==0:
            user=self.user_manager(**{
                "username":"admin",
                "password":"1234",
                "permissions":None,
                })

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
            return getattr(self.mutations,mutation)(query,post)
            
        # import pyyaml module

        
    def has_perm(self,perm,user):

        for model in self.query:
            pass

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
