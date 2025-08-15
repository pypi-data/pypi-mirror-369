# UpsertUpdateCommitmentSegmentInput

Update an existing Commitment.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**ActionType**](ActionType.md) |  | 
**commitment_segment_number** | **str** | The number of the Commitment Segment. | 
**end_date** | **date** |  | [optional] 
**cycle_amount** | **float** |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 

## Example

```python
from zuora_sdk.models.upsert_update_commitment_segment_input import UpsertUpdateCommitmentSegmentInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertUpdateCommitmentSegmentInput from a JSON string
upsert_update_commitment_segment_input_instance = UpsertUpdateCommitmentSegmentInput.from_json(json)
# print the JSON string representation of the object
print(UpsertUpdateCommitmentSegmentInput.to_json())

# convert the object into a dict
upsert_update_commitment_segment_input_dict = upsert_update_commitment_segment_input_instance.to_dict()
# create an instance of UpsertUpdateCommitmentSegmentInput from a dict
upsert_update_commitment_segment_input_from_dict = UpsertUpdateCommitmentSegmentInput.from_dict(upsert_update_commitment_segment_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


