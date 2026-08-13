import requests
import time
import sys


def wait_for(url, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}")

def main():
    base = 'http://127.0.0.1:8000'
    endpoints = ['/kpis', '/orders', '/monthly_trends', '/top_products', '/revenue_by_location']

    print('Checking backend endpoints...')
    for ep in endpoints:
        url = base + ep
        try:
            r = wait_for(url, timeout=15)
            print(ep, 'OK', 'len=', len(r.content))
        except Exception as e:
            print(ep, 'FAILED', e)
            return 2

    # Check Streamlit UI
    st_url = 'http://127.0.0.1:8501'
    print('Checking Streamlit UI...')
    try:
        r = wait_for(st_url, timeout=20)
        print('Streamlit OK', 'len=', len(r.content))
    except Exception as e:
        print('Streamlit FAILED', e)
        return 2

    print('SMOKE TEST PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
