class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:mysqlrootuser@localhost/mymechanicshop'
    DEBUG = True
    
class ProductionConfig:
    pass

class TestingConfig:
    pass