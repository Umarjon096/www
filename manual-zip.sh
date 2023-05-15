#!/bin/bash

rm *.update
rm *.zip
mkdir django-starko
cp * django-starko
rm django-starko/manual-zip.sh  # Чтобы не класть в архив пароль
cp -r django_starko/ django-starko
cp -r mc/ django-starko
zip -r ./other/django-starko.zip django-starko
rm -rf django-starko
cd other
VER=$(cat .ver)
ZIP_FILE="pi_${VER}.zip"
zip -r "../${ZIP_FILE}" . -x README.MD
rm django-starko.zip
cd ..
gpg -c --batch -o "opteo_${VER}.update" --passphrase Gor1lla8myBreakfast $ZIP_FILE
rm $ZIP_FILE
echo "Done"
