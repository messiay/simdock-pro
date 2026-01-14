import requests
try:
    resp = requests.post('http://localhost:8000/projects/', json={'name': 'demo_session', 'description': 'Manual recovery'})
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print(e)
