#!/bin/bash
#
if [ ! -d .git ]; then
    echo "not a git root directory"
    exit
fi

git up

echo -e "\nYou are merging the repository $(basename $(pwd))\n"
read -p "Are you sure? [Yy] " -n 1 -r
echo

git up

if [[ $REPLY =~ ^[yY]$ ]]; then

    MYBRANCH=$(git rev-parse --abbrev-ref HEAD)
    SEPARATOR="\n============================"

    if [ $MYBRANCH == 'test' ]; then
        git checkout uat
        git merge test
        git push
        git checkout production
        git merge test
        git push
    fi

    if [ $MYBRANCH == 'uat' ]; then
        git checkout production
        git merge test
        git push
    fi

    echo -e "${SEPARATOR}\nswitching back to $MYBRANCH"
    git checkout $MYBRANCH
    echo -e "${SEPARATOR}\n"

fi
