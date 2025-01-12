from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import get_route_info


@api_view(['GET'])
def get_route(request):
    start = request.query_params.get('start')
    finish = request.query_params.get('finish')

    if not start or not finish:
        return Response({"error": "Please provide both start and finish locations"}, status=400)

    # Delegate the logic to the service layer
    route_data = get_route_info(start, finish)
    
    if "error" in route_data:
        return Response(route_data, status=route_data.get("status", 500))
    
    return Response(route_data)
