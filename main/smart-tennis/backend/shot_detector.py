import cv2
import numpy as np
from collections import deque
import math

class ShotDetector:
    def __init__(self):
        """初始化正反手檢測器（簡化版本，不依賴 mediapipe）"""
        self.mediapipe_available = False
        print("⚠️  使用簡化的擊球檢測（不依賴 MediaPipe）")
        
        # 檢測參數
        self.swing_threshold = 0.3
        self.shot_window = 15
        
    def detect_shots(self, video_path, tracking_results):
        """檢測影片中的正反手擊球（簡化版本）"""
        print("開始檢測正反手擊球（簡化模式）...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"無法開啟影片: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 基於網球軌跡變化檢測擊球
        shots = self.detect_shots_from_ball_trajectory(tracking_results, fps)
        
        cap.release()
        
        print(f"檢測完成，找到 {len(shots)} 次擊球")
        
        return {
            'shots': shots,
            'total_shots': len(shots),
            'forehand_count': len([s for s in shots if s['type'] == 'forehand']),
            'backhand_count': len([s for s in shots if s['type'] == 'backhand'])
        }
    
    def detect_shots_from_ball_trajectory(self, tracking_results, fps):
        """基於網球軌跡檢測擊球"""
        shots = []
        ball_positions = tracking_results.get('ball_positions', [])
        
        if len(ball_positions) < 10:
            return shots
        
        # 計算網球速度變化
        velocities = []
        for i in range(1, len(ball_positions)):
            prev_frame = ball_positions[i-1]
            curr_frame = ball_positions[i]
            
            if prev_frame['detections'] and curr_frame['detections']:
                prev_pos = prev_frame['detections'][0]['center']
                curr_pos = curr_frame['detections'][0]['center']
                
                # 計算速度
                dx = curr_pos[0] - prev_pos[0]
                dy = curr_pos[1] - prev_pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                
                frame_diff = curr_frame['frame_number'] - prev_frame['frame_number']
                if frame_diff > 0:
                    velocity = distance / frame_diff
                    velocities.append({
                        'frame': curr_frame['frame_number'],
                        'velocity': velocity,
                        'position': curr_pos,
                        'direction': (dx, dy)
                    })
        
        # 檢測速度突變（可能的擊球點）
        for i in range(2, len(velocities) - 2):
            current_vel = velocities[i]['velocity']
            prev_vel = velocities[i-1]['velocity']
            next_vel = velocities[i+1]['velocity']
            
            # 檢測速度突然增加（擊球）
            if (current_vel > prev_vel * 1.5 and 
                current_vel > 20 and  # 最小速度閾值
                next_vel > current_vel * 0.7):  # 確保不是雜訊
                
                shot_type = self.classify_shot_simple(velocities[i])
                
                shots.append({
                    'frame': velocities[i]['frame'],
                    'timestamp': velocities[i]['frame'] / fps,
                    'type': shot_type,
                    'side': 'right' if shot_type == 'forehand' else 'left',
                    'confidence': min(current_vel / 100, 1.0),
                    'ball_contact_frame': velocities[i]['frame'],
                    'swing_velocity': current_vel
                })
        
        # 過濾重複檢測
        return self.filter_duplicate_shots(shots)
    
    def classify_shot_simple(self, velocity_data):
        """簡化的擊球分類"""
        # 基於球的移動方向簡單分類
        direction = velocity_data['direction']
        
        # 如果球向右移動較多，假設是正手
        if direction[0] > abs(direction[1]) * 0.5:
            return 'forehand'
        else:
            return 'backhand'
    
    def filter_duplicate_shots(self, shots):
        """過濾重複的擊球檢測"""
        if not shots:
            return shots
        
        filtered_shots = []
        shots.sort(key=lambda x: x['frame'])
        
        for shot in shots:
            is_duplicate = False
            for existing_shot in filtered_shots:
                frame_diff = abs(shot['frame'] - existing_shot['frame'])
                if frame_diff < 30:  # 30幀內的檢測視為重複
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_shots.append(shot)
        
        return filtered_shots