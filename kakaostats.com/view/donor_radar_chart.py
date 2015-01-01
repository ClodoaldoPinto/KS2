# -*- coding: utf-8 -*-
import pychartdir, sys, locale
from app import app
from flask import request, json, make_response
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

@app.route("/donor-radar-chart")
def donor_radar_chart():

    d = request.args
    radar = d.get('radar')
    try:
        radar = json.loads(radar) # donor_name, days, pontos_0, pontos_7
    except ValueError:
        return ''

    lowX, bigX = 0, 0
    lowY, bigY = sys.maxint, -sys.maxint -1
    days, name, points, slope, y, x = list(), list(), list(), list(), list(), list()

    for l in radar:
        days.append(l[1]); name.append(l[0])
        points.append(float(l[2])); slope.append(float(l[3]) / 7)
        if len(points) == 1:
            x.append(0); y.append(0)
        else:
            x.append((points[-1] - points[0]) / (slope[0] - slope[-1]))
            y.append(points[-1])

    bigX = lowX + 100
    if len(x) > 1:
        if x[1] > lowX + 100: bigX = x[1]
    n = len(radar) - 1

    for i in range(n, 0, -1):
        if x[i] < bigX:
            n = i
            bigX = x[i]
            break

    x, y = list(), list()

    for i in range(0, n + 1):
        x.append([lowX, 1])
        y.append([points[i], 1])
        if y[i][0] < lowY: lowY = y[i][0]
        y[i][1] = slope[i] * bigX + points[i]
        if y[i][1] > bigY: bigY = y[i][1]
        x[i][1] = bigX

    chartX, chartY, plotX, plotY = 640, 300, 520, 220
    c = pychartdir.XYChart(chartX, chartY, pychartdir.Transparent)
    setPlotAreaObj = c.setPlotArea(80, 35, plotX, plotY)
    setPlotAreaObj.setGridColor(0xc0c0c0, 0xc0c0c0, -1, pychartdir.Transparent)
    c.setNumberFormat(',')
    layer = c.addLineLayer2()
    layer.setLineWidth(2)

    for i in range(0, n + 1):
        layer.addDataSet(y[i], -1, name[i])
        layer.setXData(x[i])

    xLabels = list()
    if bigX > 9:
        for i in range(0, 10):
            xLabels.append(locale.format('%.0f', bigX * i / 9.0, True))
    else:
        if bigX < 1: div = bigX
        else: div = int(bigX)
        i = 0
        while i <= max(1, bigX):
            xLabels.append(locale.format('%.1f', i, True))
            i += 1 if div == 0 else bigX/div

    yLabels = list()
    for i in range(0, 10):
        yLabels.append(locale.format('%.0f', (lowY + ((bigY - lowY) * i / 9.0)) / 100, True))

    c.yAxis().setLinearScale2(lowY, bigY, yLabels)
    c.xAxis().setLinearScale2(lowX, bigX, xLabels)
    legend = c.addLegend(95, 40, 1, "normal", 11)
    legend.setBackground(pychartdir.Transparent, pychartdir.Transparent)
    legend.setFontColor(0x202020)
    c.yAxis().setLabelStyle("normal", 8)
    c.xAxis().setLabelStyle("normal", 8)
    c.yAxis().setTitle("Hundred Points", "normal", 10);
    c.xAxis().setTitle("Days","normal", 10)

    m = pychartdir.MultiChart (chartX, chartY, 0xfafafa)
    m.addChart(0, 0, c)
    m.addTitle("Radar Scope", "normal", 13)

    response = make_response(m.makeChart2(pychartdir.PNG))
    response.headers['Content-type'] = 'image/png'
    return response
