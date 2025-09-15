import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { getResults, getVideoUrl, getProcessedVideoUrl, AnalysisResults } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const ResultsPage: React.FC = () => {
  const { fileId } = useParams<{ fileId: string }>();
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    if (fileId) {
      loadResults(fileId);
    }
  }, [fileId]);

  const loadResults = async (id: string) => {
    try {
      setLoading(true);
      const data = await getResults(id);
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">⏳</div>
        <h2 className="text-xl font-semibold">載入結果中...</h2>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-6xl mb-4">❌</div>
        <h2 className="text-xl font-semibold mb-4">無法載入結果</h2>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  const speedChartData = {
    labels: results.speed.trajectory_speeds.map((_, i) => `軌跡 ${i + 1}`),
    datasets: [
      {
        label: '最大速度 (km/h)',
        data: results.speed.trajectory_speeds.map(t => 
          (t.max_speed * 3.6 * 0.1).toFixed(1) // 簡化的速度轉換
        ),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      }
    ]
  };

  const shotDistributionData = {
    labels: ['正手', '反手'],
    datasets: [
      {
        data: [results.shots.forehand_count, results.shots.backhand_count],
        backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(255, 99, 132, 0.8)'],
      }
    ]
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          📊 分析結果
        </h1>
        <p className="text-lg text-gray-600">
          您的網球影片分析已完成
        </p>
      </div>

      {/* 標籤頁導航 */}
      <div className="mb-6">
        <nav className="flex space-x-8 border-b">
          {[
            { id: 'summary', label: '📈 總結', name: '總結' },
            { id: 'shots', label: '🏸 擊球分析', name: '擊球' },
            { id: 'speed', label: '⚡ 速度分析', name: '速度' },
            { id: 'videos', label: '🎥 影片', name: '影片' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* 總結標籤頁 */}
      {activeTab === 'summary' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-3xl font-bold text-blue-600">
                {results.summary.total_shots}
              </div>
              <div className="text-gray-600">總擊球數</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-3xl font-bold text-green-600">
                {results.summary.forehand_count}
              </div>
              <div className="text-gray-600">正手</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-3xl font-bold text-red-600">
                {results.summary.backhand_count}
              </div>
              <div className="text-gray-600">反手</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-3xl font-bold text-purple-600">
                {results.speed.max_speed_kmh.toFixed(1)}
              </div>
              <div className="text-gray-600">最高速度 (km/h)</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">正反手分佈</h3>
              <Bar data={shotDistributionData} options={{ responsive: true }} />
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">軌跡速度</h3>
              <Line data={speedChartData} options={{ responsive: true }} />
            </div>
          </div>
        </div>
      )}

      {/* 擊球分析標籤頁 */}
      {activeTab === 'shots' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">擊球詳細分析</h3>
          {results.shots.shots.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">時間</th>
                    <th className="px-4 py-2 text-left">類型</th>
                    <th className="px-4 py-2 text-left">方向</th>
                    <th className="px-4 py-2 text-left">信心分數</th>
                    <th className="px-4 py-2 text-left">揮拍速度</th>
                  </tr>
                </thead>
                <tbody>
                  {results.shots.shots.map((shot, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2">{shot.timestamp.toFixed(2)}s</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-sm ${
                          shot.type === 'forehand' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {shot.type === 'forehand' ? '正手' : '反手'}
                        </span>
                      </td>
                      <td className="px-4 py-2">{shot.side === 'left' ? '左側' : '右側'}</td>
                      <td className="px-4 py-2">{(shot.confidence * 100).toFixed(1)}%</td>
                      <td className="px-4 py-2">{shot.swing_velocity.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-600">未檢測到擊球動作</p>
          )}
        </div>
      )}

      {/* 速度分析標籤頁 */}
      {activeTab === 'speed' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.speed.max_speed_kmh.toFixed(1)}
              </div>
              <div className="text-gray-600">最高速度 (km/h)</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.speed.avg_speed_kmh.toFixed(1)}
              </div>
              <div className="text-gray-600">平均速度 (km/h)</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md text-center">
              <div className="text-2xl font-bold text-purple-600">
                {results.speed.trajectory_speeds.length}
              </div>
              <div className="text-gray-600">追蹤到的軌跡</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">速度分佈</h3>
            {results.speed.speed_distribution.length > 0 ? (
              <div className="space-y-2">
                {results.speed.speed_distribution.map((dist, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span>{dist.range}</span>
                    <span className="font-medium">{dist.count} 次 ({dist.percentage.toFixed(1)}%)</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">無速度分佈數據</p>
            )}
          </div>
        </div>
      )}

      {/* 影片標籤頁 */}
      {activeTab === 'videos' && fileId && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">原始影片</h3>
              <video 
                controls 
                className="w-full rounded"
                src={getVideoUrl(fileId)}
              >
                您的瀏覽器不支援影片播放
              </video>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">處理後影片</h3>
              <video 
                controls 
                className="w-full rounded"
                src={getProcessedVideoUrl(fileId)}
              >
                您的瀏覽器不支援影片播放
              </video>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
