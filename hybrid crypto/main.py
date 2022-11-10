import io
import os
import sys
import time
import subprocess
import datetime
import pymysql
from myaes import claes
from myblowfish import clbf

conn=pymysql.connect(host="localhost", user="root", passwd="", db="vm_database")
cur=conn.cursor()
virtMac_dict={1:['{11214c5e-13d0-4c3b-b7f4-177de85234e2}','Not Running'],2:['{8150d70c-3052-4a9e-9038-18dfaf29a4f2}','Not Running'],3:['{176e7342-1d7d-4429-b401-47951b883ed9}','Not Running'],4:['{529442b7-51c5-4b40-b3ed-9755a0430bfb}','Not Running']}
virtName_dict={1:'Ubuntu1',2:'Ubuntu2',3:'Windows 10',4:'Linux mint'}

def scale_vm():
    print("Enter The VM which needs to be scaled:")
    vm_id=int(input("1.Ubuntu1 2.Ubuntu2 3.Windows 10 4.Linux Mint\n"))
    if(virtMac_dict[vm_id][1]=="Not Running"):
        print("1.RAM 2.Number Of CPUs(1-8)")
        sc=int(input("Choose The Parameter to be scaled:"))
        if(sc==1):
            mem=int(input("Enter The amount of memory needed in MB(4-4096):"))
            cmd="vboxmanage modifyvm %s --memory %d"%(virtMac_dict[vm_id][0],mem)
            subprocess.run(cmd,stderr=subprocess.DEVNULL)
            timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_param="RAM allocated: %d MB"%mem
            cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime,Modified_parameter) VALUES (%s,%s,%s,%s)",(virtName_dict[vm_id],virtMac_dict[vm_id][1],timeupdate,updated_param))
            conn.commit()
        elif(sc==2):
            cpu=int(input("Enter The number of CPUs needed(1-8):"))
            cmd="vboxmanage modifyvm %s --cpus %d"%(virtMac_dict[vm_id][0],cpu)
            subprocess.run(cmd,stderr=subprocess.DEVNULL)
            timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_param="No. of CPUs allocated: %d "%cpu
            cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime,Modified_parameter) VALUES (%s,%s,%s,%s)",(virtName_dict[vm_id],virtMac_dict[vm_id][1],timeupdate,updated_param))
            conn.commit()
        else:
            print("Invalid Input\n")
    else:
        subprocess.run("vboxmanage controlvm %s poweroff"%virtMac_dict[vm_id][0])
        virtMac_dict[vm_id][1]="Not Running"
        timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime) VALUES (%s,%s,%s)",(virtName_dict[vm_id],virtMac_dict[vm_id][1],timeupdate))
        conn.commit()
        time.sleep(5)
        scale_vm()

def run_vm():
    print("Choose Your VM to run:")
    vm_id1=int(input("1.Ubuntu1 2.Ubuntu2 3.Windows 10 4.Linux Mint\n"))
    if(virtMac_dict[vm_id1][1]=="Not Running"):
        subprocess.run('vboxmanage startvm %s'%virtMac_dict[vm_id1][0])
        virtMac_dict[vm_id1][1]="Running"
        timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime) VALUES (%s,%s,%s)",(virtName_dict[vm_id1],virtMac_dict[vm_id1][1],timeupdate))
        conn.commit()
    else:
        check_id=str(input("Do u want to restart VM (Y/N):")).lower()
        if(check_id=="y"):
            subprocess.run("vboxmanage controlvm %s poweroff"%virtMac_dict[vm_id1][0])
            time.sleep(5)
            subprocess.run('vboxmanage startvm %s'%virtMac_dict[vm_id1][0])
            virtMac_dict[vm_id1][1]="Running"
            timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime) VALUES (%s,%s,%s)",(virtName_dict[vm_id1],virtMac_dict[vm_id1][1],timeupdate))
            conn.commit()

def free_vm():
    print("Choose Your VM which you want to free:")
    vm_id2=int(input("1.Ubuntu1 2.Ubuntu2 3.Windows 10 4.Linux Mint\n"))
    if(virtMac_dict[vm_id2][1]=="Not Running"):
        print("Selected VM is not in running status\n")
        timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime) VALUES (%s,%s,%s)",(virtName_dict[vm_id2],virtMac_dict[vm_id2][1],timeupdate))
        conn.commit()
    else:
        subprocess.run("vboxmanage controlvm %s poweroff"%virtMac_dict[vm_id2][0])
        virtMac_dict[vm_id2][1]="Not Running"
        timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime) VALUES (%s,%s,%s)",(virtName_dict[vm_id2],virtMac_dict[vm_id2][1],timeupdate))
        conn.commit()
        time.sleep(5)

def file_transfer():
    directory=str(input("Enter folder in which you want to perform file transfer: "))
    if os.path.isdir(directory) == False:
        os.mkdir(directory)
    os.chdir(directory)

    inputdir=str(input("Enter input directory: "))+"_"+directory
    while(os.path.isdir(inputdir)):
        inputdir=str(input("Directory already exits, Enter new input directory name:"))+"_"+directory
    os.mkdir(inputdir)

    outputdir=str(input("Enter output directory: "))+"_"+directory
    while(os.path.isdir(outputdir)):
        outputdir=str(input("Directory already exits, Enter new input directory name:"))+"_"+directory
    os.mkdir(outputdir)
    
    encryptedfile=inputdir+"_enc"
    print("Available VMs")
    print("1.Ubuntu1\n2.Ubuntu2\n3.Windows 10\n4.Linux Mint")
    v_id1=int(input("Enter VM no. to receive data :"))
    v_id2=int(input("Enter VM no. to send data :"))

    if(virtMac_dict[v_id1][1]=="Running"):
        subprocess.run("vboxmanage controlvm %s poweroff"%virtMac_dict[v_id1][0])
        virtMac_dict[v_id1][1]="Not Running"
        time.sleep(5)
    if(virtMac_dict[v_id2][1]=="Running"):
        subprocess.run("vboxmanage controlvm %s poweroff"%virtMac_dict[v_id2][0])
        virtMac_dict[v_id2][1]="Not Running"
        time.sleep(5)

    subprocess.run('vboxmanage sharedfolder add %s --name %s --hostpath %s --automount'%(virtMac_dict[v_id1][0],inputdir,(os.path.join(os.getcwd(),inputdir))))
    subprocess.run('vboxmanage sharedfolder add %s --name %s --hostpath %s --automount'%(virtMac_dict[v_id2][0],outputdir,(os.path.join(os.getcwd(),outputdir))))
    
    timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime,Transfer_from,Transfer_to) VALUES (%s,%s,%s,%s,%s)",(virtName_dict[v_id1],virtMac_dict[v_id1][1],timeupdate,virtName_dict[v_id1],virtName_dict[v_id2]))
    conn.commit()
    timeupdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO vm_datatable (VM_name,VM_state,Datetime,Transfer_from,Transfer_to) VALUES (%s,%s,%s,%s,%s)",(virtName_dict[v_id2],virtMac_dict[v_id2][1],timeupdate,virtName_dict[v_id1],virtName_dict[v_id2]))
    conn.commit()
    master_key = 0x2b7e151628aed2a6abf7158809cf4f3c
    abc = claes(master_key)
    key = 'This is atest key'
    bey = list(map(ord, key))
    cipher = clbf(bey)
    i = 0
    k = 0

    with open("C:\\files\\hybridcrypto1\\send.txt","r") as readfile:
        with open(os.path.join(os.getcwd(),inputdir,"%s.txt"%(inputdir)),"w") as writefile:
            writefile.write(readfile.read())

    with open((os.path.join(os.getcwd(),inputdir,"%s.txt"%(inputdir))), 'r') as f:
        dat = f.read()
        dat = len(dat)
        f.close()

    with io.open((os.path.join(os.getcwd(),inputdir,"%s.txt"%(inputdir))), 'r') as f:
        with io.open(encryptedfile, "w", encoding="utf-8") as f1:
            while i < dat / 2:
                c = f.read(16)
                if not c:
                    break
                i += 16
                plaintext = int(c.encode("utf-8").hex(), 16)
                crypted = abc.encrypt(plaintext)
                k += len(hex(crypted))
                f1.write(hex(crypted))
            f1.write('0x')
            key = '(' + str(k) + ')' + key
            while True:
                c = f.read(8)
                if not c:
                    break
                crypted = cipher.encrypt(c)
                f1.write(crypted)
            f1.close()
        f.close()

    l = ''
    key1 = key[1:]

    for siz in key1:
        if siz == ')':
            break
        l += siz

    l = int(l) + 4

    with io.open(encryptedfile, "r", encoding="utf-8") as f1:
        with io.open((os.path.join(os.getcwd(),outputdir,"%s.txt"%(outputdir))), "w", encoding="utf-8") as f:
            p = f1.read(2)
            p = f1.read()
            p = p.split("0x")
            m = l - 2 * len(p)
            for x in p:
                m -= len(x)
                if m < 0:
                    for a in range(0, len(x), 8):
                        n = x[a:a + 8]
                        decrypted = cipher.decrypt(n)
                        d = decrypted.decode('UTF-8')
                        f.write(d)
                else:
                    y = int(x, 16)
                    decrypted = abc.decrypt(y)
                    d = bytes.fromhex(hex(decrypted)[2:]).decode("utf-8")
                    f.write(d)
            f.close()
        f1.close()

while(1):
    print("Enter Operation u want to perform:\n")
    ch1=int(input("1.Scale VM\n2.Run VM\n3.Free VM\n4.File transfer\n"))
    if(ch1==1):
        scale_vm()
    elif(ch1==2):
        run_vm()   
    elif(ch1==3):
        free_vm()
    elif(ch1==4):
        file_transfer() 
    else:
        exit()