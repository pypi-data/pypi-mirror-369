django-chelseruA Django package for real-time chat, SMS authentication, and sending SMS messages with Iranian providers.AuthorSobhan Bahman Rashnu🚀 Features📱 SMS Authentication (OTP): Secure user authentication using one-time passwords sent via SMS.💬 Real-time Chat: WebSocket-based real-time messaging functionality.✉️ SMS Services: Send SMS messages through popular Iranian SMS providers.⚙️ InstallationInstall the package using pip:pip install django-chelseru
Add 'drfchelseru' to your INSTALLED_APPS in settings.py:INSTALLED_APPS = [
    ...
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'drfchelseru',
    ...
]
🛠️ ConfigurationTo configure the package, add the DJANGO_CHELSERU dictionary to your settings.py file. This dictionary allows you to customize authentication and SMS settings.# settings.py

DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD'           : 'OTP',                        # Supported methods: OTP, PASSWD
        'AUTH_SERVICE'          : 'rest_framework_simplejwt',   # Supported services: rest_framework_simplejwt
        'OPTIONS': {
            'OTP_LENGTH'            : 8,    # Default: 8
            'OTP_EXPIRE_PER_MINUTES': 4,    # Default: 4
            'OTP_SMS_TEMPLATE_ID'   : 1,    # SMS template ID for OTP
        }
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',  # Supported providers: PARSIAN_WEBCO_IR, MELI_PAYAMAK_COM, KAVENEGAR_COM
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY'  : 'YOUR_PARSIAN_WEBCO_API_KEY',
            'MELI_PAYAMAK_COM_USERNAME' : 'YOUR_MELI_PAYAMAK_USERNAME',
            'MELI_PAYAMAK_COM_PASSWORD' : 'YOUR_MELI_PAYAMAK_PASSWORD',
            'MELI_PAYAMAK_COM_FROM'     : 'YOUR_MELI_PAYAMAK_FROM_NUMBER',
            'KAVENEGAR_COM_API_KEY'     : 'YOUR_KAVENEGAR_API_KEY',
            'KAVENEGAR_COM_FROM'        : 'YOUR_KAVENEGAR_FROM_NUMBER',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            ...
        }
    }
}
AUTH_METHOD: Specifies the authentication method. Use 'OTP' for SMS-based authentication.OTP_LENGTH: The length of the one-time password.OTP_EXPIRE_PER_MINUTES: The expiration time for the OTP in minutes.OTP_SMS_TEMPLATE_ID: The template ID of the SMS message used for sending the OTP.SMS_SERVICE: Select your desired SMS provider.SETTINGS: Provide the necessary credentials for your chosen SMS provider.TEMPLATES: Define your SMS template IDs.🔌 EndpointsAdd the following URLs to your urls.py file to use the package's functionality.# urls.py

from django.urls import path, include

urlpatterns = [
    ...
    path('api/', include('drfchelseru.urls')),
    ...
]
The package provides the following API endpoints:EndpointDescriptionMethod/api/otp/send/Sends an OTP to the specified phone number.POST/api/authenticate/Authenticates a user with the received OTP.POST/api/sessions/Lists and manages active user sessions.GET/api/message/send/Sends an SMS message using the configured provider.POSTEndpoint Usage1. OTP Code Sending (/api/otp/send/)Method: POSTDescription: Sends a one-time password to the user's mobile number.Required Parameters:ParameterTypeDescriptionExamplemobile_numberstrThe user's mobile number.09121234567Responses:HTTP 200 OK: OTP code sent successfully.{"details": "The OTP code was sent correctly."}
HTTP 400 BAD REQUEST: Invalid mobile_number format.HTTP 409 CONFLICT: An OTP has already been sent and is still valid.{"details": "An OTP code has already been sent. Please wait X seconds before trying again."}
HTTP 500 INTERNAL SERVER ERROR: An issue occurred on the server.2. Authentication (/api/authenticate/)Method: POSTDescription: Authenticates the user with the provided OTP. On success, it returns JWT tokens (access and refresh).Required Parameters:ParameterTypeDescriptionExamplemobile_numberstrThe user's mobile number.09121234567codestrThe OTP received via SMS.12345678groupintOptional: A group identifier for the user.1Responses:HTTP 200 OK: Authentication successful.{
  "access": "...",
  "refresh": "..."
}
HTTP 401 UNAUTHORIZED: Invalid or expired OTP code.{"error": "The code sent to this mobile number was not found."}
HTTP 400 BAD REQUEST: Missing required parameters or invalid format.HTTP 500 INTERNAL SERVER ERROR: An issue occurred on the server.3. Message Sending (/api/message/send/)Method: POSTDescription: Sends a custom SMS message using the configured provider.Required Parameters:ParameterTypeDescriptionExamplemobile_numberstrThe recipient's mobile number.09121234567message_textstrThe text of the message. (Max 290 chars)Hello, World!template_idintRequired for some providers (e.g., Parsian).1Responses:HTTP 200 OK: Message sent successfully.{"details": "The Message was sent correctly."}
HTTP 400 BAD REQUEST: Validation errors for parameters.HTTP 401 UNAUTHORIZED: Authentication failed.HTTP 500 INTERNAL SERVER ERROR: An issue occurred on the server.HTTP 502 BAD GATEWAY: SMS provider returned an error.4. Session List (/api/sessions/)Method: GETDescription: Lists all active user sessions. Requires authentication (IsAuthenticated).Required Headers:HeaderValueAuthorizationBearer <your_access_token>💡 ModelsThis package includes a Session model for managing active user sessions. You can access and manage these sessions through the /api/sessions/ endpoint.