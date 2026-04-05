import stripe
import secrets

# Generate a secure random string for the webhook secret
webhook_secret = 'whsec_' + secrets.token_hex(24)

print("Generated Stripe webhook secret:")
print(webhook_secret)
print("\nUpdate your config.py with this webhook secret.")
print("Add this line to your config.py:")
print(f"    STRIPE_WEBHOOK_SECRET = '{webhook_secret}'")
