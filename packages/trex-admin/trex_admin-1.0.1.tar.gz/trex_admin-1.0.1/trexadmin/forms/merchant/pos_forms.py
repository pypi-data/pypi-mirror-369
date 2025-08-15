

from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from trexlib.libs.wtforms import validators as custom_validator
from wtforms.fields.core import BooleanField, IntegerField
from trexmodel import pos_conf
from trexlib.libs.wtforms.fields import JSONField




class POSSettingForm(ValidationBaseForm):
    pos_setting_key                         = StringField('POS Device Key')
    device_name                             = StringField(gettext('POS Device name'),[
                                                validators.InputRequired(message=gettext("POS Device name is required")),
                                                validators.Length(max=100, message="POS Device name length must not more than 100 characters")
                                            ])
    
    assign_outlet_key                      = StringField(gettext('Assign Outlet'),[
                                                validators.InputRequired(message=gettext("Assign outlet is required")),
                                                
                                            ])
    
    
class POSCatalogueForm(ValidationBaseForm):
    pos_catalogue_key                       = StringField('POS Catalogue Key')
    catalogue_key                           = StringField(gettext('Assign Catalogue'),[
                                                validators.InputRequired(message=gettext("Assign Catalogue is required")),
                                                
                                            ])
    
    assign_outlet                           = StringField('Assign Outlet',[
                                                validators.InputRequired(message=gettext("Assign Outlet is required")),
                                                
                                            ])
    
class DinningTableSetupForm(ValidationBaseForm):
    dinning_table_setup_key              = StringField('Dinning Table Setup Key')
    name                                 = StringField(gettext('Table list'),[
                                                validators.InputRequired(message=gettext("Name is required")),
                                                validators.length(min=3, max=150, message=gettext('Name is minimum 3 characters and maximum 150 characters')),
                                            ])
    table_list                           = StringField(gettext('Table list'),[
                                                validators.InputRequired(message=gettext("Table list is required")),
                                                
                                            ])  
    show_occupied                        = BooleanField()
     
    assign_outlet                        = StringField('Assign Outlet',[
                                                validators.InputRequired(message=gettext("Assign Outlet is required")),
                                                
                                            ]) 
    
class DinningOptionForm(ValidationBaseForm):
    dinning_option_key                   = StringField('Dinning Option Key')
    name                                 = StringField(gettext('Option Name'),[
                                                validators.InputRequired(message=gettext("Option Name is required")),
                                                validators.length(min=3, max=50, message=gettext('Option Name is minimum 3 characters and maximum 50 characters')),
                                            ])
    prefix                               = StringField(gettext('Option Prefix'),[
                                                validators.InputRequired(message=gettext("Option Prefix is required")),
                                                validators.length(min=2, max=50, message=gettext('Option Prefix is minimum 2 characters and maximum 10 characters')),
                                            ])
    is_default                           = BooleanField()
    is_dinning_input                     = BooleanField()
    is_delivery_input                    = BooleanField()
    is_takeaway_input                    = BooleanField()
    is_self_order_input                  = BooleanField()
    is_self_payment_mandatory            = BooleanField()   
    dinning_table_is_required            = BooleanField()
    assign_queue                         = BooleanField()
    
class PosPaymentMethodForm(ValidationBaseForm):
    payment_method_key                   = StringField('Payment method Key')
    label                                = StringField(gettext('Payment method Label'),[
                                                validators.InputRequired(message=gettext("Payment method Label is required")),
                                                validators.length(min=3, max=50, message=gettext('Payment method Label is minimum 3 characters and maximum 50 characters')),
                                            ])
    is_default                           = BooleanField()       
    is_rounding_required                 = BooleanField()
    
    
class ServiceChargeSetupForm(ValidationBaseForm):
    service_charge_setup_key             = StringField('Service Charge Setup Key')
    charge_name                             = StringField('Charge Name', [
                                                validators.DataRequired(message="Charge Name is required"),
                                                validators.Length(min=0, max=150, message='Charge Name length must be within 3 and 150 characters')
                                            ])
    charge_label                         = StringField('Charge Label', [
                                                validators.DataRequired(message="Charge Label is required"),
                                                validators.Length(min=0, max=30, message='Charge Label length must be within 3 and 30 characters')
                                            ])
    charge_pct_amount                    = IntegerField(gettext('Charge percentage amount'),[
                                                validators.InputRequired(message=gettext("Charge percentage amount is required")),
                                                validators.NumberRange(min=0, max=100),
                                            ])
    applyed_dinning_option               = StringField('Apply to Dinning Option', [
                                                validators.DataRequired(message="Apply to Dinning Option"),
                                                
                                            ])
    assign_outlet                        = StringField('Assign Outlet',[
                                                validators.InputRequired(message=gettext("Assign Outlet is required")),
                                                
                                            ])     
    
class RoundingSetupForm(ValidationBaseForm):
    rounding_setup_key                   = StringField('Rounding Setup Key')
    rounding_interval                    = StringField(gettext('Rounding interval'),[
                                                validators.InputRequired(message=gettext("Rounding interval is required")),
                                                
                                            ])
    rounding_rule                       = StringField(gettext('Rounding rule'),[
                                                custom_validator.RequiredIf(message=gettext("Rounding rule is required"),
                                                                      rounding_interval=(
                                                                                        pos_conf.ROUNDING_INTERVAL_100,
                                                                                        pos_conf.ROUNDING_INTERVAL_050,
                                                                                        pos_conf.ROUNDING_INTERVAL_010,
                                                                                        pos_conf.ROUNDING_INTERVAL_005,
                                                                                    )
                                                                      ),
                                                
                                            ])
    
class ReceiptSetupForm(ValidationBaseForm):
    receipt_setup_key             = StringField('Service Charge Setup Key')
    receipt_settings              = JSONField(gettext('Receipt settings'))
        
    