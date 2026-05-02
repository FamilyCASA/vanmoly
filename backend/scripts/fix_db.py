#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    print("Database tables created/updated successfully")
