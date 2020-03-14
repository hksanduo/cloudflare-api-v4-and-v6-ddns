#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Automatically update your CloudFlare DNS record to the IP, Dynamic DNS
# Can retrieve cloudflare Domain id and list zone's, because, lazy

# Place at:
# curl https://raw.githubusercontent.com/hksanduo/cloudflare-api-v4-and-v6-ddns/master/cf-v4-and-v6-ddns.sh > /usr/local/bin/cf-ddns.sh && chmod +x /usr/local/bin/cf-ddns.sh
# run `crontab -e` and add next line:
# */1 * * * * /usr/local/bin/cf-ddns.sh >/dev/null 2>&1
# or you need log:
# */1 * * * * /usr/local/bin/cf-ddns.sh >> /var/log/cf-ddns.log 2>&1


# Usage:
# cf-ddns.sh -k cloudflare-api-key \
#            -u user@example.com \
#            -h host.example.com \     # fqdn of the record you want to update
#            -z example.com \          # will show you all zones if forgot, but you need this

# Optional flags:
#            -f false|true \           # force dns update, disregard local stored ip

# default config

# API key, see https://www.cloudflare.com/a/account/my-account,
# incorrect api-key results in E_UNAUTH error
CFKEY=

# Username, eg: user@example.com
CFUSER=

# Zone name, eg: example.com
CFZONE_NAME=

# Hostname to update, eg: homeserver.example.com
CFRECORD_NAME=

# Cloudflare TTL for record, between 120 and 86400 seconds
CFTTL=120

# Ignore local file, update ip anyway
FORCE=false

# Site to retrieve WAN ip, other examples are: bot.whatismyipaddress.com, https://api.ipify.org/ ...
WANIPSITE_IPV4="http://ipv4.icanhazip.com"
WANIPSITE_IPV6="http://ipv6.icanhazip.com"

# get parameter
while getopts k:u:h:z:f: opts; do
  case ${opts} in
    k) CFKEY=${OPTARG} ;;
    u) CFUSER=${OPTARG} ;;
    h) CFRECORD_NAME=${OPTARG} ;;
    z) CFZONE_NAME=${OPTARG} ;;
    f) FORCE=${OPTARG} ;;
  esac
done

# If required settings are missing just exit
if [ "$CFKEY" = "" ]; then
  echo "Missing api-key, get at: https://www.cloudflare.com/a/account/my-account"
  echo "and save in ${0} or using the -k flag"
  exit 2
fi
if [ "$CFUSER" = "" ]; then
  echo "Missing username, probably your email-address"
  echo "and save in ${0} or using the -u flag"
  exit 2
fi
if [ "$CFRECORD_NAME" = "" ]; then
  echo "Missing hostname, what host do you want to update?"
  echo "save in ${0} or using the -h flag"
  exit 2
fi

# If the hostname is not a FQDN
if [ "$CFRECORD_NAME" != "$CFZONE_NAME" ] && ! [ -z "${CFRECORD_NAME##*$CFZONE_NAME}" ]; then
  CFRECORD_NAME="$CFRECORD_NAME.$CFZONE_NAME"
  echo " => Hostname is not a FQDN, assuming $CFRECORD_NAME"
fi

# Get current and old WAN ip
WAN_IPv4=`curl -s ${WANIPSITE_IPV4}`
WAN_IPv4_FILE=$HOME/.cf-WAN_IPv4_$CFRECORD_NAME.txt
if [ -f $WAN_IPv4_FILE ]; then
  OLD_WAN_IPv4=`cat $WAN_IPv4_FILE`
else
  echo "No file, need IP"
  OLD_WAN_IPv4=""
fi


# If WAN IP is unchanged an not -f flag, exit here
if [ "$WAN_IPv4" = "$OLD_WAN_IPv4" ] && [ "$FORCE" = false ]; then
  echo "WAN IP Unchanged, to update anyway use flag -f true"
  exit 0
fi

# Get zone_identifier & record_identifier
ID_FILE=$HOME/.cf-id_$CFRECORD_NAME.txt
if [ -f $ID_FILE ] && [ $(wc -l $ID_FILE | cut -d " " -f 1) == 5 ] \
  && [ "$(sed -n '4,1p' "$ID_FILE")" == "$CFZONE_NAME" ] \
  && [ "$(sed -n '5,1p' "$ID_FILE")" == "$CFRECORD_NAME" ]; then
    CFZONE_ID=$(sed -n '1,1p' "$ID_FILE")
    CFRECORD_V4_ID=$(sed -n '2,1p' "$ID_FILE")
    CFRECORD_V6_ID=$(sed -n '3,1p' "$ID_FILE")
else
    echo "Updating zone_identifier & record_identifier"
    CFZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$CFZONE_NAME" -H "X-Auth-Email: $CFUSER" -H "X-Auth-Key: $CFKEY" -H "Content-Type: application/json" | grep -Po '(?<="id":")[^"]*' | head -1 )
    CFRECORD_V4_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CFZONE_ID/dns_records?name=$CFRECORD_NAME" -H "X-Auth-Email: $CFUSER" -H "X-Auth-Key: $CFKEY" -H "Content-Type: application/json"  | grep -Po '(?<="id":")[^"]*' | sed -n '1p' )
    CFRECORD_V6_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CFZONE_ID/dns_records?name=$CFRECORD_NAME" -H "X-Auth-Email: $CFUSER" -H "X-Auth-Key: $CFKEY" -H "Content-Type: application/json"  | grep -Po '(?<="id":")[^"]*' | sed -n '2p' )
    echo "$CFZONE_ID" > $ID_FILE
    echo "$CFRECORD_V4_ID" >> $ID_FILE
    echo "$CFRECORD_V6_ID" >> $ID_FILE
    echo "$CFZONE_NAME" >> $ID_FILE
    echo "$CFRECORD_NAME" >> $ID_FILE
fi

# If WAN is changed, update cloudflare
echo "Updating DNS to $WAN_IPv4"

RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CFZONE_ID/dns_records/$CFRECORD_V4_ID" \
  -H "X-Auth-Email: $CFUSER" \
  -H "X-Auth-Key: $CFKEY" \
  -H "Content-Type: application/json" \
  --data "{\"id\":\"$CFZONE_ID\",\"type\":\"A\",\"name\":\"$CFRECORD_NAME\",\"content\":\"$WAN_IPv4\", \"ttl\":$CFTTL}")

if [ "$RESPONSE" != "${RESPONSE%success*}" ] && [ $(echo $RESPONSE | grep "\"success\":true") != "" ]; then
  echo "Updated succesfuly!"
  echo $WAN_IPv4 > $WAN_IPv4_FILE
else
  echo 'Something went wrong :('
  echo "Response: $RESPONSE"
fi



# IPv6
# Get current and old WAN ip
WAN_IPv6=`curl -s ${WANIPSITE_IPV6}`
WAN_IPv6_FILE=$HOME/.cf-WAN_IPv6_$CFRECORD_NAME.txt
if [ -f $WAN_IPv6_FILE ]; then
  OLD_WAN_IPv6=`cat $WAN_IPv6_FILE`
else
  echo "No file, need IP"
  OLD_WAN_IPv6=""
fi


# If WAN IP is unchanged an not -f flag, exit here
if [ "$WAN_IPv6" = "$OLD_WAN_IPv6" ] && [ "$FORCE" = false ]; then
  echo "WAN IP Unchanged, to update anyway use flag -f true"
  exit 0
fi


# If WAN is changed, update cloudflare
echo "Updating DNS to $WAN_IPv6"

RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CFZONE_ID/dns_records/$CFRECORD_V6_ID" \
  -H "X-Auth-Email: $CFUSER" \
  -H "X-Auth-Key: $CFKEY" \
  -H "Content-Type: application/json" \
  --data "{\"id\":\"$CFZONE_ID\",\"type\":\"AAAA\",\"name\":\"$CFRECORD_NAME\",\"content\":\"$WAN_IPv6\", \"ttl\":$CFTTL}")

if [ "$RESPONSE" != "${RESPONSE%success*}" ] && [ $(echo $RESPONSE | grep "\"success\":true") != "" ]; then
  echo "Updated succesfuly!"
  echo $WAN_IPv6 > $WAN_IPv6_FILE
  exit
else
  echo 'Something went wrong :('
  echo "Response: $RESPONSE"
  exit 1
fi
