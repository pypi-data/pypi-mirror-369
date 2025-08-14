from dash import Dash, html, Input, Output, callback
import dash_daq as daq

app = Dash()

app.layout = html.Div([
    daq.Knob(id='my-knob-1'),
    html.Div(id='knob-output-1')
])

@callback(Output('knob-output-1', 'children'), Input('my-knob-1', 'value'))
def update_output(value):
    return f'The knob value is {value}.'

if __name__ == '__main__':
    app.run(debug=True)
