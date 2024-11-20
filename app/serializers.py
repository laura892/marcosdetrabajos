from rest_framework import serializers
import base64
from rest_framework.exceptions import ValidationError
from .models import Author, Message


def validate_base64(value, field_name):
    if not value:
        return value

    try:
        if field_name == 'image' and not value.startswith('data:image/'):
            raise ValidationError(f"El campo '{field_name}' debe tener un formato válido data:image/")
        elif field_name == 'pdf' and not value.startswith('data:application/pdf'):
            raise ValidationError(f"El campo '{field_name}' debe tener un formato válido data:application/pdf")

        base64_part = value.split(',')[1]
        base64.b64decode(base64_part, validate=True)
        return value
    except IndexError:
        raise ValidationError(f"El campo '{field_name}' no tiene el formato correcto")
    except Exception as e:
        raise ValidationError(f"El campo '{field_name}' no contiene un Base64 válido: {str(e)}")


class AuthorSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Author
        fields = '__all__'

    def validate_profile_picture(self, value):
        return validate_base64(value, 'profile_picture')


class MessagesSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    content = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    image = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    pdf = serializers.CharField(allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Message
        fields = '__all__'

    def validate_image(self, value):
        return validate_base64(value, 'image')

    def validate_pdf(self, value):
        return validate_base64(value, 'pdf')

    def validate(self, data):
        if not any([
            data.get('content'),
            data.get('image'),
            data.get('pdf')
        ]):
            raise ValidationError("Al menos uno de los campos (content, image, pdf) debe estar presente")
        return data