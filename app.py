from fastapi import FastAPI, HTTPException
from typing import List
import requests
from pydantic import BaseModel

app = FastAPI()

# PowerDNS API configuration (replace with your server details)
PDNS_API_URL = "http://localhost:8081/api/v1"
PDNS_API_KEY = "hello"

class DNSRecordCreate(BaseModel):
    name: str
    type: str
    content: str
    ttl: int

class DNSRecord(BaseModel):
    id: int
    name: str
    type: str
    content: str
    ttl: int

def make_pdns_api_request(method, path, data=None):
    try:
        headers = {"X-API-Key": PDNS_API_KEY}
        url = f"{PDNS_API_URL}{path}"
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error connecting to PowerDNS")

@app.get("/check_pdns_connection")
def check_pdns_connection():
    try:
        headers = {"X-API-Key": PDNS_API_KEY}
        response = requests.get(f"{PDNS_API_URL}/servers", headers=headers)
        response.raise_for_status()
        return {"message": "Connected to PowerDNS API"}
    except requests.exceptions.RequestException as e:
        return {"message": f"Failed to connect to PowerDNS API: {str(e)}"}

@app.post("/api/v1/", response_model=DNSRecord)
def create_dns_record(record: DNSRecordCreate):
    pdns_record = {
        "name": record.name,
        "type": record.type,
        "content": record.content,
        "ttl": record.ttl
    }
    response = make_pdns_api_request("POST", "/servers/localhost/zones", data=pdns_record)
    return response

@app.get("/api/v1/", response_model=List[DNSRecord])
def get_dns_records():
    response = make_pdns_api_request("GET", "/servers/localhost/zones")
    return response

@app.put("/api/v1/{record_id}", response_model=DNSRecord)
def update_dns_record(record_id: int, record: DNSRecordCreate):
    pdns_record = {
        "name": record.name,
        "type": record.type,
        "content": record.content,
        "ttl": record.ttl
    }
    response = make_pdns_api_request("PUT", f"/servers/localhost/zones/test.com/{record_id}", data=pdns_record)
    return response

@app.delete("/api/v1/{record_id}")
def delete_dns_record(record_id: int):
    response = make_pdns_api_request("DELETE", f"/servers/localhost/zones/test.com/{record_id}")
    return {"message": "Record deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
