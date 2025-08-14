# DtoGetCompletedMapResp


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_anomaly** | **List[str]** | List of trace IDs with detected anomalies | [optional] 
**no_anomaly** | **List[str]** | List of trace IDs without anomalies | [optional] 

## Example

```python
from rcabench.openapi.models.dto_get_completed_map_resp import DtoGetCompletedMapResp

# TODO update the JSON string below
json = "{}"
# create an instance of DtoGetCompletedMapResp from a JSON string
dto_get_completed_map_resp_instance = DtoGetCompletedMapResp.from_json(json)
# print the JSON string representation of the object
print DtoGetCompletedMapResp.to_json()

# convert the object into a dict
dto_get_completed_map_resp_dict = dto_get_completed_map_resp_instance.to_dict()
# create an instance of DtoGetCompletedMapResp from a dict
dto_get_completed_map_resp_form_dict = dto_get_completed_map_resp.from_dict(dto_get_completed_map_resp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


