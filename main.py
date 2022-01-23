import os
import fastapi
from fastapi import HTTPException
import random
import uvicorn
from enum import Enum
from decouple import config
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
app = fastapi.FastAPI()

client = AsyncIOMotorClient("mongodb+srv://teleruby:ilovelostinspace@cluster0.ck4qf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.teleruby
collection = db.users


@app.get("/verify")
async def verify(key: str = None, machine_code: str = None, product: str = None,version:str = None):
    if (not key and not machine_code and not version) or (not key or not machine_code or not version):
        return {"error": True, "message": "You must provide both key and machine_code"}
    if(version == "2.0"):
        return {"error": True, "message": "There is an update available"}
    else:
        keys = await collection.find_one({"_id": "keys"})
        if keys is None:
            return {"error": True, "message": "Database error"}
        if key in keys.get("keys"):
            result = await collection.find_one({"key": key})
            if (result.get("machine_code") is None) and (product == result.get("product")):
                await collection.update_one({"key": key}, {"$push": {"machine_code": machine_code}}, upsert=True)
                result = await collection.find_one({"key": key})
                return {"error": False, "message": "Successfully Registered"}
            if (machine_code in result.get("machine_code")) and (product == result.get("product")):
                return {"error": False, "message": "Success"}
            elif (result.get("machine_code") not in result.get("machine_code") ) and (len(result.get("machine_code")) < result.get("no_of_machines")) and (product == result.get("product")):
                await collection.update_one({"key": key}, {"$push": {"machine_code": machine_code}}, upsert=True)
                return {"error": False, "message": "Successfully registered the device."}
            elif product != result.get("product"):
                return {"error": True, "message": "Product key didn't match with the product bought!"}
            else:
                return {"error": True, "message": "No of devices limit exceeded."}
        else:
            return {"error": True, "message": "Invalid license key"}


@app.get("/login")
async def login(username:str=None,key:str=None,version:str=None):
    if(not username and not key and not version):
        return {"error": True, "message": "Please Enter Username and Password"}
    else:
        keys = await collection.find_one({"_id": "keys"})
        if keys is None:
            return {"error": True, "message": "Database error"}
        if key in keys.get("keys"):
            result = await collection.find_one({"key": key})
            if(result.get("username") == username):
                return {"error":False,"message":result}
            else:
                return {"error": True, "message": "Username Not Match"}