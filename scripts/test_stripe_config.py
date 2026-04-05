import stripe
import os
import sys
sys.path.append('d:\\mypart\\Ghoori.com')
from config import Config

def test_stripe_configuration():
    """Test the Stripe configuration to ensure API keys are valid."""
    try:
        # Set the API key
        stripe.api_key = Config.STRIPE_SECRET_KEY
        
        # Try to retrieve account information to verify the API key works
        account = stripe.Account.retrieve()
        
        print("✓ Stripe configuration test successful!")
        print(f"Connected to Stripe account: {account.id}")
        print(f"Account email: {account.email}")
        print("\nStripe configuration in config.py:")
        print(f"  STRIPE_PUBLISHABLE_KEY: {Config.STRIPE_PUBLISHABLE_KEY[:10]}...{Config.STRIPE_PUBLISHABLE_KEY[-4:]}")
        print(f"  STRIPE_SECRET_KEY: {Config.STRIPE_SECRET_KEY[:10]}...{Config.STRIPE_SECRET_KEY[-4:]}")
        print(f"  STRIPE_WEBHOOK_SECRET: {Config.STRIPE_WEBHOOK_SECRET[:10]}...{Config.STRIPE_WEBHOOK_SECRET[-4:]}")
        
        return True
    except stripe.error.AuthenticationError:
        print("✗ Authentication failed: Invalid API key")
        return False
    except Exception as e:
        print(f"✗ Error testing Stripe configuration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Stripe configuration...")
    test_stripe_configuration()
