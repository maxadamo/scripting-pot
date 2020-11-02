#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "You need to supply the domain name to check"
fi

openssl s_client -connect ${1}:443 </dev/null 2>/dev/null |
    openssl x509 -noout -text |
    awk '/DNS:/{
        gsub(/, DNS:/, "\"\n - \"");
        sub(/^.*DNS:/, " - \"");
        printf $0"\"\n"
    }'
