#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务模块 API - 完整版
"""
import requests
import json

BASE_URL = 'http://localhost:8080/api/v3'

def test_finance_apis():
    """测试财务 API"""
    
    # 1. 登录
    print("=== 1. 登录 ===")
    login_resp = requests.post(f'{BASE_URL}/auth/login', json={
        'identifier': 'admin',
        'password': 'van654321'
    })
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.text}")
        return
    
    login_data = login_resp.json()
    token = login_data['data']['token']
    print(f"✅ 登录成功，Token前50字符: {token[:50]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试获取角色列表
    print("\n=== 2. 测试获取财务角色列表 ===")
    resp = requests.get(f'{BASE_URL}/finance/roles', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取成功，共 {len(data['data'])} 个角色")
        for role in data['data'][:3]:
            print(f"  - {role['role_code']}: {role['role_name']}")
    else:
        print(f"❌ 失败: {resp.text[:200]}")
    
    # 3. 测试获取分类列表
    print("\n=== 3. 测试获取收支分类 ===")
    resp = requests.get(f'{BASE_URL}/finance/categories', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取成功，共 {len(data['data'])} 个分类")
    else:
        print(f"❌ 失败: {resp.text[:200]}")
    
    # 4. 测试获取流水列表
    print("\n=== 4. 测试获取流水列表 ===")
    resp = requests.get(f'{BASE_URL}/finance/transactions', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取成功")
    else:
        print(f"❌ 失败: {resp.text[:200]}")
    
    # 5. 测试获取财务总览
    print("\n=== 5. 测试获取财务总览 ===")
    resp = requests.get(f'{BASE_URL}/finance/overview', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取成功")
    else:
        print(f"❌ 失败: {resp.text[:200]}")
    
    # 6. 测试获取我的权限
    print("\n=== 6. 测试获取我的权限 ===")
    resp = requests.get(f'{BASE_URL}/finance/my-permissions', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取成功: {data['data']}")
    else:
        print(f"❌ 失败: {resp.text[:200]}")

if __name__ == '__main__':
    test_finance_apis()
