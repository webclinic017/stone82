FROM ubuntu:18.04


RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y \
	--allow-downgrades --allow-change-held-packages --no-install-recommends \
        # basic
        build-essential git curl vim wget ca-certificates \
        tzdata bzip2 unzip  g++ cmake autoconf automake \
        # monitor tools
        htop iftop iputils-ping net-tools \
        # python
        python3 python3-dev python3-distutils python3-pip
    

WORKDIR /opt
ENV DEV_ENV=/opt/dev
RUN python3 -m venv $DEV_ENV --without-pip
ENV PATH="$DEV_ENV/bin:$PATH"

RUN curl https://bootstrap.pypa.io/pip/3.6/get-pip.py | python3 && \
    pip install --no-cache-dir \
        autopep8 \
        beautifulsoup4 \
        matplotlib \
        numpy \
        pandas \
        slackclient \
        sqlparse \
        PyMySQL \
        lxml \
        requests \
        pandas_datareader \
        dart_fss \
        sklearn \
        mplfinance \
        flask \
        slackeventsapi \
        Pyyaml \
        aiomysql

