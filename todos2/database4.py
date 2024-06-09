from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sql_database = "sqlite:///./todoapp_html.db"
# sql_database = "postgresql://postgres:popsipopsi999@localhost/ToDoApplicationDatabase"
# sql_database = "mysql+pymysql://root:popsipopsi999@127.0.0.1:3306/todoapplicationdatabase"


engine = create_engine(sql_database, connect_args={'check_same_thread':False})
# engine = create_engine(sql_database)
sessionlocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
base = declarative_base()
