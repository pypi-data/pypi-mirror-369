# UpsertCreateCommitmentSegmentInput

create a new segment

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_segment_number** | **str** | The number of the Commitment Segment. | [optional] 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**association_rule** | [**AssociationRule**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 
**cycle_amount** | **float** |  | 
**action** | [**ActionType**](ActionType.md) |  | 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_segment_input import UpsertCreateCommitmentSegmentInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentSegmentInput from a JSON string
upsert_create_commitment_segment_input_instance = UpsertCreateCommitmentSegmentInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentSegmentInput.to_json())

# convert the object into a dict
upsert_create_commitment_segment_input_dict = upsert_create_commitment_segment_input_instance.to_dict()
# create an instance of UpsertCreateCommitmentSegmentInput from a dict
upsert_create_commitment_segment_input_from_dict = UpsertCreateCommitmentSegmentInput.from_dict(upsert_create_commitment_segment_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


