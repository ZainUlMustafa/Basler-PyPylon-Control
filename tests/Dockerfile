# 1 
FROM python:3.6.9-slim-buster

# IMPORTANT FOR CV2 DONT TOUCH
# RUN apt-get update -y 
# RUN apt-get install -y libsm6 libxext6 libxrender-dev ffmpeg
# FOR NMCLI
# RUN apt-get install network-manager -y


#2
RUN pip3 install --upgrade pip
# COPY req.txt .
# RUN pip3 install opencv-python
# RUN pip3 install -r req.txt
RUN pip3 install Jetson.GPIO

# 3
COPY ./jetson_gpio_trigger.py /app/jetson_gpio_trigger.py
WORKDIR /app

# 4
# ENV PORT 8080
# EXPOSE 8080

# 5
# CMD exec gunicorn --bind :$PORT --workers 4 --timeout 0 app:app
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD exec python3 jetson_gpio_trigger.py