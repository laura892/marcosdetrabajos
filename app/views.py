from django.core.serializers import serialize
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Author, Message
from .serializers import AuthorSerializer, MessagesSerializer
import base64
import re


@api_view(["GET"])
def get_messages(request):
    messages = Message.objects.all().order_by("create_at")
    serializer = MessagesSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_message(request):
    username = request.data.get("username")
    print(username)
    print(request.data)

    if not username:
        return Response(
            {"error": "username is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not any([
        request.data.get('content'),
        request.data.get('image'),
        request.data.get('pdf')
    ]):
        return Response(
            {"error": "Al menos uno de los campos (content, image, pdf) debe estar presente"},
            status=status.HTTP_400_BAD_REQUEST
        )

    author, _ = Author.objects.get_or_create(name=username)

    message_data = {}

    for field in ['content', 'image', 'pdf']:
        if field in request.data:
            message_data[field] = request.data.get(field)

    serializer = MessagesSerializer(data=message_data)

    if serializer.is_valid():
        serializer.save(author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def is_base64_image(base64_string):
    """Valida si el string es una imagen en base64 válida"""
    try:
        # Patrón para validar el formato de imagen base64
        pattern = r'^data:image/[a-zA-Z]+;base64,'

        # Si tiene el prefijo de data:image
        if re.match(pattern, base64_string):
            # Remover el prefijo para obtener solo los datos
            base64_string = re.sub(pattern, '', base64_string)

        # Intentar decodificar
        decoded = base64.b64decode(base64_string)
        return True
    except Exception:
        return False


#elimar mensaje
@api_view(["DELETE"])
def delete_message(request, message_id):

    try:
        # Obtener el mensaje
        message = Message.objects.get(id=message_id)


        # Si todo está bien, eliminar el mensaje
        message.delete()
        return Response(
            {"message": "Mensaje eliminado exitosamente"},
            status=status.HTTP_200_OK
        )

    except Message.DoesNotExist:
        return Response(
            {"error": "Mensaje no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Error al eliminar el mensaje", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["PUT"])
def update_profile_picture(request, author_id):
    # Intentar obtener el autor o crearlo si no existe
    author, created = Author.objects.get_or_create(id=author_id)

    if created:
        author.name = f"Autor_{author_id}"  # Nombre por defecto, puede ser ajustado
        author.save()

    # Verificar si hay datos en el request
    if not request.data:
        return Response(
            {"error": "No data provided in the request"},
            status=status.HTTP_400_BAD_REQUEST
        )

    profile_picture_base64 = request.data.get('profile_picture')
    if not profile_picture_base64:
        return Response(
            {"error": "'profile_picture' field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar si es una imagen base64 válida
    if not is_base64_image(profile_picture_base64):
        return Response(
            {"error": "The 'profile_picture' field must contain a valid Base64 encoded image"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Actualizar directamente el campo en el modelo
        author.profile_picture = profile_picture_base64
        author.save()

        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"Error saving profile picture: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(["GET"])
def get_author_by_username(request, username):
    try:
        # Busca al autor con el nombre proporcionado
        author = Author.objects.get(name=username)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serializa los datos del autor
    serializer = AuthorSerializer(author)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_author_state(request, author_id):

    try:
        # Obtener el autor
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return Response(
            {'error': 'Autor no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Obtener el nuevo estado del request
    new_state = request.data.get('state')

    # Validar que se proporcionó el estado
    if new_state is None:
        return Response(
            {'error': 'El campo "state" es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar que el valor es booleano
    if not isinstance(new_state, bool):
        return Response(
            {'error': 'El campo "state" debe ser un valor booleano (true/false)'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Actualizar el estado
        author.state = new_state
        author.save()

        # Serializar y retornar la respuesta
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error al actualizar el estado: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )