#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Tennis API 測試腳本
"""

import requests
import json

def test_health_endpoint():
    """測試健康檢查端點"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("✅ 健康檢查端點正常")
            print(f"回應: {response.json()}")
            return True
        else:
            print(f"❌ 健康檢查失敗，狀態碼: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🎾 Smart Tennis API 測試")
    print("=" * 40)
    
    print("\n🔍 測試後端 API...")
    
    # 測試健康檢查
    if test_health_endpoint():
        print("\n🎉 後端 API 運行正常！")
        print("\n📋 可用的 API 端點:")
        print("- GET  /api/health - 健康檢查")
        print("- POST /api/upload - 上傳影片")
        print("- POST /api/analyze/<file_id> - 分析影片")
        print("- GET  /api/results/<file_id> - 獲取結果")
        print("- GET  /api/video/<file_id> - 獲取影片")
        
        print("\n💡 提示:")
        print("- 根路徑 / 沒有處理，所以會返回 404")
        print("- 這是正常的，API 服務器只處理 /api/* 路徑")
        print("- 前端應用會在 http://localhost:3000")
    else:
        print("\n❌ 後端 API 測試失敗")
        print("請檢查後端服務是否正在運行")

if __name__ == "__main__":
    main()