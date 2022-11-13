from rq import Queue

class CustomQueue(Queue):
    def __init__(self, name='default', default_timeout=None, connection=None, is_async=True, job_class=None, serializer=None, **kwargs):
        name='golf'
        super().__init__(name, default_timeout, connection, is_async, job_class, serializer, **kwargs)



