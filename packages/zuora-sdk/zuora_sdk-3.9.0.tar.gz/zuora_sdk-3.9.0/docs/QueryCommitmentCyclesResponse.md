# QueryCommitmentCyclesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCommitmentCycle]**](ExpandedCommitmentCycle.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_commitment_cycles_response import QueryCommitmentCyclesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCommitmentCyclesResponse from a JSON string
query_commitment_cycles_response_instance = QueryCommitmentCyclesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCommitmentCyclesResponse.to_json())

# convert the object into a dict
query_commitment_cycles_response_dict = query_commitment_cycles_response_instance.to_dict()
# create an instance of QueryCommitmentCyclesResponse from a dict
query_commitment_cycles_response_from_dict = QueryCommitmentCyclesResponse.from_dict(query_commitment_cycles_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


