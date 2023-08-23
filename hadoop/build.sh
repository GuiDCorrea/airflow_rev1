
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
set -e
mkdir -p build
if [ ! -d "$DIR/build/apache-rat-0.12" ]; then
   wget "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=creadur/apache-rat-0.12/apache-rat-0.12-bin.tar.gz" -O "$DIR/build/apache-rat.tar.gz"
	cd $DIR/build
	tar zvxf apache-rat.tar.gz
	cd -
fi
java -jar $DIR/build/apache-rat-0.12/apache-rat-0.12.jar $DIR -e public -e apache-rat-0.12 -e .git -e .gitignore
docker build -t apache/hadoop:2 .