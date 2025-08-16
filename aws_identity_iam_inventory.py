import json
from datetime import datetime, timezone

def fetch_iam_inventory(session):
    try:
        iam_client = session.client('iam')
        all_iam_users = []
        password_policy = iam_client.get_account_password_policy()
        # Fetch all IAM users
        response = iam_client.list_users()
        for user in response.get('Users', []):
            # Generate Direct Link to IAM Console
            account_id = user.get('Arn').split(":")[4]
            direct_link = f"https://console.aws.amazon.com/iam/home?region=us-east-1#/users/{user.get('UserName')}"

            # Parse the creation date to ISO format with timezone info
            creation_timestamp = user.get('CreateDate')
            if isinstance(creation_timestamp, str):
                    # Parse string to datetime
                    creation_timestamp = datetime.strptime(creation_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')

             # Fetch tags for the user
            tags_response = iam_client.list_user_tags(UserName=user.get('UserName'))
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
            asset_details = user.copy()
            asset_details['password_policy'] = password_policy['PasswordPolicy']


            # Build IAM resource structure
            iam_resource = {
                "provider": "AWS",
                "account_id": account_id,
                "resource_id": user.get('UserId'),
                "resource_name": user.get('UserName'),
                "primary_category": "Identity",
                "secondary_category": "IAM",
                "region": "Global",
                "tag": tags,
                "is_public": None,
                "creation_timestamp": creation_timestamp,
                "asset_details": asset_details ,
                "arn_id": user.get('Arn'),
                "direct_link": direct_link
            }
            all_iam_users.append(iam_resource)

        return all_iam_users

    except Exception as e:
        print(f"Error fetching IAM inventory: {str(e)}")
        return []
