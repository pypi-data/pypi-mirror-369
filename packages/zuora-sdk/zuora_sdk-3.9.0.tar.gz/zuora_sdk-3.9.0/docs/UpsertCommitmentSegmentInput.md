# UpsertCommitmentSegmentInput

upsert an Commitment segment, when the action is create, create a new segment, when the action is update, update the segment by the segment number.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_segment_number** | **str** | The number of the Commitment Segment. | 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**association_rule** | [**AssociationRule**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 
**cycle_amount** | **float** |  | 
**action** | [**ActionType**](ActionType.md) |  | 

## Example

```python
from zuora_sdk.models.upsert_commitment_segment_input import UpsertCommitmentSegmentInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCommitmentSegmentInput from a JSON string
upsert_commitment_segment_input_instance = UpsertCommitmentSegmentInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCommitmentSegmentInput.to_json())

# convert the object into a dict
upsert_commitment_segment_input_dict = upsert_commitment_segment_input_instance.to_dict()
# create an instance of UpsertCommitmentSegmentInput from a dict
upsert_commitment_segment_input_from_dict = UpsertCommitmentSegmentInput.from_dict(upsert_commitment_segment_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


