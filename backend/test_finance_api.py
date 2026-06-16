#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务模块 API
"""
import requests
import json

BASE_URL = 'http://localhost:8080/api/v3'

def login():
    """登录获取 token"""
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'identifier': 'admin',
        'password': 'van654321'
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token')
    else:
        print(f"登录失败: {response.text}")
        return None

def test_apis():
    """测试 API"""
    token = login()
    if not token:
        print("无法获取 token，请检查后端服务")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试获取角色列表
    print("\n=== 测试获取财务角色列表 ===")
    response = requests.get(f'{BASE_URL}/finance/roles', headers=headers)
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 测试获取分类列表
    print("\n=== 测试获取收支分类列表 ===")
    response = requests.get(f'{BASE_URL}/finance/categories', headers=headers)
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 测试获取流水列表
    print("\n=== 测试获取流水列表 ===")
    response = requests.get(f'{BASE_URL}/finance/transactions', headers=headers)
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 测试获取财务总览
    print("\n=== 测试获取财务总览 ===")
    response = requests.get(f'{BASE_URL}/finance/overview', headers=headers)
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 测试获取我的权限
    print("\n=== 测试获取我的权限 ===")
    response = requests.get(f'{BASE_URL}/finance/my-permissions', headers=headers)
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test_apis()
