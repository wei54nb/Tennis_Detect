import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="text-center">
      <div className="mb-12">
        <h1 className="text-5xl font-bold text-gray-800 mb-6">
          🎾 Smart Tennis
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          使用 AI 技術分析您的網球技巧
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🎯</div>
          <h3 className="text-xl font-semibold mb-2">網球追蹤</h3>
          <p className="text-gray-600">
            使用 YOLOv8 模型精確追蹤網球軌跡
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🏸</div>
          <h3 className="text-xl font-semibold mb-2">正反手檢測</h3>
          <p className="text-gray-600">
            自動識別球員的正手和反手擊球
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">⚡</div>
          <h3 className="text-xl font-semibold mb-2">速度分析</h3>
          <p className="text-gray-600">
            計算網球飛行速度和軌跡統計
          </p>
        </div>
      </div>

      <div className="bg-blue-50 p-8 rounded-lg">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          開始分析您的網球影片
        </h2>
        <p className="text-gray-600 mb-6">
          上傳您的網球比賽或練習影片，我們的 AI 將為您提供詳細的技術分析
        </p>
        <Link
          to="/upload"
          className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          立即上傳影片
        </Link>
      </div>

      <div className="mt-12 text-left">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">功能特點</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start space-x-3">
            <div className="text-green-600 text-xl">✓</div>
            <div>
              <h4 className="font-semibold">高精度追蹤</h4>
              <p className="text-gray-600">使用最新的 YOLO 模型進行物件檢測</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-green-600 text-xl">✓</div>
            <div>
              <h4 className="font-semibold">姿態分析</h4>
              <p className="text-gray-600">使用 MediaPipe 進行人體姿態檢測</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-green-600 text-xl">✓</div>
            <div>
              <h4 className="font-semibold">速度計算</h4>
              <p className="text-gray-600">精確計算網球飛行速度和軌跡</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-green-600 text-xl">✓</div>
            <div>
              <h4 className="font-semibold">統計分析</h4>
              <p className="text-gray-600">提供詳細的比賽統計和可視化圖表</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
