import requests
import re

s = requests.Session()

# Step 1: Get login page and extract CSRF token
r = s.get('https://MuyinzaSolomon10.pythonanywhere.com/accounts/login/')
print('Login page status:', r.status_code)

# Try multiple CSRF patterns
m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', r.text)
if not m:
    m = re.search(r'csrfmiddlewaretoken.*?value="([^"]+)"', r.text)
if not m:
    # Try from cookie
    csrf = s.cookies.get('csrftoken', '')
    print('CSRF from cookie:', csrf[:20] if csrf else 'NONE')
else:
    csrf = m.group(1)
    print('CSRF from form:', csrf[:20])

# Step 2: Login
r = s.post('https://MuyinzaSolomon10.pythonanywhere.com/accounts/login/',
    data={'csrfmiddlewaretoken': csrf, 'username': 'Group_16', 'password': 'Group_16'},
    headers={'Referer': 'https://MuyinzaSolomon10.pythonanywhere.com/accounts/login/'},
    allow_redirects=True)
print('Login result:', r.status_code)
print('Redirected to:', r.url)
print('Is dashboard?:', 'dashboard' in r.url or 'Dashboard' in r.text)

# Step 3: Check disease list
r = s.get('https://MuyinzaSolomon10.pythonanywhere.com/disease/')
print('\n--- Disease List ---')
print('Status:', r.status_code, 'Length:', len(r.text))
print('Has alerts:', 'alert-strip' in r.text)
print('Has Fall Armyworm:', 'Fall Armyworm' in r.text)

# Step 4: Check disease report
r = s.get('https://MuyinzaSolomon10.pythonanywhere.com/disease/report/')
print('\n--- Disease Report ---')
print('Status:', r.status_code, 'Length:', len(r.text))
print('Has district dropdown:', 'kampala' in r.text.lower())

# Step 5: Check market
r = s.get('https://MuyinzaSolomon10.pythonanywhere.com/market/')
print('\n--- Market ---')
print('Status:', r.status_code, 'Length:', len(r.text))
print('Has Maize:', 'Maize' in r.text)
print('Has Owino:', 'Owino' in r.text or 'St. Balikuddembe' in r.text)

# Step 6: Dashboard
r = s.get('https://MuyinzaSolomon10.pythonanywhere.com/')
print('\n--- Dashboard ---')
print('Status:', r.status_code, 'Length:', len(r.text))
print('Has alerts:', 'alert-strip' in r.text)
print('Has location badge:', 'location-badge' in r.text or 'No location' in r.text)
