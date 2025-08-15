# CommitmentCycleAttributes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cycle_period_type** | [**CyclePeriodTypeEnum**](CyclePeriodTypeEnum.md) |  | [optional] 
**specific_cycle_period_length** | **int** | When the cyclePeriodType is SpecificWeeks, SpecificDays or SpecificMonths, this field is required. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_cycle_attributes import CommitmentCycleAttributes

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentCycleAttributes from a JSON string
commitment_cycle_attributes_instance = CommitmentCycleAttributes.from_json(json)
# print the JSON string representation of the object
print(CommitmentCycleAttributes.to_json())

# convert the object into a dict
commitment_cycle_attributes_dict = commitment_cycle_attributes_instance.to_dict()
# create an instance of CommitmentCycleAttributes from a dict
commitment_cycle_attributes_from_dict = CommitmentCycleAttributes.from_dict(commitment_cycle_attributes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


