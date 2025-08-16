import json
from datetime import datetime

# Global list to store Lambda-supported regions
lambda_regions = []

def get_lambda_regions(session, regions):
    """
    Appends only those regions to the global 'lambda_regions' list which have Lambda functions.
    No return value.
    """
    for region in regions:
        try:
            lambda_client = session.client('lambda', region_name=region)
            response = lambda_client.list_functions()
            if len(response.get('Functions', [])) > 0:
                lambda_regions.append(region)
        except Exception as e:
            print(f"Error checking Lambda support in region {region}: {str(e)}")
            continue


def fetch_lambda_inventory(session, regions):
    try:
        # Step 1: Fill the lambda_regions list
        get_lambda_regions(session, regions)

        if not lambda_regions:
            print("No Lambda functions found in any region.")
            return []

        all_lambdas = []

        # Step 2: Fetch Lambda inventory only from relevant regions
        for region in lambda_regions:
            print(f"Fetching Lambda inventory from region: {region}")
            lambda_client = session.client('lambda', region_name=region)
            response = lambda_client.list_functions()

            for function in response.get('Functions', []):
                # If VPC ID is None, the function is publicly accessible
                is_public = function.get('VpcConfig', {}).get('VpcId') is None

                # Generate Direct Link to Lambda Console
                account_id = function.get('FunctionArn').split(":")[4]
                direct_link = f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{function.get('FunctionName')}?tab=configuration"
                
                 # Convert creation_timestamp to ISO format if it's a string
                creation_timestamp = function.get('LastModified')
                if isinstance(creation_timestamp, str):
                    # Parse string to datetime
                    creation_timestamp = datetime.strptime(creation_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')

                # Build Lambda resource structure
                lambda_resource = {
                    "provider": "AWS",
                    "account_id": account_id,
                    "resource_id": function.get('FunctionArn'),
                    "resource_name": function.get('FunctionName'),
                    "primary_category": "Compute",
                    "secondary_category": "AWS Lambda",
                    "region": region,
                    "tag": function.get('Tags', {}),
                    "is_public": is_public,
                    "creation_timestamp": creation_timestamp,
                    "asset_details": function,
                    "arn_id": function.get('FunctionArn'),
                    "direct_link": direct_link
                }
                all_lambdas.append(lambda_resource)

        return all_lambdas

    except Exception as e:
        print(f"Error fetching Lambda inventory: {str(e)}")
        return []