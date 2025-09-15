#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Tennis 環境測試腳本
"""

def test_imports():
    """測試所有必要的模組是否可以正常導入"""
    print("🔍 測試模組導入...")
    
    try:
        import flask
        print("✅ Flask:", flask.__version__)
    except ImportError as e:
        print("❌ Flask 導入失敗:", e)
        return False
    
    try:
        import cv2
        print("✅ OpenCV:", cv2.__version__)
    except ImportError as e:
        print("❌ OpenCV 導入失敗:", e)
        return False
    
    try:
        import numpy as np
        print("✅ NumPy:", np.__version__)
    except ImportError as e:
        print("❌ NumPy 導入失敗:", e)
        return False
    
    try:
        import torch
        print("✅ PyTorch:", torch.__version__)
    except ImportError as e:
        print("❌ PyTorch 導入失敗:", e)
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO 可用")
    except ImportError as e:
        print("❌ Ultralytics 導入失敗:", e)
        return False
    
    return True

def test_backend_modules():
    """測試後端模組"""
    print("\n🔍 測試後端模組...")
    
    try:
        from tennis_tracker import TennisTracker
        print("✅ TennisTracker 可用")
    except ImportError as e:
        print("❌ TennisTracker 導入失敗:", e)
        return False
    
    try:
        from shot_detector import ShotDetector
        print("✅ ShotDetector 可用")
    except ImportError as e:
        print("❌ ShotDetector 導入失敗:", e)
        return False
    
    try:
        from speed_analyzer import SpeedAnalyzer
        print("✅ SpeedAnalyzer 可用")
    except ImportError as e:
        print("❌ SpeedAnalyzer 導入失敗:", e)
        return False
    
    return True

def main():
    """主測試函數"""
    print("🎾 Smart Tennis 環境測試")
    print("=" * 40)
    
    # 測試基本模組
    if not test_imports():
        print("\n❌ 基本模組測試失敗")
        return False
    
    # 測試後端模組
    if not test_backend_modules():
        print("\n❌ 後端模組測試失敗")
        return False
    
    print("\n🎉 所有測試通過！環境配置成功！")
    print("\n📋 下一步:")
    print("1. 執行 start_project.bat 啟動完整專案")
    print("2. 或者分別啟動:")
    print("   - 後端: python backend/app.py")
    print("   - 前端: cd frontend && npm start")
    
    return True

if __name__ == "__main__":
    main()