from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Event.objects.all()
        status_param = self.request.query_params.get('status')
        venue_param = self.request.query_params.get('venue')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if venue_param:
            queryset = queryset.filter(venue__icontains=venue_param)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if Event.objects.filter(created_by=user, status__in=['upcoming', 'ongoing']).exists():
            raise serializers.ValidationError('You already have an active event. Complete or cancel it first.')
        serializer.save(created_by=user)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Reservation.objects.filter(user=self.request.user)
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.user != request.user:
            return Response({'error': 'Not your reservation.'}, status=403)
        if reservation.status == 'cancelled':
            return Response({'error': 'Already cancelled.'}, status=400)
        reservation.event.available_seats += reservation.seats_reserved
        reservation.event.save()
        reservation.status = 'cancelled'
        reservation.save()
        return Response(self.get_serializer(reservation).data)
