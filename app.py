from flask import Flask, render_template, Response
import cv2
import redis
import base64
import numpy as np

def base64_to_image(jpg_as_text):
    jpg_original = base64.b64decode(jpg_as_text)
    # jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    # jpg_as_np = np.fromstring(jpg_original, dtype=np.uint8)
    # img = cv2.imdecode(jpg_as_np, flags=1)
    # return img
    return jpg_original

app = Flask(__name__)

# 测试显示视频流
class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        self.video = cv2.VideoCapture('http:10.28.213.54:8080/video')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

class VideoCamera2(object):

    def __init__(self):
        self.rc = redis.StrictRedis(host="10.103.238.162", port="3799", db=0, decode_responses=True, password="123456")
        self.ps = self.rc.pubsub()
        self.ps.subscribe('ch2')

    def get_frame(self):
        for item in self.ps.listen():
            if (isinstance(item['data'], str)):
                frame = base64_to_image(bytes(item['data'], encoding="utf8"))
                return frame


class VideoPose(object):
    def __init__(self):
        self.rc = redis.StrictRedis(host="10.103.238.162", port="3799", db=0, decode_responses=True, password="123456")
        self.ps = self.rc.pubsub()
        self.ps.subscribe('ch1')

    def get_frame(self):
        for item in self.ps.listen():
            if (isinstance(item['data'], str)):
                frame = base64_to_image(bytes(item['data'], encoding="utf8"))
                return frame

class VideoPose3D(object):
    def __init__(self):
        self.rc = redis.StrictRedis(host="10.103.238.162", port="3799", db=0, decode_responses=True, password="123456")
        self.ps = self.rc.pubsub()
        self.ps.subscribe('ch3')

    def get_frame(self):
        for item in self.ps.listen():
            if (isinstance(item['data'], str)):
                frame = base64_to_image(bytes(item['data'], encoding="utf8"))
                return frame


@app.route('/')  # 主页
def index():
    # jinja2模板，具体格式保存在index.html文件中
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')  # 这个地址返回视频流响应
def video_feed():
    return Response(gen(VideoCamera2()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_pose')
def video_pose():
    return Response(gen(VideoPose()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_pose3d')
def video_pose3d():
    return Response(gen(VideoPose3D()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    pass