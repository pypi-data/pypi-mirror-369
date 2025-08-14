from django.dispatch import Signal


__all__ = 'code_sent', 'code_confirmed',


# Arguments: "user_id", "code"
code_sent: Signal = Signal()

# Arguments: "user_id", "code"
code_confirmed: Signal = Signal()
