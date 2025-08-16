import boto3

def get_aws_regions(session):
    # Create a session with the provided credentials
    # Initialize EC2 resource
    try:
        ec2_client = session.client('ec2', region_name='us-east-1')  # Use a default region to call describe_regions
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        return regions
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []