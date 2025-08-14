# WebCase 2factor API

Package to create general API for 2factor checkers.

## Installation

```sh
pip install wc-django-2factor
```

In `settings.py`:

```python
INSTALLED_APPS += [
  'wcd_2factor',
]

WCD_2FACTOR = {
  # Available ways to send confirmation messages.
  'SENDERS': {
    'default': {
      'verbose_name': 'Phone sender',
      # Your own sender backend implementation.
      'backend': 'some.method.path.to.Backend',
      # Any options that that backend will receive(if it requires).
      'options': {
        'SOME: 'OPTION',
      },
    },
  },
  # Default sender key that will be used by default(if None specified).
  'DEFAULT_SENDER': 'default',
  # Generator function that will generate confirmation code.
  'CONFIRM_CODE_GENERATOR': 'wcd_2factor.services.confirmer.make_confirmation_code',
  # Since [0.1.1]. Show code, sended to backend straight in code request response. That done for faster debugging during development.
  'DEBUG_CODE_RESPONSE': False,
}

# All root options could also be provided as standalone ones(for overriding, etc.):
WCD_2FACTOR_DEFAULT_SENDER = 'default'
```

### Services

#### Confirmer

Service for confirmation state management.

```python
from wcd_2factor.services import confirmer

# Create new confirmation request.
state = confirmer.make_confirmation(meta={'any': 'json'})

print(state.is_confirmed)
# > False

# Check whether the confirmation request is confirmed.
state, confirmed = confirmer.check(state.id)

print(confirmed)
# > False

# Confirm confirmation request in two ways:
# Manually if you sure that all requirements had been accomplished.
state.confirm()
# or
# By running confirmation logic from service:
state, confirmed = confirmer.confirm(state.id, 'confirmation-code-provided-by-user')

# ...

# In some place in your application yop may "use" confirmation request.
# For example to prove that provided phone number is that one that user owns.
# It's one time usage, so it will not be accessible to use anymore elsewhere.
used = confirmer.use(state)

if not used:
  raise Exception('This state is not confirmed yet.')
```

#### Sender

Sender is a service that sends message with generated code.

```python
from wcd_2factor.services import sender

# It has only one method: `.send`.
sender.send(
  'sender-backend-key',
  'email.or.a.phone.number.etc@email.com',
  # Request confirmation state object.
  state,
  # Additional context if required.
  context={}
)
```

### Sender backend development

Sender backend is a callable that takes confirmation options and returns another callable that can handle data sending.

So it could look like that:

```python
def send(
  # Key for sender in configuration.
  name: str,
  options,
  verbose_name=None,
  **kwargs
):
  # Do something with confirmation state and confirmation options.
  # ...
  # Return callable that will handle data sending.
  def send(token, state, context):
    return send_somewhere(f'Here is yor code: {state.code}')

  return send
```

There are two helper classes for a little bit easier backend development:

```python
from wcd_2factor.sender import SenderBackend, FunctionalSenderBackend


# You may create a simple class as a backend.
class CustomBackend(SenderBackend):
  def send(self, token, state, context: dict = {}):
    return send_somewhere(f'Here is yor code: {state.code}')


# Or just made a function(it also will be resolved into a class-return wrapper):
@FunctionalSenderBackend.from_callable
def custom_callable_backend(
  token, state, name, context={}, options={}, **self.kwargs
):
  send_phone_confirmation_task.delay(token, state.code)
```

## Contrib

### DRF

There are ready for use frontend for django rest framework.

In `urls.py`:

```python
from wcd_2factor.contrib.drf.views import make_urlpatterns as twofactor_make_urlpatterns

urlpatters = [
  ...
  path(
    'api/v1/auth/2factor/',
    include((twofactor_make_urlpatterns(), 'wcd_2factor'),
    namespace='2factor')
  ),
]
```

There will be 2 views:
- `request-confirmation/` - To request confirmation code to your device.
- `confirm/` - To confirm that two factor request.
