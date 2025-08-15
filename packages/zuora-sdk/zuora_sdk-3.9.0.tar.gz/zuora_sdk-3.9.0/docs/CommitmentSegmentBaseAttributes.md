# CommitmentSegmentBaseAttributes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_segment_number** | **str** | The number of the Commitment Segment. | [optional] 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**association_rule** | [**AssociationRule**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_segment_base_attributes import CommitmentSegmentBaseAttributes

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentSegmentBaseAttributes from a JSON string
commitment_segment_base_attributes_instance = CommitmentSegmentBaseAttributes.from_json(json)
# print the JSON string representation of the object
print(CommitmentSegmentBaseAttributes.to_json())

# convert the object into a dict
commitment_segment_base_attributes_dict = commitment_segment_base_attributes_instance.to_dict()
# create an instance of CommitmentSegmentBaseAttributes from a dict
commitment_segment_base_attributes_from_dict = CommitmentSegmentBaseAttributes.from_dict(commitment_segment_base_attributes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


