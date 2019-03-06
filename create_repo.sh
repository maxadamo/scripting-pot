#!/bin/bash
#
if ! test -f ~/.gitlabrc; then
    cat >~/.gitlabrc <<'EOF'
GITLAB_TOKEN='your-token'
GIT_SERVER='gitlab.geant.net'
APPS_GROUP='xx'
PUPPET_GROUP='xx'
export GITLAB_TOKEN GIT_SERVER APPS_GROUP PUPPET_GROUP
EOF
    exit
fi
source ~/.gitlabrc

if [ "$#" -ne 2 ]; then
    echo "You need to provide two arguments: group and repo"
    echo "example: create_repo.sh puppet-apps new_repo"
    exit
fi

if [ "$1" == 'puppet-apps' ]; then
    GROUP="${APPS_GROUP}"
elif [ "$1" == 'puppet' ]; then
    GROUP="${PUPPET_GROUP}"
else
    echo "group name $1 is not recognized"
    exit
fi

REPO=$2

curl --insecure --silent --request POST --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" "https://${GIT_SERVER}/api/v4/projects?name=${REPO}&namespace_id=${GROUP}" | jq

echo -e "\nsleep 3 seconds\n"
sleep 3

mkdir -p ~/puppet6
cd ~/puppet6
git clone gitlab@${GIT_SERVER}:${1}/${REPO}.git
cd ${REPO}
touch README.md
mkdir manifests
cat >./manifests/init.pp <<EOF
# Class: ${REPO}
#
#
class ${REPO} {
  # resources
}
EOF
cat >README.md <<EOF
## module for app ${REPO}
EOF
git add .
git commit -m "add README.md and init.pp"
git push -u origin master

for branch in devops uat production test; do
    git checkout -b $branch
    git push --set-upstream origin $branch
done
