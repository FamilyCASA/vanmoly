import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r'D:\desktop\DESIGNARY-SYS-V3.0\backend')

from app import create_app, db
from app.models.lead_v2 import Lead, LeadFollow, LeadPoint, LeadDistribution
from datetime import datetime, timedelta, date
from sqlalchemy import func, desc, and_

app = create_app()
with app.app_context():
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    tests = [
        ('today_new', lambda: Lead.query.filter(Lead.created_at >= today_start).count()),
        ('today_follow', lambda: LeadFollow.query.filter(LeadFollow.created_at >= today_start).count()),
        ('today_visit', lambda: Lead.query.filter(Lead.visited_at >= today_start).count()),
        ('today_deposit', lambda: Lead.query.filter(Lead.deposit_at >= today_start).count()),
        ('status_stats', lambda: db.session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()),
        ('level_stats', lambda: db.session.query(Lead.conversion_level, func.count(Lead.id)).group_by(Lead.conversion_level).all()),
    ]

    for name, fn in tests:
        try:
            result = fn()
            print(f'OK  {name}: {result}')
        except Exception as e:
            print(f'FAIL {name}: {type(e).__name__}: {e}')
