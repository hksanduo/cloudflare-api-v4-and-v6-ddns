#!/usr/bin/env python3
# _*_coding:utf-8 _*_
import json
import sys,os
import requests
import configparser
import optparse

# get direct path
dir_path = os.path.dirname(os.path.abspath(__file__))

# get args
def getOpts(argc,argv):
    strUsage = "Usage: %prog [option] args"
    parser = optparse.OptionParser(usage=strUsage, description="cloudfalre ipv4 or ipv6 ddns program ")
    parser.add_option('-f', '--force', action="store_false",dest='force', help='force to update ddns',default="false")
    (options, args) = parser.parse_args()
    dict = {'FORCE': ''}
    dict['FORCE'] = options.force
    return dict

#get config.ini data
def getConfigValue(zone,key):
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(dir_path, 'config.ini'))
    value = cfg.get(zone,key,raw=True)
    return value

#set config.ini data
def setConfigValue(zone,key,value):
    cfg = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    cfg.read(os.path.join(dir_path, 'config.ini'))
    cfg[zone][key] = value
    with open(os.path.join(dir_path, 'config.ini'), 'w', encoding='utf-8') as file:
        cfg.write(file)
        file.close()

# get wan ipv4 or ipv6
def getWanIP(force):
    ip = {'IPv4': '','IPv6':''}
    if len(getConfigValue('WANIP','WAN_IS_IPV4')) != 0 and getConfigValue('WANIP','WAN_IS_IPV4') == "true":
        print(getConfigValue('default','WANIPSITE_IPV4'))
        try:
            reponseIpv4 = requests.get(getConfigValue('default','WANIPSITE_IPV4'))
            if reponseIpv4.status_code == 200:
                ip['IPv4']=reponseIpv4.text.replace("\n", "")
            else:
                print("get wan ipv4 error!!! ")
        except Exception:
            print("get wan ipv4 address error!!!")
            # setConfigValue('WANIP','WAN_IS_IPV4','false')
        else:
            # setConfigValue('WANIP','WAN_IS_IPV4','true')
            print("get wan ipv4 address success!!!")
            print("wan ipv4 is:"+ip['IPv4'])
    if len(getConfigValue('WANIP','WAN_IS_IPV6')) != 0 and getConfigValue('WANIP','WAN_IS_IPV6') == "true":
        try:
            reponseIpv6 = requests.get(getConfigValue('default','WANIPSITE_IPV6'))
            if reponseIpv6.status_code == 200:
                ip['IPv6']=reponseIpv6.text.replace("\n", "")
            else:
                print("get wan ipv6 error!!! ")
        except Exception:
            # setConfigValue('WANIP','WAN_IS_IPV6','false')
            print("get wan ipv6 address error!!!")
        else:
            # setConfigValue('WANIP','WAN_IS_IPV6','true')
            print("get wan ipv6 address success!!!")
            print("wan ipv6 is:"+ip['IPv6'])

    old_wan_ipv4  = getConfigValue('WANIP','WAN_IPV4')
    old_wan_ipv6  = getConfigValue('WANIP','WAN_IPV6')

    # determine update ip address
    if old_wan_ipv4 == ip['IPv4'] and old_wan_ipv6 == ip['IPv6'] and force == 'false':
        print("WAN IP Unchanged, to update anyway use flag -f true")
        sys.exit(0)
    else:
        setConfigValue('WANIP','WAN_IPV4',ip['IPv4'])
        setConfigValue('WANIP','WAN_IPV6',ip['IPv6'])
    return ip

def getCFZoneId(cfzone_name):
    CF_USER = getConfigValue('default','cfuser')
    CF_KEY = getConfigValue('default','cfkey')
    cfzone_url = "https://api.cloudflare.com/client/v4/zones?name="+cfzone_name
    headers = {'X-Auth-Email': CF_USER,'X-Auth-Key':CF_KEY,'Content-Type':'application/json'}
    re = requests.get(cfzone_url,headers=headers)
    # print(re.json())
    if re.status_code == 200:
        CFZONE_ID = re.json()['result'][0]['id']
        print("CFZONE_ID is :"+CFZONE_ID)
        return CFZONE_ID
    else:
        print("get CFZone id error !!!")
        sys.exit(0)

def getCFRecordId(cfzone_id,cfrecord_name,ip_type):
    CF_USER = getConfigValue('default','cfuser')
    CF_KEY = getConfigValue('default','cfkey')
    cfzone_url = "https://api.cloudflare.com/client/v4/zones/"+cfzone_id+"/dns_records?name="+cfrecord_name
    headers = {'X-Auth-Email': CF_USER,'X-Auth-Key':CF_KEY,'Content-Type':'application/json'}
    re = requests.get(cfzone_url,headers=headers)
    if re.status_code == 200:
        if ip_type == 'v4':
            CFRECORD_V4_ID = re.json()['result'][0]['id']
            print("CFRECORD_V4_ID is :"+CFRECORD_V4_ID)
            return CFRECORD_V4_ID
        elif ip_type == 'v6':
            CFRECORD_V6_ID = re.json()['result'][1]['id']
            print("CFRECORD_V6_ID is :"+CFRECORD_V6_ID)
            return CFRECORD_V6_ID
        else:
            print("ip type error")
            sys.exit(0)
    else:
        print("get CFZone id error !!!")
        sys.exit(0)

# update cf record info
def updateRecordAndZone():
    CFZONE_ID = getConfigValue('default','cfzone_id')
    CFRECORD_V4_ID = getConfigValue('default','cfrecord_v4_id')
    CFRECORD_V6_ID = getConfigValue('default','cfrecord_v6_id')
    CFZONE_NAME = getConfigValue('default','cfzone_name')
    CFRECORD_NAME = getConfigValue('default','cfrecord_name')
    if CFZONE_ID is None or CFZONE_ID == "":
        print("Updating zone_identifier")
        CFZONE_ID = getCFZoneId(CFZONE_NAME)
        setConfigValue('default','cfzone_id',CFZONE_ID)
    if CFRECORD_V4_ID is None or CFRECORD_V4_ID== "":
        print("Updating record_identifier")
        CFRECORD_V4_ID = getCFRecordId(CFZONE_ID,CFRECORD_NAME,'v4')
        setConfigValue('default','cfrecord_v4_id',CFRECORD_V4_ID)
    if CFRECORD_V6_ID is None or CFRECORD_V6_ID== "":
        print("Updating record_identifier")
        CFRECORD_V6_ID = getCFRecordId(CFZONE_ID,CFRECORD_NAME,'v6')
        setConfigValue('default','cfrecord_v6_id',CFRECORD_V6_ID)

def updateDNS():
    # get update ddns config
    CF_USER = getConfigValue('default','cfuser')
    CF_KEY = getConfigValue('default','cfkey')
    CFZONE_ID = getConfigValue('default','cfzone_id')
    CFRECORD_V4_ID = getConfigValue('default','cfrecord_v4_id')
    CFRECORD_V6_ID = getConfigValue('default','cfrecord_v6_id')
    CFZONE_NAME = getConfigValue('default','cfzone_name')
    CFRECORD_NAME = getConfigValue('default','cfrecord_name')
    WAN_IPV4 = getConfigValue('WANIP','wan_ipv4')
    WAN_IPV6 = getConfigValue('WANIP','wan_ipv6')
    WAN_IS_IPV4 = getConfigValue('WANIP','wan_is_ipv4')
    WAN_IS_IPV6 = getConfigValue('WANIP','wan_is_ipv6')
    CFTTL = getConfigValue('default','cfttl')
    
    # update ddns by ipv4
    if WAN_IS_IPV4 == 'true' and len(WAN_IPV4) !=0 :
        print("Updating DNS to wan ipv4")
        cfrecord_v4_url = "https://api.cloudflare.com/client/v4/zones/"+CFZONE_ID+"/dns_records/"+CFRECORD_V4_ID
        headers = {'X-Auth-Email': CF_USER,'X-Auth-Key':CF_KEY,'Content-Type':'application/json'}
        data = {"id": CFZONE_ID ,"type":"A","name":CFRECORD_NAME,"content":WAN_IPV4,"ttl":CFTTL}
        re = requests.put(cfrecord_v4_url,headers=headers,data=json.dumps(data))
        # print(re.json())
        if re.status_code == 200:
            if re.json()['success'] == True:
                print("update wan ipv4 success")
            else:
                print("update wan ipv4 fail")
        else:
            print("update wan ipv4 request error !!!")
            sys.exit(0)

    # update ddns by ipv6
    if  WAN_IS_IPV6 == 'true' and len(WAN_IPV6) !=0:
        print("Updating DNS to wan ipv6")
        cfrecord_v6_url = "https://api.cloudflare.com/client/v4/zones/"+CFZONE_ID+"/dns_records/"+CFRECORD_V6_ID
        headers = {'X-Auth-Email': CF_USER,'X-Auth-Key':CF_KEY,'Content-Type':'application/json'}
        data = {"id": CFZONE_ID ,"type":"AAAA","name":CFRECORD_NAME,"content":WAN_IPV6,"ttl":CFTTL}
        re = requests.put(cfrecord_v6_url,headers=headers,data=json.dumps(data))
        # print(re.json())
        if re.status_code == 200:
            if re.json()['success'] == True:
                print("update wan ipv6 success")
            else:
                print("update wan ipv6 fail")
        else:
            print("update wan ipv6  request error !!!")
            sys.exit(0)


def main(argc,argv):
    opts = getOpts(argc,argv)
    ip = getWanIP(opts['FORCE'])
    print(ip)
    updateRecordAndZone()
    updateDNS()


if __name__ == '__main__':
    argv = sys.argv[1:]
    argc = len(argv)
    main(argc,argv)
