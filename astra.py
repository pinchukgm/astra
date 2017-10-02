#!/usr/bin/python3
### BEGIN INIT INFO
# Provides:          skeleton
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       For Astra 4.X to start a many astra pid.
#                    Soon add to Astra PID monitor.
### END INIT INFO
import sys
import subprocess
import os
import time


#Astra path
astrapath = '/bin/astra'
#Astra configs
configspath = '/etc/astra/'
pidfilepath = '/run/astra.pid'

#
astraconfigs = os.listdir(configspath)

def call_help():
    var = """
Мини help()
Запустить все потоки - аргумент [start]
Остановить все потоки - аргумент [stop]
        
Запустить дополнительный поток - аргумент [start] [Название КОНФИГУРАЦИОННОГО ФАЙЛА(НЕ ПУТЬ)]
Остановить один поток - аргумент [stop] [Название КОНФИГУРАЦИОННОГО ФАЙЛА(НЕ ПУТЬ)]
    
Название конфигов:\n
"""
    for conf in astraconfigs:
        var = var + '[' + conf + ']\n'
    print(var)

def get_proc_info(*args):
    if not args:
        script_path = '*'
    else:
        script_path = os.path.join(configspath, args[0])
    running_procs = []
    ps_aux_proc = subprocess.Popen(['/bin/ps aux | grep \'/bin/astra ' + script_path + '\''], shell=True, stdout=subprocess.PIPE)
    ps_info = ps_aux_proc.communicate()[0].split(b'\n')[:-3]
    for index, proc in enumerate(ps_info):
        running_procs.append(proc.decode().split(' '))
        tmp_number_of_space = []
        for sub_index, value in enumerate(running_procs[index]):
            if value == '':
                tmp_number_of_space.append(sub_index)
        tmp_number_of_space.reverse()
        for number in tmp_number_of_space:
            running_procs[index].pop(number)
    return running_procs

def start_proc_astra(conf):
    if conf not in astraconfigs:
        call_help()
    else:
        astra_proc = subprocess.Popen([astrapath, os.path.join(configspath, conf)], stdout=subprocess.DEVNULL)
        open(pidfilepath, 'a').write(astra_proc.pid.__str__() + ' ' + os.path.join(configspath, conf) + '\n')


def start(*args):
    if not args:
        running_procs = get_proc_info()
        if os.path.exists(pidfilepath):
            running = False
            pids = open(pidfilepath).readlines()
            for index, pid in enumerate(pids):
                pids[index] = pid.split(' ')
            for proc in running_procs:
                for pid in pids:
                    if proc[1] == pid[0] and proc[-1].rstrip() == pid[1].rstrip():
                        print('Astra running on pid =', proc[1], 'and config = ', proc[-1])
                        running = True
            if running:
                print('Astra processes start, try [stop or restart]')
            else:
                print('START THREADS')
                for conf in astraconfigs:
                    start_proc_astra(conf)

        else:
            print('START THREADS')
            for conf in astraconfigs:
                start_proc_astra(conf)

    else:
        running_procs = get_proc_info(args[0])
        if running_procs:
            print('Astra process running on pid =', running_procs[0][1], 'and config =', running_procs[0][-1])
        else:
            start_proc_astra(args[0])


def stop(*args):
    if not args:
        running_procs = get_proc_info()
        if running_procs:
            if os.path.exists(pidfilepath):
                if os.path.getsize(pidfilepath) > 0:
                    pids = open(pidfilepath, 'r').readlines()
                    for index, pid in enumerate(pids):
                        pids[index] = pid.split(' ')
                    procs_need_to_kill = []
                    for pid in pids:
                        for proc in running_procs:
                            if pid[0] == proc[1] and pid[1].rstrip() == proc[-1].rstrip():
                                procs_need_to_kill.append(proc)
                    for proc in procs_need_to_kill:
                        print('Stopping astra on pid =', proc[1])
                        os.kill(int(proc[1]), 9)
                    open(pidfilepath, 'w').write('')

                else:
                    os.remove(pidfilepath)
                    print('Astra process not running')
            else:
                print('Astra processes not running')
        else:
            print('Astra processes not running')
    else:
        running_proc = get_proc_info(args[0])
        if running_proc:
            pids = open(pidfilepath, 'r').readlines()
            for index, pid in enumerate(pids):
                pids[index] = pid.split(' ')
            for pid in pids:
                if pid[0] == running_proc[0][1] and pid[1].rstrip() == running_proc[0][-1].rstrip():
                    os.kill(int(running_proc[0][1]), 9)
                    pids.remove(pid)
                    print('Astra proc pid =', running_proc[0][1], 'cfg =', running_proc[0][-1], 'stopped')
            file = open(pidfilepath, 'w')
            for pid in pids:
                file.write(' '.join(pid))
            file.close()
        else:
            print('Astra proc is not running')



if len(sys.argv) == 2:
    if sys.argv[1] == 'start':
        start()
    elif sys.argv[1] == 'stop':
        stop()
    elif sys.argv[1] == 'restart':
        stop()
        start()
    else:
        call_help()
elif len(sys.argv) == 3:
    if sys.argv[1] == 'start':
        start(sys.argv[2])
    elif sys.argv[1] == 'stop':
        print(sys.argv[2])
        stop(sys.argv[2])
    elif sys.argv[1] == 'restart':
        stop(sys.argv[2])
        start(sys.argv[2])
    else:
        call_help()
else:
    start()
