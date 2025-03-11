import eel
import sys
import logging
from dbreader import *
import socket
import time
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database readers
ar = account_reader()
tr = transaction_reader()
gr = goals_reader()

# Store start time
start_time = time.time()

@eel.expose
def check_eel_status():
    """Check if Eel is running and return status information"""
    try:
        return {
            'status': 'active',
            'python_version': sys.version,
            'eel_port': 8000,
            'websocket_connected': True,
            'uptime': time.time() - start_time,
            'process_id': os.getpid(),
            'platform': sys.platform,
            'python_path': sys.executable,
            'working_directory': os.getcwd()
        }
    except Exception as e:
        logger.error(f"Error checking Eel status: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def on_websocket_close(page, sockets):
    """Handle WebSocket closure gracefully"""
    try:
        logger.info(f"WebSocket closed for page: {page}")
        logger.info(f"Remaining active sockets: {len(sockets)}")
        
        if not sockets:
            logger.warning("All WebSockets closed - application will continue running")
            # Don't exit, let the application continue
    except Exception as e:
        logger.error(f"Error in WebSocket close handler: {e}")

def start_application():
    try:
        port = 8000
        if is_port_in_use(port):
            logger.error(f"Port {port} is already in use. Please close other instances first.")
            sys.exit(1)

        # Initialize eel with more robust options
        eel.init('web')
        
        # Configure Eel with better error handling and connection management
        eel_kwargs = {
            'host': 'localhost',
            'port': port,
            'size': (1280, 800),
            'close_callback': on_websocket_close,
            'mode': 'chrome-app',
            'app_mode': True,
            'shutdown_delay': 5.0,  # Increased delay for cleanup
            'block': False,
            'disable_cache': True,  # Prevent caching issues
            'all_interfaces': False  # More secure, only listen on localhost
        }

        # Start the application
        eel.start('index.html', **eel_kwargs)
        
        # Keep the application running with better error handling
        while True:
            try:
                eel.sleep(1.0)
            except (SystemExit, KeyboardInterrupt):
                logger.info("Received exit signal, shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                # Add small delay before retry to prevent tight loop
                time.sleep(0.1)
                continue

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        start_application()
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        sys.exit(1)

@eel.expose
def print_text(text):
    print(text)

def check_session():
    """Check if user has a valid session"""
    try:
        email = eel.get_cookie('email')()
        if not email:
            logger.warning("No email found in session")
            return None
        return email
    except Exception as e:
        logger.error(f"Error checking session: {e}")
        return None

@eel.expose
def get_monthly_averages():
    """Get monthly transaction averages"""
    try:
        email = check_session()
        if not email:
            return {'error': 'No active session', 'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}
        
        account = ar.lookup_account(email)
        if not account:
            logger.error(f"No account found for email: {email}")
            return {'error': 'Account not found', 'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}
            
        # Get transactions and calculate averages
        transactions = tr.lookup_transactions(email)
        if not transactions:
            return {'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}
            
        # Calculate averages logic here
        monthly_gains = sum(t['amount'] for t in transactions if t['amount'] > 0)
        monthly_losses = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
        monthly_net = monthly_gains - monthly_losses
        
        return {
            'avg_gains': monthly_gains,
            'avg_losses': monthly_losses,
            'avg_net': monthly_net
        }
    except Exception as e:
        logger.error(f"Error calculating monthly averages: {e}")
        return {'error': str(e), 'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0} 