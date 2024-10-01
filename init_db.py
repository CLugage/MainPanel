from app import app, db
from app.models import Plan

with app.app_context():
    db.create_all()

    # Create some example plans
    plan1 = Plan(name='Basic', resources='1 CPU, 2048 MB RAM', cost=10, cpus=1, ram=512)
    plan2 = Plan(name='Standard', resources='2 CPU, 4096 MB RAM', cost=20, cpus=1, ram=1500)
    plan3 = Plan(name='Premium', resources='4 CPU, 8192 MB RAM', cost=40, cpus=2, ram=2500)


    db.session.add_all([plan1, plan2, plan3])
    db.session.commit()
