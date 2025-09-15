import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
});

export interface VideoInfo {
  duration: number;
  fps: number;
  width: number;
  height: number;
  frame_count: number;
}

export interface UploadResponse {
  success: boolean;
  file_id?: string;
  filename?: string;
  video_info?: VideoInfo;
  error?: string;
}

export interface AnalysisResults {
  file_id: string;
  timestamp: string;
  tracking: any;
  shots: {
    shots: Shot[];
    total_shots: number;
    forehand_count: number;
    backhand_count: number;
  };
  speed: {
    max_speed: number;
    avg_speed: number;
    max_speed_kmh: number;
    avg_speed_kmh: number;
    speed_distribution: SpeedDistribution[];
    trajectory_speeds: TrajectorySpeed[];
  };
  summary: {
    total_shots: number;
    forehand_count: number;
    backhand_count: number;
    max_speed: number;
    avg_speed: number;
  };
}

export interface Shot {
  frame: number;
  timestamp: number;
  type: 'forehand' | 'backhand';
  side: 'left' | 'right';
  confidence: number;
  ball_contact_frame: number;
  swing_velocity: number;
}

export interface SpeedDistribution {
  range: string;
  count: number;
  percentage: number;
}

export interface TrajectorySpeed {
  trajectory_id: number;
  speeds: number[];
  max_speed: number;
  avg_speed: number;
}

// 上傳影片
export const uploadVideo = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('video', file);

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress(progress);
        }
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || '上傳失敗');
  }
};

// 開始分析
export const analyzeVideo = async (fileId: string): Promise<AnalysisResults> => {
  try {
    // 分析可能耗時數分鐘，覆蓋預設 30 秒的逾時設定
    const response = await api.post(`/analyze/${fileId}`, null, { timeout: 0 }); // 0 = 不逾時
    return response.data.results;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || '分析失敗');
  }
};

// 獲取分析結果
export const getResults = async (fileId: string): Promise<AnalysisResults> => {
  try {
    const response = await api.get(`/results/${fileId}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || '獲取結果失敗');
  }
};

// 獲取原始影片 URL
export const getVideoUrl = (fileId: string): string => {
  return `${API_BASE_URL}/video/${fileId}`;
};

// 獲取處理後影片 URL
export const getProcessedVideoUrl = (fileId: string): string => {
  // 加上時間戳避免瀏覽器快取造成只播放片段
  const ts = Date.now();
  return `${API_BASE_URL}/processed-video/${fileId}?t=${ts}`;
};

// 健康檢查
export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error: any) {
    throw new Error('無法連接到後端服務');
  }
};

export default api;
