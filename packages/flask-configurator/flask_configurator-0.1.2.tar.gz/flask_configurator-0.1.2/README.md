# Flask-Configurator

Env and file based configuration for Flask

## Installation

    pip install flask-configurator

## Usage

```python
from flask import Flask
from flask_configurator import Configurator

app = Flask(__name__)
Configurator(app)
```

By default this will load configuration from:

- environment variables with the *FLASK_* prefix
- .env (only variables with the *FLASK_* prefix)
- .env.ENV (only variables with the *FLASK_* prefix)
- config.yml
- config.ENV.yml

Where ENV is the environment defined as defined by:

1. *development* if app.debug, *production* otherwise
2. `FLASK_ENV` environment variable
2. `ENV` key from any loaded file

## Options

```python
Configurator(
    app,
    default_file="config.yml", # default configuration file to load from (set to None to disable)
    env_prefix="FLASK", # environment variable prefix
    default_env="production", # default env name (None for default, False to not set any env)
)
```

Supported configuration formats: *yml*, *json*, *toml*.

## Manual loading

Rather than going through an extension, you can use our custom Config class.

```python
from flask_configurator import Config
config = Config()
config.load()
print(config["KEY"])
app.config.update(config)
```

Use it as your flask config class:

```python
from flask import Flask
from flask_configurator import Config

class CustomFlask(Flask):
    config_class = Config

app = CustomFlask(__name__)
app.config.load()
```