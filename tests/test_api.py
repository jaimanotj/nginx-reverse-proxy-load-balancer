import pytest
import requests

class TestAPI:
    http_url = "http://localhost/"
    https_url = "https://localhost/"

    def test_http_to_https_redirection(self):
        response = requests.get(self.http_url, allow_redirects=False)
        assert response.status_code in (301, 302)
        assert response.headers['Location'] == "https://localhost/"

    def test_https_get_request(self):
        response = requests.get(self.https_url, verify=False)
        assert response.status_code == 200

        assert "Welcome to app" in response.text
    
    def test_load_balancing(self):
        backend_names = set()
        for _ in range(6):
            response = requests.get(self.https_url, verify=False)
            assert response.status_code == 200

            for app_name in ("app1", "app2", "app3"):
                if f"Welcome to {app_name}" in response.text:
                    backend_names.add(app_name)
                    break
        assert backend_names == {"app1", "app2", "app3"}