from django.db import close_old_connections

class CloseOldConnectionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Before handling the request (optional, good for checking the connection)
        # close_old_connections()
        
        response = self.get_response(request)

        # 2. After handling the request (Most Common Placement)
        close_old_connections()
        
        return response