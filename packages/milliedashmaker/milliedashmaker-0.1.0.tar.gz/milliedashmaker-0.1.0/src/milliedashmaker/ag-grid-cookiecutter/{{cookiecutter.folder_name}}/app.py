import dash_ag_grid as dag
from dash import Dash, html
import pandas as pd


app = Dash()


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
)


columnDefs = [
    {"field": "athlete"},
    {"field": "age", "filter": "agNumberColumnFilter", "maxWidth": 100},
    {"field": "country"},
    {
        "headerName": "Date",
        "filter": "agDateColumnFilter",
        "valueGetter": {"function": "d3.timeParse('%d/%m/%Y')(params.data.date)"},
        "valueFormatter": {"function": "params.data.date"},
    },
    {"field": "sport"},
    {"field": "total"},
]

app.layout = html.Div(
    [
        html.P("This project was done by {{cookiecutter.author}}"),
     
        dag.AgGrid(
             id="filter-options-example-simple",
            columnDefs=columnDefs,
            rowData=df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": "agTextColumnFilter"},
            dashGridOptions={"animateRows": False}
        ),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
