from datetime import datetime, timedelta
import uuid

from googleapiclient import discovery
import httplib2
from oauth2client.appengine import AppAssertionCredentials
from webapp2 import RequestHandler
from google.appengine.api import taskqueue

from models.backup.datastore_admin_operation import _AE_DatastoreAdmin_Operation as DbOperation

_BIGQUERY_OAUTH_SCOPE = 'https://www.googleapis.com/auth/bigquery'
_ANALYTICS_APP_DATASET = 'automation-demo'
_service = None


class LoadDataHandler(RequestHandler):
    def get(self):

        q = taskqueue.Queue('backupqueue')
        op = DbOperation.query(DbOperation.status == 'Active').get()
        if not op:
            # All is okay
            load_to_bigquery()
        else:
            # Data is not uploaded to Google Cloud yet. Should wait 5 minutes
            current_time = datetime.today()
            time_to_launch = current_time + timedelta(minutes=1)
            task = taskqueue.Task(url='/cron/load_backup', method='GET', countdown=time_to_launch)
            q.add(task)


def load_to_bigquery():
    bigquery = get_service()
    project_id = 'automation-demo'
    dataset_id = 'backup_dataset'
    url_dict = {
        'client_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.Client.backup_info',
        'client_push_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.ClientPushSending.backup_info',
        'client_session_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.ClientSession.backup_info',
        'geo_push_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.GeoPush.backup_info',
        'order_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.Order.backup_info',
        'share_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.Share.backup_info',
        'venue_backup': 'gs://automation-demo.appspot.com/ahFzfmF1dG9tYXRpb24tZGVtb3JBCxIcX0FFX0RhdGFzdG9yZUFkbWluX09wZXJhdGlvbhiBm-4CDAsSFl9BRV9CYWNrdXBfSW5mb3JtYXRpb24YAQw.Venue.backup_info'
    }
    for key, value in url_dict.iteritems():
        load_table(bigquery=bigquery, project_id=project_id, dataset_id=dataset_id, table_name=key,
                   source_path=value)


def load_table(bigquery, project_id, dataset_id, table_name,
               source_path, num_retries=5):
    job_data = {
        'jobReference': {
            'projectId': project_id,
            'job_id': str(uuid.uuid4())
        },
        'configuration': {
            'load': {
                'sourceFormat': 'DATASTORE_BACKUP',
                'sourceUris': [source_path],
                'destinationTable': {
                    'projectId': project_id,
                    'datasetId': dataset_id,
                    'tableId': table_name
                }
            }
        }
    }

    return bigquery.jobs().insert(
        projectId=project_id,
        body=job_data).execute(num_retries=num_retries)


def get_service():
    global _service
    if not _service:
        credentials = AppAssertionCredentials(scope=_BIGQUERY_OAUTH_SCOPE)
        http = credentials.authorize(httplib2.Http())
        _service = discovery.build('bigquery', 'v2', http=http)
    return _service
