FROM python:3.12.4

#RUN git clone https://github.com/manconeg/ssh-over-telegram.git

WORKDIR /ssh-over-telegram

RUN echo '#!/bin/bash' >> setup.sh
RUN echo 'rm -rf config' >> setup.sh
RUN echo 'echo "tg_username=$tg_username" >> config' >> setup.sh
RUN echo 'echo "tg_bot_token=$tg_bot_token" >> config' >> setup.sh
RUN echo 'echo "username=$username" >> config' >> setup.sh
RUN echo 'echo "hostname=$hostname" >> config' >> setup.sh
RUN echo 'echo "port=$port" >> config' >> setup.sh
RUN echo 'echo "path_to_keys=$path_to_keys" >> config' >> setup.sh
RUN echo 'server' >> setup.sh

RUN chmod a+x setup.sh

COPY . .

RUN pip3 install .

CMD ["./setup.sh"]
