import os
import json
import tempfile
import sys
import logging

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    AWS Lambda handler for GabeGardener.
    
    This function creates a temporary configuration file from environment variables
    and runs the GabeGardener main function.
    
    Args:
        event: AWS Lambda event data
        context: AWS Lambda context
        
    Returns:
        dict: Response with status code and message
    """
    try:
        # Disable dashboard for Lambda
        os.environ['GABEGARDENER_DASHBOARD'] = 'false'
        
        # Create temp config file from environment variable if provided
        config_json = os.environ.get('GABEGARDENER_CONFIG_JSON')
        if config_json:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(config_json)
                temp_config_path = f.name
                os.environ['GABEGARDENER_CONFIG'] = temp_config_path
                logger.info(f"Created temporary config file at {temp_config_path}")
        
        # Import main only after setting up environment
        from main import main
        
        # Run GabeGardener
        main()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "GabeGardener started successfully"
            })
        }
    except Exception as e:
        logger.error(f"Error running GabeGardener: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error: {str(e)}"
            })
        }
