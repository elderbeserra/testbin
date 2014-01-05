# -*- coding: UTF-8 -*-

import os
import numpy as np
from scipy import ndimage
from datetime import datetime
from dateutil.relativedelta import relativedelta


def readslice(inputfilename, nx, ny):
    fd = open(inputfilename, 'rb')
    data = np.fromfile(file=fd, dtype=np.float32)
    fd.close()
    return data


def latlon_to_grid(lat, lon):
    ylat = lat + 89.
    if lon > 0:
        xlon = lon
    else:
        xlon = lon + 360.
    return [round(xlon, 2), round(ylat, 2)]


def calcula_lapse_rate(dheight, prec, var):
    if dheight > 200:
        if prec > 2:
            return int(round(var - (dheight * 0.0065)))
        else:
            return int(round(var - (dheight * 0.01)))
    else:
        return var


def converte_mes(mes):
    if mes < 10:
        return '0' + str(mes)
    else:
        return str(mes)


""" Lendo da estac_total as listas das latlons e altitudes """

lat = []
latp = []
lon = []
lonp = []
cid = []
dheight = []

with open('estac_total', 'r') as latlonestac:
    latlon = latlonestac.readlines()
    for linha in latlon:
        linha_lixo = linha.split()
        lat.append(float(linha_lixo[0]))
        lon.append(float(linha_lixo[1]))

with open('estac_total_altitudes', 'r') as listaestac:
    lista = listaestac.readlines()
    for data in lista:
        data_lixo = data.split()
        dheight.append(abs(float(data_lixo[2]) - float(data_lixo[3])))
        cid.append(data_lixo[6])


coor = map(latlon_to_grid, lat, lon)

lat_coor = []
lon_coor = []


""""""""""""""""""""""""""""""""""""""
# DEFINICAO DE PARAMETROS DA GRADE
""""""""""""""""""""""""""""""""""""""
# Numero de pontos zonais LON - nx
nx = 360
# Numero de pontos meridionais lat - ny
ny = 180
# Longitude mais OESTE
rlonini = 0.
rlonfim = 360.
# Latitude mais SUL
rlatini = -89.
rlatfim = 90.

""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""
entrada = '/home/operacao/cfst2mprate8meses/cfs30dydados/CFSv2/'
ontem = datetime.today() - relativedelta(days=1)
dataontem = str(ontem.year) + converte_mes(
    ontem.month) + converte_mes(ontem.day)

tmin = readslice(entrada + dataontem +
                 '/tmin.01.' + dataontem + '00.daily_1.0.dat', nx, ny)
tmax = readslice(entrada + dataontem +
                 '/tmax.01.' + dataontem + '00.daily_1.0.dat', nx, ny)
prec = readslice(entrada + dataontem +
                 '/prate.01.' + dataontem + '00.daily_1.0.dat', nx, ny)

rec = tmin.shape[0]
rec /= nx * ny
tmin = tmin.reshape(nx, ny, rec, order='F')
tmax = tmax.reshape(nx, ny, rec, order='F')
prec = prec.reshape(nx, ny, rec, order='F')


output = '/home/operacao/cfst2mprate8meses/cfs30dydados/CFSv2/relatorios_novo/' + \
    dataontem + '/'
os.mkdir(output)
today = datetime.today()
datarodada = today - relativedelta(days=1)
anorod = datarodada.year
mesarod = converte_mes(datarodada.month)
dayarod = converte_mes(datarodada.day)
datarodada1 = str(anorod) + '-' + mesarod + '-' + dayarod

for i in coor:
    saida = ''
    coor_estac = np.array([[i[1]], [i[0]]])
    with open(output + cid[coor.index(i)] + '.csv', 'wb') as writecsv:
        for x in xrange(0, rec):
            prec1 = prec[:, :, x].T
            precip = ndimage.map_coordinates(
                prec[:, :, x].T, coor_estac, order=1, output=np.int)
            tmin1 = tmin[:, :, x].T
            tmini = ndimage.map_coordinates(
                tmin[:, :, x].T, coor_estac, order=1, output=np.int)
            tmax1 = tmax[:, :, x].T
            tmaxi = ndimage.map_coordinates(
                tmax[:, :, x].T, coor_estac, order=1, output=np.int)
            timestamp = today + relativedelta(days=x) - relativedelta(days=1)
            ano = timestamp.year
            mesa = converte_mes(timestamp.month)
            daya = converte_mes(timestamp.day)
            timestampfinal = str(ano) + '-' + mesa + '-' + daya
            saida += timestampfinal + ',' + datarodada1 + ',' + str(precip[0]) + ',' + str(calcula_lapse_rate(
                dheight[coor.index(i)], precip[0], tmini[0])) + ',' + str(calcula_lapse_rate(
                dheight[coor.index(i)], precip[0], tmaxi[0]))
            saida += '\n'
        writecsv.write(saida)

# im = plt.imshow(testet1, origin='lower',
#                 interpolation='nearest', extent=[0, ncols, 0, nrows])
# plt.colorbar(im)
# plt.show()


# fd = open('tmax.01.2013120300.mensal_1.0.dat')

# print map(calcula_lapse_rate(dheight, 3, teste1[:, :, 5].T))
