import sys, os, base64, datetime, hashlib, hmac
import requests  # pip install requests

# ************* REQUEST VALUES *************
method = 'GET'
service = 'rds'
host = 'rds.us-east-1.amazonaws.com'
region = 'us-east-1'
endpoint = 'https://rds.us-east-1.amazonaws.com'
request_parameters = 'Action=DescribeDBInstances&Version=2014-10-31'


# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
access_key = 'AKIAXHTXJSBLERO2INMD'
secret_key = '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'
if access_key is None or secret_key is None:
    print('No access key is available.')
    sys.exit()

# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

# amzdate = '20210112T200214Z'
# datestamp = '20210112'  # Date w/o time, used in credential scope

canonical_uri = '/'
canonical_querystring = request_parameters
canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
signed_headers = 'host;x-amz-date'
payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()

canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

# ************* TASK 2: CREATE THE STRING TO SIGN*************
# Match the algorithm to the hashing algorithm you use, either SHA-1 or
# SHA-256 (recommended)
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(
    canonical_request.encode('utf-8')).hexdigest()

print(string_to_sign)


signing_key = getSignatureKey(secret_key, datestamp, region, service)

signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

print(signature)

# ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# The signing information can be either in a query string value or in
# a header named Authorization. This code shows how to use a header.
# Create authorization header and add to request headers
authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

# The request can include any headers, but MUST include "host", "x-amz-date",
# and (for this scenario) "Authorization". "host" and "x-amz-date" must
# be included in the canonical_headers and signed_headers, as noted
# earlier. Order here is not significant.
# Python note: The 'host' header is added automatically by the Python 'requests' library.
headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}

# ************* SEND THE REQUEST *************
request_url = endpoint + '?' + canonical_querystring

print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
print('Request URL = ' + request_url)
print('Request header = '+str(headers))
r = requests.get(request_url, headers=headers)

print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
print('Response code: %d\n' % r.status_code)
print(r.text)



