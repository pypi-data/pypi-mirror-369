'''
Created on 3 Sep 2024

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
#from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexlib.utils.string_util import is_not_empty, is_empty
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexconf import program_conf
from trexconf import conf
from trexlib.utils.common.common_util import sort_dict_list, sort_list
from trexlib.libs.flask_wtf.request_wrapper import request_values, request_files,\
    request_debug
from trexmodel.models.datastore.marketing_models import MerchantNewsFile
from trexadmin.forms.merchant.marketing.merchant_news_setup_forms import MerchantNewsSetupForm,\
    MerchantNewsForm
from trexconf.program_conf import is_merchant_news_current_status_reach
from flask_restful import abort
import jinja2
from trexadmin.libs.jinja.merchant_filters import merchant_news_completed_status_label as merchant_news_completed_status_label_filter

merchant_news_setup_bp = Blueprint('merchant_news_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/marketing/news')

logger = logging.getLogger('controller')


@jinja2.contextfilter
@merchant_news_setup_bp.app_template_filter()
def merchant_news_completed_status_label(context, completed_status_code):
    return merchant_news_completed_status_label_filter(completed_status_code)


'''
Blueprint settings here
'''


@merchant_news_setup_bp.context_processor
def merchant_manage_news_bp_inject_settings():
    
    return dict(
                MERCHANT_NEWS_STATUS_BASE               = program_conf.MERCHANT_NEWS_STATUS_BASE,
                MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL    = program_conf.MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL,
                MERCHANT_NEWS_STATUS_PUBLISH            = program_conf.MERCHANT_NEWS_STATUS_PUBLISH,
                MERCHANT_NEWS_BASE_URL                  = conf.MERCHANT_NEWS_BASE_URL, 
                )


@merchant_news_setup_bp.route('/', methods=['GET'])
@login_required
def manage_merchant_news(): 
    return show_merchant_news_setup_listing(
                'merchant/marketing/news/manage_merchant_news.html',
                
                )

def show_merchant_news_setup_listing(template_name, show_page_title=True, is_archived=False): 
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    merchant_news_list              = []
    
    logger.debug('template_name=%s', template_name)
    logger.debug('show_page_title=%s', show_page_title)
    logger.debug('is_archived=%s', is_archived)
    
    db_client = create_db_client(caller_info="show_merchant_news_setup_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                #logger.debug('merchant_acct=%s', merchant_acct)
                if is_archived:
                    _merchant_news_setup_list  = sort_list(MerchantNewsFile.list_archived_by_merchant_acct(merchant_acct), 'created_datetime', reverse_order=True)
                else:
                    _merchant_news_setup_list  = sort_list(MerchantNewsFile.list_by_merchant_acct(merchant_acct), 'created_datetime', reverse_order=True)
                
                for mp in _merchant_news_setup_list:
                    merchant_news_list.append(mp.to_dict())
            
    except:
        logger.error('Fail to list merchant news due to %s', get_tracelog())
           
    
    logger.debug('merchant_news_setup_list count=%d', len(merchant_news_list))
    
    return render_template(template_name,
                           page_title = gettext('Manage News') if show_page_title else None,
                           merchant_news_list = merchant_news_list,
                           )
    
@merchant_news_setup_bp.route('/news-listing-content', methods=['GET'])
@login_required
def manage_merchant_news_listing_content(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_merchant_news_listing_content")
    news_file_list = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        result_listing = MerchantNewsFile.list_by_merchant_acct(merchant_acct)
        logger.debug('result_listing=%s', result_listing)
                
        if result_listing:
            for news_file in result_listing:
                news_file_list.append(news_file.to_dict())
    
    #sorted_banner_file_list = sort_dict_list(banner_file_list, sort_attr_name='sequence')
        
    return render_template('merchant/marketing/news/manage_merchant_news_content.html',
                           merchant_news_list     = news_file_list

                           )  
    
 
    

@merchant_news_setup_bp.route('/list/content', methods=['GET'])
def merchant_news_setup_listing_content():
    return show_merchant_news_setup_listing(
                'merchant/marketing/news/latest_merchant_news_setup_listing_content.html',
                )

@merchant_news_setup_bp.route('/list/archived', methods=['GET'])
def archived_merchant_news_setup_listing():
    return show_merchant_news_setup_listing(
                'merchant/marketing/news/archived_merchant_news_setup_listing.html',
                show_page_title = False,
                is_archived = True
                ) 

@merchant_news_setup_bp.route('/create-merchant-news', methods=['GET'])
@login_required
def create_merchant_news(): 
    logger.debug('---create_merchant_news---')
    
    return render_template('merchant/marketing/news/setup/create_merchant_news.html',
                           define_merchant_news_base                  = url_for('merchant_news_setup_bp.define_merchant_news_base_post'),
                           upload_image_file_url                      = url_for('merchant_news_setup_bp.upload_merchant_news_upload_material_post'),
                           define_merchant_news_material_post         = url_for('merchant_news_setup_bp.define_merchant_news_material_post'),
                           publish_merchant_news                      = url_for('merchant_news_setup_bp.publish_merchant_news_post'),
                           show_merchant_news_review                  = url_for('merchant_news_setup_bp.show_merchant_news_review'),
                           update_merchant_news_material_uploaded     = url_for('merchant_news_setup_bp.define_merchant_news_material_post'),
                           
                           merchant_news_default_image_url            = conf.MERCHANT_NEWS_DEFAULT_IMAGE,
                           ) 

@merchant_news_setup_bp.route('/edit-merchant-news/<merchant_news_key>', methods=['GET'])
@login_required
def edit_merchant_news(merchant_news_key): 
    logger.debug('---edit_merchant_news---')
    merchant_news                 = None
    
    if is_not_empty(merchant_news_key):
        db_client = create_db_client(caller_info="edit_merchant_news")
            
        try:
            with db_client.context():
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                
            merchant_news_dict = merchant_news.to_dict()
            
            return render_template('merchant/marketing/news/setup/create_merchant_news.html', 
                           define_merchant_news_base                      = url_for('merchant_news_setup_bp.define_merchant_news_base_post'),
                           upload_image_file_url                          = url_for('merchant_news_setup_bp.upload_merchant_news_upload_material_post'),
                           publish_merchant_news                          = url_for('merchant_news_setup_bp.publish_merchant_news_post'),
                           show_merchant_news_review                      = url_for('merchant_news_setup_bp.show_merchant_news_review'),
                           update_merchant_news_material_uploaded         = url_for('merchant_news_setup_bp.define_merchant_news_material_post'),
                           
                           MERCHANT_NEWS_STATUS_BASE_COMPLETED            = True,
                           MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL_COMPLETED = is_merchant_news_current_status_reach(program_conf.MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL, merchant_news.completed_status),
                           MERCHANT_NEWS_STATUS_PUBLISH_COMPLETED         = is_merchant_news_current_status_reach(program_conf.MERCHANT_NEWS_STATUS_PUBLISH, merchant_news.completed_status),
                           merchant_news                                  = merchant_news_dict,
                           merchant_news_completed_status                 = merchant_news.completed_status,
                           is_edit_merchant_news                          = True,
                           merchant_news_default_image_url                = conf.MERCHANT_NEWS_DEFAULT_IMAGE,
                           )
                
        except:
            logger.error('Fail to read merchant news due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)
    
@merchant_news_setup_bp.route('/view-merchant-news/<merchant_news_key>', methods=['GET'])
@login_required
def view_merchant_news(merchant_news_key): 
    logger.debug('---view_merchant_news---')
    merchant_news                 = None
    
    if is_not_empty(merchant_news_key):
        db_client = create_db_client(caller_info="view_merchant_news")
            
        try:
            with db_client.context():
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                
            merchant_news_dict = merchant_news.to_dict()
            
            return render_template('merchant/marketing/news/setup/create_merchant_news.html', 
                           
                           MERCHANT_NEWS_STATUS_BASE_COMPLETED            = True,
                           MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL_COMPLETED = True,
                           MERCHANT_NEWS_STATUS_PUBLISH_COMPLETED         = True,
                           merchant_news                                  = merchant_news_dict,
                           merchant_news_completed_status                 = merchant_news.completed_status,
                           is_view_mode                                   = True,
                           merchant_news_default_image_url                = conf.MERCHANT_NEWS_DEFAULT_IMAGE,
                           
                           )
                
        except:
            logger.error('Fail to read merchant news due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)    

@merchant_news_setup_bp.route('/define-merchant-news-base', methods=['POST'])
@login_required
def define_merchant_news_base_post(): 
    logger.debug('---define_merchant_news_base_post---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    merchant_news_setup_data = request.form
    
    merchant_news_setup_form  = MerchantNewsSetupForm(merchant_news_setup_data)
    
    try:
        if merchant_news_setup_form.validate():
            db_client = create_db_client(caller_info="define_merchant_news_base_post")
            merchant_news = None
            
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                label               = merchant_news_setup_form.label.data
                desc                = merchant_news_setup_form.desc.data
                news_text           = merchant_news_setup_form.news_text.data
                start_date          = merchant_news_setup_form.start_date.data
                end_date            = merchant_news_setup_form.end_date.data
                merchant_news_key   = merchant_news_setup_form.merchant_news_key.data
                
                if is_not_empty(merchant_news_key):
                    merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                    
                if merchant_news is None:
                    merchant_news       = MerchantNewsFile.create(
                                            merchant_acct, 
                                            label       = label, 
                                            desc        = desc, 
                                            news_text   = news_text,
                                            start_date  = start_date,
                                            end_date    = end_date,
                                            created_by  = merchant_user,
                                            )
                    
                else:
                    MerchantNewsFile.update(
                                            merchant_news, 
                                            label       = label, 
                                            desc        = desc, 
                                            news_text   = news_text,
                                            start_date  = start_date,
                                            end_date    = end_date,
                                            modified_by = merchant_user,
                                            )
                
                merchant_news_key   = merchant_news.key_in_str
            
            return create_rest_message(status_code=StatusCode.OK, 
                                    merchant_news_key  = merchant_news_key,
                                    )
        else:
            return create_rest_message(gettext('Failed to create news'), status_code=StatusCode.BAD_REQUEST)
    
    except:
        logger.error('Failed to define merchant news due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to create news'), status_code=StatusCode.BAD_REQUEST)

@merchant_news_setup_bp.route('/publis-merchant-news-base', methods=['POST'])
@login_required
def publish_merchant_news_post(): 
    logger.debug('---MERCHANT_NEWS_STATUS_PUBLISH---')
    merchant_news_data = request.form
    
    merchant_news_form = MerchantNewsForm(merchant_news_data)
    
    logger.debug('merchant_news_form=%s', merchant_news_form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    merchant_news_key = merchant_news_form.merchant_news_key.data
    
    logger.debug('merchant_news_key=%s', merchant_news_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if merchant_news_form.validate():
    
        db_client               = create_db_client(caller_info="publish_merchant_news")
        
        try:
            with db_client.context():
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                if merchant_news: 
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    MerchantNewsFile.publish(merchant_news, 
                                                         published_by    = merchant_user
                                                         )
            
            if merchant_news is None:
                return create_rest_message(gettext('Invalid merchant news data'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to publish merchant news due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to publish merchant news'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    merchant_news_key                             = merchant_news_key,
                                    )
        
    else:
        error_message = merchant_news_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  


@merchant_news_setup_bp.route('/show-merchant-news-review', methods=['GET'])
@login_required
def show_merchant_news_review(): 
    logger.debug('---show_merchant_news_review---')
    
    merchant_news_key       = request.args.get('merchant_news_key')
    
    db_client = create_db_client(caller_info="show_merchant_news_review")
    try:
        
        with db_client.context():
            merchant_news = MerchantNewsFile.fetch(merchant_news_key)
            if merchant_news:
                merchant_news = merchant_news.to_dict()
            
            
    except:
        logger.error('Fail to get merchant news setup due to %s', get_tracelog())
           
    
    
    
    return render_template('merchant/marketing/news/setup/merchant_news_review_content.html', 
                           merchant_news = merchant_news,
                           )

@merchant_news_setup_bp.route('/upload-news-file', methods=['GET'])
@login_required
def upload_merchant_news_material():
    
    try:
        return render_template('merchant/marketing/news/setup/upload_news_image_form.html', 
                           page_title                          = gettext('Upload News File'),
                           upload_image_file_url               = url_for('merchant_news_setup_bp.upload_merchant_news_upload_material_post'),
                           )
        
    except:
        logger.error('Fail to read news image due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to read news image'), status_code=StatusCode.BAD_REQUEST)   

@merchant_news_setup_bp.route('/upload-news-file', methods=['POST'])
@request_debug   
@limit_content_length(conf.MAX_CONTENT_FILE_LENGTH)
#@login_required
#@request_values
#@request_files
#@request_values
def upload_merchant_news_upload_material_post():
    logger.debug('---upload_merchant_news_upload_material_post---')    
    #news_file_type    = request_values.get('news_file_type')
    merchant_news_key       = request.form.get('merchant_news_key')
    uploaded_file           = request.files.get('file')
    #uploaded_file           = request_files.get('file')
    
    uploaded_url = None
    
    #logger.debug('news_file_type=%s', news_file_type)
    logger.debug('merchant_news_key=%s', merchant_news_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="upload_news_file_post")
    try:
        with db_client.context():
        
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            merchant_news = MerchantNewsFile.fetch(merchant_news_key)
        
        if merchant_news:
            bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
            with db_client.context():
                MerchantNewsFile.upload_file(merchant_news, uploaded_file, merchant_acct, bucket, 
                                                           
                                                           )
                
                uploaded_url        = merchant_news.news_file_public_url
                
    except:
        logger.error('Failed to upload image due to %s', get_tracelog())
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
         
    return create_rest_message(status_code=StatusCode.OK, uploaded_image_url=uploaded_url)
    

@merchant_news_setup_bp.route('/define-news-upload-material', methods=['POST'])
@login_required
def define_merchant_news_material_post(): 
    logger.debug('---define_merchant_news_material_post---')
    
    merchant_news_data = request.form
    merchant_news_form = MerchantNewsForm(merchant_news_data)
    
    logger.debug('merchant_news_form=%s', merchant_news_form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    merchant_news_key = merchant_news_form.merchant_news_key.data
    
    logger.debug('merchant_news_key=%s', merchant_news_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if merchant_news_form.validate():
    
        db_client               = create_db_client(caller_info="define_merchant_news_material_post")
        
        try:
            with db_client.context():
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                if merchant_news: 
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    MerchantNewsFile.update_news_material_uploaded(merchant_news, 
                                                         modified_by    = merchant_user
                                                         )
            
            if merchant_news is None:
                return create_rest_message(gettext('Invalid merchant news data'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to update merchant news due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant news'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    merchant_news_key                             = merchant_news_key,
                                    )
        
    else:
        error_message = merchant_news_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  
    
@merchant_news_setup_bp.route('/<news_file_key>', methods=['DELETE'])    
@login_required
def delete_news_file_post(news_file_key):    
    if is_not_empty(news_file_key):
        db_client       = create_db_client( caller_info="delete_news_file_post")
        news_file    = None
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
        with db_client.context():
            news_file = MerchantNewsFile.fetch(news_file_key)
            MerchantNewsFile.remove_file(news_file, bucket)
        
        if news_file:
            return create_rest_message(status_code=StatusCode.ACCEPTED)
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@merchant_news_setup_bp.route('/archive/<merchant_news_key>', methods=['post','get'])
def archive_merchant_news(merchant_news_key):
    logger.debug('--- archive_merchant_news ---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="archive_merchant_news")
    
    try:
        with db_client.context():
            merchant_news     = MerchantNewsFile.fetch(merchant_news_key)
            merchant_user     = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            
            if merchant_news:
                merchant_news.archived(merchant_user)
            
            return create_rest_message(status_code=StatusCode.OK)
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to archive news'), status_code=StatusCode.BAD_REQUEST)    
     
@merchant_news_setup_bp.route('/disable', methods=['POST','GET'])
@login_required
def disable_merchant_news_post(): 
    
    logger.debug('---disable_merchant_news_post---')
    
    merchant_news_key = request.args.get('merchant_news_key')
    
    logger.debug('merchant_news_key=%s', merchant_news_key)
    
    db_client               = create_db_client(caller_info="disable_merchant_news_post")
    try:
        with db_client.context():
            if is_empty(merchant_news_key):
                return create_rest_message(gettext('Invaid merchant news data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                if merchant_news:
                    logger.info('going to disable merchant news')
                    MerchantNewsFile.disable_news(merchant_news) 
                    
        if merchant_news is None:
            return create_rest_message(gettext('Invalid merchant news'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to disable merchant news due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to disable merchant news'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,) 

@merchant_news_setup_bp.route('/enable', methods=['POST','GET'])
@login_required
def enable_merchant_news_post(): 
    
    logger.debug('---enable_merchant_news_post---')
    
    merchant_news_key = request.args.get('merchant_news_key')
    
    logger.debug('merchant_news_key=%s', merchant_news_key)
    
    db_client               = create_db_client(caller_info="enable_merchant_news_post")
    try:
        with db_client.context():
            if is_empty(merchant_news_key):
                return create_rest_message(gettext('Invaid merchant news data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                if merchant_news:
                    logger.info('going to enable merchant news')
                    MerchantNewsFile.enable_news(merchant_news)
                    
        if merchant_news is None:
            return create_rest_message(gettext('Invalid merchant news'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to enable merchant news due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to enable merchant news'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)  

@merchant_news_setup_bp.route('/<merchant_news_key>/show', methods=['GET'])
def show_merchant_news(merchant_news_key):
    
    logger.debug('---show_merchant_news---')
    merchant_news                 = None
    
    if is_not_empty(merchant_news_key):
        db_client = create_db_client(caller_info="show_merchant_news")
            
        try:
            with db_client.context():
                merchant_news = MerchantNewsFile.fetch(merchant_news_key)
                
            merchant_news_dict = merchant_news.to_dict()
            
            return render_template('merchant/marketing/news/view/show_merchant_news.html', 
                           merchant_mew = merchant_news_dict
                           
                           
                           )
                
        except:
            logger.error('Fail to read merchant news due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to read merchant news'), status_code=StatusCode.BAD_REQUEST)  
           

