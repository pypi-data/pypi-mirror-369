# UpsertCreateCommitmentInputAllOfSegments


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_segment_number** | **str** | The number of the Commitment Segment. | [optional] 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**association_rule** | [**AssociationRule**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 
**cycle_amount** | **float** |  | 
**action** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_input_all_of_segments import UpsertCreateCommitmentInputAllOfSegments

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentInputAllOfSegments from a JSON string
upsert_create_commitment_input_all_of_segments_instance = UpsertCreateCommitmentInputAllOfSegments.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentInputAllOfSegments.to_json())

# convert the object into a dict
upsert_create_commitment_input_all_of_segments_dict = upsert_create_commitment_input_all_of_segments_instance.to_dict()
# create an instance of UpsertCreateCommitmentInputAllOfSegments from a dict
upsert_create_commitment_input_all_of_segments_from_dict = UpsertCreateCommitmentInputAllOfSegments.from_dict(upsert_create_commitment_input_all_of_segments_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


