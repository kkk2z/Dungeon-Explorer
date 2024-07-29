from quart import Quart, request, send_file, send_from_directory, jsonify
from pytube import YouTube
import os
import shutil
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Quart(__name__)

# フォルダの作成
if not os.path.exists('mp4'):
    os.makedirs('mp4')

# スケジューラの設定
scheduler = BackgroundScheduler()

def delete_old_files():
    now = datetime.now()
    for filename in os.listdir('mp4'):
        file_path = os.path.join('mp4', filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if now - file_creation_time > timedelta(weeks=1):
                os.remove(file_path)

scheduler.add_job(delete_old_files, 'interval', days=1)
scheduler.start()

@app.route('/')
async def index():
    return '''
        <form action="/download" method="post">
            YouTube URL: <input type="text" name="url"><br>
            <input type="submit" value="Download">
        </form>
    '''

@app.route('/download', methods=['POST'])
async def download():
    url = (await request.form)['url']
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        output_path = os.path.join('mp4', f"{yt.title}.mp4")

        # ダウンロード処理
        stream.download(output_path=os.path.dirname(output_path), filename=os.path.basename(output_path))
        
        return f"Download completed: <a href='/videos/{yt.title}.mp4'>{yt.title}.mp4</a>"
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/videos/<filename>')
async def videos(filename):
    try:
        return await send_from_directory('mp4', filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)