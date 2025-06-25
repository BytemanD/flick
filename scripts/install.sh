set -e
pip install flick-*-py3-none-any.whl -U

mkdir -p /usr/share
rm -rf /usr/share/flick-view
cp -r flick-view /usr/share
