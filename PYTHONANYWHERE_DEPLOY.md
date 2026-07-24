# Deploying Kilimo Hub on PythonAnywhere — Step by Step

## 1. Clone Your Repository

Open the **Bash console** on PythonAnywhere (Dashboard → Bash):

```bash
cd ~
git clone https://github.com/Muyinza-Solomon-Sempangi-20/Kilimo-Farmers-Hub.git kilimo-hub
cd kilimo-hub
```

## 2. Create Virtualenv & Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Set Environment Variables

In the same Bash console:

```bash
nano ~/.bashrc
```

Add these lines at the end:

```bash
export OPENWEATHER_API_KEY="your-openweather-api-key"
export DJANGO_SECRET_KEY="replace-with-a-real-secret-key"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="your-username.pythonanywhere.com"
export SUNBIRD_API_URL="https://api.sunbird.ai/tasks/nllb_translate"
export SUNBIRD_API_KEY="your-sunbird-key"
export PYTHONANYWHERE_HOSTNAME="your-username.pythonanywhere.com"
```

Save (Ctrl+O, Enter) and exit (Ctrl+X), then:

```bash
source ~/.bashrc
```

## 4. Run Migrations & Collect Static Files

```bash
cd ~/kilimo-hub
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5. Create a Superuser (if needed)

```bash
python manage.py createsuperuser
```

## 6. Configure the Web App on PythonAnywhere

1. Go to **Dashboard → Web** → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.10+**
3. Set the **Source code** path to: `/home/your-username/kilimo-hub`

### WSGI Configuration

Click the **WSGI configuration file** link (near the top of the Web page).
Delete everything and paste:

```python
"""
WSGI config for Kilimo Hub on PythonAnywhere.
"""
import os
import sys

project_home = os.path.expanduser('~/kilimo-hub')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kilimo_hub.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Virtualenv

In the **Virtualenv** section, enter:
```
/home/your-username/kilimo-hub/venv
```

### Static Files

Add a **Static files** mapping:
| URL | Directory |
|---|---|
| `/static/` | `/home/your-username/kilimo-hub/staticfiles` |
| `/media/` | `/home/your-username/kilimo-hub/media` |

### WSGI Configuration File Location

The WSGI file needs to be at the path PythonAnywhere expects.
In the Bash console:

```bash
cp ~/kilimo-hub/pythonanywhere_wsgi.py ~/pythonanywhere_wsgi.py
```

Then in the Web app settings, set the WSGI file path to:
```
/home/your-username/pythonanywhere_wsgi.py
```

## 7. Reload the App

Click the big green **Reload** button on the Web page.

## 8. Test

Visit: `https://your-username.pythonanywhere.com`

---

## Troubleshooting

- **500 error**: Check the **Error log** on the Web page — usually an env var is missing
- **Static files not loading**: Re-run `python manage.py collectstatic --noinput`
- **Database errors**: Make sure `python manage.py migrate` ran successfully
