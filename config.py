import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Jab289503097@localhost/mechanic_shop_db'
    DEBUG = True
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CHACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://jobadiahbryant:yxc4W3OAAUCSJ2rfrjxofHMZLSoydV4N@dpg-d6mcftrh46gs73bj1hr0-a.ohio-postgres.render.com/mechanic_shop_7out')
    CACHE_TYPE = 'SimpleCache'

