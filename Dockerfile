# 1 
FROM python:3.6.9-slim-buster

# IMPORTANT FOR CV2 DONT TOUCH
RUN apt-get update -y 
RUN apt-get install -y libsm6 libxext6 libxrender-dev ffmpeg
# FOR NMCLI
# RUN apt-get install network-manager -y

# RUN apt-get install build-essential locales-all joe vim -y
# RUN apt-get install dialog apt-utils usbutils -y
# COPY pylon_arm64.deb .
# RUN dpkg -i pylon_arm64.deb

#2
RUN pip install --upgrade pip
COPY req.txt .
RUN pip install opencv-python==4.5.4.60
RUN pip install -r req.txt
# RUN pip3 install Jetson.GPIO

# 3
COPY aware_cam_control.py /app/aware_cam_control.py
WORKDIR /app

# 4
# ENV PORT 8080
# EXPOSE 8080

# 5
# CMD exec gunicorn --bind :$PORT --workers 4 --timeout 0 app:app
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD exec python3 aware_cam_control.py
# CMD exec sleep 3600