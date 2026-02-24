class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Jab289503097@localhost/mechanic_shop_db'
    DEBUG = True
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CHACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    pass

