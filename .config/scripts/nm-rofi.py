import subprocess
import re

class Network(object):
    def __init__(self,ssid,strength,protocols,used):
        self.ssid = ssid
        self.strength = int(strength)
        self.protocols = protocols
        if used == '*':
            self.used = True
        else:
            self.used = False
    def icon(self):
        icons = ["","","","",""]
        strength = self.strength
        if strength<=35:
            return icons[0]
        elif strength <=50:
            return icons[1]
        elif strength <=75:
            return icons[2]
        elif strength <= 85:
            return icons[3]
        else:
            return icons[4]
    def __str__(self):
        if len(self.ssid)>20:
            padded_ssid = self.ssid[:21]
        else:
            padded_ssid = self.ssid
            padded_ssid = padded_ssid.ljust(21)
        right = ("" if self.protocols is not None else " ") + " " + self.icon()
        return "{0} {1} {2}".format("" if self.used else "",
            padded_ssid,
            right)

nmcli_cmd = ["nmcli", "-c", "no", "-m", "tabular", "-t", "-f", "SSID,IN-USE,SIGNAL,SECURITY", "device", "wifi"]
if __name__ == "__main__":
    placeholder = subprocess.Popen(["rofi","-dmenu","-p","Looking for Networks","-location","3","-xoffset","-20","-yoffset","60","-width","23","-lines","0"])
    p = subprocess.Popen(nmcli_cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out,_ = p.communicate()
    out = out.decode("utf-8")
    placeholder.kill()
    networks = []
    regex = re.compile(r'^(.*?)(?:\:)(.*?)(?:\:)(.*?)(?:\:)(.*?)(?:$)', re.MULTILINE)
    for network in re.findall(regex,out):
        should_add = True
        for n in networks:
            if n.ssid == network[0]:
                n.used=network[1]=='*'or n.used
                should_add = False
        if len(networks)==0 or should_add:
            networks.append(Network(network[0],network[2],network[3],network[1]))
    networks.sort(key=lambda x: x.strength, reverse=True)
    for i in range(len(networks)):
        if networks[i].used:
            temp = networks.pop(i)
            networks.insert(0,temp)
    s = ""
    rofi = subprocess.Popen(["rofi","-dmenu","-p","Wifi","-location","3","-xoffset","-20","-yoffset","60","-width","26","-lines",str(len(networks))],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    i=0
    for n in networks:
        s+=str(n)+" ("+str(i)+")\n"
        i+=1
    out,err = rofi.communicate(input=s.encode())
    if len(out)==0:
        quit()
    output = out.decode("utf-8")
    id = int(output[29:len(output)-2])
    password = ""
    #If there are protocols detected, get a password from the user.
    if len(networks[id].protocols)>0:
        rofi_pass = subprocess.Popen(["rofi","-dmenu","-p","Password","-location","3","-xoffset","-20","-yoffset","60","-width","23","-lines","0"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out,err=rofi_pass.communicate()
        password=out.decode('utf-8')
    #Conenct to network using nmcli
    if password != "":
        connect = subprocess.Popen(["nmcli","device","wifi","connect",networks[id].ssid,"password",password])
        out,_=connect.communicate()
    else:
        connect = subprocess.Popen(["nmcli","device","wifi","connect",networks[id].ssid])
        out,_=connect.communicate()
