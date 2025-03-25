class ClientVO:
    def __init__(self, id=None, username=None, password=None, email=None, mobile_no=None, city=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.mobile_no = mobile_no
        self.city = city

class ServiceProviderVO:
    def __init__(self, s_id=None, s_name=None, s_email=None, s_pass=None, s_skills=None, s_mobile=None, s_city=None):
        self.s_id = s_id
        self.s_name = s_name
        self.s_email = s_email
        self.s_pass = s_pass
        self.s_skills = s_skills
        self.s_mobile = s_mobile
        self.s_city = s_city

class AdminVO:
    def __init__(self, id=None, name=None, email=None, password=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

class AppointmentVO:
    def __init__(self, id=None, client_id=None, service_provider_id=None, service_date=None, status=None):
        self.id = id
        self.client_id = client_id
        self.service_provider_id = service_provider_id
        self.service_date = service_date
        self.status = status 