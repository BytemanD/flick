# rm -rf dist/flick-view
set -e


echo "====== 构建前端 ======="
cd ../flick-view
npm install
npm run build
cd -

echo "====== 构建后端 ======="
uv build

echo "======= 打包 =========="
cd dist
rm -rf flick-view
cp -r ../../flick-view/dist ./flick-view
cp ../scripts/install.sh ./

rm -f flick-all.tar.gz
tar -czf flick-all.tar.gz flick-view flick-*-py3-none-any.whl install.sh
