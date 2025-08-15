from datetime import datetime, timezone
import json

def bytesToJson(bytesData: bytes):
    preData = bytesData.decode("utf-8")

    jsonData = json.loads(preData)

    return jsonData

def convertToUTC(dtObj: datetime) -> datetime:
    """
    Ensures the input datetime is UTC-aware.
    
    Parameters:
        dt (datetime): The datetime object to process.
        
    Returns:
        datetime: A UTC-aware datetime object.
    """
    if dtObj.tzinfo is None:  # If naive, assume it's already in UTC and make it aware
        return dtObj.replace(tzinfo=timezone.utc)
    return dtObj.astimezone(timezone.utc)  # Convert to UTC if not already