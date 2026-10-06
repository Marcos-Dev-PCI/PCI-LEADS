from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lead
from .serializers import LeadSerializer
from .services import search_leads

from rest_framework.permissions import IsAuthenticated # Linha adicionada

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

class UserMeView(APIView):
    # Esta linha obriga o robô do DRF a verificar se quem bateu na porta está autenticado.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Quando o usuário passa um token válido, o Django automaticamente descobre
        # quem ele é e joga os dados dele dentro da variável 'request.user'
        user = request.user
        
        # Devolvemos os dados mastigados em formato de texto estruturado (JSON) para o React
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })