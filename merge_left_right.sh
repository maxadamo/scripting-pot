#!/bin/bash
#
if ! git remove -v &>/dev/null; then
    echo "not a git repository"
    exit
fi

git up

echo -e "\nYou are merging the repository $(basename $(pwd))\n"
read -p "Are you sure? [Yy] " -n 1 -r
echo

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
