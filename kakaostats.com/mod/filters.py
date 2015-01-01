from app import app
import locale, datetime

@app.template_filter()
def number_group(value, decimals='0'):
    if value is None: value = 0
    else: value = float(value)
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return locale.format('%%.%sf' % decimals, value, True)

@app.template_filter()
def locale_format(value, format_string, group=False):
    if value is None: value = 0
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return locale.format(format_string, value, group)

@app.template_filter()
def zero2empty(value):
    try:
        float(value)
    except:
        return value
    if abs(float(value)) < 0.00000001:
        return ''
    return value

@app.template_filter()
def small_thousands(value):
    value = number_group(value)
    value = zero2empty(value)
    if not value or value > 999.999:
        value = '%s<span class="xxSmall st">%s</span>' % (value[:-4], value[-4:])
    return value

@app.template_filter()
def justify(value, size):
    l = len(value)
    value = '%s%s' % (
        '&nbsp;' * (size - l),
        value,
    )
    return value

@app.template_filter()
def avg(value, attribute):

    l = list()
    for d in value:
        if d[attribute] is not None:
            l.append(d[attribute])

    if len(l) == 0:
        return 0
    else:
        return float(sum(l)) / len(l)

@app.template_filter()
def date_to_monday(value):

    day = value['day']
    day = datetime.date(int(day[:4]), int(day[5:7]), int(day[8:])) - datetime.timedelta(value['dow'] - 1)
    return day.isoformat()
