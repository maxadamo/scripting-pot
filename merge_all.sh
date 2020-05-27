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

    for BRANCH in $(ls .git/refs/heads); do
        if [ $BRANCH != $MYBRANCH -a $BRANCH != 'master' ]; then
            echo -e "${SEPARATOR}\nswitching to $BRANCH"
            git checkout $BRANCH
            git merge $MYBRANCH
            git push
        fi
    done

    echo -e "${SEPARATOR}\nswitching back to $MYBRANCH"
    git checkout $MYBRANCH
    echo -e "${SEPARATOR}\n"

fi
