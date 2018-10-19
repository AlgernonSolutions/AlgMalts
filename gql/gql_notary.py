import datetime
import hashlib
import hmac
import json
import os
import tkinter
import urllib.parse

import boto3


class GqlNotary:
    _region = os.getenv('AWS_REGION', 'us-east-1')
    _service = 'appsync'

    def __init__(self, gql_endpoint):
        self._host = 'vi2wfvboq5aozlqmstb24p5tbq.appsync-api.us-east-1.amazonaws.com'
        self._endpoint = 'https://vi2wfvboq5aozlqmstb24p5tbq.appsync-api.us-east-1.amazonaws.com/'
        self._uri = '/graphql'
        self._method = 'POST'
        self._signed_headers = 'host;x-amz-date'
        self._algorithm = 'AWS4-HMAC-SHA256'
        self._gql_credentials = GqlCredentials.retrieve()
        self._access_key = self._gql_credentials.access_key_id
        self._secret_key = self._gql_credentials.access_key
        self._security_token = self._gql_credentials.token
        self._credentials = f"Credentials={self._gql_credentials.access_key_id}"

    def generate_headers(self, query, variables):
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')
        canonical_request = self._generate_canonical_request(amz_date, query, variables)
        credential_scope = self._generate_scope(date_stamp)
        string_to_sign = self._generate_string_to_sign(canonical_request, amz_date, credential_scope)
        signature = self._generate_signature(string_to_sign, date_stamp)
        headers = self._generate_headers(credential_scope, signature, amz_date)
        return headers

    def _generate_canonical_request(self, amz_date, query, variables):
        payload = {'query': query, 'variables': variables}
        canonical_headers = f'host:{self._host}\nx-amz-date:{amz_date}\n'
        payload_hash = hashlib.sha256(json.dumps(payload).encode('utf-8')).hexdigest()
        canonical_request = f"{self._method}\n{self._uri}\n\n{canonical_headers}\n{self._signed_headers}\n{payload_hash}"
        return canonical_request

    def _generate_string_to_sign(self, canonical_request, amz_date, scope):
        hash_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        return f"{self._algorithm}\n{amz_date}\n{scope}\n{hash_request}"

    def _generate_scope(self, date_stamp):
        return f"{date_stamp}/{self._region}/{self._service}/aws4_request"

    def _get_signature_key(self, date_stamp):
        k_date = self._sign(f'AWS4{self._secret_key}'.encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, self._region)
        k_service = self._sign(k_region, self._service)
        k_signing = self._sign(k_service, 'aws4_request')
        return k_signing

    def _generate_signature(self, string_to_sign, date_stamp):
        signing_key = self._get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def _generate_headers(self, credential_scope, signature, amz_date):
        credentials_entry = f'Credential={self._access_key}/{credential_scope}'
        headers_entry = f'SignedHeaders={self._signed_headers}'
        signature_entry = f'Signature={signature}'
        authorization_header = f"{self._algorithm} {credentials_entry}, {headers_entry}, {signature_entry}"
        return {'X-Amz-Security-Token': self._security_token, 'x-amz-date': amz_date, 'Authorization': authorization_header, 'Content-Type': "application/graphql"}

    @classmethod
    def _generate_request_parameters(cls, command):
        payload = {'gremlin': command}
        request_parameters = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
        payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
        return payload_hash, request_parameters

    @classmethod
    def _sign(cls, key, message):
        return hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()


class GqlCredentials:
    _duration_seconds = 10800

    def __init__(self, mfa_serial, access_key_id, access_key, token, expiration, sts_file_path):
        self._mfa_serial = mfa_serial
        self._access_key_id = access_key_id
        self._access_key = access_key
        self._token = token
        self._expiration = expiration
        self._sts_file_path = sts_file_path

    @classmethod
    def generate(cls, mfa_serial=None):
        window = MfaWindow(mfa_serial)
        mfa_value, serial_number = window.run()
        sts_file_path = cls.derive_sts_path()
        client = boto3.client('sts')
        response = client.get_session_token(
            DurationSeconds=cls._duration_seconds,
            SerialNumber=serial_number,
            TokenCode=mfa_value
        )
        credentials = response['Credentials']
        gql_credentials = cls(
            serial_number, credentials['AccessKeyId'], credentials['SecretAccessKey'],
            credentials['SessionToken'], credentials['Expiration'].timestamp(), sts_file_path
        )
        gql_credentials.record()
        return gql_credentials

    @classmethod
    def retrieve(cls):
        sts_file_path = cls.derive_sts_path()
        try:
            with open(sts_file_path) as sts_file:
                sts_dict = json.load(sts_file)
                gql_credentials = cls(**sts_dict)
                if gql_credentials.are_expired:
                    return cls.generate(gql_credentials.mfa_serial)
                return gql_credentials
        except FileNotFoundError:
            return cls.generate()

    def record(self):
        with open(self._sts_file_path, 'w') as sts_file:
            json.dump({
                'mfa_serial': self._mfa_serial,
                'access_key_id': self._access_key_id,
                'access_key': self._access_key,
                'expiration': self._expiration,
                'sts_file_path': self._sts_file_path,
                'token': self._token
            }, sts_file)

    @property
    def are_expired(self):
        expired_buffer = datetime.timedelta(minutes=5)
        return datetime.datetime.fromtimestamp(self._expiration) - datetime.datetime.now() <= expired_buffer

    @property
    def access_key(self):
        return self._access_key

    @property
    def access_key_id(self):
        return self._access_key_id

    @property
    def token(self):
        return self._token

    @property
    def mfa_serial(self):
        return self._mfa_serial

    @classmethod
    def derive_sts_path(cls):
        from pathlib import Path
        sts_file_name = 'alg_malt_sts.json'
        return str(Path.home().joinpath('.aws', sts_file_name))


class MfaWindow:
    def __init__(self, mfa_serial=False):
        self._top = tkinter.Tk()
        self._mfa_code = tkinter.StringVar()
        self._serial_number = tkinter.StringVar()
        self._needs_serial = mfa_serial
        if self._needs_serial:
            self._serial_number.set(self._needs_serial)

    def run(self):
        self._generate()
        return self._mfa_code.get(), self._serial_number.get()

    def _generate(self):
        if not self._needs_serial:
            serial_label = tkinter.Label(
                self._top, text='please input the serial number of the MFA device', relief=tkinter.RAISED)
            serial_label.pack()
            serial_field = tkinter.Entry(self._top, textvariable=self._serial_number)
            serial_field.pack()
        label = tkinter.Label(self._top, text='please input the MFA code', relief=tkinter.RAISED)
        label.pack()
        mfa_field = tkinter.Entry(self._top, textvariable=self._mfa_code)
        mfa_field.pack()
        submit = tkinter.Button(text='submit', command=self.exit)
        submit.pack()
        self._top.mainloop()

    def exit(self):
        self._top.destroy()
