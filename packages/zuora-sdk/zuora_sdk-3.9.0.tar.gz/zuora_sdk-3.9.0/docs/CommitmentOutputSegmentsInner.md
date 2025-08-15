# CommitmentOutputSegmentsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_segment_number** | **str** | The number of the Commitment Segment. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_output_segments_inner import CommitmentOutputSegmentsInner

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentOutputSegmentsInner from a JSON string
commitment_output_segments_inner_instance = CommitmentOutputSegmentsInner.from_json(json)
# print the JSON string representation of the object
print(CommitmentOutputSegmentsInner.to_json())

# convert the object into a dict
commitment_output_segments_inner_dict = commitment_output_segments_inner_instance.to_dict()
# create an instance of CommitmentOutputSegmentsInner from a dict
commitment_output_segments_inner_from_dict = CommitmentOutputSegmentsInner.from_dict(commitment_output_segments_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


