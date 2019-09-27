import subprocess
import random
import string


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def setUCIOption(option, value):
    command = "/sbin/uci set {}={}".format(option, value)
    print(command)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.communicate()


def setUCIOptions(conf, section_name, section, options, add=False):
    if add:
        command = "/sbin/uci add {} {}".format(conf, section_name)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        process.communicate()

    for option, value in options.items():
        setUCIOption("{}.{}.{}".format(conf, section, option), value)


def commitUCI():
    process = subprocess.Popen("/sbin/uci commit".split(), stdout=subprocess.PIPE)
    process.communicate()


print("Configure router")
router_num = int(input("Router num: "))

print("Configure hostname")
setUCIOptions("system", "", "@system[0]", {
    "hostname": "Router{}".format(router_num),
    "zonename": "Asia/Yekaterinburg",
    "timezone": "<+05>-5"
})

print("Configure network")
setUCIOptions("network", "", "wan", {
    "proto": "static",
    "ipaddr": "192.168.3.{}".format(router_num),
    "netmask": "255.255.252.0",
    "gateway": "192.168.1.141",
    "dns": "8.8.8.8"
})

setUCIOptions("network", "", "lan", {
    "ipaddr": "192.168.100.1",
    "netmask": "255.255.255.0"
})

print("Configure DHCP")
setUCIOptions("dhcp", "", "lan", {
    "ignore": "1",
})
setUCIOptions("dhcp", "", "wan", {
    "ignore": "1",
})

print("Configure wireless")
setUCIOptions("wireless", "", "radio0", {
    "legacy_rates": "1",
    "htmode": "VHT20",
    "channel": "auto",
    "country": "RU",
    "disabled": "0"
})
setUCIOptions("wireless", "", "radio1", {
    "legacy_rates": "1",
    "htmode": "HT20",
    "channel": "auto",
    "country": "RU",
    "disabled": "0"
})
setUCIOptions("wireless", "", "default_radio0", {
    "ssid": "SFBSU_FREE_WIFI{}_5G".format(router_num),
    "isolate": "1"
})
setUCIOptions("wireless", "", "default_radio1", {
    "ssid": "SFBSU_FREE_WIFI{}".format(router_num),
    "isolate": "1"
})

print("Update opkg packages list")
process = subprocess.Popen("/bin/opkg update".split(), stdout=subprocess.PIPE)
process.communicate()

print("Install Chilli, Nginx, Softflowd")
process = subprocess.Popen("/bin/opkg install coova-chilli nginx softflowd".split(), stdout=subprocess.PIPE)
process.communicate()

print("Purge Chilli config")
open('/etc/config/chilli', 'w').close()

print("Set Chilli config")
radiussecret = randomword(12)
setUCIOptions("chilli", "chilli", "@chilli[0]", {
    "tundev": "tun0",
    "network": "",
    "debug": "9",
    "dns1": "8.8.8.8",
    "dns2": "8.8.4.4",
    "radiusserver1": "192.168.1.75",
    "radiusserver2": "192.168.1.75",
    "radiussecret": radiussecret,
    "dhcpif": "br-lan",
    "uamserver": "http://192.168.182.1/"
}, True)

print("Purge Softflowd config")
open('/etc/config/softflowd', 'w').close()

print("Set Softflowd config")
setUCIOptions("softflowd", "softflowd", "@softflowd[0]", {
    "enabled": "1",
    "interface": "tun0",
    "pcap_file": "",
    "timeout": "",
    "max_flows": "8192",
    "host_port": "192.168.1.75:555",
    "pid_file": "/var/run/softflowd.pid",
    "control_socket": "/var/run/softflowd.ctl",
    "export_version": "5",
    "hoplimit": "",
    "tracking_level": "full",
    "track_ipv6": "0",
    "sampling_rate": "1"
}, True)

print("Configure uhttpd")
setUCIOption("uhttpd.main.listen_http", "192.168.3.{}:80".format(router_num))
setUCIOption("uhttpd.main.listen_https", "192.168.3.{}:443".format(router_num))

print("Configure Dropbear")
setUCIOption("dropbear.@dropbear[0].Interface", "wan")

commitUCI()

print("Setup Nginx config")
nginx_conf = """
user nobody nogroup;
worker_processes 1;
events {
    worker_connections 1024;
}
http {
    sendfile on;
    keepalive_timeout 65;
    gzip on;
    server {
        listen 192.168.182.1:80;
        server_name localhost;
        root /www/;
        location / {
            proxy_pass http://192.168.1.75;
            proxy_set_header Host localhost;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
        }
        error_page 403 404 500 502 503 504 /error.html;
        location /error.html {
            internal;
        }
    }
}"""
nginx_conf_file = open("/etc/nginx/nginx.conf", "w")
nginx_conf_file.write(nginx_conf)
nginx_conf_file.close()

error_html = """
<html>
<head>
    <meta charset="utf-8">
    <title>Технические проблемы</title>
</head>
<body>
<h1>Технические проблемы. Попробуйте позже.</h1>
</body>
</html>"""
error_file = open("/www/error.html", "w")
error_file.write(error_html)
error_file.close()

print("Activate services autostart")
process = subprocess.Popen("/etc/init.d/chilli enable".split(), stdout=subprocess.PIPE)
process.communicate()
process = subprocess.Popen("/etc/init.d/softflowd enable".split(), stdout=subprocess.PIPE)
process.communicate()
process = subprocess.Popen("/etc/init.d/nginx enable".split(), stdout=subprocess.PIPE)
process.communicate()

print("Configuration complete")
print("Freeradius secret:", radiussecret)
