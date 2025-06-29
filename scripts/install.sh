set -e

pip uninstall -y flick || true
pip install flick-*-py3-none-any.whl -U -I

mkdir -p /usr/share
rm -rf /usr/share/flick-view
cp -r flick-view /usr/share
