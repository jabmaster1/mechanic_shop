import os
from application import create_app
from application.models import db

app = create_app('ProductionConfig')

with app.app_context():
    # db.drop_all()
    db.create_all()
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)