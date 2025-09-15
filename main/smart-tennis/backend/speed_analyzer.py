import numpy as np
import cv2
from scipy.signal import savgol_filter
from scipy.spatial.distance import euclidean
import math

class SpeedAnalyzer:
    def __init__(self):
        """
        初始化速度分析器
        """
        # 標準網球場尺寸 (米)
        self.court_length = 23.77  # 78 feet
        self.court_width = 10.97   # 36 feet for doubles
        
        # 像素到真實世界的轉換比例 (需要標定)
        self.pixel_to_meter_ratio = None
        
        # 平滑參數
        self.smoothing_window = 5
        self.polynomial_order = 2
        
    def analyze_speed(self, tracking_results):
        """
        分析網球速度
        """
        print("開始分析網球速度...")
        
        if not tracking_results or not tracking_results.get('trajectories'):
            return {
                'max_speed': 0,
                'avg_speed': 0,
                'speed_distribution': [],
                'trajectory_speeds': []
            }
        
        fps = tracking_results['video_info']['fps']
        
        trajectory_speeds = []
        all_speeds = []
        
        for trajectory in tracking_results['trajectories']:
            if trajectory and len(trajectory['positions']) > 2:
                speeds = self.calculate_trajectory_speed(trajectory, fps)
                trajectory_speeds.append({
                    'trajectory_id': trajectory['id'],
                    'speeds': speeds,
                    'max_speed': max(speeds) if speeds else 0,
                    'avg_speed': np.mean(speeds) if speeds else 0
                })
                all_speeds.extend(speeds)
        
        # 統計分析
        max_speed = max(all_speeds) if all_speeds else 0
        avg_speed = np.mean(all_speeds) if all_speeds else 0
        
        # 速度分布
        speed_distribution = self.create_speed_distribution(all_speeds)
        
        # 估算真實世界速度
        estimated_real_speeds = self.estimate_real_world_speeds(all_speeds, tracking_results)
        
        return {
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'max_speed_kmh': estimated_real_speeds['max_speed_kmh'],
            'avg_speed_kmh': estimated_real_speeds['avg_speed_kmh'],
            'speed_distribution': speed_distribution,
            'trajectory_speeds': trajectory_speeds,
            'pixel_speeds': all_speeds,
            'calibration_info': {
                'pixel_to_meter_ratio': self.pixel_to_meter_ratio,
                'calibration_method': estimated_real_speeds.get('calibration_method', 'estimated')
            }
        }
    
    def calculate_trajectory_speed(self, trajectory, fps):
        """
        計算單條軌跡的速度
        """
        positions = trajectory['positions']
        if len(positions) < 2:
            return []
        
        # 平滑軌跡
        smoothed_positions = self.smooth_trajectory(positions)
        
        speeds = []
        for i in range(1, len(smoothed_positions)):
            # 計算位移
            dx = smoothed_positions[i][0] - smoothed_positions[i-1][0]
            dy = smoothed_positions[i][1] - smoothed_positions[i-1][1]
            distance = math.sqrt(dx**2 + dy**2)
            
            # 計算時間差
            dt = 1.0 / fps
            
            # 計算速度 (像素/秒)
            speed = distance / dt if dt > 0 else 0
            speeds.append(speed)
        
        return speeds
    
    def smooth_trajectory(self, positions):
        """
        平滑軌跡數據
        """
        if len(positions) < self.smoothing_window:
            return positions
        
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        try:
            # 使用 Savitzky-Golay 濾波器平滑
            smoothed_x = savgol_filter(x_coords, self.smoothing_window, self.polynomial_order)
            smoothed_y = savgol_filter(y_coords, self.smoothing_window, self.polynomial_order)
            
            return list(zip(smoothed_x, smoothed_y))
        except:
            # 如果平滑失敗，返回原始數據
            return positions
    
    def estimate_real_world_speeds(self, pixel_speeds, tracking_results):
        """
        估算真實世界速度
        """
        if not pixel_speeds:
            return {
                'max_speed_kmh': 0,
                'avg_speed_kmh': 0,
                'calibration_method': 'none'
            }
        
        # 方法1: 如果有標定信息
        if self.pixel_to_meter_ratio:
            meter_speeds = [speed * self.pixel_to_meter_ratio for speed in pixel_speeds]
            kmh_speeds = [speed * 3.6 for speed in meter_speeds]  # m/s to km/h
            
            return {
                'max_speed_kmh': max(kmh_speeds),
                'avg_speed_kmh': np.mean(kmh_speeds),
                'calibration_method': 'calibrated'
            }
        
        # 方法2: 基於影片解析度的估算
        video_info = tracking_results.get('video_info', {})
        width = video_info.get('width', 1920)
        height = video_info.get('height', 1080)
        
        # 假設網球場佔據影片的大部分區域
        # 這是一個粗略的估算，實際應用中需要更精確的標定
        estimated_court_width_pixels = width * 0.8  # 假設場地寬度佔80%螢幕寬度
        estimated_pixel_to_meter = self.court_width / estimated_court_width_pixels
        
        meter_speeds = [speed * estimated_pixel_to_meter for speed in pixel_speeds]
        kmh_speeds = [speed * 3.6 for speed in meter_speeds]
        
        # 應用合理性檢查（網球速度通常在10-200 km/h之間）
        filtered_kmh_speeds = [speed for speed in kmh_speeds if 10 <= speed <= 250]
        
        if not filtered_kmh_speeds:
            # 如果所有速度都不合理，使用縮放因子
            scale_factor = 100 / max(pixel_speeds) if pixel_speeds else 1
            kmh_speeds = [speed * scale_factor for speed in pixel_speeds]
            filtered_kmh_speeds = kmh_speeds
        
        return {
            'max_speed_kmh': max(filtered_kmh_speeds) if filtered_kmh_speeds else 0,
            'avg_speed_kmh': np.mean(filtered_kmh_speeds) if filtered_kmh_speeds else 0,
            'calibration_method': 'estimated'
        }
    
    def create_speed_distribution(self, speeds):
        """
        創建速度分布統計
        """
        if not speeds:
            return []
        
        # 創建速度區間
        min_speed = min(speeds)
        max_speed = max(speeds)
        
        if max_speed == min_speed:
            return [{'range': f'{min_speed:.1f}', 'count': len(speeds)}]
        
        num_bins = min(10, len(set(speeds)))  # 最多10個區間
        bin_width = (max_speed - min_speed) / num_bins
        
        distribution = []
        for i in range(num_bins):
            bin_start = min_speed + i * bin_width
            bin_end = bin_start + bin_width
            
            count = sum(1 for speed in speeds if bin_start <= speed < bin_end)
            if i == num_bins - 1:  # 最後一個區間包含最大值
                count = sum(1 for speed in speeds if bin_start <= speed <= bin_end)
            
            distribution.append({
                'range': f'{bin_start:.1f}-{bin_end:.1f}',
                'count': count,
                'percentage': (count / len(speeds)) * 100
            })
        
        return distribution
    
    def calibrate_with_court_markers(self, frame, court_corners):
        """
        使用場地標記進行標定
        """
        if len(court_corners) < 4:
            return False
        
        # 計算已知距離的像素長度
        # 這裡假設 court_corners 是場地四個角的座標
        pixel_width = euclidean(court_corners[0], court_corners[1])
        pixel_length = euclidean(court_corners[1], court_corners[2])
        
        # 計算像素到米的比例
        meter_per_pixel_width = self.court_width / pixel_width
        meter_per_pixel_length = self.court_length / pixel_length
        
        # 使用平均值
        self.pixel_to_meter_ratio = (meter_per_pixel_width + meter_per_pixel_length) / 2
        
        print(f"標定完成，像素到米的比例: {self.pixel_to_meter_ratio:.6f}")
        return True
    
    def analyze_ball_bounce(self, trajectory):
        """
        分析網球彈跳
        """
        if not trajectory or len(trajectory['positions']) < 10:
            return []
        
        positions = trajectory['positions']
        y_coords = [pos[1] for pos in positions]
        
        # 尋找Y軸的局部最大值（可能的彈跳點）
        bounces = []
        for i in range(2, len(y_coords) - 2):
            # 檢查是否為局部最大值（Y軸向下為正）
            if (y_coords[i] > y_coords[i-1] and y_coords[i] > y_coords[i+1] and
                y_coords[i] > y_coords[i-2] and y_coords[i] > y_coords[i+2]):
                
                bounces.append({
                    'frame': i,
                    'position': positions[i],
                    'height': y_coords[i]
                })
        
        return bounces
    
    def calculate_trajectory_statistics(self, trajectory):
        """
        計算軌跡統計信息
        """
        if not trajectory or len(trajectory['positions']) < 2:
            return {}
        
        positions = trajectory['positions']
        
        # 計算軌跡總長度
        total_distance = 0
        for i in range(1, len(positions)):
            distance = euclidean(positions[i-1], positions[i])
            total_distance += distance
        
        # 計算直線距離
        straight_distance = euclidean(positions[0], positions[-1])
        
        # 計算曲率
        curvature = total_distance / straight_distance if straight_distance > 0 else 1
        
        return {
            'total_distance': total_distance,
            'straight_distance': straight_distance,
            'curvature': curvature,
            'start_position': positions[0],
            'end_position': positions[-1]
        }
