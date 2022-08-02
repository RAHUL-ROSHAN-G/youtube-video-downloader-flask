from flask import Flask, request, render_template, session, url_for, redirect, send_file
from pytube import YouTube, extract
from io import BytesIO
from six.moves.urllib.parse import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] =  "654c0fb3968af9d5e6a9b3edcbc7051b"

@app.route("/", methods = ["GET","POST"])
def home():
	if request.method == 'POST':
		session['link'] = request.form.get('url')
		try:
			url = YouTube(session['link'])
			url.check_availability()
			

			def find_video_length():
                # Find the length of the video in hours, minutes, seconds
				duration = url.length
				hours = duration // 3600
				minutes = (duration - hours * 3600) // 60
				seconds = duration % 60
				video_length = str(hours) + ":" + str(minutes) + ":" + str(seconds)
				return video_length

			def get_video_file_size():
                # Convert file size of video to GB or MB
				file_size = url.streams.get_highest_resolution().filesize
				video_file_size_GB = round(file_size / (1024 * 1024 * 1024), 2)
				video_file_size_MB = round(file_size / (1024 * 1024), 2)
				best_video_file_size = str(video_file_size_GB) + ' GB' if video_file_size_GB > 1 else str(video_file_size_MB) + ' MB'
				return best_video_file_size


			video_id = "https://www.youtube.com/embed/"+url.video_id
			video_duration = find_video_length()
			video_file_size = get_video_file_size()
			resolution = url.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()

		except:
			return render_template('error.html')
		return render_template('download.html', 
			url=url,
            video_duration=video_duration,
            resolution=resolution,
            best_video_file_size=video_file_size,
            video_id = video_id
			)
	return render_template('home.html')

@app.route("/download", methods = ["GET","POST"])
def download_video():
	if request.method == "POST":
		buffer = BytesIO()
		url = YouTube(session['link'])
		itag = request.form.get('itag')
		video = url.streams.get_by_itag(itag)
		#video = url.streams.get_highest_resolution()
		video.stream_to_buffer(buffer)
		buffer.seek(0)
		video_name = url.title

		return send_file(buffer,download_name=f'{url.title}.mp4' ,as_attachment=True, mimetype='video/mp4')
	return redirect(url_for('home'))




if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5000, debug = True)
