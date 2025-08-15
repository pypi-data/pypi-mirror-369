'''
Created on 22 Dec 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexconf import conf as admin_conf
from google.cloud import storage
from datetime import datetime
from trexlib.utils.google.gcloud_util import connect_to_bucket

test_upload_bp = Blueprint('test_upload_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/test/upload'
                     )

'''
Blueprint settings here
'''
@test_upload_bp.context_processor
def test_upload_bp_inject_settings():
    return dict(
                side_menu_group_name    = "test"
                )




@test_upload_bp.route('/single-image', methods=['GET'])
def upload_image():
    return render_template("test/upload_single_image.html", 
                           page_title="Upload a Image",
                           page_url         = url_for('test_upload_bp.upload_image'),
                           upload_url       = url_for('test_upload_bp.upload_image'),
                           )
    
@test_upload_bp.route('/google-storage-permission', methods=['GET'])
def test_google_cloud_storage_permission():    
    bucket  = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
    
    return "Bucket is permitted path %s-%s" % (admin_conf.CLOUD_STORAGE_BUCKET, datetime.now()), 200
    
    
@test_upload_bp.route('/single-image', methods=['POST'])    
def upload_image_post():    
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(admin_conf.CLOUD_STORAGE_BUCKET)
