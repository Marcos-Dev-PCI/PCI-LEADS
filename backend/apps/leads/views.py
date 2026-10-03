from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lead
from .serializers import LeadSerializer
from .services import search_leads

class LeadListCreateView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class LeadSearchView(APIView):
    def post(self, request):
        query = request.data.get("query", "").strip()
        city = request.data.get("city", "").strip()

        results = search_leads(query=query, city=city)
        return Response({
            "query": query,
            "city": city,
            "results": results,
        })
