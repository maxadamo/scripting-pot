#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo "You need to supply the domain name to check"
    echo "and optionally the second argument is the port number"
    exit
fi

if [ "$#" -eq 1 ]; then
    PORT=$2
else
    PORT="443"
fi

echo "connecting to $1 on port $2 ..."

openssl s_client -connect ${1}:${PORT} </dev/null 2>/dev/null |
    openssl x509 -noout -text |
    awk '/DNS:/{
        gsub(/, DNS:/, "\"\n  - \"");
        sub(/^.*DNS:/, "  - \"");
        printf $0"\"\n"
    }'

