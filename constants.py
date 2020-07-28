import logging
import os

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
