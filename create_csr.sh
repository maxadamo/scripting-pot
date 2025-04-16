#!/usr/bin/env bash
# Script to generate an ECC private key and corresponding Certificate Signing
# Request, without writing key material to disk.

show_help() {
    cat <<EOF
Usage: ${BASH_SOURCE} fqdn <fqdn_2 fqdn_3 fqdn_4 ... fqdn_x>

The first argument will be treated as the Common Name.
Any further arguments will treated as Subject Altenative Names.

EOF
    exit
}

if [ $# -lt 1 ] || [[ "$1" == '-h' ]] || [[ "$1" == '--help' ]]; then
    show_help
fi

CN=$1

if [ -d ./${CN} ]; then
    echo "A directory called ${CN} is already present"
    exit
fi

mkdir $CN
cd $CN
openssl ecparam -out ecparams.txt -name prime256v1

if [ $# -eq 1 ]; then
    # One argument => cn
    openssl req -newkey ec:ecparams.txt \
        -nodes -subj /CN=${CN}/ -keyout ${CN}.key -out ${CN}.csr
else
    # More than one argument => first is cn, rest is SANs
    s="subjectAltName="
    for san in $(echo $@); do
        s="${s}DNS:$san,"
    done
    openssl req -newkey ec:ecparams.txt \
        -nodes -subj /CN=${CN}/ -keyout ${CN}.key -out ${CN}.csr \
        -reqexts SAN -extensions SAN \
        -config <(printf "[req]\ndistinguished_name=rdn\n[rdn]\n[SAN]\n$(echo ${s} | sed 's/.$//')") 2>/dev/null
fi
