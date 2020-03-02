from enum import Enum


class BULK_STATE(Enum):
    OPEN = 'Open'
    UPLOAD_COMPLETE = 'UploadComplete'
    ABORTED = 'Aborted'
    JOB_COMPLETE = 'JobComplete'
    FAILED = 'Failed'

BULK_STATES_DONE = [BULK_STATE.JOB_COMPLETE, BULK_STATE.ABORTED, BULK_STATE.FAILED]
BULK_STATES_FAIL = [BULK_STATE.ABORTED, BULK_STATE.FAILED]
