from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
import json
from werkzeug.utils import secure_filename
from tennis_tracker import TennisTracker
from shot_detector import ShotDetector
from speed_analyzer import SpeedAnalyzer
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 設定
UPLOAD_FOLDER = '../uploads'
OUTPUT_FOLDER = '../output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB 限制

# 確保資料夾存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 初始化分析器
tennis_tracker = TennisTracker()
shot_detector = ShotDetector()
speed_analyzer = SpeedAnalyzer()

# 確保處理後影片為瀏覽器可播放的 H.264 MP4 格式
# 若系統未安裝 ffmpeg，會嘗試透過 imageio-ffmpeg 自動下載內建版本
# 若未安裝 imageio-ffmpeg，將跳過轉碼（可能導致瀏覽器無法播放）

def ensure_h264_mp4_safe(input_path: str):
    """以非破壞方式轉碼：輸出到 *_h264.mp4，成功後再原子替換。避免 Windows 檔案佔用導致 500。"""
    try:
        import os
        import subprocess
        try:
            import imageio_ffmpeg as ioff
        except Exception:
            print("提示: 建議安裝 imageio-ffmpeg 以轉碼為 H.264，確保瀏覽器可播放。\n    安裝指令: pip install imageio-ffmpeg")
            return None

        ffmpeg_exe = ioff.get_ffmpeg_exe()
        tmp_output = input_path.rsplit('.mp4', 1)[0] + '_h264.mp4'
        # 若前次殘留，先嘗試刪除暫存輸出
        try:
            if os.path.exists(tmp_output):
                os.remove(tmp_output)
        except Exception:
            pass
        # 將 moov atom 前移（+faststart），並使用瀏覽器通用的像素格式
        cmd = [
            ffmpeg_exe,
            '-y',
            '-i', input_path,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-preset', 'veryfast',
            tmp_output
        ]
        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # 嘗試原子替換，若失敗則保留原檔與新檔並回傳新檔路徑讓呼叫者改用
            try:
                os.replace(tmp_output, input_path)
                return input_path
            except Exception as e:
                print(f"原檔替換失敗，改用轉碼檔回傳：{e}")
                return tmp_output if os.path.exists(tmp_output) else None
        except Exception as e:
            print(f"轉碼失敗（保留原檔）：{e}\n詳細: {getattr(e, 'stderr', b'').decode('utf-8', errors='ignore')}")
            return None
    except Exception as e:
        print(f"轉碼流程發生異常（保留原檔）：{e}")
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上傳影片端點"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': '沒有選擇文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '沒有選擇文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一檔名
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{file_id}.{file_extension}"
            
            # 保存檔案
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
            
            # 獲取影片資訊
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'video_info': {
                    'duration': duration,
                    'fps': fps,
                    'width': width,
                    'height': height,
                    'frame_count': frame_count
                }
            })
        
        return jsonify({'error': '不支援的檔案格式'}), 400
    
    except Exception as e:
        return jsonify({'error': f'上傳失敗: {str(e)}'}), 500

@app.route('/api/analyze/<file_id>', methods=['POST'])
def analyze_video(file_id):
    """分析影片端點"""
    try:
        # 尋找檔案
        video_file = None
        for ext in ALLOWED_EXTENSIONS:
            potential_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{ext}")
            if os.path.exists(potential_file):
                video_file = potential_file
                break
        
        if not video_file:
            return jsonify({'error': '找不到影片檔案'}), 404
        
        # 執行分析
        print(f"開始分析影片: {video_file}")
        
        # 1. 網球追蹤（同時輸出處理後影片）
        processed_video_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_processed.mp4")
        tracking_results = tennis_tracker.track_ball(video_file, output_path=processed_video_path)
        
        # 2. 正反手檢測
        shot_results = shot_detector.detect_shots(video_file, tracking_results)
        
        # 3. 速度分析
        speed_results = speed_analyzer.analyze_speed(tracking_results)

        # 將處理後影片轉碼為瀏覽器兼容格式（若可用，非破壞性輸出）
        try:
            h264_out = ensure_h264_mp4_safe(processed_video_path)
            if h264_out:
                print("已將處理後影片轉碼為 H.264，瀏覽器可播放。")
        except Exception as _:
            pass
        
        # 整合結果
        analysis_results = {
            'file_id': file_id,
            'timestamp': datetime.now().isoformat(),
            'tracking': tracking_results,
            'shots': shot_results,
            'speed': speed_results,
            'summary': {
                'total_shots': len(shot_results.get('shots', [])),
                'forehand_count': len([s for s in shot_results.get('shots', []) if s.get('type') == 'forehand']),
                'backhand_count': len([s for s in shot_results.get('shots', []) if s.get('type') == 'backhand']),
                'max_speed': speed_results.get('max_speed', 0),
                'avg_speed': speed_results.get('avg_speed', 0)
            }
        }
        
        # 保存結果
        result_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_analysis.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'results': analysis_results
        })
    
    except Exception as e:
        print(f"分析錯誤: {str(e)}")
        return jsonify({'error': f'分析失敗: {str(e)}'}), 500

@app.route('/api/results/<file_id>', methods=['GET'])
def get_results(file_id):
    """獲取分析結果"""
    try:
        result_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_analysis.json")
        
        if not os.path.exists(result_file):
            return jsonify({'error': '找不到分析結果'}), 404
        
        with open(result_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'讀取結果失敗: {str(e)}'}), 500

@app.route('/api/video/<file_id>', methods=['GET'])
def get_video(file_id):
    """獲取影片檔案"""
    try:
        for ext in ALLOWED_EXTENSIONS:
            video_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{ext}")
            if os.path.exists(video_file):
                return send_file(video_file)
        
        return jsonify({'error': '找不到影片檔案'}), 404
    
    except Exception as e:
        return jsonify({'error': f'讀取影片失敗: {str(e)}'}), 500

@app.route('/api/processed-video/<file_id>', methods=['GET'])
def get_processed_video(file_id):
    """獲取處理後的影片。注意：不要在此處做任何轉碼或覆蓋，避免 Windows 檔案佔用導致 500。"""
    try:
        processed_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_processed.mp4")
        alt_file = processed_file.rsplit('.mp4', 1)[0] + '_h264.mp4'

        # 優先使用已轉碼的 h264 檔，否則退回原檔
        candidate = None
        if os.path.exists(alt_file):
            candidate = alt_file
        elif os.path.exists(processed_file):
            candidate = processed_file

        if not candidate:
            return jsonify({'error': '找不到處理後的影片'}), 404

        # 明確指定 MIME 類型，並允許 Range 請求（部分內容）
        resp = send_file(candidate, mimetype='video/mp4', conditional=True)
        # 額外保險：確保回應頭包含 Accept-Ranges
        try:
            resp.headers['Accept-Ranges'] = 'bytes'
        except Exception:
            pass
        return resp
    
    except Exception as e:
        return jsonify({'error': f'讀取處理後影片失敗: {str(e)}'}), 500

if __name__ == '__main__':
    print("啟動 Smart Tennis 後端服務...")
    print("伺服器地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
