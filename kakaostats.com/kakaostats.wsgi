# -*- coding: utf-8 -*-
from app import app
from jinja2 import FileSystemLoader
import config

app.jinja_loader = FileSystemLoader(config.templates_path)
app.debug = False
app.jinja_env.autoescape = False
app.jinja_env.line_statement_prefix = "#"
app.jinja_env.line_comment_prefix = "##"
#app.jinja_env.trim_blocks = True

import filters
import index
import members
import donors
import donor_log
import donor_history
import donor_history_chart
import donor_radar
import donor_radar_chart
import team_history
import team_history_chart
import team_radar
import team_radar_chart
import team_size
import team_size_chart
