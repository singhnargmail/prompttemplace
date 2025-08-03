#!/usr/bin/env python3
import requests
import json

url = "http://localhost:5000/api/getPersonaPrompts"
response = requests.get(url)
print(response.json())

#url = "http://localhost:5000/api/getAdvancedPrompts"
#response = requests.get(url)
#print(response.json())

# convert json
 
#inputstring = response.text
#print (type(inputstring))
#inputstring = '[{\\"name\\": \\"Alice\\", \\"age\\": 30, \\"details\\": {\\"city\\": \\"New York\\"}}]'
#cleaned_string = inputstring.replace('\\"', '"')
#parsed_data = json.loads(cleaned_string)
#if isinstance(parsed_data, list) and len(parsed_data) > 0:
#    result = parsed_data[0]
#else:
#    result = parsed_data
#clean_json = json.dumps(result)

#print(clean_json)