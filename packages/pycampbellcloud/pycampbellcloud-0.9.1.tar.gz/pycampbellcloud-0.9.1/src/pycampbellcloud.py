import requests
from requests.exceptions import JSONDecodeError

# Wrapper setup
def request_wrapper(func):
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs)
        if results is None:
            return {'status': 'Results is type None'}
        elif results.status_code == 304:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'message': 'No metadata fields provided for update'}
        elif results.status_code == 204:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'status': 'Success', 'message': 'Response returned a 204 with no content'}
        elif results.status_code == 200:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'status': 'Success', 'message': "Response returned a 200 with no content"}
        try:
            return results.json()
        except JSONDecodeError:
            return {'status': f'Result code of request is {results.status_code}. Could not convert to JSON.'}
    return wrapper

def wrap_all_methods(cls):
    no_wrap = ["__init__", "_CampbellCloud__build_auth_header", "_CampbellCloud__get_data_of_datastream",
               "get_datapoints"]
    for name, method in cls.__dict__.items():
        if callable(method) and name not in no_wrap:
            setattr(cls, name, request_wrapper(method))
    return cls


@wrap_all_methods
class CampbellCloud:

    def __init__(self, organization_id: str, username: str, password: str):
        self._organization_id = organization_id
        self._username = username
        self._password = password
        self._base_api_url = f"https://us-west-2.campbell-cloud.com/api/v1/organizations/{self._organization_id}/"
        self._measurement_api_url = "https://us-west-2.campbell-cloud.com/api/v1/libraries/"
        self._token_api_url = "https://us-west-2.campbell-cloud.com/api/v1/tokens"
        self._product_api_url = "https://us-west-2.campbell-cloud.com/api/v1/product-registrations"
        self._token = self.__build_auth_header()

    def __build_auth_header(self):
        try:
            raw_token = self.create_token(self._username, self._password, "cloud", "password")['access_token']
            return {"Authorization": "Bearer " + raw_token}
        except KeyError:
            raise SyntaxError("Invalid credentials. Please check username and password.")

    def __get_data_of_datastream(self, datastream_id, start_epoch, end_epoch, data_list: list=[], latest_datapoints: int=None):
        if not latest_datapoints:
            # If nothing provided it will set it to the default value
            tmp_latest_datapoints = 15000
        else:
            tmp_latest_datapoints = latest_datapoints
        datastream_data = self.get_datastream_datapoints(datastream_id, start_epoch, end_epoch, limit=tmp_latest_datapoints)
        new_data_list = datastream_data['data'] + data_list
        if datastream_data['range']['exceeded_request'] and tmp_latest_datapoints > datastream_data['range']['count'] and latest_datapoints:
            latest_epoch = datastream_data['range']['start']
            # Increment value only if latest_datapoints was provided
            if latest_datapoints:
                latest_datapoints -= datastream_data['range']['count']
            return self.__get_data_of_datastream(datastream_id, start_epoch, latest_epoch, new_data_list, latest_datapoints)
        else:
            return new_data_list

    # ===================================================
    #                   Custom Endpoints
    # ===================================================

    def get_datapoints(self, asset_id, datatables: list = None, fieldnames: list = None, start_epoch: str = '0000000000000',
                       end_epoch: str = '9999999999999', latest_datapoints: int=None):

        all_datastreams = self.list_datastreams(asset_id=asset_id)
        approved_datastreams = list()

        # Filter for approved datastreams
        for datastream in all_datastreams:
            asset_datatable = datastream['metadata']['table']
            asset_fieldname = datastream['metadata']['field']
            asset_asset_id = datastream['asset_id']
            if (not datatables or asset_datatable in datatables) and (
                    not fieldnames or asset_fieldname in fieldnames) and asset_id == asset_asset_id:
                approved_datastreams.append(datastream)
        all_approved_data = list()

        # Get the data from the approved datastreams
        for datastream in approved_datastreams:
            asset_datastream_id = datastream['id']
            asset_datatable = datastream['metadata']['table']
            asset_fieldname = datastream['metadata']['field']
            datastream_data = self.__get_data_of_datastream(asset_datastream_id, start_epoch, end_epoch, latest_datapoints=latest_datapoints)
            new_field_data = {f"{asset_datatable}.{asset_fieldname}": datastream_data}
            all_approved_data.append(new_field_data)
        return all_approved_data

    # ===================================================
    #                   API Endpoints
    # ===================================================

    def list_assets(self):
        return requests.get(f"{self._base_api_url}assets", headers=self._token)

    def create_asset(self, metadata: dict):
        return requests.post(f"{self._base_api_url}assets", headers=self._token, json=metadata)

    def get_asset(self, asset_id: str):
        return requests.get(f"{self._base_api_url}assets/{asset_id}", headers=self._token)

    def update_asset(self, asset_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}assets/{asset_id}", headers=self._token, json=metadata)

    def delete_asset(self, asset_id: str):
        return requests.delete(f"{self._base_api_url}assets/{asset_id}", headers=self._token)

    def get_asset_state(self, asset_id: str):
        return requests.get(f"{self._base_api_url}assets/{asset_id}/state", headers=self._token)

    def update_asset_state(self, asset_id: str, status: str):
        return requests.put(f"{self._base_api_url}assets/{asset_id}/status", headers=self._token, json={"status": status})

    def update_asset_metadata(self, asset_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}assets/{asset_id}/metadata", headers=self._token, json=metadata)

    def list_asset_historical(self, asset_id: str, start_epoch: int, end_epoch: int):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch}
        return requests.get(f"{self._base_api_url}assets/{asset_id}/historical", headers=self._token, params=params)

    def get_asset_historical_by_id(self, asset_id: str, asset_historical_id: str):
        return requests.get(f"{self._base_api_url}assets/{asset_id}/historical/{asset_historical_id}", headers=self._token)

    def list_datastreams(self, limit: int=100, offset: int=0, asset_id: str=None, station_id: str=None):
        params = {"limit": limit, "offset": offset, "assetID": asset_id, "stationID": station_id}
        return requests.get(f"{self._base_api_url}datastreams", headers=self._token, json=params)

    def update_datastream(self, datastream_id: str, profile: str="datastream", version: int=1):
        params = {"metadata": {"$profile": profile, "$version": version, "field": "Temp"}}
        return requests.put(f"{self._base_api_url}datastreams/{datastream_id}", headers=self._token, json=params)

    def get_datastream(self, datastream_id: str):
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}", headers=self._token)

    def list_datastream_historical(self, datastream_id: str, start_epoch: int, end_epoch: int):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch}
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}/historical", headers=self._token, params=params)

    def get_datastream_historical_by_id(self, datastream_id: str, datastream_historical_id: str):
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}/historical/{datastream_historical_id}",
                            headers=self._token)

    def update_datastream_metadata(self, datastream_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}datastreams/{datastream_id}/metadata", headers=self._token, json=metadata)
    
    def get_datastream_datapoints(self, datastream_id: str, start_epoch: str, end_epoch: str, brief: bool=True, limit: int=100):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "brief": brief, "limit": limit}
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}/datapoints", headers=self._token, params=params)
    
    def get_datastream_datapoints_last(self, datastream_id: str):
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}/datapoints/last", headers=self._token)

    def get_datastream_datapoints_count(self, datastream_id: str, start_epoch: int, end_epoch: int):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch}
        return requests.get(f"{self._base_api_url}datastreams/{datastream_id}/datapoints/count", headers=self._token, params=params)

    def count_datastreams(self, asset_id: str=None, station_id: str=None):
        params = {"assetID": asset_id, "stationID": station_id}
        return requests.get(f"{self._base_api_url}datastreams/count", headers=self._token, params=params)

    def list_groups(self):
        return requests.get(f"{self._base_api_url}groups", headers=self._token)

    def create_group(self, metadata: dict):
        return requests.post(f"{self._base_api_url}groups", headers=self._token, json=metadata)

    def get_group(self, group_id: str):
        return requests.get(f"{self._base_api_url}groups/{group_id}", headers=self._token)

    def update_group(self, group_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}groups/{group_id}", headers=self._token, json=metadata)

    def delete_group(self, group_id: str):
        return requests.delete(f"{self._base_api_url}groups/{group_id}", headers=self._token)

    def get_users_in_group(self, group_id: str):
        return requests.get(f"{self._base_api_url}groups/{group_id}/users", headers=self._token)

    def list_group_permissions(self, group_id: str):
        return requests.get(f"{self._base_api_url}groups/{group_id}/permissions", headers=self._token)

    def add_permission_to_group(self, group_id: str, permission_id: str):
        return requests.put(f"{self._base_api_url}groups/{group_id}/permissions/{permission_id}", headers=self._token)

    def remove_permission_from_group(self, group_id: str, permission_id: str):
        return requests.delete(f"{self._base_api_url}groups/{group_id}/permissions/{permission_id}", headers=self._token)

    def list_measurement_classification_types(self, measurement_classification_type_id: str):
        return requests.get(f"{self._measurement_api_url}measurement-types/{measurement_classification_type_id}", headers=self._token)

    def list_measurement_classification_systems(self):
        return requests.get(f"{self._measurement_api_url}measurement-systems", headers=self._token)

    def get_measurement_classification_system_by_id(self, measurement_classification_system_id: str):
        return requests.get(f"{self._measurement_api_url}measurement-systems/{measurement_classification_system_id}",
                            headers=self._token)

    def get_measurement_classification_conversions_by_id(self, measurement_classification_classification_id: str,
                                                         measurement_classification_source_uom_id: str,
                                                         measurement_classification_target_uom_id: str):
        return requests.get(
            f"{self._measurement_api_url}measurement-conversions/{measurement_classification_classification_id}/{measurement_classification_source_uom_id}/{measurement_classification_target_uom_id}",
            headers=self._token)

    def get_part(self, part_id: str):
        return requests.get(f"{self._measurement_api_url}parts/{part_id}", headers=self._token)

    def get_organization_plan(self):
        return requests.get(f"{self._base_api_url}plan", headers=self._token)

    def get_reach_component_version_state(self, reach_component_id: str, reach_component_version_id: str):
        return requests.get(
            f"{self._base_api_url}reach-components/{reach_component_id}/versions/{reach_component_version_id}/state",
            headers=self._token)

    def list_station_groups(self):
        return requests.get(f"{self._base_api_url}station-groups", headers=self._token)

    def create_station_group(self, metadata):
        return requests.post(f"{self._base_api_url}station-groups", headers=self._token, json=metadata)

    def get_station_group(self, station_group_id: str):
        return requests.get(f"{self._base_api_url}station-groups/{station_group_id}", headers=self._token)

    def update_station(self, station_group_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}station-groups/{station_group_id}", headers=self._token, json=metadata)

    def delete_station_group(self, station_group_id: str):
        return requests.delete(f"{self._base_api_url}station-groups/{station_group_id}", headers=self._token)

    def update_station_group_metadata(self, station_group_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}station-groups/{station_group_id}/metadata", headers=self._token, json=metadata)

    def list_stations(self):
        return requests.get(f"{self._base_api_url}stations", headers=self._token)

    def create_station(self, metadata: dict):
        return requests.post(f"{self._base_api_url}stations", headers=self._token, json=metadata)

    def get_station(self, station_id: str):
        return requests.get(f"{self._base_api_url}stations/{station_id}", headers=self._token)

    def delete_station(self, station_id: str):
        return requests.delete(f"{self._base_api_url}stations/{station_id}", headers=self._token)

    def get_station_state(self, station_id: str):
        return requests.get(f"{self._base_api_url}stations/{station_id}/state", headers=self._token)

    def list_station_historical(self, station_id: str, start_epoch: int, end_epoch: int):
        params = {'start_epoch': start_epoch, "endEpoch": end_epoch}
        return requests.get(f"{self._base_api_url}stations/{station_id}/historical", headers=self._token, params=params)

    def get_station_historical_by_id(self, station_id: str, station_historical_id: str):
        return requests.get(f"{self._base_api_url}stations/{station_id}/historical/{station_historical_id}", headers=self._token)

    def update_station_metadata(self, station_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}stations/{station_id}/metadata", headers=self._token, json=metadata)

    def list_subscriptions(self):
        return requests.get(f"{self._base_api_url}subscriptions", headers=self._token)

    def create_subscriptions(self, po_number: str, subscriptions: list):
        return requests.post(f"{self._base_api_url}subscriptions", headers=self._token,
                             json={"po_number": po_number, "organization_id": self._organization_id,
                                   "subscriptions": subscriptions})

    def get_subscription(self, subscription_id: str):
        return requests.get(f"{self._base_api_url}subscriptions/{subscription_id}", headers=self._token)

    def update_subscription(self, subscription_id: str, auto_renew: bool, renewal_part: str):
        json_params = {"auto_renew": auto_renew, "renewal_part": renewal_part}
        return requests.put(f"{self._base_api_url}subscriptions/{subscription_id}", headers=self._token,
                            json=json_params)

    def delete_subscription(self, subscription_id: str):
        return requests.delete(f"{self._base_api_url}subscriptions/{subscription_id}", headers=self._token)

    def upgrade_subscription_part(self, subscription_id: str, part_id: str):
        return requests.put(f"{self._base_api_url}subscriptions/{subscription_id}/parts/{part_id}", headers=self._token)

    def create_token(self, username: str, password: str, client_id: str, grant_type: str):
        return requests.post(f"{self._token_api_url}",
                             json={"username": username, "password": password, "client_id": client_id,
                                   "grant_type": grant_type})

    def refresh_token(self):
        return requests.put(f"{self._token_api_url}", headers=self._token, json={"refresh_token": ""})

    def list_users(self):
        return requests.get(f"{self._base_api_url}users", headers=self._token)

    def create_user(self, metadata):
        return requests.post(f"{self._base_api_url}users", headers=self._token, json={"metadata": metadata})

    def get_user(self, user_id: str):
        return requests.get(f"{self._base_api_url}users/{user_id}", headers=self._token)

    def update_user(self, user_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}users/{user_id}", headers=self._token, json={"metadata": metadata})

    def delete_user(self, user_id: str):
        return requests.delete(f"{self._base_api_url}users/{user_id}", headers=self._token)

    def list_user_groups(self, user_id: str):
        return requests.get(f"{self._base_api_url}users/{user_id}/groups", headers=self._token)

    def count_user_groups(self, user_id: str):
        return requests.get(f"{self._base_api_url}users/{user_id}/groups/count", headers=self._token)

    def add_user_to_group(self, user_id: str, group_id: str):
        return requests.put(f"{self._base_api_url}users/{user_id}/groups/{group_id}", headers=self._token)

    def remove_user_from_group(self, user_id: str, group_id: str):
        return requests.delete(f"{self._base_api_url}users/{user_id}/groups/{group_id}", headers=self._token)

    def list_variables(self):
        return requests.get(f"{self._base_api_url}variables", headers=self._token)

    def create_variable(self, name: str, metadata: dict):
        return requests.post(f"{self._base_api_url}variables", headers=self._token, json={"name": name, "metadata": metadata})

    def list_alert_configurations(self):
        return requests.get(f"{self._base_api_url}alert-configurations", headers=self._token)

    def create_alert_configuration(self):
        params = {"$profile": "configuration", "$version": 1}
        return requests.post(f"{self._base_api_url}alert-configurations", headers=self._token, json=params)

    def get_alert_configuration(self, alert_id: str):
        return requests.get(f"{self._base_api_url}alert-configurations/{alert_id}", headers=self._token)

    def update_alert_configuration(self, alert_id: str,  metadata: dict):
        json_params = {"$profile": "configuration", "$version": 1}
        json_params.update(metadata)
        return requests.put(f"{self._base_api_url}alert-configuration/{alert_id}", headers=self._token, json=json_params)

    def delete_alert_configuration(self, alert_id: str):
        return requests.delete(f"{self._base_api_url}alert-configurations/{alert_id}", headers=self._token)

    def list_alert_configuration_historical(self, alert_id: str, end_epoch: int, start_epoch: int=0, offset: int=0, limit: int=100):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "limit": limit}
        return requests.get(f"{self._base_api_url}alert-configurations/{alert_id}/historical", headers=self._token, params=params)

    def get_alert_configuration_historical(self, alert_id: str, alert_historical_id: str):
        return requests.get(f"{self._base_api_url}alert-configurations/{alert_id}/historical/{alert_historical_id}", headers=self._token)

    def list_alert_events(self, alert_filter: str, end_epoch: int, start_epoch: int=0, offset: int=0):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "filter": alert_filter}
        return requests.get(f"{self._base_api_url}/alert-events", headers=self._token, params=params)

    def get_alert_events_id(self, alert_event_id: str):
        return requests.get(f"{self._base_api_url}alert-events/{alert_event_id}", headers=self._token)

    def search_alert_events(self, filters: dict):
        return requests.post(f"{self._base_api_url}alert_events/search", headers=self._token, json=filters)

    def list_alert_logs(self, alert_filter: str, end_epoch: int, start_epoch: int=0, offset: int=0, limit: int=100):
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "limit": limit, "filter": alert_filter}
        return requests.get(f"{self._base_api_url}alert-logs", headers=self._token, params=params)

    def create_alert_log(self, alert_event_id: str, metadata: dict):
        json_params = {"alert_event_id": alert_event_id}
        json_params.update(metadata)
        return requests.post(f"{self._base_api_url}alert-logs", headers=self._token, json=json_params)

    def get_alert_logs_id(self, alert_log_id: str):
        return requests.get(f"{self._base_api_url}alert-logs/{alert_log_id}", headers=self._token)

    def search_alert_logs(self, filters: dict):
        return requests.post(f"{self._base_api_url}alert-log/search", headers=self._token, json=filters)

    def update_asset_software(self, asset_id: str, software_type: str, os_metadata: dict=dict, program_metadata: dict=dict):
        headers = {"x-campbell-software-type": software_type}
        headers.update(self._token)
        if software_type == "datalogger-os" and os_metadata != dict:
            json_params = os_metadata
        elif software_type == "datalogger-program" and program_metadata != dict:
            json_params = program_metadata
        else:
            raise SyntaxError("software_type can only be 'datalogger-os' or 'datalogger-program'. Along with passing the appropriate metadata parameter.")

        return requests.put(f"{self._base_api_url}assets/{asset_id}/software-packages", headers=headers, json=json_params)

    def execute_asset_command(self, asset_id: str, command: str, start_epoch: int, end_epoch: int, table: str):
        json_params = {"command": command, "parameters": {"startEpoch": start_epoch, "endEpoch": end_epoch, "table": table}}
        return requests.put(f"{self._base_api_url}assets/{asset_id}/commands", headers=self._token, json=json_params)

    def list_exports(self):
        return requests.get(f"{self._base_api_url}exports", headers=self._token)

    def list_dashboards(self, before: str=str, after: str=str, first: int=100, last: int=100, brief: bool=True, latest: bool=True):
        params = {"before": before, "after": after, "first": first, "last": last, "brief": brief, "latest": latest}
        return requests.get(f"{self._base_api_url}dashboards", headers=self._token, params=params)

    def create_dashboard(self, metadata: dict):
        return requests.post(f"{self._base_api_url}dashboards", headers=self._token, json=metadata)

    def get_dashboard(self, dashboard_id: str, latest: bool=True):
        params = {"latest": latest}
        return requests.get(f"{self._base_api_url}dashboards/{dashboard_id}", headers=self._token, params=params)

    def update_dashboard(self, dashboard_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}dashboards/{dashboard_id}", headers=self._token, json=metadata)

    def delete_dashboard(self, dashboard_id: str):
        return requests.delete(f"{self._base_api_url}dashboard/{dashboard_id}", headers=self._token)

    def list_dashboard_historical(self, dashboard_id: str, before: str=None, after: str=None, first: int=100, last: int=100, reverse: bool=None, brief: bool=None):
        params = {"before": before, "after": after, "first": first, "last": last, "reverse": reverse, "brief": brief}
        return requests.get(f"{self._base_api_url}dashboards/{dashboard_id}/historical", headers=self._token, params=params)

    def get_dashboard_historical_by_id(self, dashboard_id: str, dashboard_historical_id: str):
        return requests.get(f"{self._base_api_url}dashboards/{dashboard_id}/historical/{dashboard_historical_id}", headers=self._token)

    def list_data_collections(self):
        return requests.get(f"{self._base_api_url}data-collections/collections", headers=self._token)

    def create_data_collections(self, metadata: dict):
        return requests.post(f"{self._base_api_url}data-collections/collections", headers=self._token, json=metadata)

    def get_data_collection(self, data_collection_id: str):
        return requests.get(f"{self._base_api_url}data-collections/collections/{data_collection_id}", headers=self._token)

    def update_data_collection(self, data_collection_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}data-collections/collections/{data_collection_id}", headers=self._token, json=metadata)

    def delete_data_collection(self, data_collection_id: str):
        return requests.delete(f"{self._base_api_url}data-collections/collections/{data_collection_id}", headers=self._token)

    def list_data_collection_types(self):
        return requests.get(f"{self._base_api_url}data-collections/types", headers=self._token)

    def create_data_collection_type(self, metadata: dict):
        return requests.post(f"{self._base_api_url}data-collections/types", headers=self._token, json=metadata)

    def get_data_collection_type(self, data_collection_type_id: str):
        return requests.get(f"{self._base_api_url}data-collections/types/{data_collection_type_id}", headers=self._token)

    def update_data_collection_type(self, data_collection_type_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}data-collections/types/{data_collection_type_id}", headers=self._token, json=metadata)

    def delete_data_collection_type(self, data_collection_type_id: str):
        return requests.delete(f"{self._base_api_url}data-collections/types/{data_collection_type_id}", headers=self._token)

    def list_data_collection_type_historical(self, data_collection_type_id: str):
        return requests.get(f"{self._base_api_url}data-collections/types/{data_collection_type_id}/historical", headers=self._token)

    def list_datastreams_labels(self, limit: int=1000, start_after: str=None):
        params = {"limit": limit, "startAfter": start_after}
        return requests.get(f"{self._base_api_url}datastreams/labels", headers=self._token, params=params)

    def list_distribution_groups(self):
        return requests.get(f"{self._base_api_url}distribution-groups", headers=self._token)

    def create_distribution_groups(self, metadata: dict):
        return requests.post(f"{self._base_api_url}distribution-groups", headers=self._token, json=metadata)

    def get_distribution_group(self, distribution_group_id: str):
        return requests.get(f"{self._base_api_url}distribution-groups/{distribution_group_id}", headers=self._token)

    def update_distribution_group(self, distribution_group_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}distributions-groups/{distribution_group_id}", headers=self._token, json=metadata)

    def delete_distribution_group(self, distribution_group_id: str):
        return requests.delete(f"{self._base_api_url}distributions-groups/{distribution_group_id}", headers=self._token)

    def create_export(self, metadata: dict):
        return requests.post(f"{self._base_api_url}exports", headers=self._token, json=metadata)

    def get_export(self, export_id: str):
        return requests.get(f"{self._base_api_url}exports/{export_id}", headers=self._token)

    def update_export(self, export_id: str, metadata: dict):
        return requests.put(f"{self._base_api_url}exports/{export_id}", headers=self._token, json=metadata)

    def delete_export(self, export_id: str):
        return requests.delete(f"{self._base_api_url}exports/{export_id}", headers=self._token)

    def list_export_jobs(self, export_id: str):
        return requests.get(f"{self._base_api_url}exports/{export_id}/jobs", headers=self._token)

    def get_export_job(self, export_id: str, export_job_id: str):
        return requests.get(f"{self._base_api_url}exports/{export_id}/jobs/{export_job_id}", headers=self._token)

    def delete_export_job(self, export_id: str, export_job_id: str):
        return requests.delete(f"{self._base_api_url}exports/{export_id}/jobs/{export_job_id}", headers=self._token)

    def list_export_job_files(self, export_id: str, export_job_id: str):
        return requests.get(f"{self._base_api_url}exports/{export_id}/jobs/{export_job_id}/files", headers=self._token)

    def get_export_job_file(self, export_id: str, export_job_id: str, export_file_id: str):
        return requests.get(f"{self._base_api_url}exports/{export_id}/jobs/{export_job_id}/files/{export_file_id}", headers=self._token)

    def get_group_permission_by_id(self, group_id: str, permission_id: str):
        return requests.get(f"{self._base_api_url}groups/{group_id}/permissions/{permission_id}", headers=self._token)

    def switch_organization(self, new_organization_id: str):
        metadata = {"organization_id": new_organization_id}
        return requests.put(f"{self._base_api_url}switch", headers=self._token, json=metadata)

    def list_organizations(self):
        return requests.get("https://us-west-2.campbell-cloud.com/api/v1/organizations", headers=self._token)

    def create_product_registration(self, content: str, signature: str, signature_alg: str, nonce: str):
        metadata = {"content": content, "signature": signature, "signature_alg": signature_alg, "nonce": nonce}
        return requests.post(f"{self._product_api_url}", headers=self._token, json=metadata)

    def export_reach_component(self, reach_component_id: str, reach_component_version_id: str):
        return requests.get(f"{self._base_api_url}reach-components/{reach_component_id}/versions/{reach_component_version_id}/export", headers=self._token)

    def preflight_create_station(self):
        return requests.options(f"{self._base_api_url}stations", headers=self._token)

    def get_subscription_claim(self, billing_transaction_id: str):
        return requests.get(f"{self._base_api_url}subscriptions-claims/{billing_transaction_id}", headers=self._token)

    def update_subscription_claims(self, billing_transaction_id: str, subscription_ids: list):
        metadata = {"subscription_ids": subscription_ids}
        return requests.put(f"{self._base_api_url}subscriptions-claims/{billing_transaction_id}", headers=self._token, json=metadata)

    def get_subscription_organization(self):
        return requests.get(f"{self._base_api_url}subscription-organization", headers=self._token)