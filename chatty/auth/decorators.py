from functools import wraps


def login_required(handler):
    '''
    This function adds 'login_required' property to provided 'handler',
    which indicates that only authorized user can access handler.
    '''
    handler.login_required = True
    return handler

def anonymous_required(handler):
    '''
    Marks handler as anonymous-only.
    '''
    handler.anonymous_required = True
    return handler
