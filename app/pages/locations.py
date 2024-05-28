"""
The main map page of the application.
"""

import dash
import dash_bootstrap_components as dbc
from src.data_loading.main import AppDataManager
from src.utils import Logging, COLUMN
from src.app_components import (
    LeafletMapComponentManager,
    LocationComponentManager,
    CallbackManager,
    COMPONENT_ID,
)
from dash import callback, Input, Output, dcc, html, State, clientside_callback

logger = Logging.get_console_logger(__name__)


### Data loading ###

data_manager = AppDataManager()
data_manager.load_and_format_locations()


### Graph component and Callback manager ###

location_component_manager = LocationComponentManager()

CallbackManager.initialize_callbacks()

### Dash Page Setup ###

dash.register_page(
    __name__,
    path="/locations",
    title="tRacket",
    path_template="/locations/<device_id>",
)

### CALLBACKS ###

# NOTE: need to be defined outside the layer() function for these to work

clientside_callback(
    """
    function(feature) {
        var base_url = window.location.href;
        console.log(feature)
        if (!feature.properties.cluster) {
            var url = new URL("locations/".concat(feature.properties.id), base_url);
            console.log(`Redirecting to ${url}`);
            window.open(url, '_blank');
        }
    }
    """,
    Output(COMPONENT_ID.map_markers, "hideout"),
    Input(COMPONENT_ID.map_markers, "clickData"),
    prevent_initial_call=True,
)

### LAYOUT DEFINITION ###


def layout(device_id: str = None, **kwargs):
    leaflet_manager = LeafletMapComponentManager(data_manager.locations)
    if device_id is None:
        map = leaflet_manager.get_map()
        layout = map

    else:
        # get map for specific location
        map = leaflet_manager.get_map(
            device_id=device_id, style={"height": "50vh"}
        )

        # load data for location
        data_manager.load_and_format_location_noise(location_id=device_id)
        data_manager.load_and_format_location_info(location_id=device_id)

        info = data_manager.location_info.to_dict("records")[0]
        label = info[COLUMN.LABEL]
        radius = info[COLUMN.RADIUS]

        # explanation
        level_card = location_component_manager.get_explanation_card()

        # get components
        indicator = location_component_manager.get_mean_indicator(
            data_manager.location_noise
        )
        noise_line_graph = location_component_manager.get_noise_line_graph(
            data_manager.location_noise
        )

        # define layout
        layout = dbc.Container(
            [
                dbc.Row(
                    [html.H1(dcc.Markdown(f"**Location**")), html.H1(label)]
                ),
                dbc.Row(
                    [
                        dbc.Col(indicator, width=4),
                        dbc.Col(noise_line_graph, width=8),
                    ],
                ),
                dbc.Row([dbc.Col(map)]),
            ], 
        )

    return layout
