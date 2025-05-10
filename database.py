from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "mysql+pymysql://root:mypassword@mysql:3306/usuariosdb"
# docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=mypassword -e MYSQL_DATABASE=usuariosdb -p 3306:3306 -d mysql:8.0
# DATABASE_URL = "mysql+pymysql://root:mypassword@127.0.0.1:3306/usuariosdb"

DATABASE_URL = "mysql+pymysql://root:utecmysql@172.31.25.35:8005/usuariosdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
