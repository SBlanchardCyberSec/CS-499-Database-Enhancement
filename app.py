# Setup the Jupyter version of Dash
from jupyter_dash import JupyterDash

# Configure the necessary Python module imports for dashboard components
import dash_leaflet as dl
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output, State
import base64

# Configure OS routines
import sys, os, pprint

sys.path.append(os.path.expanduser('~/Desktop'))

# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#### Done #####
# change animal_shelter and AnimalShelter to match your CRUD Python module file name and class name
from main import DatabaseLayer

###########################
# Data Manipulation / Model
###########################
# Done update with your username and password and CRUD Python module name

username = os.environ["MONGO_USER"]
password = os.environ["MONGO_PASS"]



#mHost = os.environ["MONGO_HOST"]
#mPort = os.environ["MONGO_PORT"]
mHost = 'localhost'
mPort = '27017'

# Connect to database via CRUD Module
db = DatabaseLayer(mHost, mPort, username, password)
db.connect(True)
db.usedb('AAC', 'animals')

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(db.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invlaid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will reeturn a new dataframe that does not contain the dropped column(s)
df.drop(columns=['_id'],inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)

# Defining Queries here

prefWaterBreeds = { '$or' : [{'breed' : {'$regex' : 'Labrador*'}}, 
                             {'breed' : {'$regex' : '^Chesa*'}},
                             {'breed' : {'$regex' : '^Newfound*'}}
                            ]}
prefWaterSex = {'sex_upon_outcome' : 'Intact Female'}
prefWaterAge = {'age_upon_outcome_in_weeks': {'$gt':26, '$lt':156}}
wq = prefWaterBreeds
wq.update(prefWaterSex)
wq.update(prefWaterAge)


prefMountBreeds = { '$or' : [ {'breed': {'$regex' : 'German Shep*'}},
                              {'breed': {'$regex' : 'Alaskan Malamute*'}},
                              {'breed': {'$regex' : 'Old English*'}},
                              {'breed': {'$regex' : 'Siberian Husky*'}},
                              {'breed': {'$regex' : 'Rott*'}}
                              ]}

prefMountSex = {'sex_upon_outcome' : 'Intact Male'}
prefMountAge = {'age_upon_outcome_in_weeks': {'$gt':26, '$lt':156}}

mq = prefMountBreeds
mq.update(prefMountSex)
mq.update(prefMountAge)


prefDBreeds = { '$or' : [
    {'breed' : {'$regex' : 'Doberman*'}},
    {'breed' : {'$regex' : 'German Shep*'}},
    {'breed' : {'$regex' : 'Golden Retr*'}},
    {'breed' : {'$regex' : 'Bloodhound*'}},
    {'breed' : {'$regex' : 'Rott*'}}   
]}

prefDSex = {'sex_upon_outcome' : 'Intact Male'}
prefDAge = {'age_upon_outcome_in_weeks': {'$gt':20, '$lt':300}}

dq = prefDBreeds
dq.update(prefDSex)
dq.update(prefDAge)



#########################
# Dashboard Layout / View
#########################
app = JupyterDash(__name__)

#Done Add in Grazioso Salvare’s logo
image_filename = 'Grazioso Salvare Logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


app.layout = html.Div([
    html.Div(id='hidden-div', style={'display':'none'}),
    html.Center(html.B(html.H1('Scott Blanchard SNHU CS-340 MongoDB Dashboard'))),
    html.Hr(),
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
    html.Div(
        className='row',
            style={'width': '60%'},
            children=[dcc.RadioItems(['Water Rescue', 'Mountain/Wilderness', 
                                      'Disaster/Individual', 'All'], 'All', id='filter-type', inline=True)]
        

    ),
    html.Hr(),
    dash_table.DataTable(id='datatable-id',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
                         data=df.to_dict('records'),
#DONE: Set up the features for your interactive data table to make it user-friendly for your client
#If you completed the Module Six Assignment, you can copy in the code you created here 
        editable=False,
        filter_action="native",
        #default to case insensitive search for filters under table columns
        filter_options={"case": "insensitive"},
        sort_action="native",
        sort_mode="multi",
        #changing this to True
        column_selectable="single",
        row_selectable="single",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[0],
        page_action="native",
        page_current=0,
        page_size=10

                        ),
    
    
    html.Br(),
    html.Hr(),
    
#This sets up the dashboard so that your chart and your geolocation chart are side-by-side
    html.Div(className='row',
         style={'display' : 'flex'},
             children=[
        html.Div(
            dcc.Graph(id='graph-id'),
            className='col s12 m6',

            ),
        html.Div(
            id='map-id',
            className='col s12 m6',
            ),
        ]),
    html.Br(),
    html.Hr(),
    html.Center(html.B(html.H1('Scott Blanchard SNHU CS-340 MongoDB Dashboard')))
])

#############################################
# Interaction Between Components / Controller
#############################################


    
@app.callback(Output('datatable-id','data'),
              Input('filter-type', 'value')
              )
def update_dashboard(filter_type):
    
    if filter_type is None:
        df = pd.DataFrame.from_records(db.read({'animal_type':'Dog'}))
    elif filter_type == 'All':
        df = pd.DataFrame.from_records(db.read({'animal_type':'Dog'}))
    elif filter_type == 'Water Rescue':
        df = pd.DataFrame.from_records(db.read(wq))
    elif filter_type == 'Mountain/Wilderness':
        df = pd.DataFrame.from_records(db.read(mq))
    elif filter_type == 'Disaster/Individual':
        df = pd.DataFrame.from_records(db.read(dq))
    else:
        print('This should not happen. Check Radio Item callback update_dashboard.')
        df = pd.DataFrame.from_records(db.read({'animal_type':'Dog'}))
    
    # dont forget to drop _id
    df.drop(columns=['_id'],inplace=True)

    return df.to_dict('records')




@app.callback(
    Output('graph-id', 'figure'),
    Input('datatable-id', "derived_virtual_data"),
    Input('filter-type', 'value'))
def update_graphs(data, rfilter):
    
    #fig = px.pie(data, names='breed')
    #fig.update(layout_title_text=f'{rfilter} Candidates')
    #return fig
    
    # histogram time
    #print (rfilter)
    if rfilter == 'All':
        xrange = [-0.5, 10.5]
        
    else:
        xrange = None

    fig = px.histogram(data, x = 'breed', nbins=8, text_auto=True, range_x=xrange).update_xaxes(categoryorder='total descending')
    
    fig.update(layout_title_text=f'{rfilter} Candidates')

    return fig  
    
#This callback will highlight a cell on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of 
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):  
    if viewData is None:
        return
    elif index is None:
        return
    
    dff = pd.DataFrame.from_dict(viewData)
    # Because we only allow single row selection, the list can be converted to a row index here
    if index is None:
        row = 0
    else: 
        row = index[0]
        
    # Austin TX is at [30.75,-97.48]
    return [
        #center=[30.75,-97.48]
        dl.Map(style={'width': '1000px', 'height': '500px'}, center=[dff.iloc[row,13],dff.iloc[row,14]], zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            # Marker with tool tip and popup
            # Column 13 and 14 define the grid-coordinates for the map
            # Column 4 defines the breed for the animal
            # Column 9 defines the name of the animal
            dl.Marker(position=[dff.iloc[row,13],dff.iloc[row,14]], children=[
                dl.Tooltip(dff.iloc[row,4]),
                dl.Popup([
                    html.H1("Animal Name"),
                    html.P(dff.iloc[row,9])
                ])
            ])
        ])
    ]


app.run_server(debug=True)
