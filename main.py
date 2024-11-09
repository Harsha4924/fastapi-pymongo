from bson import ObjectId
from fastapi import FastAPI,APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from config import get_product_collection
import fileuploads
from logg_middle import LoggingMiddleware
from schemas import all_tasks
from models import Products, ProductUpdate
from pymongo.collection import Collection
import user
import oauth2
from rate_limit import RateLimitMiddleware


app = FastAPI()
router = APIRouter()

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

@router.get('/products')
async def get_all_products(page: int = 1,page_size: int = 10,products_collection: Collection = Depends(get_product_collection),current_user: int = Depends(oauth2.get_current_user)):

    skip = (page - 1) * page_size
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Page and page_size must be greater than 0.")
    products = list(products_collection.find().skip(skip).limit(page_size))
    print(products)
    print(all_tasks(products))

    total_products = products_collection.count_documents({})
    total_pages = (total_products + page_size - 1) // page_size  # Calculate total pages

    return {
        "status": "success",
        "total_products": total_products,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "products": all_tasks(products)
    }



@router.get('/one_product/{id}')
async def get_one_product(id: str, products_collection: Collection = Depends(get_product_collection)):
    try:
        
        one_product = products_collection.find_one(
            {'_id': ObjectId(id)},
            {'name': 1, 'description': 1, 'stock': 1, 'price': 1}
        )
        
        if not one_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        
        one_product['_id'] = str(one_product['_id'])
        
        return {"status": "success", "product": one_product}
    
    except Exception as e:
        print(f"Error fetching product: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the product.")
    






@router.post('/add_products')
async def insert_product(new_product: Products,user_id: str = Depends(oauth2.get_current_user),products_collection: Collection = Depends(get_product_collection)):
    try:
        # resp = collection.insert_one(dict(new_product))
        # product_data = new_product.dict()
        product_data = new_product.model_dump()
        product_data['created_by'] = user_id
        result = products_collection.insert_one(product_data)
        return {"status": "success", "message": "Product has been successfully added!", "product_id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error inserting product: {e}")
        return HTTPException(status_code=500, detail=f'some error occured')
    
@router.delete('/delete/{id}')
async def delete_post(id:str,user_id: str = Depends(oauth2.get_current_user),products_collection: Collection = Depends(get_product_collection)):
    try:

        print("user",user_id)
        
        product_objectid = ObjectId(id)

        product = products_collection.find_one({"_id": product_objectid})

        print(product.get('created_by'))

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get('created_by') != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this product")
        
        result = products_collection.delete_one({"_id": product_objectid})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found or already deleted")
        
        return {"status": "success", "message": "Product deleted successfully"}
    
    # except HTTPException as e:
    #     # Handle HTTP errors specifically
    #     raise e
    except Exception as e:
        
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": f"An error occurred: Product Not Found"}
        )
    


@router.put("/update/{id}")
async def update_product(id: str, updated_product: ProductUpdate, user_id: str = Depends(oauth2.get_current_user), products_collection: Collection = Depends(get_product_collection)):
    try:
        
        product_objectid = ObjectId(id)
        product = products_collection.find_one({"_id": product_objectid})
        print(product)
        print(type(product))
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get('created_by') != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to Modify this product")
  
        

        print(updated_product)
        print(type(updated_product))
        
        update_data = {key: value for key, value in updated_product.model_dump(exclude_unset=True).items()}

        print(update_data)
        print(type(update_data))
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update.")
        
        
        result = products_collection.update_one({"_id": product_objectid}, {"$set": update_data})

        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Prepare response
        return {
            "status": "success",
            "message": "Product updated successfully"
        }

    except HTTPException as e:
        raise e
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": f"An error occurred: {str(e)}"}
        )


app.include_router(router)
app.include_router(user.router)
app.include_router(fileuploads.router)
