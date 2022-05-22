from pprint import  pprint
def clear(user,data,model,schema):
        """
        permissos show
        """
        if user and user.is_superuser:
            print("##########################")
            print("VERIFICANDO PERMISOS USUARIO")
            print("LECTURA")

            return data
        if type(model)!=str:
            model=model.__class__.__name__
        if user:
            fields=list(data.keys())
            for line in schema.query:
                raw=line.split(" ")
           
                if " " in raw:
                    raw.remove(" ")
                _model,*permissions=raw
                print("DDDDDDDDD",[model,_model])
                
                if model==_model:
                    print("##########################")
                    print("VERIFICANDO PERMISOS PUBLICOS")
                    print("LECTURA")
                    print(fields)
                    print("kkkkkkkk",permissions)
                    """
                    for perm in permissions:
                        if perm not in user.permissions:
                            return None
                    """
                    print("$$$$$$",schema.query[line])
                    #El modelo es visible
                    for field in schema.query[line]:
                        print("##### ",field)
                        name,*field_permissions=field.split(" ")
                        
                        if name=="...":
                            fields=[]#hay que checar esto 
                            break
                        print("xxxxxxxxx",name)
                        fields.remove(name)
                        print("--------",field_permissions)
                        for perm in field_permissions:
                            if perm not in user.permissions:
                                print("mmmmmm",name)
                                data.pop(name)
       
     
            for field in fields:
                data.pop(field)
            
        return data