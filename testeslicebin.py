# -*- coding: UTF-8 -*-

import numpy as np
import csv
import math
from scipy import ndimage, interpolate
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta


def readslice(inputfilename, nx, ny):
    fd = open(inputfilename, 'rb')
    data = np.fromfile(file=fd, dtype=np.float32)
    fd.close()
    return data


def latlon_to_grid(lat, lon):
    ylat = lat + 90.
    if lon > 0:
        xlon = lon
    else:
        xlon = lon + 360.
    return [round(xlon, 2), round(ylat, 2)]


def calcula_lapse_rate(dheight, prec, var):
    if dheight > 200.:
        if prec > 2.:
            return var - (dheight * 0.0065)
        else:
            return var - (dheight * 0.01)
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


"""PASSAR O COOR NA PORRA DO SCIPY INTERPOLATE CARAI DE ASA!!!"""

""" O CAVALINHO EH FODA!"""

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
# tmax.01.2013121700.daily_1.0.dat
# tmax.01.2013120300.mensal_1.0.dat
# tmax = readslice('tmax.01.2013121700.daily_1.0.dat', nx, ny)
tmin = readslice('tmin.01.2013120300.mensal_1.0.dat', nx, ny)
prec = readslice('prate.01.2013120300.mensal_1.0.dat', nx, ny)

rec = tmin.shape[0]
rec /= nx * ny
tmin = tmin.reshape(nx, ny, rec, order='F')
prec = prec.reshape(nx, ny, rec, order='F')

cidteste = '/home/elder/cidteste/'
for i in coor:
    lat_coor.append(i[0])
    lon_coor.append(i[1])
    coor_estac = np.array([lon_coor, lat_coor])
    with open(cidteste + cid[coor.index(i)] + '.csv', 'wb') as writecsv:
        for x in xrange(0, rec):
            prec1 = prec[:, :, x].T
            precip = ndimage.map_coordinates(prec1, coor_estac)
            tmin1 = tmin[:, :, x].T
            tmini = ndimage.map_coordinates(tmin1, coor_estac)
            timestamp = datetime.today() + relativedelta(months=x)
            ano = timestamp.year
            mesa = converte_mes(timestamp.month)
            timestampfinal = str(ano) + '-' + mesa
            saida = timestampfinal + ',' + str(precip.tolist()) + ',' + str(calcula_lapse_rate(
                dheight[coor.index(i)], precip, tmini).tolist())
            saida = saida.translate(None, '[]')
            writecsv.write(saida + '\n')
    lat_coor.pop()
    lon_coor.pop()

""" IMPORTANTE >> teste1[:.:,1].T
 tranposta, fortran inverte os axis por default! """

# im = plt.imshow(testet1, origin='lower',
#                 interpolation='nearest', extent=[0, ncols, 0, nrows])
# plt.colorbar(im)
# plt.show()


# fd = open('tmax.01.2013120300.mensal_1.0.dat')

# print map(calcula_lapse_rate(dheight, 3, teste1[:, :, 5].T))
