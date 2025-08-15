'''
Created on 15 Jul 2022

@author: jacklok
'''

from wtforms import StringField, validators
from trexweb.forms.base_forms import ValidationBaseForm

class SendEmailForm(ValidationBaseForm):
    send_to               = StringField('Recipient Email Address', [
                                        validators.DataRequired(message="Recipient Email is required"),
                                        validators.Length(min=7, max=150, message="Recipient Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    subject             = StringField('Subject', [
                                        validators.Length(max=300, message="Subject length must not more than 300 characters")
                                        ]
                                        )
    
    message             = StringField('Message', [
                                        validators.Length(max=3000, message="Message length must not more than 3000 characters")
                                        ]
                                        )
    
class EncryptForm(ValidationBaseForm):
    plain               = StringField('Plain text', [
                                        validators.DataRequired(message="Plain text is required"),
                                        ]
                                        )
    fernet_key          = StringField('Fernet key', [
                                        validators.DataRequired(message="Fernet key is required"),
                                        ]
                                        )
class AESEncryptForm(ValidationBaseForm):
    plain               = StringField('Plain text', [
                                        validators.DataRequired(message="Plain text is required"),
                                        ]
                                        )
    aes_key          = StringField('AES key', [
                                        validators.DataRequired(message="AES key is required"),
                                        ]
                                        )    
    
class DecryptForm(ValidationBaseForm):
    encrypted               = StringField('Encrypted text', [
                                        validators.DataRequired(message="Encrypted text is required"),
                                        ]
                                        )
    fernet_key          = StringField('Fernet key', [
                                        validators.DataRequired(message="Fernet key is required"),
                                        ]
                                        )  
    
class AESDecryptForm(ValidationBaseForm):
    encrypted               = StringField('Encrypted text', [
                                        validators.DataRequired(message="Encrypted text is required"),
                                        ]
                                        )
    aes_key          = StringField('AES key', [
                                        validators.DataRequired(message="AES key is required"),
                                        ]
                                        )        