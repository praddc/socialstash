__author__ = 'prad'

import json
import requests
import ConfigParser
import logging
import ast
import os

# == Start the logger ==
# == Because of this logger, this should be the first library we import ==
logging.basicConfig(filename='socialStash.log', level=logging.DEBUG, format='%(levelname)s: %(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s()]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.debug('Starting: ' + __name__)
 # Reset the level of logging coming from the Requests library
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Local directories
cache_directory = 'cache' + os.sep + 'instagram'

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_user_object = config.get('SnapbundleCredentials', 'snapbundle_user_object')
base_url_server = 'snapbundle'
#base_url_server = 'stage'
url_server = 'http://' + base_url_server + '.tagdynamics.net:8080'
base_url_objects = url_server + '/objects'
base_url_object_interaction = url_server + '/interactions'
base_url_relationship = url_server + '/relationships'
base_url_relationship_query_object = url_server + '/relationships/Object'
base_url_metadata_objects = url_server + '/metadata/Object'
base_url_metadata_objects_query = url_server + '/metadata/Object'
base_url_metadata_mapper_encode = url_server + '/metadata/mapper/encode/'
base_url_metadata_mapper_decode = url_server + '/metadata/mapper/decode/'
base_url_files_metadata_query = url_server + '/files/Metadata/'
base_url_files = url_server + '/files'
base_url_tags = url_server + '/tags'
base_url_devices = url_server + '/devices'
# == End Snapbundle Variables ==

metadataDataTypes = {'STRING': 'StringType',
                     'STRINGTYPE': 'StringType',
                     'DATE': 'DataType',
                     'DATETYPE': 'DataType',
                     'INTEGER': 'IntegerType',
                     'INTEGERTYPE': 'IntegerType',
                     'LONG': 'LongType',
                     'LONGTYPE': 'LongType',
                     'BOOLEAN': 'BooleanType',
                     'BOOLEANTYPE': 'BooleanType',
                     'FLOAT': 'FloatType',
                     'FLOATTYPE': 'FloatType',
                     'DOUBLE': 'DoubleType',
                     'DOUBLETYPE': 'DoubleType',
                     'JSON': 'JSONType',
                     'JSONTYPE': 'JSONType',
                     'XML': 'XMLType',
                     'XMLTYPE': 'XMLType'
                     }


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_object(urn_to_check_for):
    url = base_url_objects + '/object/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 404) or (response.json()['objectUrn'] != urn_to_check_for):
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return response.json()
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_object(name, objectUrn, objectType):
    json_info = {"name": name,
                 "active": "true",
                 "objectUrn": objectUrn,
                 "objectType": objectType
                 }
    url = base_url_objects
    headers = {'content-type': 'application/json'}
    payload = json.dumps(json_info)
    logging.info("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectURN " + objectUrn + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code == 201:
        # Created new user
        logging.info("Created new object")
    elif response.status_code == 200:
        # Updating user
        logging.info("Object existed, updated")
    urn = response.json()['message']
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object(urn_to_check_for):
    url = base_url_objects + '/object/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 404) or (response.json()['objectUrn'] != urn_to_check_for):
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return response.json()
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata(urn_to_check_for):
    url = base_url_metadata_objects_query + '/' + urn_to_check_for + "?view=Full"
    logging.info("Looking for object metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata_dictionary(urn_to_check_for):
    url = base_url_metadata_objects_query + '/' + urn_to_check_for
    logging.info("Looking for object metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            temp_dict = {}
            for current in response.json():
                value = str(get_raw_value_decoded(current['rawValue'], str(current['dataType'])))
                # Check to see if it's really a dictionary stored as a string
                # If so, clear off all the unicode u'' crap from the beginning
                if (value[0] == '{') and (value[-1] == '}'):
                    value = ast.literal_eval(value)
                    non_unicode_value = {}
                    for key in value.keys():
                        non_unicode_value[str(key)] = str(value[key])
                    value = non_unicode_value
                temp_dict[str(current['key'])] = value
            return temp_dict
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_encoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_encode + metadataDataTypes[var_type.upper()]
    try:
        payload = str(var_passed_in)
    except UnicodeEncodeError:
        logging.critical("GAH, UnicodeEncodeError, don't know what to do!")
        payload = ''
        #payload = var_passed_in.encode("utf-8")
        #payload = unicode(var_passed_in, 'utf8')
    if payload == '':
        payload = 'NULL'
    headers = {'content-type': 'text/plain'}
    #print "Get_raw_value: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        logging.critical("uh oh, 404 error when trying to get raw value encoded!!")
    else:
        logging.debug("Get_raw_value: Encoded Response: " + str(response))
        logging.debug("Get_raw_value: Encoded Response JSON: " + str(response.json()))
        return response.json()['rawValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_decoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_decode + metadataDataTypes[var_type.upper()]
    payload = {'rawValue': var_passed_in}
    payload = json.dumps(payload)
    headers = {'content-type': 'application/json'}
    #print "Get_raw_value decoded: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        logging.critical("uh oh, 404 error when trying to get raw value decoded!!")
    else:
        logging.debug("Get_raw_value: Decoded Response: " + str(response))
        logging.debug("Get_raw_value: Decoded Response JSON: " + str(response.json()))
        return response.json()['decodedValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_metadata(reference_type, referenceURN, dataType, key, value, moniker=None):
    # Moniker check test hopefully temp
    if moniker is None:
        # First need to see if this object even has any metadata, if not, don't want to cause a 500 response
        url = base_url_metadata_objects_query + '/' + referenceURN + '?view=Full'
        response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
        for list_item in response.json():
            if list_item['key'] == 'moniker':
                moniker = list_item['rawValue']
                break

    # Back to normal application
    raw_value = get_raw_value_encoded(value, dataType)
    temp_meta_data = dict(
        entityReferenceType=reference_type,
        referenceURN=referenceURN,
        dataType=metadataDataTypes[dataType.upper()],
        key=key,
        rawValue=str(raw_value)
    )
    if moniker is not None:
        temp_meta_data['moniker'] = moniker

    url = base_url_metadata_objects + '/' + referenceURN
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_meta_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    try:
        logging.info("Response (for key/value " + str(key) + "/" + str(value) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    except UnicodeEncodeError:
        logging.info("Response (for key/value " + str(key) + "/" + "UnicodeEncodeError Value Here" + "): " + str(response.status_code) + " <--> " + str(response.json()))


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_add_update_relationship(entityReferenceType, referenceURN, relationshipType, relatedEntityReferenceType, relatedReferenceURN):
    # First check to see if it exists before add/update
    url = base_url_relationship + '/' + entityReferenceType + '/' + referenceURN + '/' + relatedEntityReferenceType + '/' + relatedReferenceURN + '/' + relationshipType
    logging.debug("Sending to URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response: " + str(response.status_code))
    if response.status_code == 204:
        # Relationship doesn't exist, do it
        temp_meta_data = dict(
            entityReferenceType=entityReferenceType,
            referenceURN=referenceURN,
            relationshipType=relationshipType,
            relatedEntityReferenceType=relatedEntityReferenceType,
            relatedReferenceUrn=relatedReferenceURN
        )

        url = base_url_relationship + '/' + entityReferenceType + '/' + referenceURN
        headers = {'content-type': 'application/json'}
        payload = json.dumps(temp_meta_data)
        logging.debug("Sending to URL: " + str(url))
        logging.debug("Submitting Payload: " + str(payload))
        response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
        try:
            logging.info("Response (for relationship " + str(referenceURN) + " " + str(relationshipType) + " " + str(relatedReferenceURN) + "): " + str(response.status_code) + " <--> " + str(response.json()))
        except UnicodeEncodeError:
            logging.info("Response (for relationship " + str(referenceURN) + " " + str(relationshipType) + " " + str(relatedReferenceURN) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    elif response.status_code == 200:
        return True
    elif response.status_code == 201:
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_relationship_urn_list(urn_to_check_for, relationship):
    url = base_url_relationship_query_object + '/' + urn_to_check_for + '/' + relationship
    logging.info("Looking for object relationships at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            temp_dict = {}
            for current in response.json():
                value = str(current['relatedReferenceURN'])
                temp_dict[str(value)] = str(current['urn'])
            return temp_dict
        else:
            return {}
    except KeyError:
        return {}


## ----------------------------------- FXN ------------------------------------------------------------------------
def delete_relationship(urn_to_delete):
    url = base_url_relationship + '/' + urn_to_delete
    logging.info("Looking to delete relationship at URL: " + str(url))
    response = requests.delete(url, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for url (" + str(url) + "): " + str(response.status_code))
    if response.status_code == 204:
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_object_interaction(objectUrn, device_id, data, recordedTimestamp, moniker=None):
    # Back to normal application
    temp_meta_data = dict(
        object=objectUrn,
        identification=device_id,
        data=data,
        recordedTimestamp=recordedTimestamp
    )
    if moniker is not None:
        temp_meta_data['moniker'] = moniker

    url = base_url_object_interaction
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_meta_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectInteractionURN " + str(data) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code == 201:
        # Created new user
        logging.info("Created new object interaction")
    elif response.status_code == 200:
        # Updating user
        logging.info("Object interaction existed, updated")
    urn = response.json()['message']
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_url(reference_type, referenceURN, mimeType, source_url):
    temp_data = {"entityReferenceType": reference_type,
                 "referenceUrn": referenceURN,
                 "mimeType": mimeType,
                 "contentUrl": source_url}
    url = base_url_files
    headers = {'content-type': 'application/json'}
    payload = json.dumps(temp_data)
    #print payload
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    #print response
    logging.info("Response for url (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        return response.json()['message']
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_url_jpg(reference_type, referenceURN, source_url):
    return add_file_from_url(reference_type, referenceURN, "image/jpeg", source_url)


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_file_object(file_urn):
    url = base_url_files + "/" + file_urn
    logging.info("Looking for file object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_file_object_contents(file_urn, check_cache=False):
    url = base_url_files + "/" + file_urn + "/contents"
    logging.info("Looking for file object at URL: " + str(url))
#   It's crucial that we add the "stream=True" part to the following response request.
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password), stream=True)
    logging.info(str(response))
    try:
        if response.status_code == 200:
            content_disposition = response.headers['content-disposition']
            index = content_disposition.index('filename="') + 10
            r_fileName, r_fileExtension = os.path.splitext(content_disposition[index:-1])
            fileName_use = r_fileName.split('/')
            fileName_use = fileName_use[len(fileName_use)-1]
            outFilePath = cache_directory + os.sep + fileName_use + r_fileExtension
            # If we want to use the cache, and the file already exists there, just use it
            if check_cache:
                logging.debug("Checked cache for file: " + outFilePath)
                if os.path.isfile(outFilePath):
                    logging.debug("Found file " + outFilePath + " in cache!  Not re-downloading it!")
                    return outFilePath
                else:
                    logging.debug("File " + outFilePath + " NOT found in cache!")

            logging.debug("Pulling file: " + fileName_use + r_fileExtension + " from stream")
            with open(outFilePath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
            logging.info("Successfully wrote file: " + outFilePath)
            return outFilePath
        else:
            return ''
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_tag_association(entity_reference_type, reference_urn, name):
    temp_data = dict(name=name)
    url = base_url_tags + "/" + entity_reference_type + "/" + reference_urn
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for url (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def count_objects():
    url = base_url_objects
    print "Looking at URL: " + str(url)
    count = 0
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    for record in response.json():
        count += 1
    print "Count: " + str(count)
    return response.json()

## ----------------------------------- END ------------------------------------------------------------------------
## ----------------------------------- END ------------------------------------------------------------------------

#count_objects()

#raw = get_raw_value_encoded("True", "Boolean")
#print raw
#val = get_raw_value_decoded("Nzk4NjM1Ng==", "String")
#print val
#add_update_metadata("Object", 'paulr:twitter:praddc', "String", "test_metadata", 'Test Successful')

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#print "Looking for URN: " + str(urn_to_check_for)
#response = requests.get(base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
#print response.json()

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#url = base_url_object_interaction + '/' + 'urn:uuid:3f893a56-f145-46f8-9b32-17d515190df9' #urn_to_check_for
#print response.json()['moniker']

#urn_to_check_for = snapbundle_user_object + ":instagram:" + "praddc"
#url = base_url_metadata_objects_query + '/' + urn_to_check_for + "/id"
#print "Looking at URL: " + str(url)
#response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
##logging.debug(response.json())
#print response
#exit()
#temp = list((response.json()))
#for item in temp:
#    print str(item)
#    url = base_url_metadata_objects + '/Object/' + urn_to_check_for + "/urn:uuid:e9894cb1-e7ea-4be9-9830-40054302cda7"    #urn_to_check_for
#    print "Looking at URL: " + str(url)
#    #response = requests.delete(url, auth=(snapbundle_username, snapbundle_password))
#    exit()
