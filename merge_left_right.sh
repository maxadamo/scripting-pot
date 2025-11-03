#!/bin/bash
#
if ! git remote &>/dev/null; then
    echo "not a git repository"
    exit
fi

git-up

echo -e "\nYou are merging the repository $(basename "$(pwd)")\n"
read -p "Are you sure? [Yy] " -n 1 -r
echo

if git branch -a | grep "remotes/origin/production" &>/dev/null; then
    prod_branch='production'
else
    prod_branch='prod'
fi

if [[ $REPLY =~ ^[yY]$ ]]; then

    MYBRANCH=$(git rev-parse --abbrev-ref HEAD)
    SEPARATOR="\n============================"

    if [ "$MYBRANCH" == 'test' ]; then
        git merge uat; git push
        git merge "$prod_branch"; git push
        git checkout uat
        git merge test
        git push
        git checkout "$prod_branch"
        git merge test
        git push
    fi

    if [ "$MYBRANCH" == 'uat' ]; then
        # try to merge back first
        git merge "$prod_branch"; git push
        # checkout "$prod_branch"
        git checkout "$prod_branch"
        git merge uat
        git push
    fi

    echo -e "${SEPARATOR}\nswitching back to $MYBRANCH"
    git checkout "$MYBRANCH"
    echo -e "${SEPARATOR}\n"

fi
