"""
Test Supabase Connection
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

print("=" * 50)
print("Testing Supabase Connection")
print("=" * 50)
print(f"URL: {url}")
print(f"Key: {key[:30]}...")

if not url or not key:
    print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_KEY")
    exit(1)

try:
    supabase = create_client(url, key)
    result = supabase.table('users').select('*').limit(1).execute()
    print(f"✅ Connection successful! Found {len(result.data)} users")
    print(result.data)
except Exception as e:
    print(f"❌ Connection failed: {e}")