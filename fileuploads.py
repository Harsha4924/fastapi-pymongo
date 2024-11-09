from bson import ObjectId
from fastapi import FastAPI, File, Response, UploadFile, status, HTTPException, Depends, APIRouter
from fastapi.responses import FileResponse
from models import Users,Login
from config import get_product_collection
from pymongo.collection import Collection
import os



import oauth2

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post('/upload/{product_id}')
async def upload_file(product_id: str, file: UploadFile = File(...), products_collection: Collection = Depends(get_product_collection), user_id: str = Depends(oauth2.get_current_user)):
    try:
        
        product_objectid = ObjectId(product_id)
        product = products_collection.find_one({"_id": product_objectid})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        print(product.get('created_by'))
        print(user_id)
        
        if product.get('created_by') != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to upload the file")
    
        
        file_extension = os.path.splitext(file.filename)[1]

        file_path = os.path.join(UPLOAD_DIR, f"{product_id}_{product.get('name')}{file_extension}")
        # file_path = os.path.join(UPLOAD_DIR, f"{product_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        
        products_collection.update_one(
            {"_id": product_objectid},
            {"$set": {"image": file_path}}
        )
        
        return {"status": "success", "file_path": file_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    




@router.get("/download/{product_id}/{file_name}")
async def download_file(product_id: str, file_name: str, user_id: str = Depends(oauth2.get_current_user)):
    try:
        print(product_id)
        print(file_name)
        
        
        base_name, _ = os.path.splitext(file_name)
        
        
        file_found = False
        for file in os.listdir(UPLOAD_DIR):
            if file.startswith(f"{product_id}_{base_name}"):
                file_path = os.path.join(UPLOAD_DIR, file)
                file_found = True
                break
        
        if not file_found:
            raise HTTPException(status_code=404, detail="File not found")
        
        
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while downloading the file: {str(e)}")


    


@router.get("/list-files")
async def list_files(user_id: str = Depends(oauth2.get_current_user)):
    try:
        files = os.listdir(UPLOAD_DIR)
        return {"files": files}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error listing files")
    

