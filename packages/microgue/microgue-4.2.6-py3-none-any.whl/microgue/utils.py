def mask_fields_in_data(data, fields, mask="*****"):
    if type(data) is dict:
        data = data.copy()
        for field in fields:
            if field in data:
                data[field] = mask
    return data
