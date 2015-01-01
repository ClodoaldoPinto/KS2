# -*- coding: utf-8 -*-
import pychartdir
from app import app
#from datetime import datetime
from flask import request, json, make_response

def dt(s):
    return pychartdir.chartTime(s[0:4], s[5:7], s[8:10])

@app.route("/team-size-chart")
def team_size_chart():

    d = request.args
    history = d.get('history')
    try:
        history = json.loads(history) # nm, am, day
    except ValueError:
        return ''

    am, am_x, nm, nm_x = [], [], [], []

    am_title = "Active Members"
    nm_title = "New Members"

    d = history[0]
    am.append(pychartdir.NoValue if d[0] is None else d[0])
    am_x.append(dt(d[2]))
    nm.append(pychartdir.NoValue if d[1] is None else d[1])
    nm_x.append(dt(d[2]))
    for d in history[1:-2]:
        nm.append(pychartdir.NoValue if d[1] is None else d[1])
        nm_x.append(dt(d[2]))
        if d[0] is not None:
            am.append(d[0])
            am_x.append(dt(d[2]))
    d = history[-1]
    am.append(pychartdir.NoValue if d[0] is None else d[0])
    am_x.append(dt(d[2]))
    nm.append(pychartdir.NoValue if d[1] is None else d[1])
    nm_x.append(dt(d[2]))

    #return repr([am, am_x, nm, nm_x])

    chartX, chartY, plotX, plotY = 640, 300, 520, 220
    c = pychartdir.XYChart(chartX, chartY, 0xfafafa)
    c.addTitle("Team Size History", "normal", 13)
    c.yAxis().setAutoScale(0.01, 0.01, 0.1)
    c.yAxis().setColors(0x000000, 0xbb0000)
    c.xAxis().setTickLength2(6,3)
    c.xAxis().setLabelFormat('{value|mm-dd}')
    c.setNumberFormat(',')
    setPlotAreaObj = c.setPlotArea(60, 35, plotX, plotY)
    setPlotAreaObj.setGridColor(0xc0c0c0, 0xc0c0c0, -1, pychartdir.Transparent)
    legend = c.addLegend(60 + plotX / 2, 10, 0, "vera.ttf", 10)
    legend.setBackground(pychartdir.Transparent)
    legend.setAlignment(pychartdir.Top)

    layer = c.addLineLayer()
    layer.setXData(am_x)
    dataSetObj = layer.addDataSet(am, 0xbb0000, am_title)
    dataSetObj.setDataSymbol(pychartdir.CircleSymbol, 3, 0xdd0000, 0xdd0000)
    layer.setLineWidth(1)

    curve = pychartdir.ArrayMath(am)
    curve.lowess2(am_x)
    splineLayerObj = c.addSplineLayer(curve.result(), 0xff0000, "")
    splineLayerObj.setXData(am_x)
    splineLayerObj.setLineWidth(2)

    labelStyleObj = c.xAxis().setLabelStyle("normal", 8)
    labelStyleObj.setFontAngle(0)
    labelStyleObj.setPos(0, 5)
    trendLayerObj = c.addTrendLayer(am, c.dashLineColor(0xbb0000, pychartdir.DashLine), "")
    trendLayerObj.setLineWidth(2)
    trendLayerObj.setXData(am_x)

    c.yAxis2().setAutoScale(0.01, 0.01, 0.1)
    c.yAxis2().setColors(0x000000, 0x004400)

    layer = c.addLineLayer()
    layer.setUseYAxis2()
    layer.setXData(nm_x)
    dataSetObj = layer.addDataSet(nm, 0x004400, nm_title)
    dataSetObj.setDataSymbol(pychartdir.CircleSymbol, 3, 0x00bb00, 0x00bb00)
    layer.setLineWidth(1)

    response = make_response(c.makeChart2(pychartdir.PNG))
    response.headers['Content-type'] = 'image/png'
    return response
