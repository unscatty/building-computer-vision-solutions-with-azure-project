def __combine_common_properties(fields: list, field_properties: list) -> dict:
    return {field: field_properties for field in fields}


__common_field_properties = ['name', 'value', 'confidence']

__identity_fields = ['Address', 'FirstName', 'LastName', 'Sex', 'DateOfBirth']

IDENTITY_SCHEMA = __combine_common_properties(
    __identity_fields, __common_field_properties)

__boarding_pass_fields = ['Airline Name',
                          'Baggage',
                          'Boarding Pass ID',
                          'Boarding Time',
                          'Boarding Time Alt',
                          'Carrier',
                          'Class',
                          'Date',
                          'Date Alt',
                          'Flight Number',
                          'From',
                          'From Alt',
                          'Gate',
                          'Gate Alt',
                          'Passenger Name',
                          'Passenger Name Alt',
                          'Seat',
                          'Seat Alt',
                          'To',
                          'To Alt']

BOARDING_PASS_SCHEMA = __combine_common_properties(
    __boarding_pass_fields, __common_field_properties)
