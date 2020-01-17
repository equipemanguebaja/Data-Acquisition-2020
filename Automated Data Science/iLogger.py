import os
import getpass
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

#diretório do sd
path = '/media/'+getpass.getuser()+'/14DD-7BAE/'

#lista os RUN's
sd = os.listdir(path)
vec = []
for folder in sd:
    if folder.startswith('RUN'):
        num = int(folder[3:])
        vec.append(num)

#diretório atual
arq = os.path.realpath(__file__)[:len(os.path.realpath(__file__))-10]
os.system("cd {} && cp ./arquivos/nao.c . && mv nao.c sim.c".format(arq))

#modifica o programa do read
with open("{}".format(arq+'sim.c'), 'r') as file:
    data = file.readlines()

data[31] = '    sprintf(foldername, "{}");'.format(path)
data[32] = ' \n'
vec.append(-1)
x = list('    int  RUN, part = 0, i = 0, vet[{}] = {};\n'.format(len(vec)+1, vec))

if len(str(len(vec)+1)) == 1:    
    x[40] = '{'
else:
    x[41] = '{'

x[len(x)-3] = '}'
data[26] = "".join(x)


with open("{}".format(arq+'sim.c'), 'w') as file:
    file.writelines(data)

#inicia o programa
os.system("cd {} && gcc sim.c -o suporte".format(arq))
os.system("cd {} && ./suporte".format(arq))

#reseta o arquivo e puxa os arquivos
os.system("cd {} && rm sim.c && rm suporte".format(arq))
for n in vec:
    if n != -1:
        os.system("cd {} && mv RUN{}.csv {}".format(path, n, arq))

#processa o csv
def grafico(numero):
    df = pd.read_csv('{}RUN{}.csv'.format(arq, numero))
    tabela1 = df.set_index('f1')
    tabela2 = df.set_index('f2')
    f2 = tabela1.index.values
    f1 = tabela2.index.values

    vel_bruto =[]
    rot_bruto = []
    rel=[]
    cont = 0

    for i in range(int(len(f1)/10)):
        rot_bruto.append(sum(f1[i*10:i*10+10]))
        vel_bruto.append(sum(f2[i*10:i*10+10]))
    

    rot = [j*20*60 for j in rot_bruto]
    vel = [i*0.584*3.1415*20*3.6/15 for i in vel_bruto]
    
    t = np.linspace(0, 0.05*len(f1)/10, len(f1)/10)


    b, a = signal.butter(4, 0.10, analog=False)

    # Show that frequency response is the same
    impulse = np.zeros(1000)
    impulse[500] = 1

    # Applies filter forward and backward in time
    imp_ff = signal.filtfilt(b, a, impulse)

    # Applies filter forward in time twice (for same frequency response)
    imp_lf = signal.lfilter(b, a, signal.lfilter(b, a, impulse))


    sig_rot = signal.filtfilt(b, a, rot)


    c, d = signal.butter(4, 0.15, analog=False)

    # Show that frequency response is the same
    impulse = np.zeros(1000)
    impulse[500] = 1

    # Applies filter forward and backward in time
    imp_ff = signal.filtfilt(c, d, impulse)

    # Applies filter forward in time twice (for same frequency response)
    imp_lf = signal.lfilter(c, d, signal.lfilter(c, d, impulse))


    sig_vel = signal.filtfilt(c, d, vel)

    maior = 0
    for pnt in range(len(sig_vel)):
        if sig_vel[pnt] > 2:
            maior = pnt
            break
    print(maior)

    plt.plot(sig_vel[maior:maior+240], sig_rot[maior:maior+240], marker='o', linestyle='--', color='b') 
    plt.xlabel('Km/h')
    plt.ylabel('RPM')
    plt.minorticks_on()
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    plt.savefig('{} - Vel x Rot.jpeg'.format(p))
    plt.show()

    t2 = np.linspace(1, len(sig_vel), len(sig_vel))
    t2 = [int(k) for k in t2]

    t_motor = [j*20 for j in rot_bruto]
    t_roda = [i*20/15 for i in vel_bruto]

    sig_t_motor = signal.filtfilt(c, d, t_motor)
    sig_t_roda = signal.filtfilt(c, d, t_roda)


    relacao = [sig_t_motor[i-1]/sig_t_roda[i-1] for i in t2]

    sig_relacao = signal.filtfilt(c, d, relacao)


    relacaocvt = [relacao[i]/8 for i in t2[:-1]]

    plt.plot(sig_rot[30:240],relacaocvt[30:240])
    plt.minorticks_on()
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    plt.xlabel('rotação (RPM)')
    plt.ylabel('Relação de transmissão')

    plt.savefig('{} - relação'.format(p))
    
    plt.show()

#gera os gráficos
p = 1
for o in vec:
    if o != -1:
        grafico(o)
        p +=1
grafico(4)

#reseta a pasta
for m in vec:
    if m != -1:
        os.system("cd {} && rm RUN{}.csv".format(arq, m))
