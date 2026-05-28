# -*- coding: utf-8 -*-
"""
迁移脚本：为 theme_config 表添加 description 和 section_configs 字段
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
import sqlite3

app = create_app()

with app.app_context():
    # Get the database path from SQLAlchemy
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
    else:
        db_path = 'instance/vanmoly.db'
    
    print(f'Database: {db_path}')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(theme_config)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f'Current columns: {columns}')
    
    # Add missing columns
    if 'description' not in columns:
        cursor.execute("ALTER TABLE theme_config ADD COLUMN description VARCHAR(500)")
        print('Added: description')
    
    if 'section_configs' not in columns:
        cursor.execute("ALTER TABLE theme_config ADD COLUMN section_configs JSON")
        print('Added: section_configs')
    
    conn.commit()
    
    # Verify
    cursor.execute("PRAGMA table_info(theme_config)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f'Final columns: {columns}')
    
    # Show existing themes
    cursor.execute("SELECT id, theme_key, theme_name, is_active FROM theme_config")
    themes = cursor.fetchall()
    print(f'\nExisting themes: {len(themes)}')
    for t in themes:
        print(f'  id={t[0]}, key={t[1]}, name={t[2]}, active={t[3]}')
    
    conn.close()
    print('\nMigration complete!')
