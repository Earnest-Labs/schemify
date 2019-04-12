FROM phusion/baseimage:0.11

# Install prerequisites for building python versions
RUN apt-get update && apt-get install -y git postgresql-client gcc \
    make zlib1g-dev build-essential libncursesw5-dev libgdbm-dev \
    libc6-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev 

# Install pyenv
RUN curl https://pyenv.run | bash \
    && echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.pyenv/bin/init \
    && echo 'eval "$(pyenv init -)"' >> ~/.pyenv/bin/init \
    && echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.pyenv/bin/init \
    && echo '. ~/.pyenv/bin/init' >> ~/.bashrc

# Install Python 3.7.2
RUN . ~/.pyenv/bin/init \
    && pyenv install -v 3.7.2

RUN apt-get install -y libyaml-dev