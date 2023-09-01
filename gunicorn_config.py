bind = "0.0.0.0:8080"
workers = 2

forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
