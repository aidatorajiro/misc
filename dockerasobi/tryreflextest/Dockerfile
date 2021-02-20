FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y curl xz-utils sudo
RUN adduser --disabled-password --gecos "" nix
RUN echo "nix:nix" | chpasswd
RUN echo "nix ALL=NOPASSWD: ALL" >> /etc/sudoers
RUN addgroup nix sudo
RUN mkdir -m 0755 /nix && chown nix:nix /nix

USER nix

WORKDIR /home/nix

RUN curl -L https://nixos.org/nix/install | sh
RUN echo 'USER=nix; . /home/nix/.nix-profile/etc/profile.d/nix.sh;' > ~/e.sh
RUN . ~/e.sh; nix-env -i git
RUN . ~/e.sh; git clone https://github.com/aidatorajiro/RDWP --recursive

WORKDIR RDWP/reflex-platform

RUN . ~/e.sh; echo 1 | ./try-reflex
