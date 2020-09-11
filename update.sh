#!/bin/bash

git config --global user.name "sakurum"
git config --global user.email "sakuranomiyu@gmail.com"

git remote set-url origin https://sakurum:${UPDATE_TOKEN}github.com/sakurum/covid19-mie-getdata.git

git checkout master
git stage data/*
git commit -m "[updater] `date +%Y/%m/%d` の更新"
git push
