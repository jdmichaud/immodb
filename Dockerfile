FROM ubuntu:xenial

# Create user
RUN useradd jedi --create-home --password jedi && echo "jedi:jedi" | chpasswd && adduser jedi sudo

RUN apt-get update

# Some utilities
RUN apt-get install -y \
  tmux \
  nano \
  curl \
  unzip \
  sudo \
  tig \
  silversearcher-ag \
# Python
  python \
  python-dev \
  python-setuptools

# pip
RUN easy_install pip
RUN pip install requests==2.11.1 \
  lxml==3.6.4


USER jedi

# dotfile configuration
RUN cd /home/jedi && \
  git clone https://github.com/jdmichaud/dotfiles && \
  rm -fr /home/jedi/.mybashrc && \
  ln -s /home/jedi/dotfiles/.mybashrc /home/jedi/.mybashrc && \
  ln -s /home/jedi/dotfiles/.vimrc /home/jedi/.vimrc && \
  ln -s /home/jedi/dotfiles/.vimrc.local /home/jedi/.vimrc.local && \
  ln -s /home/jedi/dotfiles/.vimrc.local.bundles /home/jedi/.vimrc.local.bundles && \
  ln -s /home/jedi/dotfiles/.tmux.conf /home/jedi/.tmux.conf && \
  ln -s /home/jedi/dotfiles/.git /home/jedi/.git && \
  ln -s /home/jedi/dotfiles/sh /home/jedi/sh

# Force color prompt
RUN sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/g' /home/jedi/.bashrc

# Git configuration
RUN git config --global user.email "jean.daniel.michaud@gmail.com" && \
  git config --global user.name "JD"

# Set prompt with image name
RUN echo 'export PS1="`echo $PS1 | sed s/@.h/@immodb/g` "' >> /home/jedi/.profile

