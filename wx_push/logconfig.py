import os

logfilename = "/mnt/data/monitorserver/logs/django/wx_push_hb.log"

if 'nt' in os.name:
    logfilename = "D://monitor_django.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s \npath=%(pathname)s line=%(lineno)s \n%(message)s \n'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': logfilename,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'ERROR',
        },
        # 请求相关的信息，5XX作为ERROR信息，4XX作为WARNING信息
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 每一个app对应一个looger配置
        'app': {
            'handlers': ['console' , 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}