# ExpandedCommitmentSegment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**commitment_segment_number** | **str** |  | [optional] 
**commitment_id** | **str** |  | [optional] 
**commitment_number** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**amount** | **float** |  | [optional] 
**distribution_management** | **str** |  | [optional] 
**custom_distribution_rule** | **str** |  | [optional] 
**association_rules** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_commitment_segment import ExpandedCommitmentSegment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCommitmentSegment from a JSON string
expanded_commitment_segment_instance = ExpandedCommitmentSegment.from_json(json)
# print the JSON string representation of the object
print(ExpandedCommitmentSegment.to_json())

# convert the object into a dict
expanded_commitment_segment_dict = expanded_commitment_segment_instance.to_dict()
# create an instance of ExpandedCommitmentSegment from a dict
expanded_commitment_segment_from_dict = ExpandedCommitmentSegment.from_dict(expanded_commitment_segment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


