from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Legend
from datetime import datetime as dt, timedelta, date
import pandas as pd

output_file('dashboard.html')

df = pd.read_csv("clones.csv")
df['date'] = pd.to_datetime(df['date'])

# fill in missing dates
start_date = df['date'].iloc[0]
print(start_date)
end_date = df['date'].iloc[len(df) - 1]
delta = timedelta(days=1)
row = 0


source = ColumnDataSource(df)

curdoc().theme = 'light_minimal'

p = figure(width=800, x_axis_type='datetime', toolbar_location="above")
p.circle(x='date', y='clone_count', source=source, size=10, line_width=2, line_color='#2c79de', fill_color='white')
line = p.line(x='date', y='clone_count', source=source, color='#2c79de')
p.xaxis.formatter=DatetimeTickFormatter(days=["%B %d %Y"])
p.title.text = 'Cumulative downloads'

legend = Legend(items=[
    ("dataset 1", [line])
], location="center")

p.add_layout(legend, 'right')

show(p)