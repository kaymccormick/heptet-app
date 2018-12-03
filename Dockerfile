FROM extreme6/alpine-node-python-venv
WORKDIR /opt
COPY . /opt/src/heptet-app
RUN \
  pip3 install /opt/src/heptet-app && \
  mkdir -p /heptet/pytests/heptet-app 2> /dev/null && \
  cp -r /opt/src/heptet-app/tests /heptet/pytests/heptet-app/tests && \
  rm -rf /opt/src && \
  rm -rf /opt/venv2 && \
  rm -rf /var/cache/apk && \
  python3 -m venv --system-site-packages /heptet/pytests/heptet-app/venv && \
  source /heptet/pytests/heptet-app/venv/bin/activate && \
  pip install pytest && \
  cd  /heptet/pytests/heptet-app/tests && \
  pytest -m "not integration" && \
  rm -rf /heptet/pytests/heptet-app/venv && \
  rm -rf /root/.cache && \
  echo done


  