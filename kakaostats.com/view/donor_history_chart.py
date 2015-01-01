# -*- coding: utf-8 -*-
import pychartdir
from app import app
from flask import request, json, make_response

@app.route("/donor-history-chart")
def donor_history_chart():

    d = request.args
    history = d.get('history')
    try:
        history = json.loads(history) # points, wus, day, dow
    except ValueError:
        return ''

    #history = history[:-1]
    day = list();
    dayX = list();
    points = list();
    pointsPerWu = list();
    i = 0;
    min_dow = min((d[3] for d in history))
    max_points = max((d[0] for d in history))
    if max_points >= 100000:
        divider = 1000
        points_title = "Points (1,000)"
        wus_title = "Points per WU (1,000)"
    else:
        divider = 1
        points_title = "Points"
        wus_title = "Points per WU"
    for i, d in enumerate(history):
        if d[3] == min_dow:
            day.append(d[2][-5:])
        else:
            day.append('-')
        dayX.append(i)
        points.append(d[0] / divider)
        if d[1] == 0:
            pointsPerWu.append(0)
        else:
            pointsPerWu.append(d[0] / d[1])

    chartX, chartY, plotX, plotY = 640, 300, 520, 220
    c = pychartdir.XYChart(chartX, chartY, pychartdir.Transparent)
    setPlotAreaObj = c.setPlotArea(60, 35, plotX, plotY)
    setPlotAreaObj.setGridColor(0xc0c0c0, 0xc0c0c0, -1, pychartdir.Transparent)
    c.setNumberFormat(',')
    legend = c.addLegend(60, 10, 0, "vera.ttf", 10)
    legend.setBackground(pychartdir.Transparent)
    layer = c.addLineLayer()
    dataSetObj = layer.addDataSet(points, 0xbb0000, points_title)
    dataSetObj.setDataSymbol(pychartdir.CircleSymbol, 5, 0xdd0000, 0xdd0000)
    layer.setLineWidth(1)

    curve = pychartdir.ArrayMath(points)
    curve.lowess()
    splineLayerObj = c.addSplineLayer(curve.result(), 0xff0000, "")
    splineLayerObj.setLineWidth(2)
    c.xAxis().setLabels(day)
    c.yAxis().setAutoScale(0.01, 0.01, 0.1)
    c.yAxis().setColors(0x000000, 0xbb0000)
    c.xAxis().setTickLength2(6,3)
    labelStyleObj = c.xAxis().setLabelStyle("normal", 8)
    labelStyleObj.setFontAngle(0)
    labelStyleObj.setPos(0, 5)
    trendLayerObj = c.addTrendLayer(points, c.dashLineColor(0xbb0000, pychartdir.DashLine), "")
    trendLayerObj.setLineWidth(2)

    c2 = pychartdir.XYChart(chartX, chartY, pychartdir.Transparent)
    c2.setPlotArea(60, 35, plotX, plotY, pychartdir.Transparent, -1, pychartdir.Transparent, pychartdir.Transparent, pychartdir.Transparent)
    c2.setNumberFormat(',')
    legend = c2.addLegend(420, 10, 0, "normal", 10)
    legend.setBackground(pychartdir.Transparent)
    c2.yAxis().setAutoScale(0.01, 0.01, 0.1)
    c2.yAxis().setColors(0x000000, 0x004400)
    c2.setYAxisOnRight()
    layer = c2.addLineLayer()
    dataSetObj = layer.addDataSet(pointsPerWu, 0x004400, wus_title)
    dataSetObj.setDataSymbol(pychartdir.CircleSymbol, 5, 0x00bb00, 0x00bb00)
    layer.setLineWidth(1)
    m = pychartdir.MultiChart(chartX, chartY, 0xfafafa)
    m.addChart(0, 0, c2)
    m.addChart(0, 0, c)
    title = m.addTitle("Daily (UTC) Production History", "normal", 13)

    response = make_response(m.makeChart2(pychartdir.PNG))
    response.headers['Content-type'] = 'image/png'
    return response
