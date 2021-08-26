mjpg_streamer -i "input_uvc.so -d /dev/video2" -o "output_http.so -p 8090 -w /usr/local/share/mjpg-streamer/www/"
#위 코드는 터미널 창에서 수행하는 것이고, /dev/video2 <-여기서 video2는 스트리밍용 웹캠을 연결해주는 과정이다.
