from sqlalchemy import String,DateTime
class User(Base):
    username=Column(String())
    password=Column(String())
    created_at=Column(DateTime())
    
