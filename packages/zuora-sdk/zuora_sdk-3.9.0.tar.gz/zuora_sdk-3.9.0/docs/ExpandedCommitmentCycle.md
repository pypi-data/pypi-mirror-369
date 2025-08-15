# ExpandedCommitmentCycle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**commitment_segment_number** | **str** |  | [optional] 
**commitment_segment_id** | **str** |  | [optional] 
**commitment_type** | **str** |  | [optional] 
**commitment_priority** | **int** |  | [optional] 
**commitment_created_date** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**full_cycle_start_date** | **date** |  | [optional] 
**full_cycle_end_date** | **date** |  | [optional] 
**committed_amount** | **float** |  | [optional] 
**contributed_amount** | **float** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_commitment_cycle import ExpandedCommitmentCycle

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCommitmentCycle from a JSON string
expanded_commitment_cycle_instance = ExpandedCommitmentCycle.from_json(json)
# print the JSON string representation of the object
print(ExpandedCommitmentCycle.to_json())

# convert the object into a dict
expanded_commitment_cycle_dict = expanded_commitment_cycle_instance.to_dict()
# create an instance of ExpandedCommitmentCycle from a dict
expanded_commitment_cycle_from_dict = ExpandedCommitmentCycle.from_dict(expanded_commitment_cycle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


