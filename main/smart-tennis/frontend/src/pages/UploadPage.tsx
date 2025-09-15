import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { uploadVideo } from '../services/api';

const UploadPage: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await uploadVideo(file, (progress) => {
        setUploadProgress(progress);
      });

      if (result.success) {
        // 跳轉到分析頁面
        navigate(`/analysis/${result.file_id}`);
      } else {
        setError(result.error || '上傳失敗');
      }
    } catch (err) {
      setError('上傳過程中發生錯誤');
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          上傳網球影片
        </h1>
        <p className="text-lg text-gray-600">
          支援 MP4、AVI、MOV、MKV 格式，檔案大小限制 100MB
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8">
        {!uploading ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-6xl mb-4">📹</div>
            {isDragActive ? (
              <p className="text-xl text-blue-600">放開以上傳檔案...</p>
            ) : (
              <div>
                <p className="text-xl text-gray-600 mb-2">
                  拖拽影片檔案到此處，或點擊選擇檔案
                </p>
                <p className="text-sm text-gray-500">
                  支援的格式：MP4, AVI, MOV, MKV（最大 100MB）
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center">
            <div className="text-6xl mb-4">⏳</div>
            <h3 className="text-xl font-semibold mb-4">正在上傳影片...</h3>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-gray-600">{uploadProgress.toFixed(1)}% 完成</p>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <div className="text-red-600 text-xl mr-3">❌</div>
              <div>
                <h4 className="text-red-800 font-semibold">上傳失敗</h4>
                <p className="text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">📋 上傳注意事項</h2>
        <ul className="space-y-2 text-gray-700">
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            建議使用高解析度影片以獲得更好的分析效果
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            確保影片中網球和球員清晰可見
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            影片長度建議在 30 秒到 5 分鐘之間
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            分析過程可能需要幾分鐘時間，請耐心等待
          </li>
        </ul>
      </div>
    </div>
  );
};

export default UploadPage;
