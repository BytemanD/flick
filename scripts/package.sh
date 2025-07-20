# rm -rf dist/flick-view
set -e

FRONT_DIR=$1

echo "====== 构建前端 ======="
cd ${FRONT_DIR:-"../flick-view"}
echo "前端目录: $(pwd)"
npm install
npm run build
cd -

echo "====== 构建后端 ======="
uv build

echo "======= 打包 =========="
cd dist
backend=$(ls -1 flick-*-py3-none-any.whl -v)
version=$(echo $backend | grep -oP '\d+\.\d+\.\d+')
packageName="flick-all-${version}"

rm -rf ${packageName} ${packageName}.tar.gz
mkdir ${packageName}
cp -r ../../flick-view/dist ${packageName}/flick-view
cp ../scripts/install.sh ${packageName}
cp ${backend} ${packageName}

tar -czf flick-all-${version}.tar.gz flick-all-${version}
rm -rf flick-all-${version}
