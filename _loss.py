from sklearn._loss import *  # noqa: F401,F403
from sklearn._loss import _loss as _compiled_loss

globals().update({name: getattr(_compiled_loss, name) for name in dir(_compiled_loss)})