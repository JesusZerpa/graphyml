import uuid
from pydantic import SecretStr,ValidationError
from mongomantic import BaseRepository, MongoDBModel,Index
from datetime import datetime
from pydantic import validator
import  hashlib,os,binascii
from typing import  List,Dict
from bson import ObjectId
def connect(host,db):
    from mongomantic import BaseRepository, MongoDBModel, connect
    connect(host,db)
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = b'__hash__' + hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def is_hash(pw: str) -> bool:
    return pw.startswith('__hash__') and len(pw) == 200


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored_password[:72]
    stored_password = stored_password[72:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


class User(MongoDBModel):
    _id:ObjectId
    username:str
    name:str=""
    last_name:str=""
    email:str=""
    password:str=None
    datetime_created:datetime=datetime.now
    meta:dict={}
    tokens:List[dict]=[]
    is_superuser:bool=False
    permissions:Dict[str,list]=None
    @validator('password')
    def hash_password(cls, pw: str) -> str:
        if is_hash(pw):
            return pw
        return hash_password(pw)
    def has_perm(self,perm):
        import graphyml
        return graphyml.has_perm(self,perm)


    def __repr__(self):
       return f"<User {self.username}>"


class UserRepository(BaseRepository):
    class Meta:
        model = User
        collection="user"
        indexes = [
            Index(fields=["+username", "+email"], unique=True)
        ]
