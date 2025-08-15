'''
Created on 23 Jul 2021

@author: jacklok
'''
from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from trexlib.libs.wtforms.fields import CurrencyField, JSONField
from wtforms.fields.simple import HiddenField
from wtforms.fields.core import BooleanField




class ProductCategorySetupForm(ValidationBaseForm):
    category_group_key                  = StringField(gettext('Product Category Group'),[
                                                
                                            ])
    category_label                      = StringField(gettext('Product Category Label'),[
                                                validators.InputRequired(message=gettext("Product Category Label is required")),
                                                validators.Length(max=100, message="Product Category Label length must not more than 100 characters")
                                            ])
    
    product_modifier                    = StringField(label=gettext('Product Modifier'), 
                                                                          validators = [
                                                                                        ]
                                                                    )
    
class ProductCategoryUpdateForm(ProductCategorySetupForm):
    category_key                        = StringField(gettext('Product Category Key'),[
                                                validators.InputRequired(message=gettext("Product Category Key is required")),
                                            ]) 
    
    
class ProductSearchForm(ValidationBaseForm):
    product_sku                = StringField('Product SKU', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Product SKU length must be within 1 and 30 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['product_name', 'product_category'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    
    product_name                = StringField('Product Name', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Product name length must be within 1 and 100 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['product_sku', 'product_category'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    product_category            = StringField('Product Category', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['product_name', 'product_sku'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )

class CreateProductForm(ValidationBaseForm):
    
    
    product_sku                = StringField('Product SKU', [
                                        validators.InputRequired(message=gettext("Product SKU is required")),
                                        validators.Length(min=3, max=300, message='Product SKU length must be within 1 and 30 characters'),
                                        ])
    
    product_name                = StringField('Product Name', [
                                        validators.InputRequired(message=gettext("Product name is required")),
                                        validators.Length(min=3, max=300, message='Product name length must be within 1 and 100 characters'),
                                        ])
    
    barcode                     = StringField('Barcode', [
                                        ])
    
    price                       = CurrencyField('Price',[
                                                validators.DataRequired(message="Price"),
                                            ])
    
    cost                        = CurrencyField('Cost',[
                                                validators.Optional(),
                                            ])
    
    product_desc                = StringField('Product Description', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Product description length must be within 1 and 300 characters'),
                                        ])
    
    product_category            = StringField('Product Category', [
                                        validators.InputRequired(message=gettext("Product category is required")),
                                        ])   
    
    product_modifier                    = StringField(label=gettext('Product Modifier'), 
                                                                          validators = [
                                                                                        ]
                                                                    )
    
class UpdateProductForm(CreateProductForm):
    product_key                        = StringField(gettext('Product Key'),[
                                                validators.InputRequired(message=gettext("Product key is required")),
                                            ])
    
    
class ProductSettingOnPOSForm(ValidationBaseForm):    
    product_key                                 = StringField(gettext('Product Key'),[
                                                            validators.InputRequired(message=gettext("Product key is required")),
                                                            ])
    
    representation_on_pos_option                = StringField('Representation On POS Option', [
                                                            validators.InputRequired(message=gettext("Representation On POS Option is required")),
                                                            ])
    
    image_representation_url                    = StringField('Image Representation', [
                                                            custom_validator.RequiredIf(gettext('Image Representation is required'), 
                                                                    representation_on_pos_option=(
                                                                                'image'
                                                                                
                                                                                )
                                                                    )
                                                            ])
                                                            
    color_representation                        = JSONField('Color Representation', [
                                                            custom_validator.RequiredIf(gettext('Color Representation is required'), 
                                                                    representation_on_pos_option=(
                                                                                'color'
                                                                                
                                                                                )
                                                                    )
                                                            ])
    
    product_shortcut_key                        = StringField(gettext('Product shortcut key'),[
                                                            
                                                            ])
    
class ProductModifierDetailsForm(ValidationBaseForm):
    modifier_key                        = HiddenField(gettext('Modifier key'),[
                                                
                                            ])
    
    modifier_name                       = StringField(gettext('Modifier Name'),[
                                                validators.InputRequired(message=gettext("Modifier name is required")),
                                                validators.Length(max=150, message="Modifier name length must not more than 150 characters")
                                            ])
    modifier_label                       = StringField(gettext('Modifier Label'),[
                                                validators.InputRequired(message=gettext("Modifier Label is required")),
                                                validators.Length(max=150, message="Modifier label length must not more than 150 characters")
                                            ])
    
    allow_multiple_option               = BooleanField()
    option_is_mandatory                 = BooleanField()
    
    modifier_options                    = JSONField('Multitier Prepaid Settings', [])

class ProductCatalogueForm(ValidationBaseForm):
    catalogue_key                        = HiddenField(gettext('Catalogue key'),[
                                                
                                            ])
    
class ProductCatalogueDetailsForm(ProductCatalogueForm):
    catalogue_name                       = StringField(gettext('Cataloue Name'),[
                                                validators.InputRequired(message=gettext("Cataloue name is required")),
                                            ])
    
    menu_settings                        = JSONField('Menu Settings', [])    
    
    desc                                 = StringField('Description',[
                                                validators.Length(max=500, message="Description length must not more than 500 characters")
                                            ])
    